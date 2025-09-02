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
import json
import threading
import multiprocessing
import time
import pandas as pd
import webbrowser
import requests
import traceback
from queue import Queue

from wiliot_core import set_logger, InlayTypes
from wiliot_tools.utils.wiliot_gui.wiliot_gui import popup_message
from wiliot_testers.association_tester.modules.performance_module import ReelVerification
from wiliot_testers.association_tester.modules.association_module import TagAssociation
from wiliot_testers.association_tester.modules.gui_module import AssociationAndVerificationGUI
from wiliot_testers.association_tester.modules.configuration_module import RUN_PARAMS_FILE

pd.options.mode.chained_assignment = None  # default='warn'
INLAY_TYPE = InlayTypes.TIKI_121.name


class AssociationAndVerificationTester(object):
    def __init__(self, user_input):
        start_time = datetime.datetime.now()
        common_run_name = f"{user_input['run_name']}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        self.logger_path, self.logger = set_logger(app_name='AssociationAndVerificationTester',
                                                   common_run_name=common_run_name)
        self.logger_path = os.path.dirname(self.logger_path)
        self.run_data = {'common_run_name': common_run_name,
                         'tester_type': 'association_and_verification',
                         'inlay_type': INLAY_TYPE,
                         'station_name': os.environ['testerStationName']
                         if 'testerStationName' in os.environ else 'testStation',
                         'run_start_time': start_time}
        stop_event = multiprocessing.Event()
        exception_q = Queue(maxsize=100)
        self.app_running = True
        self.performance = None
        try:
            if user_inputs['do_verification']:
                self.performance = ReelVerification(user_input=user_inputs,
                                                    stop_event=stop_event,
                                                    is_app_running=self.is_app_running,
                                                    logger_name=self.logger.name,
                                                    logger_path=self.logger_path,
                                                    exception_q=exception_q)
            self.association = TagAssociation(user_input=user_inputs,
                                            stop_event=stop_event,
                                            is_app_running=self.is_app_running,
                                            logger_config={'logger_name': self.logger.name, 'logger_path': self.logger_path},
                                            exception_q=exception_q,
                                            run_param_file=RUN_PARAMS_FILE,
                                            )

            self.gui = AssociationAndVerificationGUI(logger_name=self.logger.name,
                                                    get_data_func=self.get_data,
                                                    get_stat_func=self.get_stat,
                                                    common_run_name=common_run_name,
                                                    stop_event=stop_event)
        except Exception as e:
            self.logger.warning(f'Got error during init: {e}')
            popup_message(f'Error during initialize the Tester: {e}')
            raise e
        self.user_inputs = user_input
        self.stop_event = stop_event
        self.exception_q = exception_q
        self.results_df = pd.DataFrame()
        self.current_stat = {'n_locations': '0',
                             'scan_success': '0%', 'association_success': '0%', 'responding_rate': '0%',
                             'n_success': '0', 'success_rate': '0%'}
        self.duplicated_code = pd.DataFrame()
        self.neglected_duplication = pd.DataFrame()
        self.performance_thread = None
        self.association_thread = None
        self.gui_thread = None

    def run(self):
        if self.user_inputs['do_verification']:
            self.performance_thread = threading.Thread(target=self.performance.run_app, args=())
            self.performance_thread.start()
        
        self.association_thread = threading.Thread(target=self.association.run_app, args=())
        self.association_thread.start()
        
        self.gui_thread = threading.Thread(target=self.gui.run_app, args=())
        self.gui_thread.start()

        webbrowser.open(self.gui.get_url())

        self.run_app()

    def run_app(self):
        while True:
            try:
                time.sleep(1)
                if self.gui.is_stopped_by_user():
                    self.logger.info('run stopped by user')
                    break
                elif self.app_running != self.gui.is_app_running():
                    self.logger.info(f'run was {"paused" if self.app_running else "continued"} by user')
                    self.app_running = not self.app_running

                if not self.exception_q.empty():
                    self.app_running = False
                    self.logger.warning('got exception during run, pause the app')
                    self.handle_exceptions()
                    break  # TODO only stop for some exceptions

                if self.app_running:
                    df_ass = self.association.get_locations_df()
                    df_per = self.get_packets_df()
                    self.merge_results(location_df=df_ass, packets_df=df_per)
                    self.current_stat = self.calc_stat()
                    self.handle_stop_criteria()
                    # save data:
                    self.save_location_data()
                    self.save_run_data()
                else:
                    time.sleep(1)
            except Exception as e:
                self.logger.warning(f'got exception during run: {e}')
                if not self.exception_q.full():
                    self.exception_q.put(f'Main: {e}')
                    self.logger.warning(f'Main: {(traceback.format_exc())}')

        # stop run
        self.stop()

    def get_packets_df(self):
        return self.performance.get_packets_df() if self.performance is not None else pd.DataFrame()

    def is_app_running(self):
        return self.app_running

    def handle_stop_criteria(self):
        if int(self.current_stat['n_successive_bad_scan']) >= int(self.user_inputs['sc_n_no_scan']):
            raise Exception(f"{self.current_stat['n_successive_bad_scan']} successive bad scanning were detected. "
                            f"Check if machine is stuck")

        if self.current_stat['is_duplicated']:
            self.neglected_duplication = self.duplicated_code.copy()
            raise Exception(f"{self.duplicated_code.values} codes duplications were detected. "
                            f"Check if machine is stuck")

        if int(self.current_stat['n_locations']) < int(self.user_inputs['sc_min_location']):
            return
        if self.user_inputs['do_association']:
            if float(self.current_stat['association_success'].replace('%', '')) < float(
                    self.user_inputs['sc_association']):
                self.user_inputs['sc_association'] = 0  # pop only once
                raise Exception(f"association yield of {self.current_stat['association_success']} was detected")
        if float(self.current_stat['scan_success'].replace('%', '')) < float(self.user_inputs['sc_scanning']):
            self.user_inputs['sc_scanning'] = 0  # pop only once
            raise Exception(f"scan yield of {self.current_stat['scan_success']} was detected")
        if self.user_inputs['do_verification']:
            if float(self.current_stat['responding_rate'].replace('%', '')) < float(self.user_inputs['sc_responding']):
                self.user_inputs['sc_responding'] = 0  # pop only once
                raise Exception(f"responding yield of {self.current_stat['responding_rate']} was detected")

    def handle_exceptions(self):
        n_exceptions = self.exception_q.qsize()
        exceptions_str = []
        for _ in range(n_exceptions):
            exceptions_str.append(self.exception_q.get())
        self.logger.warning('\n'.join(exceptions_str))
        popup_message('\n'.join(exceptions_str))

    def print_run(self):  # for debug
        t_i = time.time()
        while time.time() - t_i < 60:
            try:
                time.sleep(2)
                df_ass = self.association.get_locations_df()
                print(f'n unique locations: {len(df_ass)}')
                df_per = self.get_packets_df()
                print(f'n unique adva: {len(df_per)}')
                self.merge_results(location_df=df_ass, packets_df=df_per)
                print(f'n all results: {len(self.results_df)}')
                stat = self.calc_stat()
                print(stat)
            except Exception as e:
                self.logger.warning(f'got exception during print_run: {e}')

        # stop run
        self.stop_event.set()
        self.stop()

    def calc_stat(self):
        stat_out = {}
        if self.results_df.empty:
            rel_data = []
        else:
            rel_data = self.results_df.loc[~(self.results_df['location'].isna()) & ~(self.results_df['location'] == '')]
        n_location = len(rel_data)
        stat_out['n_locations'] = str(n_location)
        stat_out['n_tags_outside_test'] = str(len(self.results_df) - n_location)
        if n_location > 0:
            stat_out['scan_success'] = f'{round(rel_data["scan_status"].sum() / n_location * 100, 2)}%'
            ass_valid = rel_data["is_associated"][rel_data["associate_status_code"] != '']
            stat_out['association_success'] = f'{round(ass_valid.sum() / max([ass_valid.count(), 1]) * 100, 2)}%'
            if 'n_packets' in rel_data.keys():
                respond_valid = rel_data["n_packets"][rel_data["wiliot_code"] != '']
                stat_out['responding_rate'] = f'{round(respond_valid.notna().sum() / len(respond_valid) * 100, 2)}%'
            else:
                stat_out['responding_rate'] = '0%'
            stat_out['n_successive_bad_scan'] = \
                rel_data['location'].iloc[-1] - rel_data['location'][rel_data['scan_status']].iloc[-1] \
                    if any(rel_data['scan_status']) else n_location

            df_per_loc = rel_data.drop_duplicates(subset=['location'])
            self.duplicated_code = pd.concat([
                df_per_loc['asset_code'].loc[
                    (df_per_loc.duplicated(subset=['asset_code']) & (df_per_loc['asset_code'] != ''))],
                df_per_loc['wiliot_code'].loc[
                    (df_per_loc.duplicated(subset=['wiliot_code'])) & (df_per_loc['wiliot_code'] != '')]
            ], axis=0)
            stat_out['is_duplicated'] = len(self.duplicated_code) > len(self.neglected_duplication)
            if 'is_success' in rel_data.keys():
                stat_out['n_success'] = f'{rel_data["is_success"].sum()}'
                stat_out['success_rate'] = f'{round(rel_data["is_success"].sum() / n_location * 100, 2)}%'
            else:
                stat_out['n_success'] = '0'
                stat_out['success_rate'] = '0%'
        else:
            stat_out['scan_success'] = '0%'
            stat_out['association_success'] = '0%'
            stat_out['responding_rate'] = '0%'
            stat_out['n_successive_bad_scan'] = 0
            stat_out['is_duplicated'] = False
            stat_out['n_success'] = '0'
            stat_out['success_rate'] = '0%'

        return stat_out

    def shutdown_server(self):
        try:
            requests.post(f'{self.gui.get_url()}shutdown')
        except Exception as e:
            pass

    def stop(self):
        self.stop_event.set()
        time.sleep(2)
        self.shutdown_server()
        all_threads = {'Performance': self.performance_thread, 'Association': self.association_thread, 'Gui': self.gui_thread}
        for t_name, t in all_threads.items():
            if t is not None:
                t.join(15)
                if t.is_alive():
                    self.logger.warning(f'{t_name} thread is still running')

        # summary
        df_ass = self.association.get_locations_df()
        df_per = self.get_packets_df()
        self.merge_results(location_df=df_ass, packets_df=df_per)
        self.current_stat = self.calc_stat()

        self.save_location_data()
        self.save_run_data()

        # handle exceptions:
        if not self.exception_q.empty():
            self.handle_exceptions()

        # show results:
        stat_out_str = "\n".join([f'{k}: {v}' for k, v in self.current_stat.items()])
        if self.user_inputs['do_scan_verification']:
            popup_message('make sure last labels are printed correctly')
        if self.user_inputs['do_association'] and self.is_bad_association_occurred():
            popup_message('Run contains Association Failure, please run and check Association report Manually', bg = 'red')
        popup_message(f'{self.run_data["common_run_name"]}\n\n{stat_out_str}')

    def save_run_data(self):
        df_path = os.path.join(self.logger_path, f'{self.run_data["common_run_name"]}@run_data.csv')
        print(f'saving run config at: {df_path}')
        data_to_save = pd.DataFrame({**self.run_data, **{'end_run_time': datetime.datetime.now()}, **self.current_stat,
                                     **self.user_inputs}, index=[0])
        data_to_save.to_csv(df_path, index=False)

    def save_location_data(self):
        if self.results_df.empty:
            return
        df_path = os.path.join(self.logger_path,
                               f'{self.run_data["common_run_name"]}@packets_data.csv')
        print(f'saving data at: {df_path}')
        data_to_save = self.results_df.loc[~self.results_df['location'].isna()]
        data_to_save.sort_values(by='location', inplace=True)
        data_to_save.to_csv(df_path, index=False)

    def is_bad_association_occurred(self):
        return float(self.current_stat['association_success'].replace('%', '')) < 100.0


    def get_data(self):
        return self.results_df

    def get_stat(self):
        return self.current_stat

    def merge_results(self, location_df, packets_df):
        if packets_df.empty and location_df.empty:
            return

        merged_df = None
        if packets_df.empty:
            merged_df = location_df
        else:
            packets_df.index = packets_df.index.set_names(['adv_address'])
            packets_df = packets_df.reset_index()

        if location_df.empty:
            merged_df = packets_df
            merged_df.insert(loc=0, column='location', value='')
            if 'n_packets' not in merged_df.keys():
                merged_df.insert(loc=0, column='n_packets', value=0)

        if merged_df is None:
            merged_df = pd.merge(location_df, packets_df, left_on='wiliot_code', right_on='external_id', how='outer')
        
        if 'n_packets' in merged_df.keys():
            is_responded = merged_df['n_packets'].apply(lambda x: int(x) > 0 if not pd.isnull(x) else False)
        else:
            is_responded = pd.Series([not self.user_inputs['do_verification']] * merged_df.shape[0], index=merged_df.index)
        if self.user_inputs['do_association']:
            is_success = pd.DataFrame([merged_df['scan_status'], merged_df['is_associated'], is_responded]).all()
        else:
            is_success = pd.DataFrame([merged_df['scan_status'], is_responded]).all()
        
        if 'is_success' in merged_df.keys():
            merged_df = merged_df.drop(columns='is_success')
        if 'common_run_name' in merged_df.keys():
            merged_df = merged_df.drop(columns='common_run_name')
        
        merged_df.insert(loc=len(merged_df.columns), column='is_success', value=is_success)
        merged_df.insert(loc=0, column='common_run_name', value=self.run_data['common_run_name'])

        self.results_df = merged_df


if __name__ == '__main__':
    from wiliot_testers.association_tester.modules.configuration_module import get_user_inputs, get_params, GUI_FILE, DEFAULT_VALUES
    user_inputs = get_user_inputs()
    print(user_inputs)
    av = AssociationAndVerificationTester(user_input=user_inputs)
    av.run()

    print('done')
