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

import threading
try:
    import tkinter
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    import pygubu
except Exception as e:
    print(f'could not import tkinter or pygubu: {e}')

import numpy
from os import makedirs, mkdir
import pandas as pd
from threading import Thread
from time import sleep
import time
import datetime
from json import load, dump
from os.path import isfile, abspath, dirname, join
from enum import Enum

from wiliot_core import InlayTypes, GetApiKey
from wiliot_testers.sample.configs_gui import ConfigsGui, OUTPUT_DIR, CONFIGS_DIR, TESTER_NAME
from wiliot_testers.sample.com_connect import ComConnect, GO, CONTINUE, CONNECT_HW, READ
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.config.unusable_inlays import UnusableInlayTypes
from wiliot_testers.utils.upload_to_cloud_api import *
from wiliot_testers.wiliot_tester_tag_result import FailBinSample
from wiliot_testers.wiliot_tester_log import WiliotTesterLog, dict_to_csv
from wiliot_testers.sample.sample_slim import SampleRun, TagStatus

RESOLVE_ENV = 'prod'

SEND = 'Send'
STOP = 'Stop'
FINISH = 'Finish'
RSSI_THR_DEFAULT = 80
TIME_BETWEEN_CALIB_RUNS = 5  # seconds
TAG_COUNTER_LEN = 4
TBP_CALC = 'tbp_mean'


class FailureCodeSampleTest(Enum):
    NONE = 0
    PASS = 1  # Pass
    NO_RESPONSE = 3
    NO_TBP = 5
    HIGH_TBP_AVG = 7
    NOT_COMPLETED = 9


class SampleTest(object):
    stop_event = threading.Event()
    sample_run_obj = None
    go_button_state = CONNECT_HW
    stop_button_state = STOP
    com_connect = None
    configs_gui = None
    testBarcodesThread = None
    finish_thread = None
    closeChambersThread = None
    timer_thread = None
    post_data = True
    force_close_requested = False
    closeRequested = False
    closeListener = False
    is_test_pass = False
    test_configs = ''
    reel_id = ''
    owner = ''
    station_name = ''
    pywiliot_version = ''
    test_time = 0
    sleep = 0
    cur_atten = 0
    test_num = 0
    default_config = {}
    run_data = {}
    all_tags_in_test = {}
    all_results = pd.DataFrame()
    results_df = pd.DataFrame()
    tags_under_test = {}
    antenna = ''
    low = 0
    high = 0
    step = 1
    n_repetitions = 1
    logger = logging.getLogger(TESTER_NAME)

    def __init__(self):
        global SEND
        self.test_is_running = False
        self.set_logger()
        self.calib = False
        self.offline = False
        self.environment = 'prod'
        self.post_data = True

        self.pywiliot_version = get_version()
        self.logger.info(f'PyWiliot version: {self.pywiliot_version}')

        defaults_file_path = abspath(join(CONFIGS_DIR, '.defaults.json'))
        defaults_old_file_path = abspath(join(dirname(dirname(CONFIGS_DIR)),
                                              'common', 'sample_test', 'configs', '.defaults.json'))
        if isfile(defaults_file_path):
            with open(defaults_file_path, 'r') as defaults:
                self.default_config = load(defaults)
        elif isfile(defaults_old_file_path):
            with open(defaults_old_file_path, 'r') as defaults:
                self.default_config = load(defaults)

        self.popup_login()
        self.check_cloud_connection()
        if self.calib or self.offline:
            SEND = 'Log'
            self.post_data = False

        self.builder = builder = pygubu.Builder()
        self.ttk = Tk()

        self.com_connect = ComConnect(top_builder=builder, new_tag_func=self.add_tag_to_test,
                                      update_go=self.update_go_state, default_dict=self.default_config,
                                      logger=self.logger,
                                      logger_dir=self.log_obj.log_path, tk_frame=self.ttk)
        self.update_data()
        self.configs_gui = ConfigsGui(top_builder=builder, tk_frame=self.ttk)
        self.logger.info(f'Sample test is up and running')

    def check_cloud_connection(self):
        k = GetApiKey(env=self.environment, owner_id=self.owner, gui_type='ttk')
        api_key = k.get_api_key()
        if api_key == '':
            raise Exception(f'Could not found an api key for owner id {self.owner_id} and env {self.env}')

    def set_logger(self):
        run_name = 'sample_' + datetime.datetime.now().strftime('%d%m%y_%H%M%S')
        self.log_obj = WiliotTesterLog(run_name=run_name)
        self.log_obj.set_logger(tester_name=TESTER_NAME)
        self.logger = self.log_obj.logger

    def gui(self):
        self.logger.info(f'Sample test setting the GUI')
        self.set_gui()
        self.logger.info(f'Sample test GUI is running')
        self.ttk.mainloop()

    def set_gui(self):
        uifile = abspath(join(abspath(dirname(__file__)), 'utils', 'sample_test.ui'))
        self.builder.add_from_file(uifile)

        img_path = abspath(join(abspath(dirname(__file__)), ''))
        self.builder.add_resource_path(img_path)
        img_path = abspath(join(abspath(dirname(__file__)), 'utils'))
        self.builder.add_resource_path(img_path)

        self.ttk.title("Wiliot Sample Test")
        self.mainWindow = self.builder.get_object('mainwindow', self.ttk)
        self.ttk.protocol("WM_DELETE_WINDOW", self.close)
        self.builder.connect_callbacks(self)

        self.builder.get_object('reelId').bind("<Key>", self.get_reel_id_cb)
        list_box = self.builder.get_object('scanned')
        scrollbar = self.builder.get_object('scrollbar1')
        list_box.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=list_box.yview)
        self.builder.get_object('scrollbar1').set(self.builder.get_object('scanned').index(ACTIVE),
                                                  self.builder.get_object('scanned').index(END))
        self.logger.info(f'checking available serial connection')
        self.com_connect.choose_com_ports()
        self.logger.info(f'setting up gui defaults')
        self.set_gui_defaults()

        self.builder.connect_callbacks(self)

        self.settings_combobox = self.builder.get_object('settings_combobox', self.ttk)
        self.settings_combobox.configure(values=['prod', 'test', 'dev'])
        self.settings_combobox.set('prod')
        self.settings_combobox.bind('<<ComboboxSelected>>', self.on_env_change_cb)

    def init_test(self):
        all_config = {'run': self.default_config,
                      'test': self.configs_gui.configs_test}
        test_cloud_config = {'is_online': not self.offline, 'owner_id': self.owner, 'env': RESOLVE_ENV}
        self.stop_event.clear()
        self.sample_run_obj = SampleRun(tags_in_test=list(self.tags_under_test.keys()),
                                        selected_test=self.test_configs,
                                        all_configs=all_config,
                                        cloud_config=test_cloud_config,
                                        gw_obj=self.com_connect.gateway,
                                        stop_event=self.stop_event,
                                        inlay=self.run_data['inlay'],
                                        logger_name=self.logger.name,
                                        hw_functions = {'attenuation': self.com_connect.set_attenuation})

    def init_data_log(self):
        test_name = self.builder.get_object('testName').get()
        makedirs(abspath(join(OUTPUT_DIR, test_name)), exist_ok=True)
        self.test_data_dir = abspath(join(OUTPUT_DIR, test_name, self.run_data['timestamp']))
        mkdir(self.test_data_dir)
        self.test_num = 0

    def tag_test(self):
        # init:
        self.init_test()
        self.com_connect.read_temperature_sensor()  # read temperature
        # start timer
        self.timer_thread = Thread(target=self.timer_count_down, args=())
        self.timer_thread.start()
        # start run:
        self.com_connect.set_attenuation(self.run_data)
        self.sample_run_obj.run()
        # end of run
        self.end_test()

    def end_test(self):
        self.stop_event.set()
        self.com_connect.read_temperature_sensor()  # read temperature

        if not self.calib:
            self.builder.get_object('stop')['state'] = 'disabled'
            self.iteration_finished()
        elif self.calib:
            self.post_process_iteration()
            self.calib_mode_clean_barcodes()

    def read_scanners_barcodes(self, indexes):
        self.com_connect.read_scanners_barcodes(indexes)

    def connect_all(self, gui=True):
        self.com_connect.connect_all(gui=gui)
        if self.com_connect.hwConnected:
            self.builder.tkvariables.get('go').set(READ)
            self.builder.get_object('read_qr')['state'] = 'normal'
            self.builder.get_object('reelId')['state'] = 'normal'
            self.builder.get_object('connect')['state'] = 'normal'
        else:
            self.builder.tkvariables.get('go').set(CONNECT_HW)
            self.builder.get_object('go')['state'] = 'normal'
            self.builder.get_object('connect')['state'] = 'normal'

    def add_tag_to_test(self, cur_id, reel_id, scanner_index=0, add_to_test=False):
        same_reel_id = self.reel_id == reel_id or (self.reel_id[-TAG_COUNTER_LEN:] == reel_id
                                                   if len(self.reel_id) > TAG_COUNTER_LEN else False)
        if self.reel_id != '' and not same_reel_id and not self.calib:
            do_test = popup_yes_no(f'Tag {cur_id} has a reel id different from test reel {self.reel_id}, '
                                   f'are you sure you want to include it in the test?')
            if not do_test:
                return False

        if add_to_test:
            if cur_id in self.tags_under_test.keys():
                self.com_connect.popup_message(f'Tag {cur_id} in chamber {scanner_index} already read in '
                                               f'another chamber: {self.tags_under_test[cur_id]["chamber"]}',
                                               title='Warning',
                                               log='warning')
                return False

            if cur_id in self.all_tags_in_test.keys() and not self.calib:
                retest = popup_yes_no(f'Tag {cur_id} was already tested, are you sure you want to re-test the tag?')
                if not retest:
                    return False
            # add tag to test
            self.tags_under_test[cur_id] = {'chamber': scanner_index}
            self.builder.get_object('scanned').insert(END, f'{cur_id}, {scanner_index}')

        return True

    def update_go_state(self, force_go=False):
        if self.com_connect.get_num_of_barcode_scanners() == len(self.tags_under_test.keys()) or force_go:
            if len(self.all_tags_in_test.keys()) == 0:
                self.builder.tkvariables.get('go').set(GO)
                self.update_params_state(state='normal', group=GO)
            else:
                self.builder.tkvariables.get('go').set(CONTINUE)
                self.update_params_state(state='normal', group=CONTINUE)
        else:
            self.builder.tkvariables.get('go').set(READ)
            self.update_params_state(state='normal', group=READ)

    def get_missing_ids_chambers(self):
        indexes = list(range(self.com_connect.get_num_of_barcode_scanners()))
        if len(self.tags_under_test.keys()) > 0:
            used_indexes = [barcode['chamber'] for barcode in self.tags_under_test.values()]
            indexes = [index for index in indexes if index not in used_indexes]
        return indexes

    def force_go_close_chambers(self):
        indexes = self.get_missing_ids_chambers()
        self.com_connect.close_chambers(indexes)
        self.update_go_state(force_go=True)
        self.builder.get_object('forceGo')['state'] = 'normal'
        self.builder.get_object('stop')['state'] = 'normal'
        self.builder.get_object('go')['state'] = 'normal'

    def wait_between_calib_runs(self):
        self.logger.info(f'wait between calib test for {TIME_BETWEEN_CALIB_RUNS} seconds')
        t_start = time.time()
        dt = time.time() - t_start
        while dt < TIME_BETWEEN_CALIB_RUNS:
            dt = time.time() - t_start
            if self.force_close_requested:
                break
            sleep(0.200)
        self.logger.info('continue to the next calib stage')

    def calib_mode(self):
        attenuation_list = numpy.arange(float(self.low), float(self.high) + float(self.step), float(self.step))
        n_rep = int(self.n_repetitions)
        for i, atten in enumerate(attenuation_list):
            if self.force_close_requested:
                break
            for j in range(n_rep):
                self.cur_atten = atten
                self.test_num = (i * n_rep) + j
                if self.antenna.lower() == 'ble':
                    self.run_data['bleAttenuation'] = self.cur_atten
                elif self.antenna.lower() == 'lora':
                    self.run_data['loraAttenuation'] = self.cur_atten

                self.tag_test()

                self.wait_between_calib_runs()
                if self.force_close_requested:
                    break

        self.com_connect.open_chambers()
        self.finish()
        self.com_connect.popup_message('Sample Test - Calib Mode Finished running.', title='Info', log='info')

    def calib_mode_clean_barcodes(self):
        old_barcodes = self.tags_under_test.copy()
        self.tags_under_test = {}
        self.all_tags_in_test = {}
        self.builder.get_object('scanned').delete(0, END)
        for ex_id, tag in old_barcodes.items():
            self.add_tag_to_test(ex_id, ex_id.split('T')[0], tag['chamber'], add_to_test=True)

    def update_params_state(self, state='disabled', group=GO):
        if group == READ:
            self.builder.get_object('connect')['state'] = state

            if len(self.all_tags_in_test.keys()) == 0:
                self.builder.get_object('read_qr')['state'] = state
                self.builder.get_object('reelId')['state'] = state

            if self.reel_id != '':
                self.builder.get_object('go')['state'] = state
                self.builder.get_object('add')['state'] = state
                self.builder.get_object('remove')['state'] = state
                self.builder.get_object('addTag')['state'] = state
                self.builder.get_object('stop')['state'] = state
                self.builder.get_object('forceGo')['state'] = state
            self.builder.get_object('settings_combobox')['state'] = state

        if group in [GO, CONNECT_HW, CONTINUE]:
            if group in [GO, CONTINUE]:
                self.builder.get_object('go')['state'] = state
                self.builder.get_object('connect')['state'] = state

            if group == GO:
                self.builder.get_object('configs')['state'] = state

            if group in [GO, CONNECT_HW]:
                self.builder.get_object('test_config')['state'] = state
                self.builder.get_object('testName')['state'] = state
                self.builder.get_object('operator')['state'] = state
                self.builder.get_object('inlay')['state'] = state
                self.builder.get_object('surface')['state'] = state
                self.builder.get_object('settings_combobox')['state'] = state
                if self.reel_id != '':
                    self.builder.get_object('stop')['state'] = state

            self.builder.get_object('add')['state'] = state
            self.builder.get_object('remove')['state'] = state
            self.builder.get_object('addTag')['state'] = state
            self.builder.get_object('settings_combobox')['state'] = state
            self.builder.get_object('forceGo')['state'] = 'disabled'

            if len(self.all_tags_in_test.keys()) == 0:
                self.builder.get_object('read_qr')['state'] = state
                self.builder.get_object('reelId')['state'] = state

    def set_gui_defaults(self):
        configs = self.configs_gui.get_configs()
        self.builder.get_object('test_config')['values'] = \
            [key for key, item in configs.items() if isinstance(item, dict)]

        if 'testName' in self.default_config.keys():
            self.builder.get_object('testName')['values'] = self.default_config['testName']
            self.builder.get_object('testName').set(self.default_config['testName'][0])

        if 'operator' in self.default_config.keys():
            self.builder.get_object('operator')['values'] = self.default_config['operator']
            self.builder.get_object('operator').set(self.default_config['operator'][0])

        self.builder.get_object('inlay')['values'] = tuple(
            name for name in InlayTypes._member_names_ if name not in UnusableInlayTypes.__members__)
        if 'inlay' in self.default_config.keys():
            self.builder.get_object('inlay').set(self.default_config['inlay'][0])

        if 'surface' in self.default_config.keys():
            self.builder.get_object('surface')['values'] = self.default_config['surface']
            self.builder.get_object('surface').set(self.default_config['surface'][0])
        if 'tester_hw' in self.default_config.keys():
            self.builder.get_object('tester_hw_ver')['state'] = 'enabled'
            self.builder.get_object('tester_hw_ver').delete(0, END)
            self.builder.get_object('tester_hw_ver').insert(0, self.default_config['tester_hw']['version'])
            self.builder.get_object('tester_hw_ver')['state'] = 'disabled'
            self.builder.get_object('tester_hw_desc')['state'] = 'enabled'
            self.builder.get_object('tester_hw_desc').delete(0, END)
            self.builder.get_object('tester_hw_desc').insert(0, self.default_config['tester_hw']['description'])
            self.builder.get_object('tester_hw_desc')['state'] = 'disabled'
        # if 'numOfTags' in self.default_config.keys():
        # self.builder.tkvariables.get('numTags').set(self.default_config['numOfTags'])
        # else:
        # self.builder.tkvariables.get('numTags').set(DEF_NUM_OF_TAGS)
        self.builder.tkvariables.get('numTags').set(0)
        self.builder.get_object('go')['state'] = 'normal'
        self.builder.tkvariables.get('go').set(CONNECT_HW)
        self.builder.get_object('stop')['state'] = 'normal'
        self.builder.tkvariables.get('stop').set(STOP)
        self.builder.get_object('stop')['state'] = 'disabled'
        self.builder.tkvariables.get('reelId').set('')
        self.update_params_state(group=CONNECT_HW)

        if 'config' in self.default_config.keys():
            self.test_configs = self.default_config['config']
        else:
            self.test_configs = ''
        self.builder.get_object('test_config').set(self.test_configs)
        self.configs_gui.set_default_config(self.test_configs)
        self.configs_gui.set_params(self.test_configs)

    def update_params(self):
        self.run_data = {}
        params = self.configs_gui.get_params()
        self.test_configs = self.default_config['config'] = self.builder.get_object('test_config').get()
        self.run_data['run_configs'] = params
        self.run_data['timestamp'] = datetime.datetime.now().strftime('%d%m%y_%H%M%S')
        self.common_run_name = self.reel_id + '_' + self.run_data['timestamp']
        self.test_time = float(params['testTime'])

        self.run_data['runStartTime'] = time.strftime('%d/%m/%y %H:%M:%S')
        self.run_data['antennaType'] = params.get('antennaType')
        self.run_data['bleAttenuation'] = params.get('attenBle')
        self.run_data['loraAttenuation'] = params.get('attenLoRa')
        self.run_data['energizingPattern'] = params.get('pattern')
        self.run_data['testTime'] = params.get('testTime')
        self.run_data['inlay'] = self.builder.get_object('inlay').get()
        self.run_data['surface'] = self.builder.get_object('surface').get()
        self.run_data['testerStationName'] = self.station_name
        self.run_data['commonRunName'] = self.common_run_name
        self.run_data['testerType'] = 'sample'
        self.run_data['gwVersion'] = self.com_connect.get_gw_version()
        self.run_data['operator'] = self.builder.get_object('operator').get()
        self.run_data['pyWiliotVersion'] = str(self.pywiliot_version)
        self.run_data['testTimeProfilePeriod'] = params.get('tTotal')
        self.run_data['testTimeProfileOnTime'] = params.get('tOn')
        self.run_data['numChambers'] = self.com_connect.get_num_of_barcode_scanners()
        self.run_data['timeProfile'] = '[{}, {}]'.format(params.get('tOn'), params.get('tTotal'))
        self.run_data['txPower'] = 'max'

        if 'controlLimits' in self.default_config.keys():
            self.logger.info('reset control limits')
            self.run_data['controlLimits'] = self.default_config['controlLimits'].copy()
            self.default_config['controlLimitsTestNum'] = 0
            self.run_data['tag_tbp_min'] = self.default_config['controlLimits'][0]['tag_tbp_min']
            self.run_data['tag_tbp_max'] = self.default_config['controlLimits'][0]['tag_tbp_max']
        else:
            self.run_data['tag_tbp_min'] = params.get('tag_tbp_min', 0)
            self.run_data['tag_tbp_max'] = params.get('tag_tbp_max', 9999)

        if 'rssiThresholdSW' in self.default_config.keys():
            try:
                self.run_data['rssi_threshold'] = int(self.default_config['rssiThresholdSW'])
            except Exception as e:
                self.logger.warning(f'could not convert "rssiThresholdSW" field in ,default to number: '
                                    f'{self.default_config["rssiThresholdSW"]} due to {e}. '
                                    f'rssi threshold is set to default: {RSSI_THR_DEFAULT}')
        else:
            self.run_data['rssi_threshold'] = self.default_config['rssiThresholdSW'] = RSSI_THR_DEFAULT

        self.run_data['hwVersion'] = self.default_config['tester_hw']['version'] \
            if 'tester_hw' in self.default_config.keys() else ''
        self.run_data['sub1gFrequency'] = params.get('EmulateSurfaceValue')

        self.update_data()

    def timer_count_down(self):
        """
        count down the test time
        """
        target_time = time.time() + self.test_time
        dt = int(target_time - time.time())
        while dt > 0:
            if self.stop_event.is_set():
                break
            dt = int(target_time - time.time())
            self.builder.tkvariables.get('testTime').set(str(dt))
            sleep(1)

        self.stop_event.set()
        self.builder.tkvariables.get('testTime').set(str(int(self.test_time)))

    def end_test_popup_calculation(self, df):
        """

        @param df:
        @type df: pd.Dataframe
        @return:
        @rtype:
        """
        all_answered = len(df[df['resolve_status'] == TagStatus.NO_RESPONSE]) == 0
        several_adva = []
        if 'adva_dup' in df.columns:
            several_adva = df.loc[df['adva_dup'], 'external_id'].unique()
        bad_adva = df['external_id'].loc[
            df['resolve_status'].isin([TagStatus.OUT_VALID, TagStatus.OUT_INVALID])].unique()

        warning_msg = '' if all_answered or len(bad_adva) == 0 else 'Serialization warning!\n'
        warning_msg += f'ADVA warning in tags: {several_adva}\n' if len(several_adva) else ''
        bg_color = 'yellow' if warning_msg else None

        avg_tbp = self.get_clean_tbp(df[TBP_CALC].unique()).mean()
        avg_ttfp = pd.Series(df['ttfp'].unique()).mean()

        avg_tbp = avg_tbp if pd.isnull(avg_tbp) else avg_tbp.item()
        avg_ttfp = avg_ttfp if pd.isnull(avg_ttfp) else avg_ttfp.item()

        return warning_msg, bg_color, avg_tbp, avg_ttfp

    def end_test_popup(self):
        warning_msg, bg_color, avg_tbp, avg_ttfp = self.end_test_popup_calculation(self.results_df)

        if pd.notnull(avg_ttfp):
            stat = f'Average TTFP: {avg_ttfp:.3f} [sec]\n' + \
                   f'Average TBP: {avg_tbp:.3f} [msec]'
        else:
            stat = 'No packets received'

        read_tags = '\nReplace tags and click on "Read"'

        self.com_connect.popup_message(msg=f'{warning_msg}{stat}{read_tags}',
                                       title='end test info',
                                       font=("Helvetica", 10),
                                       bg=bg_color)

    def iteration_finished(self):
        self.post_process_iteration()

        self.all_tags_in_test = {**self.all_tags_in_test, **self.tags_under_test}
        self.com_connect.open_chambers()

        self.end_test_popup()
        self.finish_test()

        self.update_params_state(state='normal', group=READ)

        self.builder.tkvariables.get('numTags').set(len(self.all_tags_in_test.keys()))
        self.builder.tkvariables.get('addTag').set('')
        self.builder.get_object('connect')['state'] = 'normal'
        self.builder.get_object('scanned').delete(0, END)
        self.builder.tkvariables.get('go').set(READ)
        self.builder.tkvariables.get('stop').set(FINISH)
        self.stop_button_state = FINISH

        self.reset_test_data()

    def reset_test_data(self):
        self.tags_under_test = {}
        self.results_df = pd.DataFrame()

    def remove_barcodes(self):
        final_barcodes = self.builder.get_object('scanned').get(0, END)
        self.builder.get_object('scanned').delete(0, END)
        test_barcodes = list(self.all_tags_in_test.keys()).copy()
        for barcode in test_barcodes:
            if barcode not in final_barcodes:
                self.all_tags_in_test.pop(barcode)

    def finish(self):
        self.remove_barcodes()
        self.finish_test(post_data=not self.calib, reset_tester=True, post_process=True)

    def is_valid_tbp(self, tbp):
        if self.run_data['tag_tbp_min'] != '' and self.run_data['tag_tbp_max'] != '':
            is_pass = int(self.run_data['tag_tbp_min']) < tbp < int(self.run_data['tag_tbp_max'])
        elif pd.isnull(tbp):
            is_pass = False
        else:
            is_pass = tbp != -1
        return is_pass

    def get_temperature_avg(self, chamber):
        if pd.isnull(chamber):
            return float('nan')
        if chamber < len(self.com_connect.temperature_sensor_readings):
            all_reading_temp = self.com_connect.temperature_sensor_readings[int(chamber)]
        else:
            all_reading_temp = []
        return numpy.nanmean(all_reading_temp) if len(all_reading_temp) else float('nan')

    def post_process_iteration(self):
        self.results_df = self.sample_run_obj.get_test_results()
        # check if there are no response tags:
        all_received_tags = [] if self.results_df.empty else self.results_df['external_id'].unique()
        all_not_responded_tags = [{'external_id': ex_id,
                                   'resolve_status': TagStatus.NO_RESPONSE,
                                   'adv_address': '', 'raw_packet': '', 'gw_packet': '',
                                   'time_from_start': float('nan'),
                                   TBP_CALC: float('nan'), 'rssi_mean': float('nan'),
                                   'ttfp': float('nan'), 'tbp':float('nan'), 'rssi': float('nan')}
                                  for ex_id in self.tags_under_test.keys() if
                                  ex_id not in all_received_tags]
        self.results_df = pd.concat([self.results_df, pd.DataFrame(all_not_responded_tags)], ignore_index=True)
        tags_results = self.results_df.groupby('external_id').agg(
            adva_dup=('adv_address', lambda x: len(x.unique()) > 1),
            tag_status=('resolve_status', 'first'),
            tag_ttfp=('ttfp', 'first'),
            tag_tbp=(TBP_CALC, 'first'),
            tag_rssi=('rssi_mean', 'first')
        )
        # check pass/fail:
        tags_results['valid_tbp'] = tags_results['tag_tbp'].apply(lambda x: self.is_valid_tbp(x))
        tags_results['is_pass'] = (~tags_results['adva_dup']) & (tags_results['valid_tbp']) & (
                tags_results['tag_status'] == TagStatus.INSIDE_TEST)
        tags_results.reset_index(inplace=True)

        # calc fail bin
        tag_status_count = tags_results['tag_status'].value_counts()
        test_status = {}
        for name in dir(TagStatus):
            if not name.startswith('_'):
                stat = getattr(TagStatus, name)
                test_status[stat] = tag_status_count.loc[stat] if stat in tag_status_count.index else 0

        fail_bins = tags_results.apply(lambda x: self.calc_tag_state(x, test_status), axis=1)
        tags_results['fail_bin'] = [f_bin.name for f_bin in fail_bins]
        tags_results['state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)'] = [
            f_bin.value for f_bin in fail_bins]

        # add chamber and reel data:
        chambers = [{'external_id': ex_id, 'chamber': self.tags_under_test[ex_id]['chamber']}
                    for ex_id in self.tags_under_test.keys()]
        tags_results = pd.merge(tags_results, pd.DataFrame(chambers), on='external_id', how='outer')
        tags_results['reel'] = tags_results['external_id'].apply(lambda x: x[:-5])

        # get temperature:
        tags_results['temperature_from_sensor'] = tags_results['chamber'].apply(lambda x: self.get_temperature_avg(x))
        # add test params
        tags_results['test_num'] = self.test_num
        tags_results['attenuation_ble'] = self.run_data['bleAttenuation']
        tags_results['attenuation_lora'] = self.run_data['loraAttenuation']

        self.update_tags_data(tags_results)
        # add results
        self.results_df = pd.merge(self.results_df, tags_results, on='external_id')

        # update all test results
        self.all_results = pd.concat([self.all_results, self.results_df], ignore_index=True)

    def update_values_for_control_limits(self, control_limits):
        self.run_data['test_tbp_min'] = control_limits['test_tbp_min']
        self.run_data['test_tbp_max'] = control_limits['test_tbp_max']
        self.run_data['test_responding_min'] = control_limits['test_responding_min']
        self.run_data['test_valid_tbp'] = control_limits['test_valid_tbp']

    def reset_values_for_control_limits(self, control_limits):
        self.run_data['tag_tbp_min'] = int(control_limits['tag_tbp_min'])
        self.run_data['tag_tbp_max'] = int(control_limits['tag_tbp_max'])
        self.run_data['test_tbp_min'] = ''
        self.run_data['test_tbp_max'] = ''
        self.run_data['test_responding_min'] = ''
        self.run_data['test_valid_tbp'] = ''

    def update_control_limits(self, reset_test=False):
        next_test = False
        if 'controlLimits' in self.default_config.keys():
            self.logger.info(f'Check control limits for pre-defined phased-test:'
                             f'\nnumber of tested:{self.run_data["tested"]}')
            if reset_test and \
                    self.default_config['controlLimitsTestNum'] < len(self.default_config['controlLimits']) - 1:
                self.default_config['controlLimitsTestNum'] += 1
                self.logger.info(f'move to the next test: {self.default_config["controlLimitsTestNum"]}')

            control_limits = self.default_config['controlLimits'][self.default_config['controlLimitsTestNum']]

            if reset_test:
                self.reset_values_for_control_limits(control_limits=control_limits)

            elif self.run_data['tested'] >= int(control_limits['n_tags']):
                self.update_values_for_control_limits(control_limits=control_limits)
                next_test = True
        return next_test

    def is_test_completed(self):
        completed = True
        if 'controlLimits' in self.default_config.keys():
            control_limits = self.default_config['controlLimits'][-1]
            if self.run_data['tested'] < int(control_limits['n_tags']):
                completed = False
        return completed

    def check_control_limits(self):
        complete_sub_test = self.update_control_limits(reset_test=False)
        is_pass = True
        fail_str = ''
        fail_bin = FailureCodeSampleTest.PASS

        if self.run_data.get('test_responding_min') and self.run_data.get('test_responding_min') != '':
            if float(self.run_data.get('responding[%]').replace('%', '')) < float(self.run_data.get('test_responding_min')):
                is_pass = False
                fail_str += 'Failed % responding test. '
                if fail_bin == FailureCodeSampleTest.PASS:
                    fail_bin = FailureCodeSampleTest.NO_RESPONSE
        if self.run_data.get('test_valid_tbp') and self.run_data.get('test_valid_tbp') != '':

            if float(self.run_data.get('validTbp[%]').replace('%', '')) < float(
                    self.run_data.get('test_valid_tbp', 'nan')):
                is_pass = False
                fail_str += 'Failed % from the responded tags with valid tbp avg test. '
                if fail_bin == FailureCodeSampleTest.PASS:
                    fail_bin = FailureCodeSampleTest.NO_TBP
        if ((self.run_data.get('test_tbp_min') and self.run_data.get('test_tbp_min') != '')
                and (self.run_data.get('test_tbp_max') and self.run_data.get('test_tbp_max') != '')):

            if not int(self.run_data.get('test_tbp_min')) < float(
                    self.run_data.get('tbpAvg', 'nan')) < int(self.run_data.get('test_tbp_max')):
                is_pass = False
                fail_str += 'Failed tbp avg test. '
                if fail_bin == FailureCodeSampleTest.PASS:
                    fail_bin = FailureCodeSampleTest.HIGH_TBP_AVG

        return is_pass, fail_str, complete_sub_test, fail_bin

    def finish_test(self, post_data=False, reset_tester=False, post_process=True):
        if post_process:
            self.post_process()
            pass_fail, fail_str, complete_sub_test, fail_bin = self.check_control_limits()
            if complete_sub_test and not pass_fail:
                self.update_control_limits(reset_test=True)

            warning_msg, bg_color, avg_tbp, avg_ttfp = self.end_test_popup_calculation(self.all_results)

            if 'controlLimits' not in self.default_config.keys():
                bg_color = 'green' if bg_color is None else bg_color
            bg_color = bg_color if pass_fail else 'red'
            pass_fail_str = 'Passed' if pass_fail else 'Failed'

            if 'controlLimits' in self.default_config.keys():
                if reset_tester and not complete_sub_test:
                    # user click on finish but test was not completed:
                    if fail_bin == FailureCodeSampleTest.PASS:
                        fail_bin = FailureCodeSampleTest.NOT_COMPLETED
                        pass_fail = False
                        pass_fail_str = 'Failed'
                        bg_color = 'red'
                if complete_sub_test and not reset_tester:
                    new_test_pass_str = 'SUCCESSFULLY COMPLETED THE TEST! please move to the next reel'
                    last_stage = self.is_test_completed()
                    new_test_fail_str = 'FAILED CURRENT TEST STAGE,' + \
                                        ' failed the reel' if last_stage else ' please continue to test the reel'
                    if not last_stage and not pass_fail:
                        bg_color = 'yellow'

                    if not self.calib:
                        self.com_connect.popup_message(f'Test {self.common_run_name} has {pass_fail_str}\n' +
                                                       f'{fail_str}\n' +
                                                       f'{new_test_pass_str if pass_fail else new_test_fail_str}'
                                                       f'\n' +
                                                       f'{warning_msg}'
                                                       f'Fail bin: {fail_bin.value}:{fail_bin.name}',
                                                       title='Finished test',
                                                       bg=bg_color,
                                                       log='info')
            self.is_test_pass = pass_fail

            if reset_tester:
                if not self.calib:
                    self.com_connect.popup_message(f'Test {self.common_run_name} has {pass_fail_str}\n' +
                                                   f'{fail_str}\n' +
                                                   f'{warning_msg}' +
                                                   f'Fail bin: {fail_bin.value}:{fail_bin.name}\n' +
                                                   f'Average TTFP: {self.run_data["ttfpAvg"]} [sec]\n' +
                                                   f'Average TBP: {self.run_data["tbpAvg"]} [msec]\n' +
                                                   f'STD TBP: {self.run_data["tbpStd"]} [msec]\n' +
                                                   f'Yield: {self.run_data["passed[%]"]}', title='Finished test',
                                                   bg=bg_color,
                                                   log='info')
                self.update_control_limits(reset_test=True)

            # log data:
            self.run_data['testStatus'] = pass_fail
            self.run_data['failBin'] = str(fail_bin.value) + str(self.default_config['controlLimitsTestNum']) \
                if 'controlLimitsTestNum' in self.default_config.keys() else ''
            self.run_data['failBinStr'] = fail_bin.name

            self.files_and_cloud(post_data)

        if reset_tester:
            self.reset_app_data()
            self.builder.tkvariables.get('go').set(READ)
            self.builder.get_object('stop')['state'] = 'disabled'
            self.update_params_state(group=READ, state='normal')

    def reset_app_data(self):
        self.all_results = pd.DataFrame()
        self.builder.get_object('reelId').bind("<Key>", self.get_reel_id_cb)
        self.set_gui_defaults()

        self.all_tags_in_test = {}
        self.tags_under_test = {}
        self.reel_id = ''

    def update_run_data(self):
        run_data_path = abspath(join(self.test_data_dir, f'{self.common_run_name}@run_data.csv'))
        dict_to_csv(dict_in=self.run_data, path=run_data_path)
        self.logger.info(f'updated run data at {run_data_path}')
        return run_data_path

    def update_packets_data(self):
        packets_data_path = abspath(join(self.test_data_dir, f'{self.common_run_name}@packets_data.csv'))
        if self.results_df.empty:
            return packets_data_path

        self.results_df.insert(loc=len(self.results_df.columns), column='encryptedPacket',
                               value=self.results_df['raw_packet'] + self.results_df['gw_packet'])

        self.results_df.rename(columns={'time_from_start': 'time',
                                        'external_id': 'externalId',
                                        'is_pass': 'status'}, inplace=True)
        df_to_save = self.results_df[['encryptedPacket', 'time', 'externalId', 'reel',
                                      'adv_address', 'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)',
                                      'fail_bin', 'status', 'chamber', 'tbp', 'rssi',
                                      'temperature_from_sensor', 'test_num',
                                      'attenuation_ble', 'attenuation_lora']]
        df_to_save.insert(0, 'commonRunName', self.common_run_name)
        df_to_save.to_csv(packets_data_path, index=False, mode='w' if self.test_num == 0 else 'a',
                          header=self.test_num == 0)
        self.logger.info(f'updated packets data at {packets_data_path}')
        return packets_data_path

    def update_tags_data(self, df_to_save):
        tags_data_path = abspath(join(self.test_data_dir, f'{self.common_run_name}@tags_data.csv'))
        df_to_save.to_csv(tags_data_path, index=False, mode='w' if self.test_num == 0 else 'a',
                          header=self.test_num == 0)
        self.logger.info(f'updated tags data at {tags_data_path}')

    @staticmethod
    def calc_tag_state(data, test_status):
        if data['tag_status'] == TagStatus.INSIDE_TEST:
            if data['adva_dup']:
                tag_state = FailBinSample.ADVA_DUPLICATION
            elif pd.isnull(data['tag_ttfp']):
                tag_state = FailBinSample.NO_TTFP
            elif data['tag_tbp'] == -1:
                tag_state = FailBinSample.NO_TBP
            else:
                tag_state = FailBinSample.TBP_EXISTS
        else:
            if (test_status[TagStatus.OUT_VALID] + test_status[TagStatus.OUT_INVALID]) == 0:
                tag_state = FailBinSample.NO_TTFP
            elif test_status[TagStatus.OUT_VALID] > 0:
                tag_state = FailBinSample.UNDETERMINED_ERROR
            elif test_status[TagStatus.OUT_INVALID] == test_status[TagStatus.NO_RESPONSE]:
                tag_state = FailBinSample.NO_SERIALIZATION
            else:
                tag_state = FailBinSample.UNDETERMINED_ERROR

        return tag_state

    def files_and_cloud(self, post_data=False):
        self.run_data['runEndTime'] = time.strftime('%d/%m/%y %H:%M:%S')
        self.run_data['uploadToCloud'] = post_data and self.post_data

        run_data_path = self.update_run_data()
        packets_data_path = self.update_packets_data()

        if post_data and self.post_data:
            post_success = self.post_to_cloud(run_data_path, packets_data_path, environment=self.environment)
            if post_success:
                self.logger.info('files were uploaded!')
                self.com_connect.popup_message(f'The following files were uploaded:\n' +
                                               f'{self.common_run_name}@run_data.csv\n' +
                                               f'{self.common_run_name}@packets_data.csv', log='info',
                                               title='file uploading', bg='green')
            else:
                self.com_connect.popup_message(f'Failed uploading run and/or tags data, Upload manually:\n' +
                                               f'{self.common_run_name}@run_data.csv\n' +
                                               f'{self.common_run_name}@packets_data.csv', log='warning',
                                               title='file uploading', bg='red')
                self.run_data['uploadToCloud'] = False
                self.update_run_data()

    def post_to_cloud(self, run_data_file_path, packets_data_file_path, environment='test/'):
        """
        post file to the cloud
        :type run_data_file_path: string
        :param run_data_file_path: the path to the uploaded run data file
        :type packets_data_file_path: string
        :param packets_data_file_path: the path to the uploaded packets data file
        :type environment: string
        :param environment: the environment in the cloud (dev, test, prod, etc.)
        :return: bool - True if succeeded, False otherwise
        """
        success = False
        first_iter = True
        while not success:
            if not first_iter:
                try_again = popup_yes_no(f'Could not post data to cloud, try again?')
                if not try_again:
                    return False

            success = upload_to_cloud_api(batch_name=self.reel_id, tester_type='sample-test',
                                          run_data_csv_name=run_data_file_path,
                                          packets_data_csv_name=packets_data_file_path,
                                          is_path=True,
                                          env=environment,
                                          owner_id=self.owner,
                                          logger_='sample')
            first_iter = False

        if not success:
            self.com_connect.popup_message(
                f'Run upload failed. Check exception error at the console and check Internet connection is available'
                f' and upload logs manually.',
                title='Upload Error',
                log='error')

        return success

    @staticmethod
    def get_clean_tbp(tbp_arr):
        mask = tbp_arr == -1
        tbp_arr = tbp_arr[~mask]
        return pd.Series(tbp_arr)

    def post_process(self):

        # calc ttfp
        avg_ttfp = self.all_results.groupby('external_id')['ttfp'].unique().apply(lambda x: x[-1]).mean()
        max_ttfp = self.all_results.groupby('external_id')['ttfp'].unique().apply(lambda x: x[-1]).max()
        self.run_data['ttfpAvg'] = f'{avg_ttfp:.3f}'
        self.run_data['maxTtfp'] = f'{max_ttfp:.3f}'

        # calc tbp
        all_tbp = self.get_clean_tbp(self.all_results.groupby('external_id')[TBP_CALC].unique().apply(lambda x: x[-1]))
        avg_tbp = all_tbp.mean()
        std_tbp = all_tbp.std()
        self.run_data['tbpStd'] = f'{std_tbp:.3f}'
        self.run_data['tbpAvg'] = f'{avg_tbp:.3f}'

        # rssi
        avg_rssi = self.all_results.groupby('external_id')['rssi_mean'].unique().apply(lambda x: x[-1]).mean()
        self.run_data['rssiAvg'] = str(avg_rssi)

        n_tested = len(self.all_tags_in_test.keys())
        n_answered = len(self.all_results.loc[
                             self.all_results['resolve_status'] == TagStatus.INSIDE_TEST, 'external_id'].unique())
        n_pass = sum([self.is_valid_tbp(x) for ex_id,x in zip(all_tbp.index,all_tbp.values)
                      if ex_id in self.all_tags_in_test.keys()])

        self.run_data['tested'] = n_tested
        self.run_data['responded'] = n_answered
        self.run_data['passed'] = n_pass
        self.run_data['responding[%]'] = f'{float((n_answered / n_tested) * 100) if n_tested > 0 else 0}%'
        self.run_data['passed[%]'] = f'{float((n_pass / n_tested) * 100 if n_tested > 0 else 0)}%'
        self.run_data['yield'] = self.run_data['responding[%]']
        self.run_data['validTbp[%]'] = f'{float((n_pass / n_answered) * 100 if n_answered > 0 else 0)}%'

    def close(self):
        """
        close the gui and destroy the test
        """
        try:
            self.com_connect.close()
            self.com_connect.gateway.exit_gw_api()
            self.ttk.destroy()
        except Exception as e:
            print(e)
            exit(1)

    def update_data(self):
        """
        update station name and owner in json file, for future usage.
        """
        if self.station_name.strip() != '':
            self.default_config['stationName'] = self.station_name
        if self.test_configs != '':
            self.default_config['config'] = self.test_configs
        if self.calib:
            self.default_config[f'{self.antenna}_calib'] = {'low': self.low, 'high': self.high, 'step': self.step}

        with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'w+') as defaultComs:
            dump(self.default_config, defaultComs, indent=4)

    def popup_login(self):
        """
        popup to insert fusion auth credentials, and choosing owner.
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.eval('tk::PlaceWindow . center')
        popup.wm_title('Login')

        def quit_tester():
            try:
                popup.destroy()
            except Exception as e:
                print(e)
                exit(1)

        popup.protocol("WM_DELETE_WINDOW", quit_tester)

        def ok():
            self.owner = c1.get()
            self.station_name = e3.get()
            self.calib = c_calib.get() == 'yes'
            self.offline = c_cloud.get() == 'no'
            popup.destroy()

        l1 = Label(popup, text='Run configuration:', font=default_font)
        l1.grid(row=2, column=0, padx=10, pady=10, columnspan=3)

        l3 = Label(popup, text='Online Mode (Cloud connection):', font=default_font)
        l3.grid(row=5, column=0, padx=10, pady=10)
        c_cloud = ttk.Combobox(popup, state='normal')
        c_cloud.grid(row=5, column=1, padx=10, pady=15)
        c_cloud['values'] = ['yes', 'no']
        c_cloud.set('yes')

        l3 = Label(popup, text='Calibration Mode:', font=default_font)
        l3.grid(row=4, column=0, padx=10, pady=10)
        c_calib = ttk.Combobox(popup, state='normal')
        c_calib.grid(row=4, column=1, padx=10, pady=15)
        c_calib['values'] = ['yes', 'no']
        c_calib.set('no')

        l4 = Label(popup, text='Owner:', font=default_font)
        l4.grid(row=6, column=0, padx=10, pady=10)
        c1 = ttk.Combobox(popup, state='normal')
        c1.grid(row=6, column=1, padx=10, pady=15)

        l5 = Label(popup, text='Station Name:', font=default_font)
        l5.grid(row=7, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        if 'stationName' in self.default_config.keys():
            e3.insert(0, self.default_config['stationName'])
        e3.grid(row=7, column=1, padx=10, pady=5)
        b3 = Button(popup, text="OK", command=ok, height=1, width=10)
        b3.grid(row=8, column=1, padx=10, pady=10)

        if 'owner' in self.default_config.keys():
            owner_id_list = self.default_config['owner'] \
                if isinstance(self.default_config['owner'], list) else [self.default_config['owner']]
        else:
            owner_id_list = ['']
        c1['values'] = owner_id_list
        c1.set(self.default_config.get('selected_owner', owner_id_list[-1]))

        popup.mainloop()

        # update configs:
        self.default_config['selected_owner'] = self.owner
        if self.owner not in owner_id_list:
            owner_id_list.append(self.owner)
            owner_id_list = [o for o in owner_id_list if o != '']
            self.default_config['owner'] = owner_id_list
            with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'w+') as defaults:
                dump(self.default_config, defaults, indent=4)

    def update_default_dict(self, field, value):
        antenna = self.antenna.lower()
        if f'{antenna}_calib' in self.default_config.keys():
            self.default_config[f'{antenna}_calib'][field] = value

    def popup_calib(self):
        """
        popup to choose calib mode parameters
        """
        default_font = ("Helvetica", 10)
        popup = Tk()
        popup.wm_title('Login')

        def quit_calib():
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", quit_calib)

        def ok():
            self.low = e2.get()
            self.high = e3.get()
            self.step = e4.get()
            self.n_repetitions = e5.get()
            # save the dictionary back to the file
            with open(abspath(join(CONFIGS_DIR, '.defaults.json')), 'w') as defaultComs:
                dump(self.default_config, defaultComs)
            popup.destroy()

        def update_antenna_params(*args):
            self.antenna = antenna = c2.get().lower()
            if f'{antenna}_calib' in self.default_config.keys():
                antennaDict = self.default_config[f'{antenna}_calib']
                e2.delete(0, END)
                e3.delete(0, END)
                e4.delete(0, END)
                e5.delete(0, END)
                e2.insert(0, antennaDict['low'])
                e3.insert(0, antennaDict['high'])
                e4.insert(0, antennaDict['step'])
                e5.insert(0, 1)

        l1 = Label(popup, text='Enter calibration parameters:', font=default_font)
        l1.grid(row=1, column=0, padx=10, pady=10, columnspan=3)
        l2 = Label(popup, text='Antenna Type:', font=default_font)
        l2.grid(row=2, column=0, padx=10, pady=10)
        c2 = ttk.Combobox(popup, values=['BLE', 'LoRa'])
        c2.grid(row=2, column=1, padx=10, pady=10)
        c2.bind("<FocusOut>", update_antenna_params)
        c2.bind("<<ComboboxSelected>>", update_antenna_params)
        l3 = Label(popup, text='Low value:', font=default_font)
        l3.grid(row=3, column=0, padx=10, pady=10)
        e2 = Entry(popup)
        e2.grid(row=3, column=1, padx=10, pady=5)
        e2.bind("<FocusOut>", lambda e: self.update_default_dict('low', e2.get()))
        l4 = Label(popup, text='High value:', font=default_font)
        l4.grid(row=4, column=0, padx=10, pady=10)
        e3 = Entry(popup)
        e3.grid(row=4, column=1, padx=10, pady=5)
        e3.bind("<FocusOut>", lambda e: self.update_default_dict('high', e3.get()))
        l5 = Label(popup, text='Step:', font=default_font)
        l5.grid(row=5, column=0, padx=10, pady=10)
        e4 = Entry(popup)
        e4.grid(row=5, column=1, padx=10, pady=5)
        e4.bind("<FocusOut>", lambda e: self.update_default_dict('step', e4.get()))
        l6 = Label(popup, text='Number of Repetitions per step:', font=default_font)
        l6.grid(row=6, column=0, padx=10, pady=10)
        e5 = Entry(popup)
        e5.grid(row=6, column=1, padx=10, pady=5)
        e5.bind("<FocusOut>", lambda e: self.update_default_dict('n_repetitions', e5.get()))
        b1 = Button(popup, text="Quit", command=quit_calib, height=1, width=10)
        b1.grid(row=7, column=0, padx=10, pady=10)
        b2 = Button(popup, text="Ok", command=ok, height=1, width=10)
        b2.grid(row=7, column=1, padx=10, pady=10)

        popup.mainloop()

    # ############## GUI Callbacks  #######################

    def go_cb(self):
        if self.finish_thread is not None and self.finish_thread.is_alive():
            self.logger.info('wait for finish process to be done')
            self.finish_thread.join()
        self.go_button_state = self.builder.tkvariables.get('go').get()
        self.builder.get_object('stop')['state'] = 'disabled'
        self.builder.get_object('settings_combobox')['state'] = 'disabled'

        self.update_params_state(state='disabled', group=GO)
        self.builder.get_variable('forceGo').set('0')
        self.force_close_requested = False
        if self.go_button_state == CONNECT_HW:
            self.connect_thread = Thread(target=self.connect_all, args=([False]))
            self.connect_thread.start()
        elif self.go_button_state == READ:
            self.builder.get_object('settings_combobox')['state'] = 'disabled'
            if self.stop_button_state == SEND:
                self.remove_barcodes()
                self.stop_button_state = FINISH
                self.builder.tkvariables.get('stop').set(FINISH)
            indexes = self.get_missing_ids_chambers()
            test_barcodes_thread = Thread(target=self.read_scanners_barcodes, args=([indexes]))
            test_barcodes_thread.start()
        elif self.go_button_state == GO:
            # calib data:
            if self.calib:
                pop_calib_th = Thread(target=self.popup_calib, args=())
                pop_calib_th.start()
                pop_calib_th.join()

            self.update_params()

            self.builder.get_object('stop')['state'] = 'normal'
            self.builder.tkvariables.get('stop').set(STOP)
            self.stop_button_state = STOP
            # create a dir for log
            self.init_data_log()

            if self.calib:
                self.calib_mode_thread = Thread(target=self.calib_mode, args=())
                self.calib_mode_thread.start()
            else:
                self.tag_test_thread = Thread(target=self.tag_test, args=())
                self.tag_test_thread.start()

        elif self.go_button_state == CONTINUE:
            self.builder.tkvariables.get('stop').set(STOP)
            self.stop_button_state = STOP
            self.test_num += 1

            self.tag_test_thread.join(timeout=1)
            if self.tag_test_thread.is_alive():
                raise Exception('tag thread test still running - the application needs restart')

            self.tag_test_thread = Thread(target=self.tag_test, args=())
            self.tag_test_thread.start()

    def choose_param_cb(self, *args):
        var = args[0].widget['style'].split('.')[0]
        if self.builder.tkvariables.get(var) is not None:
            value = self.builder.get_object(var).get()
            if var not in self.default_config.keys():
                self.default_config[var] = []
            if value in self.default_config[var]:
                self.default_config[var].pop(self.default_config[var].index(value))
            self.default_config[var].insert(0, value)

    def reset_cb(self):
        """
        reset the tester (fully available only when running from bat file)
        """
        if popup_yes_no(f'Reset Sample test?'):
            try:
                self.com_connect.close()
                self.com_connect.__del__()
                self.remove_barcodes()
                self.com_connect.choose_com_ports()
                self.reset_app_data()
            except Exception as e:
                print(f'could not reset due to: {e}')
                exit(1)
        else:
            pass

    def stop_cb(self):
        """
        stop the test and run post process
        """
        if self.stop_button_state == STOP:
            self.force_close_requested = True
            self.stop_event.set()

        elif self.stop_button_state == FINISH:
            self.builder.get_object('scanned').delete(0, END)
            self.builder.tkvariables.get('stop').set(SEND)
            self.stop_button_state = SEND
            for barcode in list(self.all_tags_in_test.keys()):
                self.builder.get_object('scanned').insert(END, barcode)

        elif self.stop_button_state == SEND:
            if not self.is_test_completed() and 'controlLimits' in self.default_config.keys():
                control_limits = self.default_config['controlLimits'][self.default_config['controlLimitsTestNum']]
                self.update_values_for_control_limits(control_limits=control_limits)
                is_pass, fail_str, complete_sub_test, fail_bin = self.check_control_limits()
                self.reset_values_for_control_limits(control_limits=control_limits)
                if not is_pass or not complete_sub_test:
                    send_anyway = popup_yes_no(f'Test was FAILED!! are you sure you want to finish the test and '
                                               f'send data to the cloud?')
                    if not send_anyway:
                        self.logger.info('User decide to keep testing')
                        return
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.builder.get_object('forceGo')['state'] = 'disabled'
            self.builder.get_object('add')['state'] = 'disabled'
            self.builder.get_object('remove')['state'] = 'disabled'
            self.finish_thread = Thread(target=self.finish, args=())
            self.finish_thread.start()

    def add_cb(self):
        """
        add manually tag to the list
        """
        new_tag = self.builder.tkvariables.get('addTag').get()
        if self.builder.tkvariables.get('stop').get() != SEND or len(new_tag.split(',')) == 2:
            new_tag_id = self.get_external_id_from_monitor(new_tag)
            if new_tag_id in self.tags_under_test.keys():
                retest = popup_yes_no(f'Tag {new_tag_id} was already tested, are you sure you want to re-test the tag?')
                if not retest:
                    self.builder.tkvariables.get('addTag').set('')
                    return

            if self.builder.tkvariables.get('stop').get() == SEND:
                self.builder.get_object('scanned').delete(0, END)
                self.remove_barcodes()
                self.stop_button_state = FINISH
                self.builder.tkvariables.get('stop').set(FINISH)

            if len(new_tag.split(',')) < 2:
                self.com_connect.popup_message(f'Missing chamber index, add chamber index after a comma.',
                                               title='Error',
                                               log='error')
                return
            scan_index = int(new_tag.split(',')[1].strip())
            if 0 < self.com_connect.get_num_of_barcode_scanners() < (scan_index + 1):
                self.com_connect.popup_message(f'Chamber number {scan_index} not exists.', title='Error', log='error')
                return

            barcodes = self.builder.get_object('scanned').get(0, END)
            if any([barcode for barcode in barcodes if int(barcode.split()[1].strip()) == scan_index]):
                self.com_connect.popup_message(f'Chamber {scan_index} tag already scanned.', title='Error', log='error')
                return
            # logger.info(scan_index)

            self.builder.tkvariables.get('addTag').set('')
            added_to_test = self.add_tag_to_test(new_tag_id, self.reel_id, scan_index, add_to_test=True)
            if added_to_test:
                popup_thread = Thread(target=self.com_connect.popup_message,
                                      args=('Chambers are closing!!\nWatch your hands!!!',
                                            'Warning', ("Helvetica", 18), 'warning'))
                popup_thread.start()
                popup_thread.join()
                chambers = self.com_connect.get_chambers()
                if len(chambers) > scan_index and chambers[scan_index] is not None:
                    chambers[scan_index].close_chamber()
            self.update_go_state()
        else:
            self.builder.get_object('scanned').insert(END, new_tag)
            self.builder.tkvariables.get('addTag').set('')

    def remove_cb(self):
        """
        remove tag read from the list
        """
        tag = self.builder.get_object('scanned').get(ACTIVE)
        tags = list(self.builder.get_object('scanned').get(0, END))
        tag_index = tags.index(tag)
        self.builder.get_object('scanned').delete(tag_index, tag_index)
        tags.pop(tag_index)
        self.builder.tkvariables.get('addTag').set(tag)
        if self.stop_button_state != SEND:
            self.tags_under_test.pop(self.get_external_id_from_monitor(tag))
            self.com_connect.open_chambers(indexes=[int(tag.split(',')[1].strip())])
            self.update_go_state()

    def get_external_id_from_monitor(self, tag_str):
        external_id = tag_str.split(',')[0].strip()
        external_id = f'{self.reel_id}T{external_id}' if len(external_id) == TAG_COUNTER_LEN else external_id
        return external_id

    def open_configs_cb(self):
        """
        open Configs GUI
        """
        if self.configs_gui is not None and not self.configs_gui.is_gui_opened():
            self.configs_gui.gui()

    def test_config_cb(self, *args):
        """
        update the configs in Configs module according to the main GUI
        """
        self.configs_gui.config_set(self.builder.get_object('test_config').get())

    def open_com_ports_cb(self):
        """
        open ComConnect GUI
        """
        if self.com_connect is not None and not self.com_connect.is_gui_opened():
            self.com_connect.gui()

    def read_qr_cb(self):
        indexes = self.com_connect.get_all_scanners_index()
        barcode, reel = None, None
        for i in indexes:
            barcode, reel = self.com_connect.read_barcode(scanner_index=i)
            if barcode is not None:
                break

        if barcode is None:
            read_qr_thread = Thread(target=self.com_connect.popup_message, args=(
                [f'Error reading external ID, try repositioning the tag.', 'Error', ("Helvetica", 10), 'error']))
            read_qr_thread.start()
            read_qr_thread.join()
            if not self.calib:
                return

        if reel is not None:
            reel_id = self.builder.tkvariables.get('reelId')
            reel_id.set(reel)
            self.reel_id = reel

        if 'config' in self.default_config.keys():
            self.test_configs = self.default_config['config']
        else:
            self.test_configs = ''

        self.builder.get_object('reelId').unbind("<Key>")
        self.update_params_state(state='normal', group=GO)
        self.builder.get_object('forceGo')['state'] = 'normal'

    def get_reel_id_cb(self, *args):
        reel = self.builder.tkvariables.get('reelId').get()
        if reel.strip() != '' and (str(args[0].type) != 'KeyPress' or args[0].keysym == 'Return'):
            self.reel_id = reel
            self.update_params_state(state='normal', group=GO)
            self.builder.get_object('reelId').unbind("<Key>")
            self.builder.get_object('forceGo')['state'] = 'normal'

    def force_go_cb(self):
        """
        enable go in the GUI even if some of the chambers are empty
        """
        if self.builder.get_variable('forceGo').get() == '1':
            self.builder.get_object('forceGo')['state'] = 'disabled'
            self.builder.get_object('stop')['state'] = 'disabled'
            self.builder.get_object('go')['state'] = 'disabled'
            self.builder.get_object('add')['state'] = 'disabled'
            self.builder.get_object('remove')['state'] = 'disabled'
            self.builder.get_object('settings_combobox')['state'] = 'disabled'
            if self.closeChambersThread is not None and self.closeChambersThread.is_alive():
                self.closeChambersThread.join()
            self.closeChambersThread = Thread(target=self.force_go_close_chambers, args=())
            self.closeChambersThread.start()
        else:
            self.update_go_state()

    def on_env_change_cb(self, event=None):

        self.environment = self.settings_combobox.get()
        self.logger.info(f'Environment set to {self.environment}')
        self.check_cloud_connection()


def popup_yes_no(question, tk_frame=None):
    if tk_frame is None:
        root = Tk()
        root.eval(f'tk::PlaceWindow {str(root)} center')
    else:
        root = tk_frame
    root.wm_withdraw()
    result = messagebox.askquestion("Sample Test", question, icon='warning')
    root.destroy()
    if result == 'yes':
        return True
    else:
        return False


if __name__ == '__main__':
    sampleTest = SampleTest()
    sampleTest.gui()