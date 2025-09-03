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
import logging
import re
import time
import os
import datetime
import threading
import json
from enum import Enum
import pandas as pd

from wiliot_core.packet_data.config_files.packet_flow_map import get_packet_version_by_flow_version
from wiliot_core import WiliotDir, CommandDetails
from wiliot_core import WiliotGateway, ActionType, DataType, valid_output_power_vals
from wiliot_core import PacketList
from wiliot_testers.wiliot_tester_tag_result import WiliotTesterTagResultList, WiliotTesterTagResult, FailureCodes
from wiliot_testers.wiliot_tester_log import WiliotTesterLog

try:
    from wiliot_core import DecryptedPacketList, DecryptedPacket
    print('tag test: decryption mode is supported if needed')
except Exception as e:
    pass

supported_gw_version = [3, 5, 2]
MAX_SUB1G_POWER = 29
N_CHAR_ADVA = 8
HALF_N_CHAR_FLOW = 2


class TesterName(Enum):
    OFFLINE = 'offline'
    SAMPLE = 'sample'
    SYSTEM_TEST = 'system_test'
    TAL15K = 'tal15k'
    YIELD = 'yield'


class LoggerName(Enum):
    MAIN = 'main'
    GW = 'gw'
    RESULTS = 'results'


class WiliotTesterTagTest(object):
    """
    Wiliot Tags Tester according to configurations provided by user
    """

    def __init__(self, selected_test, test_suite=None, gw_obj=None, black_list=None,
                 stop_event_trig=None, tester_name=TesterName.OFFLINE,
                 logger_name=None, logger_result_name=None, logger_gw_name=None,
                 lock_print=None, inlay=None, verbose=True,
                 selected_test_dict=None, dir_for_gw_log=None,
                 gw_test_cmds=None, client=None):
        """
        :param logger_name: if specified the main logger is based on a predefine logger with the specified name.
                            otherwise the logger is set by the app
        :type logger_name: str
        :param logger_result_name: if specified the results logger is based on a predefine logger with the
                                   specified name. otherwise the logger is set by the app
        :type logger_result_name: str
        :param logger_gw_name: if specified the gw logger is based on a predefine logger with the specified name.
                               otherwise the logger is set by the app
        :type logger_gw_name: str
        :param tester_name: the tester type from the TesterName list
        :type tester_name: TesterName
        :param test_suite: the test suite contains all the parameters of the test.
                           the test suite structure should be as following:
                            test_suite = {"Dual Band": {"plDelay": 100,
                                                        "rssiThresholdHW": 95,
                                                        "rssiThresholdSW": 80,
                                                        "maxTtfp": 5,
                                                        "tests": [
                                                            {"name": "first_packets_ble_band",
                                                             "rxChannel": 37,
                                                             "energizingPattern": 18,
                                                             "timeProfile": [5, 10],
                                                             "absGwTxPowerIndex": -1,
                                                             "maxTime": 5,
                                                             "delayBeforeNextTest": 0,
                                                             "stop_criteria": {"num_packets": [1, 99]},
                                                             "quality_param": {"ttfp": [0, 5]}
                                                             },
                                                            {"name": "sub1G_band",
                                                             "rxChannel": 37,
                                                             "energizingPattern": 52,
                                                             "timeProfile": [5, 10],
                                                             "absGwTxPowerIndex": -1,
                                                             "maxTime": 5,
                                                             "stop_criteria": {"num_packets": [2, 99]},
                                                             "quality_param": {}
                                                             }
                                                        ]}}
        :type test_suite: dict
        :param selected_test: the name of test from the provided test suite (e.g. 'Dual Band' from the example above)
        :type selected_test: str
        :param gw_obj: if specified the gw object is based on the predefined specified gw obj,
                      otherwise the gw obj is defined by the app
        :type gw_obj: WiliotGateway
        :param black_list: a list with all the tags that are known as a noise or already tested tag that should not
                           be part of the current test
        :type black_list: list
        :param stop_event_trig: an event from outer scope which stops the app when it is triggered (set)
        :type stop_event_trig: threading.Event
        :param lock_print: if specified the logging prints according to the specified lock
        :type lock_print: threading.Lock()
        :param inlay: the tag inlay. most relevant for decrypted packets
        :type inlay: InlayTypes
        :param verbose: if True print all debug messages as well
        :type verbose: bool
        :param selected_test_dict: if specified the test suite run is based on selected_test_dict
        :type selected_test_dict: dict
        :param dir_for_gw_log: if specified the listener log would be save at the specified path
        :type dir_for_gw_log: str
        :param gw_test_cmds: if specified, the gateway will be configured with these commands each time after reset
        :type gw_test_cmds: NoneType or list
        """

        self.GwObj = gw_obj
        self.gw_ver = ''
        self.tester_name = tester_name
        self.start_test = False
        self.dev_mode = False
        self.parse_mode = False
        self.run_all = False
        self.max_ttfp = float('inf')
        self.previous_crc_env = None
        self.gw_test_cmds = gw_test_cmds if gw_test_cmds is not None else []
        self.client = client

        self.logger, self.logger_results, self.logger_gw = None, None, None
        self.init_loggers(logger_name=logger_name, logger_result_name=logger_result_name, logger_gw_name=logger_gw_name)

        self._lock_print = lock_print if lock_print is not None else threading.Lock()
        self.verbose = verbose

        self.selected_test = selected_test_dict
        self.set_test_suite(selected_test, test_suite, inlay)  # Set Test suite file - tests configuration
        self.gw_init(dir_for_gw_log=dir_for_gw_log)  # Set GW Object
        self.gw_reset_and_config()  # Init values for GW Object
        # prepare the gw for the next tag test:
        self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
        self.additional_gws = self.handle_additional_gws(dir_for_gw_log=dir_for_gw_log)

        if black_list is None:
            self.black_list = []
        else:
            self.black_list = black_list

        self.stop_event_trig = stop_event_trig
        self.test_results = WiliotTesterTagResultList()
        self.tag_results = None

    def init_loggers(self, logger_name, logger_result_name, logger_gw_name):
        if logger_name is None:
            wiliot_logger = WiliotTesterLog(run_name='wiliot_test')

            wiliot_dir = WiliotDir()
            log_path = os.path.join(wiliot_dir.get_common_dir(), 'logs')
            if not os.path.isdir(log_path):
                os.makedirs(log_path)
            wiliot_logger.set_logger(log_path=log_path)
            self.logger = wiliot_logger.logger
            self.logger_results = wiliot_logger.results_logger
            self.logger_gw = wiliot_logger.gw_logger

        else:
            self.logger = logging.getLogger(logger_name)
            if logger_result_name is None:
                self.logger_results = logging.getLogger(logger_name)
            else:
                self.logger_results = logging.getLogger(logger_result_name)
            if logger_gw_name is None:
                self.logger_gw = logging.getLogger(logger_name)
            else:
                self.logger_gw = logging.getLogger(logger_gw_name)

    def check_gw_version(self, gw_obj=None):
        """
        check if gw version is supported
        :return: True if version is supported
        :rtype: bool
        """
        is_main_gw = gw_obj is None
        gw_obj = self.GwObj if gw_obj is None else gw_obj
        gw_ver, __ = gw_obj.get_gw_version()
        gw_ver_num = [int(x, 16) for x in gw_ver.split('.')]
        if is_main_gw:
            self.gw_ver = gw_ver
        for ind, expect_ver in enumerate(supported_gw_version):
            if gw_ver_num[ind] > expect_ver:
                return True
            if gw_ver_num[ind] < expect_ver:
                raise Exception('GW version should be at least {}.{}.{} to support accurate tester features'.
                                format(supported_gw_version[0], supported_gw_version[1], supported_gw_version[2]))

        return True

    def handle_additional_gws(self, dir_for_gw_log=None):
        """
        example of test suite:
        {"Dual Gws": {
        "plDelay": 100,
        "rssiThresholdHW": 86,
        "rssiThresholdSW": 56,
        "maxTtfp": 5,
        "n_cycles": 1,
        "additionalGws": [{"gwName": "AAAAAAA", "gwMode": "ON"},
                          {"gwName": "BBBBBB", "gwMode": "MIRROR", "gwAdditionalGpio": "P030", "gwMainGpio": "P100"},
                          {"gwName": "CCCCCC", "gwMode": "INVERSE", "gwAdditionalGpio": "P030", "gwMainGpio": "P009",
                           "CH": 1, "EP": 18, "TP": [5,15], "PO": 22, "gwCommands": ["!version", "!pce"]}],
        "tests": []
    }}
        @param dir_for_gw_log:
        @type dir_for_gw_log:
        @return: list of the additional gws
        @rtype: list
        """
        additional_gws = []
        additional_gws_config = self.selected_test.get('additionalGws', [])
        if not additional_gws_config:
            return additional_gws

        for additional_gw_config in additional_gws_config:
            gw_name = additional_gw_config.get('gwName', None)
            gw_obj = self.gw_init(is_main=False, gw_name=gw_name, dir_for_gw_log=dir_for_gw_log,
                                  pass_packets=False)
            cmds = {}
            gw_short_mapping = {'CH': CommandDetails.scan_ch,
                                'EP': CommandDetails.set_energizing_pattern,
                                'TP': CommandDetails.time_profile,
                                'PO': None,
                                'SY': None}
            for k, cmd_item in gw_short_mapping.items():
                if k not in additional_gw_config.keys():
                    continue
                if k == 'PO':
                    cmds_output_power = gw_obj.get_cmds_for_abs_output_power(
                        abs_output_power=additional_gw_config['PO'])
                    cmds = {**cmds, **cmds_output_power}
                elif k == 'SY':
                    cmds[CommandDetails.set_scan_radio] = gw_obj.get_cmd_symbol_params(
                        freq_str=additional_gw_config['SY'])
                else:
                    cmds[cmd_item] = additional_gw_config[k]

            gw_obj.set_configuration(cmds=cmds, start_gw_app=False)

            for cmd in additional_gw_config.get('gwCommands', []):
                gw_obj.write(cmd=cmd, must_get_ack=True)
            if additional_gw_config.get('gwMode', 'ON').upper() == 'ON':  # options: ON, INVERSE, MIRROR
                gw_obj.set_configuration(start_gw_app=True)
            else:
                is_inverse = additional_gw_config['gwMode'].upper() == 'INVERSE'
                gw_obj.set_gw_control_gpio(is_controller=False,
                                           is_inverse=is_inverse,
                                           gpio=additional_gw_config.get('gwAdditionalGpio', None))
                self.GwObj.set_gw_control_gpio(is_controller=True,
                                               is_inverse=is_inverse,
                                               gpio=additional_gw_config.get('gwMainGpio', None))
            self.logger.info(f'additional gw was configured: {additional_gw_config}')
            additional_gws.append(gw_obj)

        return additional_gws

    def gw_init(self, is_main=True, gw_name=None, dir_for_gw_log=None, pass_packets=True):
        """
        initialize gw and the data listener
        """
        gw_obj = self.GwObj if is_main else None
        gw_name = self.selected_test.get('gwName', None) if gw_name is None else gw_name
        if gw_obj is None:
            gw_obj = WiliotGateway(auto_connect=True, logger_name=self.logger_gw.name, device_name=gw_name,
                                   log_dir_for_multi_processes=dir_for_gw_log, mp_reset_time_upon_gw_start=True,
                                   pass_packets=pass_packets)
            if is_main:
                self.GwObj = gw_obj
        try:
            if gw_obj.connected:
                gw_obj.reset_buffer()
                gw_obj.start_continuous_listener()
                if self.check_gw_version():
                    self._printing_func('GW obj initialized')
            else:
                raise Exception('gateway was not detected, please check connection')
        except Exception as e:
            self._printing_func(str(e), log_level=logging.WARNING)
            raise e
        return gw_obj

    def get_gw_object(self):
        return self.GwObj

    def get_gw_version(self):
        """
        get the gw firmware version
        :return: gw firmware version
        :rtype: str
        """
        return self.gw_ver

    def set_test_suite(self, selected_test, test_suite=None, inlay=None):
        """
        import the test suite
        :param selected_test: the test name from the test suites
        :type selected_test: str
        :param test_suite: if specified the dict of test suites as explain in the class init
        :type test_suite: dict
        :param inlay: the tag inlay (optional)
        :type inlay: InlayTypes
        """
        if not self.selected_test:
            # upload test suite:
            if test_suite is None:
                try:
                    test_suite = load_test_suite_file(tester_name=self.tester_name.value)
                except Exception as e:
                    self._printing_func('Test Suite input is wrong', log_level=logging.WARNING)
                    raise Exception(e)

            if test_suite is None:
                msg = 'Test Suite input in wrong'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)

            if selected_test not in test_suite:
                msg = 'the selected test: {} was not found in the tests suite'.format(selected_test)
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)
            self.selected_test = test_suite[selected_test]

        self.selected_test['inlay'] = inlay
        if 'devMode' in self.selected_test:
            self.dev_mode = True if self.selected_test['devMode'].lower() == 'true' else False
        if 'parseMode' in self.selected_test:
            if self.dev_mode:
                self.parse_mode = False
            else:
                self.parse_mode = True if self.selected_test['parseMode'].lower() == 'true' else False
            if self.parse_mode:
                if self.client is None:
                    raise Exception('parse mode is set to True but no client was provided')
        if 'maxTtfp' in self.selected_test:
            self.max_ttfp = float(self.selected_test['maxTtfp'])
        if 'run_all' in self.selected_test:
            if self.selected_test['run_all'].lower() == 'true':
                self.run_all = True
        self.selected_test['ignore_test_mode'] = 'ignore_test_mode' in self.selected_test
        for i, t in enumerate(self.selected_test['tests']):
            if 'sub1gGwTxPower' in t.keys():
                self.selected_test['tests'][i]['sub1g_power'] = t['sub1gGwTxPower']
            else:
                self.selected_test['tests'][i]['sub1g_power'] = MAX_SUB1G_POWER
            if 'absGwTxPowerIndex' in t.keys():
                self.selected_test['tests'][i]['gw_power_dict'] = \
                    valid_output_power_vals[t['absGwTxPowerIndex']]
            elif 'absGwTxPower' in t.keys():
                self.selected_test['tests'][i]['gw_power_dict'] = \
                    valid_output_power_vals[[p['abs_power']
                                             for p in valid_output_power_vals].index(t['absGwTxPower'])]
            elif 'GwTxPower' in t.keys():
                self.selected_test['tests'][i]['gw_power_dict'] = \
                    valid_output_power_vals[
                        [p['gw_output_power'] for p in valid_output_power_vals].index(t['GwTxPower'])]
            else:
                self.selected_test['tests'][i]['gw_power_dict'] = valid_output_power_vals[-1]
                if 'sub1gGwTxPower' not in t.keys():  # both output power are not defined
                    raise Exception('invalid tx gw power')

        self.selected_test['tests'] = int(self.selected_test.get('n_cycles', 1)) * self.selected_test['tests']

    def gw_reset_and_config(self, gw_obj=None, gw_params=None):
        """
        reset gw and config it to tester mode
        """
        gw_obj = self.GwObj if gw_obj is None else gw_obj
        gw_params = self.selected_test if gw_params is None else gw_params
        gw_obj.reconnect()
        gw_obj.reset_gw(reset_port=False)
        gw_obj.reset_listener()
        time.sleep(0.5)
        if not gw_obj.is_gw_alive():
            self._printing_func('gw_reset_and_config: wait more time since gw did not respond')
            time.sleep(5)

        cmds = {CommandDetails.set_rssi_th: [int(gw_params['rssiThresholdHW'])],
                CommandDetails.set_pl_delay: [int(gw_params['plDelay'])]}
        gw_obj.set_configuration(cmds=cmds, start_gw_app=False)
        for cmd in self.gw_test_cmds:
            gw_obj.write(cmd=cmd, must_get_ack=True)

    def check_if_trigger_was_received(self):
        n_gw_msg = self.GwObj.com_rsp_str_input_q.qsize()
        for i in range(n_gw_msg):
            gw_rsp = self.GwObj.com_rsp_str_input_q.get(timeout=None)
            if "Start Production Line GW" in gw_rsp['raw']:
                return True
        return False

    def get_wrong_crc(self):
        return self.previous_crc_env

    def wait_for_trigger(self, wait_for_gw_trigger):
        """
        wait for gw trigger, i.e. send 'Start Production Line' msg.
        if trigger was not received, gw reset and re-config to make sure there is no gw problem.
        :param wait_for_gw_trigger: the time [seconds] to wait to trigger,
                                    if the elapsed time is larger the function return False
        :type wait_for_gw_trigger: int or float
        :return: if trigger was detected return True
        :rtype: bool
        """
        gw_answer = ''
        gw_trigger_init = datetime.datetime.now()
        dt = datetime.datetime.now() - gw_trigger_init
        while gw_answer == '' and dt.total_seconds() < wait_for_gw_trigger:
            if self.is_stopped_by_user():
                break
            gw_answer = self.GwObj.read_specific_message(msg="Production Line GW", read_timeout=1)
            dt = datetime.datetime.now() - gw_trigger_init
        is_trigger_received = gw_answer != ''
        if is_trigger_received:
            match = re.search(r"WrongCRC=(\d+)", gw_answer)
            if match:
                self.previous_crc_env = match.group(1)
            self.GwObj.reset_start_time()
        else:
            self._printing_func('no trigger was detected. reset and config gw again', log_level=logging.INFO)
            self.previous_crc_env = None
            self.gw_reset_and_config()
            self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
        return is_trigger_received

    def power_index_to_value(self, power_index, abs_power=False, gw_output=False):
        """
        convert gw ouput power index to value according to valid_output_power_vals
        :param power_index: the index of the valid_output_power_vals list
        :type power_index: int
        :param abs_power: true if the desired value is the absolute output power value
        :type abs_power: bool
        :param gw_output: true if the desired value is the gw command output power value
        :type gw_output: bool
        :return: the desired value
        :rtype: int or str
        """
        all_power = self.GwObj.valid_output_power_vals
        if abs_power:
            return all_power[power_index]['abs_power']
        if gw_output:
            return all_power[power_index]['gw_output_power']

    def packet_filter(self, packet_list, filter_param='rssi', param_limits=None, ignore_test_mode_packet=False, max_time=None):
        """
        filter the packets from the packet_list according to the filter_param and the param_limits.
        packets that were filtered out of the test does no take into account during the test and considered as noise

        :param packet_list: the incoming packets list
        :type packet_list: PacketList or DecryptedPacketList
        :param filter_param: one of the packet dataframe column names
        :type filter_param: str
        :param param_limits: list of two elements [x, y] that defines the range of the valid param (x,y including)
        :type param_limits: list
        :param ignore_test_mode_packet: if true, it shall filter out test mode packet
        :type ignore_test_mode_packet: bool
        :return: the filtered packet list
        :rtype: PacketList or DecryptedPacketList
        """

        def update_custom_data(packet, key, value):
            if key in packet.custom_data.keys():
                packet.custom_data[key].append(value)
            else:
                packet.custom_data[key] = [value]

        if param_limits is None:
            param_limits = [0, float('inf')]
        filtered_packet_list = PacketList() if not self.dev_mode else DecryptedPacketList()

        for p in packet_list:
            # fix zero adva on first packet:
            if self.dev_mode and N_CHAR_ADVA * '0' in p.packet_data['adv_address']:
                tag_id = p.decoded_data.get('tag_id', N_CHAR_ADVA * '0')
                p.packet_data['adv_address'] = \
                    p.packet_data['adv_address'][:HALF_N_CHAR_FLOW] + tag_id[-N_CHAR_ADVA:] + \
                    p.packet_data['adv_address'][-HALF_N_CHAR_FLOW:]
            # filter packets from black list:
            if p.packet_data['adv_address'] in self.black_list:
                p.add_custom_data(custom_data={'packet_status': 'blacklist'})
            elif ignore_test_mode_packet and p.packet_data['test_mode'] == 1:
                p.add_custom_data(custom_data={'packet_status': 'test_mode'})
            else:
                # filter packets by filter param:
                packet_time_list = p.extract_packet_data_by_name('time_from_start') if max_time is not None else []
                packet_param_list = p.extract_packet_data_by_name(filter_param)
                sprinkler_ids = []
                for i, param in enumerate(packet_param_list):
                    if max_time is not None and packet_time_list[i] > max_time:
                        update_custom_data(p, 'packet_status', 'timeout')
                    elif param_limits[0] <= param <= param_limits[-1]:
                        update_custom_data(p, 'packet_status', 'good')
                        sprinkler_ids.append(i)
                    else:
                        update_custom_data(p, 'packet_status', filter_param)

                if len(sprinkler_ids) > 0:
                    filtered_packet_list.append(p.filter_by_sprinkler_id(sprinkler_ids=sprinkler_ids))

        return filtered_packet_list

    def select_tag_under_test(self, optional_tags):
        """
        select which tag is under test even if more than one tag sends packets
        :param optional_tags: all tags that transmits during the tag-test
        :type optional_tags: list
        :return: the packet list of the selected tag under test
        :rtype: PacketList or DecryptedPacketList
        """
        selected_adva = None
        self._printing_func('Starting to decide which tag is under test')
        optional_tags = list(set(optional_tags))
        if len(optional_tags) == 0:
            selected_adva = ''
        elif len(optional_tags) == 1:
            selected_adva = optional_tags[0]
            self.tag_results.selected_tag = self.tag_results.all_tags.tags[selected_adva]
        else:  # more than one tag reach the stop criteria:
            tags_in_tie = False
            min_rssi = None
            max_size = None
            for adva in optional_tags:
                cur_mean_rssi = self.tag_results.filtered_tags.get_avg_rssi_by_id(id=adva)
                if min_rssi is None or cur_mean_rssi < min_rssi:  # best tag
                    min_rssi = cur_mean_rssi
                    max_size = self.tag_results.filtered_tags.tags[adva].size()
                    selected_adva = adva
                elif min_rssi is not None and cur_mean_rssi == min_rssi:  # tiebreak between tags
                    if self.tag_results.filtered_tags.tags[adva].size() > max_size:
                        max_size = self.tag_results.filtered_tags.tags[adva].size()
                        selected_adva = adva
                    if self.tag_results.filtered_tags.tags[adva].size() == max_size:
                        self._printing_func('we cannot select which tag is under test since both tags: {}, {} have '
                                            'the same rssi mean and number of packets'.format(adva, selected_adva))
                        tags_in_tie = True
                elif min_rssi is not None and cur_mean_rssi > min_rssi:  # noisy tag
                    self.black_list.append(adva)
                    self._printing_func('tag: {} was added to blacklist'.format(adva))

            if selected_adva is None:
                msg = 'no rssi was found for the selected packets'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception(msg)
            elif tags_in_tie:
                pass
            else:
                self.tag_results.selected_tag = self.tag_results.all_tags.tags[selected_adva]

        return selected_adva

    def get_packets(self, filter_param='rssi', filter_value=0, data_type=DataType.PACKET_LIST, max_time=None):
        """
        receive packets from the gw (via the listener) and filter them according to packet_filter()
        :param filter_param: one of the packet dataframe column names (for packet_filter)
        :type filter_param: str
        :param filter_value: the max valid value of the specified param
        :type filter_value: int
        :param data_type: data type of the received packets
        :type data_type: DataType
        :return: True if packet were received
        :rtype: bool
        """
        packets_received_list = None
        if self.GwObj.is_data_available():
            packets_received_list = self.GwObj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                           data_type=data_type,
                                                           tag_inlay=self.selected_test['inlay'])
        if packets_received_list:
            if packets_received_list.size() > 1:
                self._printing_func('pulled more than one packet from the queue, check analysis performance')

            self.print_packets(packets_received_list)
            filtered_packets = self.packet_filter(packets_received_list, filter_param=filter_param,
                                                  param_limits=[0, filter_value],
                                                  ignore_test_mode_packet=self.selected_test['ignore_test_mode'],
                                                  max_time=max_time)
            self.tag_results.all_packets.__add__(packets_received_list)
            if filtered_packets.size():
                if self.parse_mode:
                    self.enrich_packet_list(filtered_packets)
                self.tag_results.filtered_tags = \
                    self.tag_results.add_packets_to_multi_tags(filtered_packets, self.tag_results.filtered_tags)
                self.print_packets(packets_received_list, 'pass the packet filter')
            return True
        else:
            return False
        
    def enrich_packet_list(self, packet_list):
        flow_version_list = [p.packet_data['flow_ver'] for p in packet_list]
        if len(list(set(flow_version_list))) == 1:
            # take the first flow version from the packets, and run parsing on all payloads
            flow_version = flow_version_list[0]
            payloads = list(packet_list.payload_map_list.keys())
            self.logger.info(f'send parse api request with flow version: {flow_version} and payloads: {payloads}')
            res = self.client.parse_payload(
                packet_version=str(get_packet_version_by_flow_version(flow_version)),
                flow_version=flow_version, payloads=payloads)
            self.logger.info(f'received answer from parse api: {res}')
            packet_list.enrich(res['results'])
        else:
            # take all flow versions from the packets, and run parsing on each group
            for flow_version in list(set(flow_version_list)):
                payloads = []
                for p in packet_list:
                    if p.packet_data['flow_ver'] == flow_version:
                        payloads.append(p.get_payload())
                res = self.client.parse_payload(
                    packet_version=str(get_packet_version_by_flow_version(flow_version)),
                    flow_version=flow_version,payloads=payloads)
                packet_list.enrich(res['results'])

    def print_packets(self, packets_received_list, last_str='received packets'):
        for p in packets_received_list:
            packet_print = (f'ADVA:{p.get_adva()},    FLOW:{p.get_flow()},    RSSI:{p.get_rssi()},    '
                            f'{p.get_packet_string()}')
            self._printing_func(f'{packet_print} {last_str}', log_level=logging.DEBUG)

    def is_stop_criteria_reached(self, tags_reached_criteria):
        return len(tags_reached_criteria) > 0

    def check_stop_criteria(self, stop_criteria_dict=None, check_type=['general']):
        """
        check if the received packet met the stop criteria and the test should be stopped
        :param stop_criteria_dict: dictionary according to the test suite definition, (e.g. {"num_packets": [1, 99]})
        :type stop_criteria_dict: dict
        :param check_type: specified the type of stop criteria to improve performance
        :type check_type: list[str]
        :return: the tags which reached the stop criteria
        :rtype: list
        """

        if stop_criteria_dict == {}:
            return []
        tags_stat_df = pd.DataFrame()
        if 'packets' in check_type:
            for tag_id, tag in self.tag_results.filtered_tags.tags.items():
                tags_stat_dict = {'adv_address': tag_id, 'num_packets': tag.size()}
                tag_id_df = pd.DataFrame(tags_stat_dict, index=[0])
                tags_stat_df = pd.concat([tags_stat_df, tag_id_df], axis=0)
        if 'external_sensor' in check_type:
            tags_stat_df = pd.concat([tags_stat_df, self.tag_results.get_sensor_statistics()], axis=0)
        if 'general' in check_type:
            tags_stat_df = pd.concat([tags_stat_df, self.tag_results.filtered_tags.get_statistics()], axis=0)
        tags_reached_criteria = []
        if tags_stat_df.size > 0:
            for _, tag in tags_stat_df.iterrows():
                try:
                    self.logger.debug(f'check {[(k, tag.get(k, None)) for k in stop_criteria_dict.keys()]}')
                    criteria_status = [v[0] <= tag[k] <= v[-1] if k in tag.keys() and not pd.isnull(tag[k]) else False
                                       for k, v in stop_criteria_dict.items()]
                    if all(criteria_status):
                        tags_reached_criteria.append(tag['adv_address'] if 'adv_address' in tag.keys() else
                                                     tag['tag_id'])
                except Exception as e:
                    raise e

        return tags_reached_criteria

    def is_gw_fetal_error(self, packet_list=None):
        """
        check if the gw reset itself for some reason or if it needs to be reset
        :param packet_list: the received packets list
        :type packet_list: PacketList
        :return:
        :rtype:
        """
        if not self.GwObj.is_connected():
            self._printing_func('GW was disconnected. trying to initiate connection...', log_level=logging.WARNING)
            self.GwObj.open_port(self.GwObj.port, self.GwObj.baud)
            return True

        if self.GwObj.get_read_error_status():
            self._printing_func('A GW reading Error was detected', log_level=logging.WARNING)
            return True

        if packet_list is None:
            return False
        # check if GW's clock was reset (relevant only to GW ver 3.8.14 and lower)
        try:
            is_old_gw_ver = int(self.get_gw_version().split('.')[0]) < 4
        except Exception as e:
            is_old_gw_ver = True  # do the test next test anyway

        if is_old_gw_ver:
            counter = 0
            for p in packet_list:
                if p.gw_data['stat_param'].size > 1:
                    for s in p.gw_data['stat_param']:
                        if s == 0:
                            counter = counter + 1
                            if counter > 1:
                                return True
                else:
                    if p.gw_data['stat_param'] == 0:
                        counter = counter + 1
                        if counter > 1:
                            return True
        return False

    def statistics_analyzer(self, test_param=None, test_num=None):
        """
        test the quality of the test according to test_param
        :param test_param: the test parameters including the quality parameters which defines if
                           the tag passed or failed the test (e.g.
        :type test_param: dict
        :param test_num: the test number
        :type test_num: int
        :return: True if the tag passed the test
        :rtype: bool
        """

        # add test num to the packets:
        self.tag_results.add_selected_tag_statistics(custom_data={'test_num': test_num})
        if self.is_gw_fetal_error(self.tag_results.selected_tag):
            self.logger_results.warning('gw fetal error was detected')
            self.gw_reset_and_config()
            self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
            self.tag_results.test_status = FailureCodes.GW_ERROR
            targets_status = [False]
        elif 'quality_param' in test_param and len(test_param['quality_param']) > 0:
            sensor_statistics_dict = self.tag_results.get_sensor_statistics(data_type='selected_tag').to_dict()
            sensor_statistics_dict = {k: list(v.values())[0] for k, v in sensor_statistics_dict.items()}
            self.tag_results.selected_tag_statistics = {**sensor_statistics_dict, **self.tag_results.selected_tag_statistics}
            targets_status = [v[0] <= self.tag_results.selected_tag_statistics[k] <= v[-1]
                              if k in self.tag_results.selected_tag_statistics.keys() else False
                              for k, v in test_param['quality_param'].items()]
            temp_values = {k: self.tag_results.selected_tag_statistics[k]
                           if k in self.tag_results.selected_tag_statistics.keys() else None
                           for k in test_param['quality_param'].keys()}
            self.logger_results.info(f'selected tag values: {temp_values}')
            self.tag_results.set_quality_test_failure(test_param['quality_param'], targets_status)

        else:
            targets_status = [True]

        return all(targets_status)

    def init_gw_test(self, sub_test=None, is_start_gw_app=True):
        # Config GW according to Test Suite
        self.GwObj.reset_listener()
        if sub_test is None:
            sub_test = self.selected_test['tests'][0]

        is_gw_commands = 'gw_commands' in sub_test
        cmds = {CommandDetails.set_energizing_pattern: [sub_test['energizingPattern']],
                CommandDetails.scan_ch: [int(sub_test['rxChannel'])],
                CommandDetails.time_profile: sub_test['timeProfile'],
                }
        if sub_test['gw_power_dict'] is not None:
            cmds[CommandDetails.output_power] = [sub_test['gw_power_dict']['gw_output_power']]
            cmds[CommandDetails.bypass_pa] = [sub_test['gw_power_dict']['bypass_pa']]
        if sub_test['sub1g_power'] is not None:
            cmds[CommandDetails.set_sub_1_ghz_power] = [sub_test['sub1g_power']]
        if 'symbol' in sub_test:
            cmds[CommandDetails.set_scan_radio] = self.GwObj.get_cmd_symbol_params(freq_str=sub_test['symbol'])
        self.GwObj.set_configuration(cmds=cmds,
                                     start_gw_app=is_start_gw_app and not is_gw_commands)

        if is_gw_commands:
            for cmd in sub_test['gw_commands']:
                self.GwObj.write(cmd=cmd, must_get_ack=True)
            self.GwObj.set_configuration(start_gw_app=is_start_gw_app)

    def init_test(self, sub_test, is_start_gw_app=True, test_num=0):
        """
        initialize the test
        :param sub_test: the test parameter according to the test suite definition
        :type sub_test: dict
        :param is_start_gw_app: if True, the gw starts its application (transmit and receive)
        :type is_start_gw_app: bool
        :param test_num: the number of the sub=test in the same test
        :type test_num: int
        """
        self.tag_results.test_start = datetime.datetime.now()

        self.logger_results.info(
            f'Input parameters for GW:\nStage name : {sub_test["name"]}\nPattern '
            f': {sub_test["energizingPattern"]}\nTime Profile : {sub_test["timeProfile"]}\n'
            f'GW Power : {sub_test["gw_power_dict"]["abs_power"] if sub_test["gw_power_dict"] is not None else None}dBm'
            f'\nsub1G Power : {sub_test["sub1g_power"]}dBm\nRX Channel : {sub_test["rxChannel"]}\n'
            f'-------------------------------------------------------------------------')

        # Config GW according to Test Suite
        if test_num > 0:  # first sub-test is already config before the trigger
            self.init_gw_test(sub_test=sub_test, is_start_gw_app=is_start_gw_app)

        # doc config param
        self.tag_results.add_run_data(test_param=sub_test)

    def is_stopped_by_user(self):
        return self.stop_event_trig is not None and self.stop_event_trig.is_set()

    def _printing_func(self, msg, logger_name=LoggerName.MAIN, log_level=logging.INFO):
        """
        internal function to print the logs
        :param msg: the message to print
        :type msg: str
        :param logger_name: the logger name
        :type logger_name: LoggerName
        :param log_level: the log level
        :type log_level: logging.INFO
        """
        if self.verbose or log_level != logging.DEBUG:
            with self._lock_print:
                if logger_name.value == 'main':
                    self.logger.log(log_level, msg)
                elif logger_name.value == 'gw':
                    self.logger_gw.log(log_level, msg)
                elif logger_name.value == 'results':
                    self.logger_results.log(log_level, msg)

    def add_to_blacklist(self, new_blacklist):
        """
        add tags advertising address to the black list
        :param new_blacklist: new tag id to add to the black list
        :type new_blacklist: str or list
        """
        if isinstance(new_blacklist, list):
            self.black_list += new_blacklist
        elif isinstance(new_blacklist, str):
            self.black_list.append(new_blacklist)
        else:
            raise Exception('trying to add new member to black list of unsupported type: {}'.format(new_blacklist))

    def init_run(self):
        self.test_results = WiliotTesterTagResultList()
        self.tag_results = WiliotTesterTagResult(self.dev_mode)

    @staticmethod
    def check_type_per_test(stop_criteria_dict):
        stop_criteria_list = list(stop_criteria_dict.keys())
        check_type = []
        if 'external_sensor_mean' in stop_criteria_list or 'external_sensor_n_samples' in stop_criteria_list:
            check_type.append('external_sensor')
            try: stop_criteria_list.remove('external_sensor_mean')
            except ValueError: pass
            try: stop_criteria_list.remove('external_sensor_n_samples')
            except ValueError: pass
        if 'num_packets' in stop_criteria_list:
            check_type.append('packets')
            stop_criteria_list.remove('num_packets')
        if len(stop_criteria_list) > 0:
            check_type.append('general')
        return check_type

    def run(self, wait_for_gw_trigger=None, need_to_manual_trigger=True):
        """
        Flow:
        1. wait for trigger if wait_for_gw_trigger is specified.
        2. Collect filtered packets (e.g. filtered by rssi)
        3. Check if we reached stop criteria - according to stop criteria list
        4. Check if test passed according to performance criteria:
            A. identify the tag under test
            B. test the selected tag performance

        Stop Criteria list:
        1. test time expired
        2. time to first packet expired if max_ttfp is specified
        3. external stop event, is stop_event_trig was specified whn init the class
        4. parameter according to the tests_suite.json (e.g. number of packets)

        :param wait_for_gw_trigger: if specified, the test waits the specified seconds for the gw trigger and
                                    starts only when triggered
        :type wait_for_gw_trigger: float or NoneType
        :param need_to_manual_trigger: if True and wait_for_gw_trigger is not specified, a serial command is sent to
                                       the gw at the start of the test
        :return: the test results including all the tags and test information
        :rtype: WiliotTesterTagResultList
        """

        self._printing_func('New tag test starts from API', logger_name=LoggerName.RESULTS)

        self.init_run()

        # wait for trigger if needed
        if wait_for_gw_trigger is None:
            self.start_test = True
            if need_to_manual_trigger:
                self.GwObj.set_configuration(start_gw_app=True)
                self.GwObj.reset_start_time()
        else:
            self._printing_func('Wait for GW trigger for {} second'.format(wait_for_gw_trigger))
            self.start_test = self.wait_for_trigger(wait_for_gw_trigger)

        # check if test can be started:
        if self.is_stopped_by_user():
            self._printing_func('Run was stopped by the stop event before it started', log_level=logging.INFO)
            return self.test_results

        if not self.start_test:
            return self.test_results

        self.test_results.set_trigger_time()

        # Test begins
        self._printing_func('Trigger received')

        num_of_tests = len(self.selected_test['tests'])
        all_selected_tags = []
        for test_num in range(num_of_tests):
            sub_test = self.selected_test['tests'][test_num]

            test_check_type = self.check_type_per_test(sub_test['stop_criteria'])

            # init sub-test
            self._printing_func('---------------------Started stage {} out of {} stages-----------------------'.
                                format(test_num + 1, num_of_tests), logger_name=LoggerName.RESULTS)
            self.tag_results = WiliotTesterTagResult(self.dev_mode)
            self.init_test(sub_test=sub_test, test_num=test_num)

            # Start test check
            tags_reached_criteria = []
            time_expired = False
            test_end = False
            max_test_time = float(sub_test['maxTime'])
            max_ttfp_time = min([float(sub_test['maxTime']), self.max_ttfp])
            while not test_end:
                if self.is_stopped_by_user():
                    break
                # check if trigger was received during run:
                if self.check_if_trigger_was_received():
                    self._printing_func('Gateway got trigger during run. Please check the Machine')
                    raise Exception('Gateway got trigger during run. Please check the Machine')

                # collect filtered packets
                data_type = DataType.PACKET_LIST if not self.dev_mode else DataType.DECODED
                is_received_packet = self.get_packets(filter_value=self.selected_test['rssiThresholdSW'],
                                                      data_type=data_type)
                if is_received_packet:
                    # check if we reached stop criteria:
                    tags_reached_criteria = self.check_stop_criteria(stop_criteria_dict=sub_test['stop_criteria'],
                                                                     check_type=test_check_type)

                    if self.is_stop_criteria_reached(tags_reached_criteria):
                        self._printing_func('test reached stop criteria - starting to analyze the results')
                        test_end = True
                        break
                else:
                    time.sleep(0)  # allow time for recovery
                    # check if GW ERROR occurred and fix it:
                    if self.is_gw_fetal_error():
                        self.logger_results.warning('gw fetal error was detected')
                        if not self.GwObj.is_connected():
                            raise Exception('Could not reconnect to the GW. please check connections')
                        self.gw_reset_and_config()
                        self.init_gw_test(sub_test=sub_test, is_start_gw_app=True)
                        self.tag_results.test_status = FailureCodes.GW_ERROR
                dt = (datetime.datetime.now() - self.tag_results.test_start).total_seconds()
                time_expired = dt > (max_test_time if len(self.tag_results.all_packets) > 0 else max_ttfp_time)
                if time_expired:
                    self._printing_func(f'time has expired after {dt}', logger_name=LoggerName.RESULTS)
                    break
            
            # stop gw from transmitting
            is_stopped = self.GwObj.stop_gw_app()
            if not is_stopped:
                self.logger_results.warning('could not stop GW app')
                raise Exception('could not stop GW app')

            # get remaining packets and check stop criteria again:
            is_received_packet = self.get_packets(filter_value=self.selected_test['rssiThresholdSW'],
                                                  data_type=data_type, max_time=max_test_time)
            if is_received_packet:
                tags_reached_criteria = self.check_stop_criteria(stop_criteria_dict=sub_test['stop_criteria'],
                                                                check_type=test_check_type)
                if self.is_stop_criteria_reached(tags_reached_criteria) and not test_end:
                    self._printing_func('test reached stop criteria just before time expired')
                    test_end = True

            # update results:
            self.tag_results.all_tags = self.tag_results.add_packets_to_multi_tags(
                packets_in=self.tag_results.all_packets,
                multi_tag_out=self.tag_results.all_tags)

            # check why the test is over
            if test_end or sub_test['stop_criteria'] == {}:
                self.analyze_end_of_test(sub_test, tags_reached_criteria, all_selected_tags, test_num, num_of_tests)

            elif time_expired:  # time expired before reaching stop criteria
                self.analyze_time_expired(test_num)

            elif self.is_stopped_by_user():  # Stop event was triggered
                self._printing_func('Stop was triggered')
                self._printing_func('Tag marked as Fail', logger_name=LoggerName.RESULTS)
                self.tag_results.test_status = FailureCodes.STOP_BY_USER

            else:
                msg = 'test was stopped due to unknown reason'
                self._printing_func(msg, log_level=logging.WARNING)
                raise Exception('test was stopped due to unknown reason')

            self.test_results.append(self.tag_results)
            # check if delays between stages/sub-test
            if 'delayBeforeNextTest' in sub_test:
                self._printing_func('Going to sleep for {} second '.format(sub_test['delayBeforeNextTest']))
                t_i = datetime.datetime.now()
                dt = datetime.datetime.now() - t_i
                while dt.total_seconds() < float(sub_test['delayBeforeNextTest']):
                    dt = datetime.datetime.now() - t_i
            # end of test:
            self.tag_results.test_end = datetime.datetime.now()
            if self.tag_results.test_status != FailureCodes.PASS and not self.run_all:
                break  # stop the test if one of the stages was failed

        # prepare gw for the next run:
        if num_of_tests > 1:
            self.init_gw_test(sub_test=self.selected_test['tests'][0], is_start_gw_app=False)
        return self.test_results

    def analyze_end_of_test(self, sub_test, tags_reached_criteria, all_selected_tags, test_num, num_of_tests):
        if sub_test['stop_criteria'] != {}:
            selected_test_tag = self.select_tag_under_test(optional_tags=tags_reached_criteria)  # Get the best tag
        else:
            all_optional_tags = list(self.tag_results.filtered_tags.tags.keys())
            selected_test_tag = self.select_tag_under_test(optional_tags=all_optional_tags)  # Get the best tag

        # check selected tag on all previous tests
        if selected_test_tag and selected_test_tag not in all_selected_tags:
            is_diff_tag_btwn_sub_tests = len(all_selected_tags) > 0
            all_selected_tags.append(selected_test_tag)
        else:
            is_diff_tag_btwn_sub_tests = False

        if not is_diff_tag_btwn_sub_tests and len(all_selected_tags) > 0:
            self._printing_func('Tag {} was selected'.format(selected_test_tag))
            # selected tag performance:

            self.tag_results.is_test_passed = self.statistics_analyzer(test_param=sub_test, test_num=test_num)
            if self.tag_results.is_test_passed:
                self.tag_results.test_status = FailureCodes.PASS
                self._printing_func('Stage {} out of {} Passed'.format(test_num + 1, num_of_tests),
                                    logger_name=LoggerName.RESULTS)
            else:
                self._printing_func('Tag failed quality test', logger_name=LoggerName.RESULTS,
                                    log_level=logging.DEBUG)
                self._printing_func('Stage {} out of {} Failed'.format(test_num + 1, num_of_tests),
                                    logger_name=LoggerName.RESULTS)
        elif selected_test_tag == '':
            self.tag_results.test_status = FailureCodes.NO_RESPONSE
            self._printing_func("No Responds during run_all mode")
        else:  # selected_test_tag is None:
            self.tag_results.test_status = FailureCodes.SEVERAL_TAGS_UNDER_TEST
            self._printing_func("Couldn't decide which tag transmitting, it will fail")

    def analyze_time_expired(self, test_num):
        self._printing_func('Stage {} Failed - Timeout'.format(test_num + 1),
                            logger_name=LoggerName.RESULTS)
        if self.tag_results.test_status == FailureCodes.GW_ERROR:
            pass
        elif self.tag_results.all_packets.size() == 0:
            self.tag_results.test_status = FailureCodes.NO_RESPONSE
        elif len(self.tag_results.filtered_tags) == 0:
            self.tag_results.test_status = FailureCodes.NO_PACKETS_UNDER_RSSI_THR
        else:
            self.tag_results.test_status = FailureCodes.NOT_ENOUGH_PACKETS

    def exit_tag_test(self, need_to_close_port=True):
        if need_to_close_port:
            self.GwObj.close_port(is_reset=True)
        else:
            self.GwObj.reset_gw()
        self.GwObj.exit_gw_api()
        for gw in self.additional_gws:
            gw.reset_gw()
            gw.exit_gw_api()


def load_test_suite_file(tester_name):
    tester_path = os.path.join(os.path.split(os.path.abspath(__file__))[0], tester_name)
    tests_suites_path = os.path.join(os.path.join(tester_path, 'configs'), 'tests_suites.json')
    tests_suites_eng = os.path.join(os.path.join(tester_path, 'configs'), 'tests_suites_eng.json')
    if os.path.isfile(tests_suites_eng):
        tests_suites_path = tests_suites_eng
    if os.path.isfile(tests_suites_path):
        with open(tests_suites_path) as json_file:
            test_suite = json.load(json_file)
    else:
        raise Exception(f'cannot find config file tests_suites.json under {tests_suites_path}')
    return test_suite


if __name__ == '__main__':
    from csv import DictWriter
    import os

    from wiliot_api.manufacturing.manufacturing import ManufacturingClient
    from wiliot_testers.wiliot_tester_log import WiliotTesterLog
    from wiliot_testers.wiliot_tester_tag_result import ConversionTypes, SurfaceTypes, FailureCodes
    from wiliot_testers.utils.get_version import get_version
    from wiliot_core import InlayTypes

    def stop_run():
        my_stop_event.set()


    def dict_to_csv(dict_in, path, append=False, only_titles=False):
        if append:
            method = 'a'
        else:
            method = 'w'
        with open(path, method, newline='') as f:
            dict_writer = DictWriter(f, fieldnames=dict_in.keys())
            if not append:
                dict_writer.writeheader()
            if not only_titles:
                dict_writer.writerow(dict_in)
            f.close()


    def update_run_data(run_data_path, run_data, res=None, save_to_csv=True):
        if res is not None:
            run_data['total_run_tested'] += 1
            run_data['total_run_passed_offline'] += res.get_total_test_status()
            run_data['run_responsive_tags_yield'] = \
                (run_data['total_run_responding_tags'] / run_data['total_run_tested']) * 100
            run_data['run_offline_yield'] = \
                (run_data['total_run_passed_offline'] / run_data['total_run_tested']) * 100

        if save_to_csv:
            dict_to_csv(dict_in=run_data, path=run_data_path)


    def update_packet_data(packets_data_path, res=None, test_data=None, only_titles=False):

        def save_default_packet_data(summary=None):
            default_data = {'raw_packet': None, 'adv_address': None, 'decrypted_packet_type': None,
                            'group_id': None, 'flow_ver': None,
                            'test_mode': None, 'en': None, 'type': None, 'data_uid': None, 'nonce': None,
                            'enc_uid': None, 'mic': None, 'enc_payload': None, 'gw_packet': None, 'rssi': None,
                            'stat_param': None, 'time_from_start': None, 'counter_tag': None,
                            'is_valid_tag_packet': None, 'common_run_name': test_data['common_run_name'],
                            'tag_run_location': test_data['tag_run_location'],
                            'total_test_duration': None, 'total_location_duration': None, 'status_offline': None,
                            'fail_bin': test_data['fail_bin'], 'fail_bin_str': test_data['fail_bin_str'],
                            'external_id': None,
                            'qr_validated': test_data['qr_validated'], 'test_num': test_data['test_num'],
                            'trigger_time': test_data['trigger_time'], 'packet_status': None,
                            'number_of_responding_tags': test_data['number_of_responding_tags']}
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
            default_ordered_dict = {k: default_dict[k] for k in packet_headers_default}
            dict_to_csv(dict_in=default_ordered_dict, path=packets_data_path, append=(not only_titles),
                        only_titles=only_titles)

        if res is not None:
            test_data['status_offline'] = int(res.get_total_test_status())
            test_data['total_test_duration'] = res.get_total_test_duration()
            test_data['fail_bin'] = res.get_total_fail_bin()
            test_data['fail_bin_str'] = res.get_total_fail_bin(as_name=True)
            test_data['trigger_time'] = res.get_trigger_time()
            for i, r in enumerate(res):
                test_data['test_num'] = i
                r_sum = r.get_summary()

                # add packets info:
                if r.all_packets.size():
                    # we received packets
                    for p in r.all_packets:
                        p.add_custom_data(
                            custom_data={**test_data, **r_sum})
                    r.all_packets.to_csv(path=packets_data_path, append=True, export_packet_id=False,
                                         columns=packet_headers_default)
                else:
                    # no responds in current test
                    save_default_packet_data(summary=r_sum)

        else:
            test_data['test_num'] = 0
            save_default_packet_data()


    log_path = os.path.join(os.path.expanduser('~'), 'Downloads')
    black_list = ['A', 'B']
    test_suite = {"Light_Sensors_Test": {
    "plDelay": 100,
    "rssiThresholdHW": 86,
    "rssiThresholdSW": 70,
    "maxTtfp": 5.0,
    "devMode": "false",
    "parseMode": "true",
    "tests": [
        {
            "name": "sensor_test",
            "rxChannel": 37,
            "energizingPattern": 18,
            "timeProfile": [
                5,
                10
            ],
            "absGwTxPowerIndex": -1,
            "maxTime": 5.0,
            "delayBeforeNextTest": 0.0,
            "stop_criteria": {
                "external_sensor_mean": [
                    112.0,
                    230.0
                ],
                "external_sensor_n_samples": [
                    0.0,
                    999.0
                ],
                "num_packets": [
                    1,
                    99
                ],
                "aux_meas_rate_total": [
                    1,
                    99
                ]
            },
            "quality_param": {
                "external_sensor_mean": [
                    112.0,
                    230.0
                ],
                "external_sensor_n_samples": [
                    0.0,
                    999.0
                ]
            },
            "gw_commands": []
        }
    ]
  },}
    run_data = {'common_run_name': 'test_test', 'tester_station_name': 'Wiliot',
                'operator': 'Shunit', 'reel_run_start_time': None, 'reel_run_end_time': None,
                'batch_name': 'reel1', 'tester_type': 'offline', 'comments': '',
                'total_run_tested': 0, 'total_run_responding_tags': 0,
                'total_run_passed_offline': 0,
                'total_missing_labels': 0, 'run_responsive_tags_yield': float('nan'),
                'run_offline_yield': float('nan'), 'ttfp_avg': float('nan'),
                'conversion_type': ConversionTypes.STANDARD.value, 'inlay': InlayTypes.TEO_086.value,
                'test_suite': list(test_suite.keys())[0], 'test_suite_dict': test_suite,
                'surface': SurfaceTypes.AIR.value, 'to_print': True, 'qr_validation': True,
                'print_pass_job_name': 'job_name', 'printing_format': 'SGTIN',
                'external_id_prefix': 'aaa',
                'external_id_suffix_init_value': 0,
                'coupler_partnumber': 'abcd',
                'gw_version': None, 'py_wiliot_version': get_version(), 'upload_date': None, 'owner_id': 'wiliot-ops'}
    packet_headers_default = ['common_run_name', 'tag_run_location', 'test_num', 'external_id',
                              'time_from_start', 'raw_packet', 'rssi', 'packet_status', 'adv_address',
                              'selected_tag',
                              'is_test_pass', 'status_offline', 'fail_bin', 'fail_bin_str', 'test_status',
                              'num_packets', 'num_cycles', 'sprinkler_counter_mean', 'sprinkler_counter_std',
                              'sprinkler_counter_min', 'sprinkler_counter_max', 'tbp_mean', 'tbp_std',
                              'tbp_min', 'tbp_max', 'tbp_num_vals', 'per_mean', 'per_std', 'rssi_mean',
                              'rssi_std', 'rssi_min', 'rssi_max', 'ttfp', 'rx_rate_normalized', 'rx_rate',
                              'total_test_duration', 'total_location_duration', 'test_start_time',
                              'trigger_time', 'test_end_time',
                              'qr_validated', 'rx_channel', 'energizing_pattern', 'time_profile',
                              'decrypted_packet_type', 'group_id', 'flow_ver', 'test_mode', 'en',
                              'type', 'data_uid', 'nonce', 'enc_uid', 'mic', 'enc_payload', 'gw_packet',
                              'stat_param']
    run_name = run_data['common_run_name'] + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    my_logger = WiliotTesterLog(run_name=run_name)
    my_logger.set_logger(log_path=log_path)

    my_logger.create_data_dir(data_path=log_path, tester_name='offline', run_name=run_name)
    my_stop_event = threading.Event()
    client = ManufacturingClient(api_key=os.environ.get('TEST_OWNER1_MANUFACTURING_API_KEY'), owner_id='wiliot-ops')
    wiliot_tag_test = WiliotTesterTagTest(selected_test='Light_Sensors_Test', test_suite=test_suite,
                                          stop_event_trig=my_stop_event,
                                          logger_name=my_logger.logger.name,
                                          logger_result_name=my_logger.results_logger.name,
                                          logger_gw_name=my_logger.gw_logger.name,
                                          black_list=black_list,
                                          client=client,
                                          inlay=run_data['inlay'])

    run_data['gw_version'] = wiliot_tag_test.get_gw_version()
    my_wait_for_gw_trigger = None
    cont_run = True

    my_timer = threading.Timer(20, stop_run)
    my_timer.start()
    missing_label = False
    run_data['reel_run_start_time'] = datetime.datetime.now()
    test_data = {'common_run_name': run_data['common_run_name'], 'tag_run_location': 0, 'total_test_duration': None,
                 'total_location_duration': None,
                 'status_offline': False, 'fail_bin': FailureCodes.NONE.value, 'fail_bin_str': FailureCodes.NONE.name,
                 'external_id': 0, 'qr_validated': True,
                 'test_num': 0, 'trigger_time': None, 'number_of_responding_tags': 0}
    # update data files
    update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data)
    update_packet_data(packets_data_path=my_logger.packets_data_path, only_titles=True, test_data=test_data)
    all_tags = []
    ttfp_num = 0
    ttfp_sum = 0
    while cont_run:
        # init test data:
        loc_start_time = datetime.datetime.now()
        test_data['total_test_duration'] = None
        test_data['status_offline'] = False
        # check if tag exists at the test env
        if missing_label:
            # TODO add here the logic for missing label
            run_data['total_missing_labels'] = run_data['total_missing_labels'] + 1
            test_data['fail_bin'] = FailureCodes.MISSING_LABEL.value
            test_data['tag_run_location'] = test_data['tag_run_location'] + 1

            update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data)
            update_packet_data(packets_data_path=my_logger.packets_data_path, test_data=test_data)
            continue
        # ##################### test the tag ############################## #
        rsp = wiliot_tag_test.GwObj.write(cmd='!trigger_pl', with_ack=True)
        print(rsp)
        res = wiliot_tag_test.run(wait_for_gw_trigger=my_wait_for_gw_trigger)
        if res.is_results_empty():
            my_timer.cancel()
            raise Exception('Test was stopped before it started due to some reason')
        # ##################### test the tag ############################## #
        if res.is_all_tests_passed():
            print('********* PASS ************')
        # add ttfp avg:
        for r in res:
            if 'ttfp' in r.selected_tag_statistics:
                ttfp_sum = ttfp_sum + r.selected_tag_statistics['ttfp']
                ttfp_num = ttfp_num + 1

            # for p in r.all_packets:
            #     print('packet: {}, len:{}, status: {}'.format(p.packet_data['raw_packet'], len(p),
            #                                                   p.custom_data['packet_status']))
        if ttfp_num:
            run_data['ttfp_avg'] = ttfp_sum / ttfp_num

        # TODO move machine to the next tag
        total_loc_time = datetime.datetime.now() - loc_start_time
        test_data['total_location_duration'] = total_loc_time.total_seconds()
        # check duplication:
        selected_tag = res.check_and_get_selected_tag_id()
        if selected_tag != '':
            if selected_tag in all_tags:
                res.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
                res.set_total_test_status(status=False)
                wiliot_tag_test.add_to_blacklist(selected_tag)
                res.set_packet_status(adv_address=selected_tag, status='duplication')
            else:
                all_tags.append(selected_tag)
        run_data['total_run_responding_tags'] = len(all_tags)
        test_data['number_of_responding_tags'] = len(res.get_test_unique_adva())

        # add packets to packet_data.csv:
        update_packet_data(res=res, packets_data_path=my_logger.packets_data_path, test_data=test_data)
        # update run_data:
        update_run_data(run_data_path=my_logger.run_data_path, run_data=run_data, res=res)

        if my_stop_event.is_set():
            cont_run = False
            my_timer.cancel()

        # end of tag test actions
        test_data['tag_run_location'] = test_data['tag_run_location'] + 1
        if res.is_all_tests_passed():
            test_data['external_id'] = test_data['external_id'] + 1

        time.sleep(0)

    wiliot_tag_test.exit_tag_test()
    run_data['reel_run_end_time'] = datetime.datetime.now()
    run_data['upload_date'] = datetime.datetime.now()
    dict_to_csv(run_data, path=my_logger.run_data_path)
    # upload data to cloud
    # TODO add here function to upload data to database/cloud
    print('blacklist: {}'.format(wiliot_tag_test.black_list))
    print('done')
