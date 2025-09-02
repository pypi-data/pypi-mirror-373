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
import threading
import time
import os

from wiliot_testers.wiliot_tester_tag_test import WiliotTesterTagTest
from wiliot_testers.wiliot_tester_log import WiliotTesterLog
from wiliot_testers.wiliot_tester_tag_result import FailureCodes


if __name__ == '__main__':
    def stop_run():
        my_stop_event.set()


    # for simulation stop the run after 20 seconds
    my_timer = threading.Timer(20, stop_run)
    my_stop_event = threading.Event()

    # init the class
    black_list = ['A', 'B']
    test_suite = {"Dual Band": {
        "plDelay": 100,
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
            "quality_param":
                {
                    "ttfp": [0, 5]
                }
            },
            {"name": "sub1G_band",
            "rxChannel": 37,
            "energizingPattern": 52,
            "timeProfile": [5, 10],
            "absGwTxPowerIndex": -1,
            "sub1gGwTxPower": 9,
            "maxTime": 5,
            "stop_criteria": {"num_packets": [2, 99]},
            "quality_param":
                {
                }
            }
        ]
    }}
    wiliot_tag_test = WiliotTesterTagTest(selected_test='Dual Band', test_suite=test_suite,
                                          stop_event_trig=my_stop_event,
                                          black_list=black_list)
    # simulate infinite loop of testing
    all_tags = []
    my_timer.start()
    cont_run = True
    while cont_run:
        # ##################### test the tag ############################## #
        res = wiliot_tag_test.run(wait_for_gw_trigger=None)
        # ##################### test the tag ############################## #
        if res.is_results_empty():
            my_timer.cancel()
            raise Exception('no trigger was detected or test was stopped by the user')
        if res.is_all_tests_passed():
            print('********* PASS ************')
        else:
            failure_reason = res.get_total_fail_bin(as_name=True)
            print(' --- tag failed due to {} ---'.format(failure_reason))
        
        # check duplication:
        selected_tag = res.check_and_get_selected_tag_id()
        if selected_tag != '':
            if selected_tag in all_tags:
                print('Found Tag Duplication for {}'.format(selected_tag))
                res.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
                res.set_total_test_status(status=False)
                wiliot_tag_test.add_to_blacklist(selected_tag)
                res.set_packet_status(adv_address=selected_tag, status='duplication')
            else:
                all_tags.append(selected_tag)
        
        if my_stop_event.is_set():
            cont_run = False
            my_timer.cancel()
        
        time.sleep(0)

    wiliot_tag_test.exit_tag_test()

    print('blacklist: {}'.format(wiliot_tag_test.black_list))
    print('done')
