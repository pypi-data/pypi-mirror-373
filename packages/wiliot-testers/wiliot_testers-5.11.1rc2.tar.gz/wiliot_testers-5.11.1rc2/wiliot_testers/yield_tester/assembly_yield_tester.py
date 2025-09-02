"""
Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""
import datetime
import os
import sys
import time
import json
from math import nan
from queue import Queue
import matplotlib
import pandas as pd
import threading
import numpy as np
import webbrowser

from wiliot_core import set_logger, GetApiKey
from wiliot_tools.resolver_tool.resolve_packets import ResolvePackets
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui, popup_message
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.tester_utils import dict_to_csv
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_testers.yield_tester.modules.first_gui import open_session, preparing_layout, ConversionTypes
from wiliot_testers.yield_tester.modules.adva_process import AdvaProcess
from wiliot_testers.yield_tester.modules.sensors_yield import SensorsYield
from wiliot_testers.yield_tester.modules.yield_gui import YieldPlotting
from wiliot_testers.yield_tester.utils.resolve_utils import ENV_RESOLVE, YieldTagStatus


DEFAULT_USER_INPUTS = {
    "max_temperature": 40,
    "min_temperature": 10,
    "temperature_type": "C",
    "min_humidity": 30,
    "max_humidity": 60,
    "min_light_intensity": 0,
    "max_light_intensity": 100,
    "max_y_axis": 110,
    "red_line_cumulative": 90,
    "red_line_current": 70,
    "pin_number": "004",
    "rssi_threshold": 80,
    "time_between_matrices_sec": 5,
    "resolve_wait_after_run": "no",
    "ignore_adva_before_triggers": True,
    "port": 8008,
    "host": "127.0.0.3"
        }


matplotlib.use('TkAgg')


class MainWindow:
    """
    The main class the runs the GUI and supervise the multi-threading process of fraction's calculation and GUI viewing
    """

    def __init__(self, do_init_app_config=True):
        self.tester_type = 'yield'
        self.main_gui_instance = None
        self.first_gui_vals = None
        self.last_processed_index = 0
        self.current_values = None
        self.main_gui = None
        self.test_started = True
        self.logger = None
        self.adva_process = None
        self.adva_process_thread = None
        self.resolver_thread = None
        self.yield_gui_thread = None
        self.sensors = None
        self.sensors_thread = None
        self.resolve_path = ''
        self.external_ids = []
        self.resolver = None
        self.resolve_q = Queue(maxsize=1000)
        self.packet_and_triggers_q = Queue(maxsize=1000)
        self.user_event_q = Queue(maxsize=100)
        self.folder_path = None
        self.run_data_path = None
        self.run_data_dict = None
        self.stop = threading.Event()
        self.cmn = ''
        self.packets_data_path = None
        self.advas_before_tags = set()
        self.fig_canvas_agg1 = None
        self.machine_type = 'assembly_yield_tester'
        self.yield_df = pd.DataFrame({'matrix_advas': 0, 'matrix_external_ids': 0, 'trigger_time': 0.0}, index=[0])
        self.user_inputs = self.init_user_inputs()
        self.inlays = self.init_inlays()

        if do_init_app_config:
            self.init_app_configuration()

    def init_app_configuration(self):
        # pop up GUI configuration:
        self.first_gui_setup()

        # init all proccess based on user selection
        self.setup_logger_and_paths()
        self.init_processes()
        self.init_run_data()
        self.start_processes()

    ###############  BEFORE RUN FUNCTIONS ###############

    def setup_logger_and_paths(self):
        """
        Sets logger and paths for the run
        @return:
        """
        cur_time_formatted = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.cmn = self.get_cmn(cur_time_formatted)
        logger_path, self.logger = set_logger(app_name=self.machine_type, common_run_name=self.cmn,
                                              folder_name=self.get_folder_name())
        self.folder_path = os.path.dirname(logger_path)
        self.run_data_path = os.path.join(self.folder_path, self.cmn + '@run_data.csv')
        self.packets_data_path = os.path.join(self.folder_path, self.cmn + '@packets_data.csv')
        self.resolve_path = os.path.join(self.folder_path, self.cmn + '@resolve_data.csv')

    def init_inlays(self):
        inlay_data_path = os.path.join(os.path.dirname(__file__), 'configs', 'inlay_data.json')
        inlay_data_eng_path = os.path.join(os.path.dirname(__file__), 'configs', 'inlay_data_eng.json')
        if os.path.exists(inlay_data_eng_path):
            with open(inlay_data_eng_path) as f:
                inlays = json.load(f)
        else:
            with open(inlay_data_path) as f:
                inlays = json.load(f)
        return inlays

    def init_user_inputs(self, default_values=DEFAULT_USER_INPUTS): 
        script_dir = os.path.dirname(__file__)
        json_file_path = os.path.join(script_dir, 'configs', 'user_inputs.json')
        try:
            with open(json_file_path) as f:
                user_inputs = json.load(f)
            for key, value in default_values.items():
                if key not in user_inputs:
                    user_inputs[key] = value
            with open(json_file_path, 'w') as f:
                json.dump(user_inputs, f, indent=4)
        except Exception as e:
            print('could not read the user input file, default values are set')
            user_inputs = default_values
            os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
            with open(json_file_path, 'w') as f:
                json.dump(user_inputs, f, indent=4)
        return user_inputs

    def init_run_data(self):
        """
        Initialize run data csv file.
        @return:
        """
        py_wiliot_version = get_version()
        start_time = datetime.datetime.now()
        run_start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        self.run_data_dict = {
            'common_run_name': self.cmn, 'tester_station_name': self.first_gui_vals.get('tester_station_name', ''),
            'gw_version': self.adva_process.get_gw_version(),
            'tester_type': self.tester_type,
            'operator': self.first_gui_vals.get('operator', ''), 
            'received_channel': self.inlays[self.first_gui_vals['selected']]['received_channel'],
            'run_start_time': run_start_time, 'run_end_time': '',
            'wafer_lot': self.first_gui_vals.get('wafer_lot', ''),
            'wafer_number': self.first_gui_vals.get('wafer_number', ''),
            'assembled reel': self.first_gui_vals.get('assembled_reel', ''),
            'lane_ids': self.first_gui_vals.get('lane_ids', ''),
            'window_size': self.first_gui_vals.get('window_size', ''), 'upload_date': '',
            'gw_energy_pattern': self.first_gui_vals.get('gw_energy_pattern', ''),
            'comments': self.first_gui_vals.get('comments', ''), 'inlay': self.first_gui_vals['selected'], 'total_run_tested': 0,
            'total_run_responding_tags': 0,
            'conversion_type': ConversionTypes.NOT_CONVERTED.value,
            'surface': self.first_gui_vals.get('surface', ''),
            'matrix_tags': str(self.first_gui_vals.get('matrix_size', '')), 'py_wiliot_version': py_wiliot_version,
            'number_of_columns': self.first_gui_vals.get('thermodes_col', ''),
            'number_of_lanes': self.first_gui_vals.get('rows_number', ''),
            'gw_time_profile': self.first_gui_vals.get('gw_time_profile', '')
        }

    def first_gui_setup(self):
        """
        Does all the work of the first gui.
        @return:
        """
        previous_input, inlay_info_dict = preparing_layout(inlays=self.inlays)
        layout, cols_or_rows = self.open_session_layout(previous_input=previous_input, inlay_info=inlay_info_dict)
        self.first_gui_vals = open_session(open_session_layout=layout, cols_or_rows=cols_or_rows, inlays=self.inlays, 
                                           gui_title=self.machine_type.replace('_', ' ').title())

    def get_cmn(self, time_str):
        """
        Creates the common run name of the files we want to save.
        @param day_str: Date of the day
        @param time_str: time stamp
        @return: common run name
        """
        return '{wafer_lot}.{wafer_number}_{time}'.format(wafer_lot=self.first_gui_vals['wafer_lot'],
                                                                wafer_number=self.first_gui_vals['wafer_number'],
                                                                time=time_str)

    def get_folder_name(self):
        return '{}.{}'.format(self.first_gui_vals['wafer_lot'], self.first_gui_vals['wafer_number'])

    def open_session_layout(self, previous_input, inlay_info):
        """
        Returns GUI as dictionary for wiliotGUI
        @param previous_input: Dictionary of default values.
        @param inlay_info: Info about Inlay we take from data_inlay/data_inlay_eng
        @return: GUI as dictionary for wiliotGUI
        """
        cols_or_rows = 'thermodes_col'
        open_session_layout = {
            'wafer_lot': {'text': 'Wafer Lot:', 'value': previous_input['wafer_lot'], 'widget_type': 'entry'},
            'wafer_num': {'text': 'Wafer Number:', 'value': previous_input['wafer_num'], 'widget_type': 'entry'},
            'thermodes_col': {'text': 'Number of Columns:', 'value': previous_input['thermodes_col'],
                              'widget_type': 'entry'},
            'matrix_tags': {'text': '', 'widget_type': 'label',
                            'value': f'Total Tags per Matrix: {str(inlay_info["default_matrix_tags"])}'},
            'inlay_dict': [
                {'inlay': {'text': 'Inlay:', 'value': previous_input['inlay_dict_inlay'], 'widget_type': 'combobox',
                           'options': list(self.inlays.keys())}},
                {'inlay_info': {'widget_type': 'label', 'value': inlay_info['inlay_info']}},
            ],
            'tester_station_name': {'text': 'Tester Station:', 'value': previous_input['tester_station_name'],
                                    'widget_type': 'entry'},
            'comments': {'text': 'Comments:', 'value': previous_input['comments'], 'widget_type': 'entry'},
            'operator': {'text': 'Operator:', 'value': previous_input['operator'], 'widget_type': 'entry'},
            'surface': {'text': 'Surface:', 'value': previous_input['surface'], 'widget_type': 'combobox',
                        'options': inlay_info["surfaces"]},
            'window_size': {'text': 'Window Size for Analysis:', 'value': previous_input['window_size'],
                            'widget_type': 'entry'},
            'do_resolve': {'text': 'Get External Id from Cloud', 'value': previous_input['do_resolve']},
            'owner_id': {'text': 'Owner Id for Cloud Connection', 'value': previous_input['owner_id']},

        }

        return open_session_layout, cols_or_rows

    def get_app_errors(self):
        is_error = ''
        if self.adva_process is not None:
            if self.adva_process.gw_error_connection:
                is_error += (' Gateway was disconnected! Please try to manually disconnect and reconnect.')
        return is_error
        

    ###############  RUNNING CLASS FUNCTIONS ###############

    def init_processes(self, sensors_type=None):
        """
        Initializing the two main instances and threads in order to start working
        @param inlay_select: Inlay type we are running
        @param rssi_th: RSSI threshold we want to filter according to it.
        @return:
        """
        state=''
        try:
            # init resolve
            state = 'init resolve'
            if self.first_gui_vals['do_resolve']:
                self.resolver = ResolvePackets(tags_in_test=[], owner_id=self.first_gui_vals['owner_id'], env=ENV_RESOLVE, resolve_q=self.resolve_q,
                                               set_tags_status_df=self.updated_resolved_tags, stop_event_trig=self.stop,
                                               logger_name=self.logger.name, gui_type='ttk', tag_status=YieldTagStatus,
                                               wait_after_run=self.user_inputs.get('resolve_wait_after_run').lower() == 'yes',
                                               do_parallel_request=True)
                self.resolver_thread = threading.Thread(target=self.resolver.run, args=())
            # init sensors:
            state = 'init sensors'
            self.sensors = SensorsYield(stop_event=self.stop, logger=self.logger, sensors_type=sensors_type)
            if self.sensors.is_sensor_enable():
                self.sensors_thread = threading.Thread(target=self.sensors.run, args=())
            # init adva process:
            state = 'init adva process'
            adva_process_inputs = {'selected_inlay': self.inlays.get(self.first_gui_vals['selected']), 'listener_path': self.folder_path,
                                   'cmn': self.cmn, 'user_inputs': self.user_inputs}
            self.adva_process = AdvaProcess(stop_event=self.stop, logger=self.logger,
                                            adva_process_inputs=adva_process_inputs,
                                            packet_and_triggers_q=self.packet_and_triggers_q,
                                            get_sensors_values=self.sensors.get_sensors_data,
                                            ignore_adva_before_triggers=self.user_inputs['ignore_adva_before_triggers'])
            self.adva_process_thread = threading.Thread(target=self.adva_process.run, args=())

            #init GUI process:
            state = 'init GUI process'
            self.yield_gui = YieldPlotting(get_data=self.get_yield_df,
                                           get_sensors_data=self.sensors.get_sensors_data,
                                           get_app_errors=self.get_app_errors,
                                           cmd_q=self.user_event_q,
                                           user_config={**self.first_gui_vals, **self.user_inputs},
                                           logger=self.logger,
                                           stop_event=self.stop,
                                           tester_name=self.machine_type)
            self.yield_gui_thread = threading.Thread(target=self.yield_gui.run, args=())
            webbrowser.open(f"http://{self.user_inputs['host']}:{self.user_inputs['port']}/")
            
        except Exception as e:
            self.logger.warning(f"{e}")
            popup_message(msg=f'{state} FAILED due to:\n{e}', logger=self.logger)
            sys.exit(-1)

    def start_processes(self):
        """
        Starting the work of the both threads
        @return:
        """
        self.adva_process_thread.start()
        if self.sensors_thread is not None:
            self.sensors_thread.start()
        if self.resolver_thread is not None:
            self.resolver_thread.start()
        self.yield_gui_thread.start()

    def run(self):
        """
        Viewing the window and checking if the process stops
        @return:
        """
        self.logger.info('Start Yield Update Data Run')
        while True:
            try:
                if self.stop.is_set():
                    self.logger.info('Stop Yield Update Data Run')
                    break

                self.update_data()
                self.handle_user_events()
                time.sleep(0.100 if self.packet_and_triggers_q.empty() else 0)
            except Exception as e:
                self.logger.warning(f'got exception during yield update data run: {e}')

        self.stop_yield()

    def handle_user_events(self):
        if self.user_event_q.empty():
            return
        user_event = self.user_event_q.get()
        if 'start' in user_event.lower():
            self.adva_process.set_stopped_by_user(stopped=False)
        elif 'pause' in user_event.lower():
            self.adva_process.set_stopped_by_user(stopped=True)
        elif 'stop' in user_event.lower():
            self.stop.set()
        else:
            self.logger.warning(f'handle_user_events: Unsupported commamd: {user_event}')


    def stop_yield(self):
        """
        All the work when the application is stopped (User interaction or Error).
        @return:
        """
        final_tags = self.get_number_of_tested()
        total_ex_ids = self.yield_df['matrix_external_ids'].sum()
        total_advas = self.yield_df['matrix_advas'].sum()

        self.logger.info(
            f'Final Adva Yield: {(total_advas / final_tags) * 100 if final_tags > 0 else 0}%, '
            f'Final External Ids Yield: {(total_ex_ids / final_tags if final_tags > 0 else 0) * 100}%, '
            f'Final Tags: {final_tags}, Final Advas: {total_advas}, Final External Ids: {total_ex_ids}'
            )
        self.logger.info(f"User quit from application")

        # wait to all thread to join
        threads = {'adva process': self.adva_process_thread, 'resolver': self.resolver_thread, 'sensors': self.sensors_thread, 'gui': self.yield_gui_thread}
        for n, thr in threads.items():
            if thr is None:
                continue
            thr.join(timeout=5)
            if thr.is_alive():
                self.logger.warning(f'thread {n} is still running')
            else:
                self.logger.info(f'thread {n} is completed')
        
        self.update_data()

        is_uploaded = self.upload_to_cloud()
        self.update_run_data_file(is_uploaded)
        sys.exit()

    ###############  RESOLVE FUNCTIONS ###############

    def updated_resolved_tags(self, tag_status):
        """
        Updating resolve data.
        """
        tag_status = {k: v[0] for k, v in tag_status.items()}
        new_ex_id = tag_status['external_id']
        if new_ex_id.lower() in ['unknown', 'n/a']:
            new_ex_id += tag_status['tag']
        matrix_num = tag_status['matrix_num']
        self.logger.info(f'update resolved tags: {new_ex_id}')
        if new_ex_id not in self.external_ids:
            self.external_ids.append(new_ex_id)
            self.yield_df.loc[matrix_num, 'matrix_external_ids'] += 1
        
        dict_to_csv(dict_in=tag_status, path=self.resolve_path, append=os.path.exists(self.resolve_path))

    def add_to_resolve_queue(self, packet_list_in, adva_to_matrix_location):
        """
        Adds resolve data to the queue while running.
        """
        for packet_in in packet_list_in:
            adva = packet_in.get_adva()
            matrix_num = adva_to_matrix_location[adva_to_matrix_location['adv_address'] == adva]['matrix_tags_location']
            if matrix_num.empty:
                self.logger.warning(f'add_to_resolve_queue: could not find adva: {adva} in the adva_to_matrix_location df')
                continue
            matrix_num = int(matrix_num.values[-1])
            if self.resolve_q.full():
                self.logger.warning(f'Resolve queue is full. Discard the following adva: {adva}')
                continue
            self.resolve_q.put({'tag': adva, 'payload': packet_in.get_payload(), 'matrix_num': matrix_num})

    ###############  UPDATES FUNCTIONS ###############

    def process_new_df(self, new_data):
        new_df = new_data['packet'].get_df(sprinkler_filter=True)
                
        matrix_location_ind = np.searchsorted(self.yield_df['trigger_time'], new_df['time_from_start']) - 1

        new_df.insert(loc=0, column='common_run_name', value=self.cmn)
        new_df.insert(loc=1, column='matrix_tags_location', value=self.yield_df.index[matrix_location_ind].values)
        new_df.insert(loc=2, column='matrix_timestamp', value=self.yield_df['trigger_time'].iloc[matrix_location_ind].values)
        new_df.insert(loc=3, column='tag_matrix_ttfp', value=(new_df['time_from_start'] - new_df['matrix_timestamp']).values)
        
        new_df.insert(loc=len(new_df.columns), column='environment_light_intensity', value=new_data['sensors'].get('light_intensity'))
        new_df.insert(loc=len(new_df.columns), column='environment_humidity', value=new_data['sensors'].get('humidity'))
        new_df.insert(loc=len(new_df.columns), column='environment_temperature', value=new_data['sensors'].get('temperature'))
        return new_df

    def process_new_triggers(self, new_triggers):
        new_rows_df = pd.DataFrame()
        new_rows = {'trigger_num': [], 'trigger_time': []}
        for t in new_triggers:
            if t['trigger_num'] in self.yield_df.index:
                continue
            new_rows['trigger_num'].append(t['trigger_num'])
            new_rows['trigger_time'].append(t['trigger_time'])
        if new_rows['trigger_num']:
            new_rows_df = pd.DataFrame({'trigger_time': new_rows['trigger_time']}, index=new_rows['trigger_num'])
            new_rows_df.insert(loc=len(new_rows_df.columns), column='matrix_advas', value=0)
            new_rows_df.insert(loc=len(new_rows_df.columns), column='matrix_external_ids', value=0)

        return new_rows_df


    def update_data(self):
        """
        Updates the run_data CSV file while running the program
        @return:
        """
        if self.packet_and_triggers_q.empty():
            return
        
        new_data = self.packet_and_triggers_q.get()
        # update triggers
        new_matrix_df = self.process_new_triggers(new_data['trigger'])
        self.yield_df = pd.concat([self.yield_df, new_matrix_df])

        if len(new_data['packet']):
            # update main df
            new_df = self.process_new_df(new_data=new_data)
            new_n_advas = new_df.groupby('matrix_tags_location').size()
            self.yield_df.loc[new_n_advas.index, 'matrix_advas'] += new_n_advas.values

            # send to resolve:
            if self.first_gui_vals['do_resolve']:
                self.add_to_resolve_queue(new_data['packet'], new_df)

            # log files
            if not os.path.exists(self.packets_data_path):
                new_df.to_csv(self.packets_data_path, mode='w', header=True, index=False)
            else:
                new_df.to_csv(self.packets_data_path, mode='a', header=False, index=False)
        
        self.update_run_data_file()
        self.logger.info(f"last 10 rows of yield df:\n{self.yield_df.tail(10)}")

    def update_run_data_file(self, is_uploaded=False):

        """
        Updates the run_data CSV file while running the program
        @param is_uploaded: If to update the upload date at the end of the run or not
        @return:
        """
        end_time = datetime.datetime.now()
        run_end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        advas = self.yield_df['matrix_advas'].sum()
        tags_num = self.get_number_of_tested()
        result = float(100 * (advas / tags_num)) if tags_num != 0 else float('nan')

        if is_uploaded:
            self.run_data_dict['upload_date'] = run_end_time
        self.run_data_dict['run_end_time'] = run_end_time
        self.run_data_dict['total_run_tested'] = tags_num
        self.run_data_dict['total_run_responding_tags'] = advas
        self.run_data_dict['yield'] = result
        if self.first_gui_vals['do_resolve']:
            self.run_data_dict['total_run_external_ids'] = self.yield_df['matrix_external_ids'].sum()
            self.run_data_dict['yield_external_ids'] = 100 * (
                    self.run_data_dict['total_run_external_ids'] / tags_num) if tags_num else 0
        dict_to_csv(dict_in=self.run_data_dict, path=self.run_data_path)

    def get_number_of_tested(self):
        """
        Return number of tested tags.
        @return: number of tested tags.
        """
        tags_num = self.yield_df.index[-1] * int(self.first_gui_vals['matrix_size'])
        return tags_num
    
    def get_yield_df(self):
        return self.yield_df
    
    ################ UPLOAD FUNCTION ###############
    def do_upload(self, env_choice, owner_id):
        try:
            # make sure user have the api key:
            GetApiKey(owner_id=owner_id, env=env_choice)
            tester_type = self.tester_type.replace('_', '-') + '-test'
            is_uploaded = upload_to_cloud_api(batch_name=self.cmn, tester_type=tester_type,
                                              run_data_csv_name=self.run_data_path, env=env_choice, is_path=True,
                                              packets_data_csv_name=self.packets_data_path, owner_id=owner_id)

        except Exception as ee:
            is_uploaded = False
            self.logger.warning(f"do_upload: Exception occurred: {ee}")
        return is_uploaded

    def upload_to_cloud(self):
        """
        All the process of uploading data to cloud.
        @return:
        """
        is_uploaded = False
        yes_or_no = ['Yes', 'No']
        upload_layout = {'ask_to_upload': {'widget_type': 'label', 'value': 'Do you want to stop or upload?'},
                             'upload': {'text': 'Upload:', 'value': yes_or_no[0], 'widget_type': 'combobox',
                                        'options': yes_or_no},
                             'env_choice': {'text': 'Select Environment:', 'value': 'prod', 'widget_type': 'combobox',
                                            'options': ['prod', 'test']},
                             'owner_id': {'text': 'Owner Id', 'value': self.first_gui_vals['owner_id'],
                                          'widget_type': 'entry'}
                             }
        upload_gui = WiliotGui(params_dict=upload_layout, title='Upload to cloud', exit_sys_upon_cancel=False)
        values_out = upload_gui.run()
        if values_out and values_out['upload'] == 'Yes':
            is_uploaded = self.do_upload(env_choice=values_out['env_choice'], owner_id=values_out['owner_id'])
            if is_uploaded:
                self.logger.info("Successful upload")
                popup_message(msg="Successfully upload data to cloud!", logger=self.logger, bg='green')
            else:
                self.logger.info('Failed to upload the file')
                popup_message(msg="Run upload failed.\n Please check Internet connection and upload logs manually", logger=self.logger, bg='red')

        else:
            self.logger.info('File was not uploaded')
        return is_uploaded
if __name__ == '__main__':
    m = MainWindow()
    m.run()
