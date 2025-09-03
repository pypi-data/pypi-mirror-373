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
import pandas as pd
import logging

from wiliot_testers.wiliot_tester_tag_test import WiliotTesterTagTest, TesterName, FailureCodes, LoggerName, \
    valid_output_power_vals


class TagStatus:
    INSIDE_TEST = 'inside_test'
    OUT_VALID = 'outside_test_valid'
    OUT_INVALID = 'outside_test_invalid'
    NO_RESPONSE = 'no_response'


class WiliotSampleTagTest(WiliotTesterTagTest):
    def __init__(self,
                 tags_in_test,
                 selected_test,
                 test_suite=None,
                 gw_obj=None,
                 stop_event_trig=None,
                 tester_name=TesterName.SAMPLE,
                 logger_name=None, logger_result_name=None, logger_gw_name=None,
                 inlay=None,
                 resolve_q=None,
                 hw_functions=None):
        self.hw_functions = hw_functions
        super().__init__(selected_test=selected_test,
                         test_suite=test_suite,
                         stop_event_trig=stop_event_trig, gw_obj=gw_obj, tester_name=tester_name,
                         logger_name=logger_name, logger_result_name=logger_result_name, logger_gw_name=logger_gw_name,
                         inlay=inlay)
        self.tags_status_df = pd.DataFrame({'adv_address': [], 'resolve_status': []})
        self.received_tags = []
        self.passed_tags = []
        self.tags_in_test = tags_in_test
        self.n_tags = len(tags_in_test)
        self.resolve_q = resolve_q
        

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
        # upload test suite:
        if test_suite is None:
            self._printing_func('Test Suite input is wrong', log_level=logging.WARNING)
            raise Exception('Test Suite MUST be specified')

        if selected_test not in test_suite['test']:
            msg = 'the selected test: {} was not found in the tests suite'.format(selected_test)
            self._printing_func(msg, log_level=logging.WARNING)
            raise Exception(msg)

        if test_suite['test'][selected_test].get('isTestSuite', False):
            super().set_test_suite(selected_test=selected_test, test_suite=test_suite['test'], inlay=inlay)
            for sub_test in self.selected_test['tests']:
                if 'HwUpdate' in sub_test.keys() and isinstance(sub_test['HwUpdate']['function'], str):
                    sub_test['HwUpdate']['function'] = self.hw_functions[sub_test['HwUpdate']['function']]
        else:
            self.selected_test = {
                'inlay': inlay,
                "plDelay": 0,
                "rssiThresholdHW": int(test_suite['run'].get('rssiThresholdHW', 0)),
                "rssiThresholdSW": int(test_suite['run'].get('rssiThresholdSW', 9999)),
                'ignore_test_mode': False,
                "tests": [{
                    "name": 'sample_test',
                    "rxChannel": test_suite['test'][selected_test].get('channel', 37),
                    "symbol": test_suite['test'][selected_test].get('symbol', '1Mhz'),
                    "energizingPattern": test_suite['test'][selected_test].get('pattern', 18),
                    "timeProfile": [int(test_suite['test'][selected_test].get('tOn', 5)),
                                    int(test_suite['test'][selected_test].get('tTotal', 15))],
                    "absGwTxPowerIndex": -1,
                    'gw_power_dict': valid_output_power_vals[-1],
                    'sub1g_power': 29,
                    "maxTime": test_suite['test'][selected_test].get('testTime', 60),
                    "delayBeforeNextTest": int(test_suite['test'][selected_test].get('sleep', 0)),
                    "stop_criteria": {'tbp_mean': [0, 9999],
                                    'tbp_num_vals': [int(test_suite['test'][selected_test].get('nTbpSamples', 1)), 9999],
                                    'num_packets': [int(test_suite['test'][selected_test].get('nMinPackets', 1)), 9999],
                                    'num_cycles': [int(test_suite['test'][selected_test].get('nMinUniquePackets', 1)),
                                                    9999],
                                    },
                    "quality_param": {},
                    "gw_commands": [f"!set_sub_1_ghz_energizing_frequency "
                                    f"{test_suite['test'][selected_test].get('EmulateSurfaceValue', 915000)}"]
                }]
            }

    def init_test(self, sub_test, is_start_gw_app=True, test_num=0):
        super().init_test(sub_test=sub_test, is_start_gw_app=is_start_gw_app, test_num=test_num)
        update_hw_dict = self.selected_test['tests'][test_num].get('HwUpdate')
        if update_hw_dict is not None:
            update_hw_dict['function'](**update_hw_dict['function_inputs'])
        self.passed_tags = []

    def resolve_new_tag(self, tag):
        if self.resolve_q is not None:  # online mode
            if self.resolve_q.full():
                self.logger.warning(f'resolve queue is full dropping tag: {tag}')
            else:
                self.resolve_q.put({'tag': tag,
                                    'payload': self.tag_results.filtered_tags.tags[tag][0].get_payload()},
                                   block=False)
        else:  # offline mode
            self.offline_resolve(tag=tag)

    def is_stop_criteria_reached(self, tags_reached_criteria):
        # resolve new tags:
        for tag in self.tag_results.filtered_tags.tags.keys():
            if tag not in self.received_tags:
                self.resolve_new_tag(tag=tag)
                self.received_tags.append(tag)

        # check stop criteria
        for tag in tags_reached_criteria:
            if tag not in self.passed_tags:
                self.passed_tags.append(tag)

        is_passed = False
        if len(self.passed_tags):
            n_passed_tags = sum([tag in self.passed_tags for tag in self.tags_status_df['adv_address'].loc[
                self.tags_status_df['resolve_status'] == TagStatus.INSIDE_TEST]])
            is_passed = n_passed_tags >= self.n_tags
        adva_status = {adv: status for adv, status in zip(self.tags_status_df["adv_address"],
                                                          self.tags_status_df["resolve_status"])}
        self._printing_func(f'is_stop_criteria_reached: is passed: {is_passed}, passed_tags: {self.passed_tags}, '
                            f'tag status df: {adva_status}')

        return is_passed

    def analyze_end_of_test(self, sub_test, tags_reached_criteria, all_selected_tags, test_num, num_of_tests):
        # not supporting run_all option
        self.tag_results.is_test_passed = True
        self.tag_results.test_status = FailureCodes.PASS
        self._printing_func('Stage {} out of {} Passed'.format(test_num + 1, num_of_tests),
                            logger_name=LoggerName.RESULTS)

    def set_tags_status(self, new_tags_status):
        new_tags_status_df = pd.DataFrame(new_tags_status)
        self.tags_status_df = pd.concat([self.tags_status_df, new_tags_status_df], axis=0)

    def offline_resolve(self, tag):
        n_received = len(self.received_tags)
        if n_received < self.n_tags:
            estimated_external_id = self.tags_in_test[n_received]
            status = TagStatus.INSIDE_TEST
        else:
            estimated_external_id = 'unknown'
            status = TagStatus.OUT_INVALID
        new_tag = {'adv_address': [tag],
                   'resolve_status': [status],
                   'external_id': [estimated_external_id]}
        self.set_tags_status(new_tags_status=new_tag)

    def is_all_resolve(self):
        return self.n_tags == sum(self.tags_status_df['resolve_status'] == TagStatus.INSIDE_TEST)
