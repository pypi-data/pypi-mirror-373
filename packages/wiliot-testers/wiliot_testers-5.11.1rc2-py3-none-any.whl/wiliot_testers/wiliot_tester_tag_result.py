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
import numpy as np
import pandas as pd
from enum import Enum

from wiliot_core import Packet, PacketList, TagCollection
try:
    from wiliot_core import DecryptedTagCollection, DecryptedPacketList, DecryptedPacket
    print('tag result: decryption mode is supported if needed')
except Exception as e:
    pass


class FailureCodes(Enum):
    NONE = 0
    PASS = 1  # Pass - default bin when no failure observed
    NO_RESPONSE = 2  # No response - no packets received at all in this location
    NO_PACKETS_UNDER_RSSI_THR = 3  # No packets under RSSI threshold
    MISSING_LABEL = 4  # Missing label - failure due to missing label
    FIRST_TAG_IN_RUN = 5  # First tag in run
    HIGH_TTFP = 6  # Quality Test Failure: High TTFP - time to first packet did not satisfy the configuration file
    NOT_ENOUGH_PACKETS = 7  # Quality Test Failure: Not enough packets - did not reach packet threshold as defined in configuration file
    TBP_AVG_OUT_OF_BOUNDS = 8  # Quality Test Failure: TBP Avg out of bounds - TBP Average value is out of bounds
    TBP_MIN_OUT_OF_BOUNDS = 9  # Quality Test Failure: TBP Min out of bounds - TBP Min value is out of bounds
    TBP_MAX_OUT_OF_BOUNDS = 10  # Quality Test Failure: TBP Max out of bounds - TBP Max value is out of bounds
    NO_TBP = 11  # Quality Test Failure: Could not calculate TBP - could not calculate TBP statistic at all
    NOT_ENOUGH_PACKETS_IN_SPRINKLER = 12  # Quality Test Failure: Not enough packets in sprinkler - received packet count in sprinkler is lower than specified in configuration file
    TIME_BTWN_CYCLES_OUT_OF_BOUNDS = 13  # Quality Test Failure: Time between cycles out of bounds
    DUPLICATION_OFFLINE = 14  # Duplicate offline - tag was found as duplicate during offline tester run (ADVA duplicate)
    DUPLICATION_POST_PROCESS = 15  # Duplicate post process - tag was found as duplicate in post process (UID duplicate)
    GW_ERROR = 16  # GW error
    STOP_BY_USER = 17  # test stopped by the user
    SEVERAL_TAGS_UNDER_TEST = 18  # Cannot decided which tag is under test
    FAILED_QUALITY_TEST = 19  # Failed Quality Test according to the specified statistics limits.
    NOT_PRINTED = 20  # tag was not printed due to printing offset
    CORRUPTED_PACKET_POST_PROCESS = 21  # post process - corrupted packet detection
    DIFF_TAG_ID_WITH_SAME_ADVA_POST_PROCESS = 22  # post process - same adva but different tag id
    ALTERING_ADVA_POST_PROCESS = 23  # post process - tag id with "good" packets sends diff adva
    BAD_PRINTING = 24  # as a result of printing validation, tag was decided to have a bad printing label
    INVALID_EXTERNAL_ID_POST_PROCESS = 25  # post process - specified if external id is empty or invalid
    WAFER_SORT_FAIL_POST_PROCESS = 26  # post process - tag id has failed in wafer sort
    END_OF_TEST = 27    # End of test for tags that was moved over the coupler for validating tested tags
    WRONG_POWER_MODE_POST_PROCESS = 28 # post process - tag has the wrong power mode based on the inlay expected power mode
    SHIPMENT_INTERNAL_ID_DUPLICATION = 90  # shipment API error - decided over the cloud
    SHIPMENT_EXTERNAL_ID_DUPLICATION = 91  # shipment API error - decided over the cloud
    SHIPMENT_TAG_NOT_EXIST = 92  # shipment API error - decided over the cloud
    SHIPMENT_OWNER_NOT_WILIOT_OPS = 93  # shipment API error - decided over the cloud
    SHIPMENT_SERIALIZATION_ISSUE = 94  # shipment API error - decided over the cloud
    SOFTWARE_GENERAL_ERROR = 999  # usage for debugging


class FailBinSample(Enum):
    TBP_EXISTS = 0
    NO_TBP = -1
    NO_TTFP = -2
    ADVA_DUPLICATION = -3
    NO_SERIALIZATION = -4
    UNDETERMINED_ERROR = -5


class ConversionTypes(Enum):
    NOT_CONVERTED = 'Unconverted'
    STANDARD = 'Regular Conversion'
    DURABLE = 'Durable Conversion'


class SurfaceTypes(Enum):
    AIR = 'air'
    CARDBOARD = 'cardboard'
    RPC = 'RPC'
    ER3 = 'Er3'
    ER3_5 = 'Er3.5'
    ER5 = 'Er5'
    ER7 = 'Er7'
    ER12 = 'Er12'


class WiliotTesterTagResultList(list):
    def __init__(self):
        self.tests = []
        self.trigger_time = None
        self.status = None
        self.test_info = {}
    
    def __len__(self):
        return len(self.tests)
    
    def __iter__(self):
        self.n = 0
        return iter(self.tests)
    
    def __next__(self):
        if self.n <= len(self):
            return self.tests[self.n]
        else:
            raise StopIteration
    
    def append(self, res) -> None:
        self.tests.append(res)
    
    def is_results_empty(self):
        """
        true if no test was done
        :return:
        :rtype:
        """
        return len(self.tests) == 0
    
    def is_all_tests_passed(self):
        """
        check if all sub test passed (i.e. the whole test passed)
        :return:
        :rtype:
        """
        if self.is_results_empty():
            return None
        return self.tests[-1].is_test_passed if self.status is None else self.status

    def get_total_test_duration(self):
        if self.is_results_empty():
            return None
        if self.tests[-1].test_end is None or self.trigger_time is None:
            return float('nan')
        return (self.tests[-1].test_end - self.trigger_time).total_seconds()
    
    def get_total_fail_bin(self, as_name=False):
        """
        return the test status according to the s option
        :param as_name: if true, the code is return b ts name and not its value
        :type as_name: bool
        :return: the test status code according to the FailureCodes
        :rtype: int or str
        """
        if self.is_results_empty():
            return None
        if as_name:
            return self.tests[-1].test_status.name
        else:
            return self.tests[-1].test_status.value
    
    def set_total_fail_bin(self, fail_code, overwrite=False):
        """
        set the test status to the specified fail_code
        :param fail_code: the status code
        :type fail_code: FailureCodes
        :param overwrite: if true fail bin will be overwrite according to the specified fail bin
        :type overwrite: bool
        """
        if overwrite and self.is_results_empty():
            self.append(WiliotTesterTagResult())
        if self.is_results_empty():
            return None
        if self.tests[-1].test_status == FailureCodes.NONE or self.tests[-1].test_status == FailureCodes.PASS or \
                overwrite:
            self.tests[-1].test_status = fail_code
            self.status = fail_code == FailureCodes.PASS
    
    def check_and_get_selected_tag_id(self):
        """
        check the for all sub test the same tag was selected and return the selected tag id
        :return: the selected tag id, empty string for unselected tag id
        :rtype: str
        """
        selected_tag = ''
        for r in self.tests:
            if r.selected_tag.size():
                cur_selected_tag = r.selected_tag[0].packet_data['adv_address']
                if selected_tag == '':
                    selected_tag = cur_selected_tag
                elif selected_tag != cur_selected_tag:
                    self.set_total_fail_bin(FailureCodes.SEVERAL_TAGS_UNDER_TEST)
                    self.status = False
        return selected_tag
    
    def set_trigger_time(self):
        self.trigger_time = datetime.datetime.now()
    
    def get_trigger_time(self):
        return self.trigger_time
    
    def set_total_test_status(self, status=False):
        """
        set the test pass/fail status
        :param status: if true the test was passed
        :type status: bool
        """
        self.status = status
    
    def get_total_test_status(self):
        """
        get the test pass/fail status
        :return: if true the test was passed
        :rtype: bool
        """
        if self.status is None:
            return self.is_all_tests_passed()
        else:
            return self.status
    
    def set_packet_status(self, adv_address='', status=''):
        """
        change the status per packets from outside function of the all_packets variable.
        the status can be change only if the previous status was 'good'
        :param adv_address: the packet advertising address
        :type adv_address: str
        :param status: the desired status to change
        :type status: str
        """
        for test in self.tests:
            for p in test.all_packets:
                if p.packet_data['adv_address'] == adv_address:
                    for i, s in enumerate(p.custom_data['packet_status']):
                        if s == 'good':
                            p.custom_data['packet_status'][i] = status

    def get_total_ttfp(self):
        if self.is_results_empty() or 'ttfp' not in self.tests[0].selected_tag_statistics.keys():
            return float('nan')
        return self.tests[0].selected_tag_statistics['ttfp']

    def get_test_unique_adva(self):
        all_adva = []
        for test in self.tests:
            all_adva += list(test.all_tags.tags.keys())
        return list(set(all_adva))

    def set_test_info(self, test_info):
        """
        add meta data to test
        @param test_info:
        @type test_info: dict
        @return:
        @rtype:
        """
        for k, v in test_info.items():
            self.test_info[k] = v

    def get_test_info(self):
        return self.test_info
    
    def get_payload(self):
        """get payload from one of the packets of the selected tag
        Returns:
            str: payload
        """
        for test in self.tests:
            for p in test.selected_tag:
                try:
                    payload = p.get_payload()
                    return payload
                except Exception as e:
                    print(f'could not get payloaf from packet, try again ){e}')
        raise Exception('could not extract payload from tag')


class WiliotTesterTagResult(object):
    def __init__(self, dev_mode=False):
        self.is_test_passed = False
        self.test_status = FailureCodes.NONE
        self.test_start = None
        self.test_end = None
        self.selected_tag_statistics = {}
        self.run_data = {}
        self.dev_mode = dev_mode
        if self.dev_mode:
            self.all_packets = DecryptedPacketList()
            self.selected_tag = DecryptedPacketList()
            self.all_tags = DecryptedTagCollection()
            self.filtered_tags = DecryptedTagCollection()
        else:
            self.all_packets = PacketList()
            self.selected_tag = PacketList()
            self.all_tags = TagCollection()
            self.filtered_tags = TagCollection()
    
    def add_run_data(self, test_param):
        """
        add the test data according to the test_param
        :param test_param: dictionary contains the main parameters for all test
        :type test_param: dict
        :return:
        :rtype:
        """
        self.run_data['rx_channel'] = int(test_param['rxChannel'])
        self.run_data['energizing_pattern'] = test_param['energizingPattern']
        self.run_data['time_profile'] = test_param['timeProfile']

    def add_packets_to_multi_tags(self, packets_in, multi_tag_out):
        """
        add packets_in to multi tag object
        :param packets_in: the packets needed to be append to the specified multi tag object
        :type packets_in: pd.DataFrame or PacketList or Packet or DecryptedPacket or DecryptedPacketList
        :param multi_tag_out:
        :type multi_tag_out:
        :return: the modified multi tag object
        :rtype: TagCollection
        """
        
        if isinstance(packets_in, pd.DataFrame):
            new_packet_list = PacketList() if not self.dev_mode else DecryptedPacketList
            packets_in = new_packet_list.import_packet_df(packet_df=packets_in)

        # it is by design not elif but if due to the first cond.
        if isinstance(packets_in, PacketList) or isinstance(packets_in, DecryptedPacketList):
            for packet in packets_in:
                multi_tag_out.append(packet.copy())
        
        elif isinstance(packets_in, Packet) or isinstance(packets_in, DecryptedPacket):
            multi_tag_out.append(packets_in)
        
        else:  # TODO add more options
            raise Exception('WiliotTesterTagResult: add_packets does not support the type of the specified packets_in')
        
        return multi_tag_out
    
    def add_selected_tag_statistics(self, custom_data=None):
        """
        add the statistics of the selected tag for the test
        :param custom_data: if specified the custom data is added to the packets of the selected tag
        :type custom_data: dict
        """
        if custom_data is not None:
            for packet in self.selected_tag:
                packet.add_custom_data(custom_data=custom_data)
        
        self.selected_tag_statistics = self.selected_tag.get_statistics()
    
    def set_quality_test_failure(self, statistics_limits, targets_status):
        """
        if test was failed, the correct failure code is set according to the statistics_limits, targets_status
        :param statistics_limits: the valid range of the quality parameter
        :type statistics_limits: dict
        :param targets_status: list of boolean, true if passed the quality test
        :type targets_status: list
        """
        for t, k in zip(targets_status, statistics_limits.keys()):
            if not t:  # failed the test
                if k == 'ttfp':
                    self.test_status = FailureCodes.HIGH_TTFP
                elif 'tbp' in k and self.selected_tag_statistics[k] == -1:
                    self.test_status = FailureCodes.NO_TBP
                elif k == 'tbp_mean':
                    self.test_status = FailureCodes.TBP_AVG_OUT_OF_BOUNDS
                elif k == 'tbp_min':
                    self.test_status = FailureCodes.TBP_MIN_OUT_OF_BOUNDS
                elif k == 'tbp_max':
                    self.test_status = FailureCodes.TBP_MAX_OUT_OF_BOUNDS
                elif k == 'sprinkler_counter_max':
                    self.test_status = FailureCodes.NOT_ENOUGH_PACKETS_IN_SPRINKLER
                elif k == 'time_btw_cycle':
                    self.test_status = FailureCodes.TIME_BTWN_CYCLES_OUT_OF_BOUNDS
                else:
                    self.test_status = FailureCodes.FAILED_QUALITY_TEST
                break  # return after the first failure
    
    def get_summary(self):
        """
        get a dictionary of the test summary including the tag statistics and test parameters
        :return: test summary
        :rtype: dict
        """
        if self.selected_tag.size():
            selected_tag = self.selected_tag[0].packet_data['adv_address']
        else:
            selected_tag = ''
        summary = {'is_test_pass': self.is_test_passed, 'selected_tag': selected_tag,
                   'test_start_time': self.test_start, 'test_end_time': self.test_end,
                   'test_status': self.test_status.value}
        
        run_summary = self.run_data.copy()
        run_summary['time_profile'] = str(self.run_data.get('time_profile', ''))
        
        tag_stat = {'num_packets': 0, 'num_cycles': 0, 'sprinkler_counter_mean': None,
                    'sprinkler_counter_std': None, 'sprinkler_counter_min': None, 'sprinkler_counter_max': None,
                    'tbp_mean': None, 'tbp_std': None, 'tbp_min': None, 'tbp_max': None, 'tbp_num_vals': None,
                    'per_mean': None, 'per_std': None, 'rssi_mean': None, 'rssi_std': None, 'rssi_min': None,
                    'rssi_max': None, 'ttfp': None, 'rx_rate_normalized': None, 'rx_rate': None}
        for k in tag_stat.keys():
            if k in self.selected_tag_statistics.keys():
                tag_stat[k] = self.selected_tag_statistics[k]
        
        return {**summary, **run_summary, **tag_stat}
    
    def get_sensor_statistics(self, data_type: str='filtered') -> pd.DataFrame:
        """
        get the sensor statistics according to the data type: 'filtered' or 'all'"""
        if data_type == 'filtered':
            tag_list = self.filtered_tags
        elif data_type == 'all':
            tag_list = self.all_tags
        elif data_type == 'selected_tag':
            tag_list = {self.selected_tag[0].get_adva(): self.selected_tag}
        
        statistics_dict = {'adv_address': [], 'external_sensor_mean': [], 'external_sensor_n_samples': []}
        for tag_id, packet_list  in tag_list.items():
            val_list = []
            for packet in packet_list:
                if 'rc_sensor_freq_khz' in packet.decoded_data:
                    sensor_type = packet.decoded_data.get('rc_sensor_ext_or_int_cap_str', '') + packet.decoded_data.get('rc_sensor_cap_or_res_str', '')
                    if sensor_type == 'ExtCap' or sensor_type == '':
                        val_list.append(packet.decoded_data['rc_sensor_freq_khz'])
            if val_list:
                val_mean = np.nanmean(val_list)
                val_count = len(val_list)
            else:
                val_mean = float('nan')
                val_count = 0
            statistics_dict['adv_address'].append(tag_id)
            statistics_dict['external_sensor_mean'].append(val_mean)
            statistics_dict['external_sensor_n_samples'].append(val_count)

        return pd.DataFrame(statistics_dict)
 
