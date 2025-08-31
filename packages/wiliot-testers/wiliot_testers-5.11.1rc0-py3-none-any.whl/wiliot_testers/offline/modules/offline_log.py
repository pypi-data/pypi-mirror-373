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

import os
import datetime
import logging

from wiliot_core import InlayTypes, WiliotDir

from wiliot_testers.wiliot_tester_log import dict_to_csv, WiliotTesterLog
from wiliot_testers.wiliot_tester_tag_test import TesterName
from wiliot_testers.wiliot_tester_tag_result import ConversionTypes, SurfaceTypes, FailureCodes
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.offline.modules.offline_printing_and_validation import ValidatedBin


class DataLogging(object):
    def __init__(self, exception_queue, log_config=None):
        self.exception_queue = exception_queue

        # init log config
        self.log_config = log_config
        self.log_obj = None
        self.run_data_path = ''
        self.packets_data_path = ''
        self.reel_name = ''
        self.data_folder = ''
        logger_name = self.set_log_data_dir()
        self.logger = logging.getLogger(logger_name)

        self.run_data = {}
        self.test_data = {}
        self.packet_headers_default = []
        self.tag_reel_location = 0
        self.total_tested = 0

    def get_data_folder(self):
        return self.data_folder

    def get_test_folder(self):
        return self.log_obj.data_folder

    def get_logger_name(self):
        return self.logger.name

    def get_results_logger_name(self):
        return self.log_obj.results_logger.name

    def get_gw_logger_name(self):
        return self.log_obj.gw_logger.name

    def get_lane_str(self):
        lane_str = ''
        if self.log_config['printingFormat'] == 'prePrint':
            # Taking the lane from the conversion label for pre-printed labels
            conv_label_list = self.log_config['conversionLabel'].split('_')
            if len(conv_label_list) > 2:
                lane_str = self.log_config['conversionLabel'].split('_')[2]
        
        return lane_str

    def set_log_data_dir(self):
        wiliot_dir = WiliotDir()
        app_dir = wiliot_dir.get_wiliot_root_app_dir()
        
        self.log_obj = WiliotTesterLog()
        lane_str = self.get_lane_str()
        self.reel_name = self.log_config['batchName'].rstrip()
        common_run_name = self.log_obj.set_common_run_name(reel_name=self.reel_name, lane_str=lane_str)
        lane_str = '_' + lane_str if lane_str != '' else lane_str
        log_dir = os.path.join(app_dir, 'offline', 'logs', f'{self.reel_name}{lane_str}')
        os.makedirs(log_dir, exist_ok=True)

        self.data_folder = log_dir
        
        self.log_obj.set_logger(log_path=log_dir, tester_name='offline')
        self.run_data_path, self.packets_data_path = self.log_obj.create_data_dir(data_path=log_dir,
                                                                                  tester_name='offline',
                                                                                  run_name=common_run_name)
        if 'testerStationName' not in os.environ:
            raise Exception('testerStationName is missing from PC environment variables, '
                            'please add it in the following convention: <company name>_<tester number>')
        self.log_obj.set_station_name(os.environ['testerStationName'])

        return self.log_obj.logger.name

    def update_log_config(self, log_config):
        for k, v in log_config.items():
            self.log_config[k] = v

    def get_log_config(self):
        return self.log_config

    def get_run_data_path(self):
        return self.run_data_path

    def get_packets_data_path(self):
        return self.packets_data_path

    def get_reel_name(self):
        return self.reel_name

    def run_data_init(self, is_printing, gw_version, test_suite_dict):
        common_run_name = self.log_obj.run_name
        run_start_time = self.log_obj.run_start_time

        if 'tag_reel_location' in self.log_config.keys():
            self.tag_reel_location = self.log_config['tag_reel_location']

        self.run_data = {'common_run_name': common_run_name,
                         'tester_station_name': self.log_obj.tester_station_name,
                         'operator': self.log_config['operator'], 'reel_run_start_time': run_start_time,
                         'reel_run_end_time': None,
                         'batch_name': self.log_config['batchName'],
                         'tester_type': TesterName.OFFLINE.value,
                         'comments': self.log_config['comments'],
                         'total_run_tested': 0, 'total_run_responding_tags': 0,
                         'total_run_passed_offline': 0,
                         'total_run_bad_printing': 0,
                         'total_missing_labels': 0, 'run_responsive_tags_yield': float('nan'),
                         'run_offline_yield': float('nan'),
                         'conversion_type': ConversionTypes(self.log_config['conversion']).name,
                         'inlay': InlayTypes(self.log_config['inlay']).name,
                         'product_config': self.log_config['product_config'],
                         'test_suite': self.log_config['testName'],
                         'test_suite_dict': test_suite_dict,
                         'surface': SurfaceTypes(self.log_config['surface']).name,
                         'to_print': self.log_config['toPrint'],
                         'qr_validation': self.log_config['QRRead'],
                         'qr_offset': self.log_config['QRoffset'],
                         'printing_offset': self.log_config['printOffset'],
                         'print_pass_job_name': self.log_config['passJobName'] if is_printing else '',
                         'printing_format': self.log_config['printingFormat'] if is_printing else '',
                         'external_id_prefix': self.log_config['stringBeforeCounter'] if is_printing else '',
                         'external_id_suffix_init_value': self.log_config['firstPrintingValue'] if is_printing else '',
                         'gw_version': gw_version,
                         'py_wiliot_version': get_version(),
                         'owner_id': 'wiliot-ops',
                         'sensors_enable': self.log_config['sensorsEnable'],
                         'ttfp_avg': float('nan'),
                         'user_config_dict': self.log_config,
                         'conversion_label': self.log_config['conversionLabel'],
                         'tag_sensor_type': self.log_config['tag_sensor_type']}

        self.test_data = {'common_run_name': common_run_name, 'tag_run_location': 0,
                          'total_test_duration': None,
                          'status_offline': False, 'fail_bin': FailureCodes.NONE.value,
                          'fail_bin_str': FailureCodes.NONE.name,
                          'external_id': '',
                          'label_validated': ValidatedBin.UNTESTED.name, 'trigger_time': None,
                          'test_num': 0,
                          'tag_reel_location': self.tag_reel_location}

        self.packet_headers_default = \
            ['common_run_name', 'tag_run_location', 'tag_reel_location', 'test_num', 'external_id', 'time_from_start',
             'raw_packet', 'rssi',
             'packet_status', 'adv_address', 'selected_tag', 'is_test_pass', 'status_offline', 'fail_bin',
             'fail_bin_str',
             'test_status', 'num_packets', 'num_cycles', 'sprinkler_counter_mean', 'sprinkler_counter_std',
             'sprinkler_counter_min', 'sprinkler_counter_max', 'tbp_mean', 'tbp_std', 'tbp_min', 'tbp_max',
             'tbp_num_vals',
             'per_mean', 'per_std', 'rssi_mean', 'rssi_std', 'rssi_min', 'rssi_max', 'ttfp', 'rx_rate_normalized',
             'rx_rate', 'total_test_duration', 'test_start_time', 'trigger_time',
             'test_end_time', 'label_validated', 'rx_channel', 'energizing_pattern', 'time_profile',
             'decrypted_packet_type',
             'group_id', 'flow_ver', 'test_mode', 'en', 'type', 'data_uid', 'nonce', 'enc_uid', 'mic', 'enc_payload',
             'gw_packet', 'stat_param', 'crc_environment_previous', 'temperature_sensor', 'humidity_sensor',
             'light_intensity_sensor']

        self.update_run_data()
        self.update_packets_data(only_titles=True)

    def update_run_data(self, res=None, save_to_csv=True):
        if res is not None:
            test_info = res.get_test_info()
            res_fail_bin = res.get_total_fail_bin()
            res_fail_bin = res_fail_bin if res_fail_bin is not None else FailureCodes.GW_ERROR.name
            if res_fail_bin not in [FailureCodes.END_OF_TEST.value, FailureCodes.MISSING_LABEL.value]:
                    self.total_tested += 1
            self.run_data['total_run_passed_offline'] += res_fail_bin == FailureCodes.PASS.value
            self.run_data['total_run_bad_printing'] += res_fail_bin == FailureCodes.BAD_PRINTING.value
            if 'responded' in test_info:
                self.run_data['total_run_responding_tags'] = test_info['responded']
            if 'missing_label' in test_info:
                self.run_data['total_missing_labels'] = test_info['missing_label']
            if 'ttfp_avg' in test_info:
                self.run_data['ttfp_avg'] = test_info['ttfp_avg']

            self.run_data['total_run_tested'] = self.total_tested
            self.run_data['run_responsive_tags_yield'] = \
                self.run_data['total_run_responding_tags'] / self.run_data['total_run_tested'] * 100 \
                    if self.run_data['total_run_tested'] > 0 else float(-1)
            self.run_data['run_offline_yield'] = \
                self.run_data['total_run_passed_offline'] / self.run_data['total_run_tested'] * 100 \
                    if self.run_data['total_run_tested'] > 0 else float(-1)
            self.run_data['reel_run_end_time'] = datetime.datetime.now()

        if save_to_csv:
            dict_to_csv(dict_in=self.run_data, path=self.run_data_path)

    def update_packets_data(self, res=None, only_titles=False):

        def save_default_packet_data(summary=None):
            default_data = {'raw_packet': None, 'adv_address': None, 'decrypted_packet_type': None,
                            'group_id': None, 'flow_ver': None,
                            'test_mode': None, 'en': None, 'type': None, 'data_uid': None, 'nonce': None,
                            'enc_uid': None, 'mic': None, 'enc_payload': None, 'gw_packet': None, 'rssi': None,
                            'stat_param': None, 'time_from_start': None, 'counter_tag': None,
                            'is_valid_tag_packet': None, 'common_run_name': self.test_data['common_run_name'],
                            'tag_run_location': self.test_data['tag_run_location'],
                            'tag_reel_location': self.test_data['tag_reel_location'],
                            'total_test_duration': self.test_data['total_test_duration'],
                            'status_offline': self.test_data['status_offline'],
                            'fail_bin': self.test_data['fail_bin'], 'fail_bin_str': self.test_data['fail_bin_str'],
                            'external_id': None,
                            'label_validated': self.test_data['label_validated'],
                            'test_num': self.test_data['test_num'],
                            'trigger_time': self.test_data['trigger_time'], 'packet_status': None,
                            'crc_environment_previous': self.test_data.get('crc_environment_previous', None),
                            'temperature_sensor': float('nan'), 'humidity_sensor': float('nan'),
                            'light_intensity_sensor': float('nan')}
            if summary is None:
                default_sum = {'is_test_pass': None, 'selected_tag': None, 'test_start_time': None,
                               'test_end_time': None, 'test_status': None, 'rx_channel': None,
                               'energizing_pattern': None, 'time_profile': None, 'num_packets': 0,
                               'num_cycles': 0, 'sprinkler_counter_mean': None, 'sprinkler_counter_std': None,
                               'sprinkler_counter_min': None, 'sprinkler_counter_max': None, 'tbp_mean': None,
                               'tbp_std': None, 'tbp_min': None, 'tbp_max': None, 'tbp_num_vals': None,
                               'per_mean': None, 'per_std': None, 'rssi_mean': None, 'rssi_std': None,
                               'rssi_min': None, 'rssi_max': None, 'ttfp': None, 'rx_rate_normalized': None,
                               'rx_rate': None}
            else:
                default_sum = summary

            default_packet_att = {'is_valid_packet': None, 'inlay_type': None}
            default_dict = {**default_data, **default_sum, **default_packet_att}
            default_ordered_dict = {k: default_dict.get(k, None) for k in self.packet_headers_default}
            dict_to_csv(dict_in=default_ordered_dict, path=self.packets_data_path, append=(not only_titles),
                        only_titles=only_titles)

        if res is not None:
            stat = res.get_total_test_status()
            self.test_data['status_offline'] = int(stat) if stat is not None else 0
            self.test_data['total_test_duration'] = res.get_total_test_duration()
            fail_bin = res.get_total_fail_bin(as_name=True)
            if fail_bin is None:
                fail_bin = FailureCodes.GW_ERROR.name
            self.test_data['fail_bin'] = FailureCodes[fail_bin].value
            self.test_data['fail_bin_str'] = fail_bin
            self.test_data['trigger_time'] = res.get_trigger_time()

            test_info = res.get_test_info()
            self.test_data['tag_run_location'] = test_info['tag_run_location']

            # Include new sensor readings in the test data
            self.test_data['tag_reel_location'] = test_info['tag_reel_location']
            self.test_data['external_id'] = test_info['external_id'] \
                if 'external_id' in test_info.keys() and self.test_data['status_offline'] == 1 else ''
            self.test_data['label_validated'] = test_info['validated'] \
                if 'validated' in test_info.keys() else ValidatedBin.UNTESTED.name
            self.test_data['temperature_sensor'] = test_info['temperature_sensor'] \
                if 'temperature_sensor' in test_info.keys() else float('nan')
            self.test_data['humidity_sensor'] = test_info['humidity_sensor'] \
                if 'humidity_sensor' in test_info.keys() else float('nan')
            self.test_data['light_intensity_sensor'] = test_info['light_sensor'] \
                if 'light_sensor' in test_info.keys() else float('nan')
            self.test_data['crc_environment_previous'] = test_info['crc_environment_previous'] \
                if 'crc_environment_previous' in test_info.keys() else None

            if len(res) == 0:
                save_default_packet_data()

            for i, r in enumerate(res):
                self.test_data['test_num'] = i
                r_sum = r.get_summary()

                # add packets info:
                if r.all_packets.size():
                    # we received packets
                    for p in r.all_packets:
                        p.add_custom_data(
                            custom_data={**self.test_data, **r_sum})
                    r.all_packets.to_csv(path=self.packets_data_path, append=True, export_packet_id=False,
                                         columns=self.packet_headers_default)
                else:
                    # no responds in current test
                    save_default_packet_data(summary=r_sum)

        else:
            self.test_data['test_num'] = 0
            save_default_packet_data()

    def update_default_test_data(self, new_test_data):
        for k, v in new_test_data.items():
            if k not in self.test_data:
                continue
            self.test_data[k] = v

    def exit(self, unsaved_data):
        for tag_result_to_log in unsaved_data:
            if tag_result_to_log is not None:
                # update packet data
                self.update_packets_data(res=tag_result_to_log)
                # update run data
                self.update_run_data(res=tag_result_to_log)
