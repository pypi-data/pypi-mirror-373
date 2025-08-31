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

from queue import Queue
import threading
import pandas as pd

from wiliot_testers.sample.modules.wiliot_sample_tag_test import WiliotSampleTagTest, TesterName, TagStatus
from wiliot_tools.resolver_tool.resolve_packets import ResolvePackets


class SampleRun(object):
    def __init__(self, tags_in_test, selected_test, all_configs, cloud_config,
                 gw_obj=None, stop_event=None, inlay=None, logger_name=None, hw_functions=None):
        resolve_q = Queue(maxsize=100) if cloud_config['is_online'] else None
        self.stop_event = stop_event if stop_event is not None else threading.Event()
        self.stop_event.clear()
        self.results_df = None

        self.sample_tester = WiliotSampleTagTest(tags_in_test=tags_in_test,
                                                 selected_test=selected_test,
                                                 test_suite=all_configs,
                                                 gw_obj=gw_obj,
                                                 stop_event_trig=self.stop_event,
                                                 tester_name=TesterName.SAMPLE,
                                                 logger_name=logger_name,
                                                 inlay=inlay,
                                                 resolve_q=resolve_q,
                                                 hw_functions=hw_functions
                                                 )
        self.logger = self.sample_tester.logger
        self.resolver = ResolvePackets(tags_in_test=tags_in_test,
                                       owner_id=cloud_config['owner_id'],
                                       env=cloud_config['env'],
                                       resolve_q=resolve_q,
                                       set_tags_status_df=self.sample_tester.set_tags_status,
                                       stop_event_trig=self.stop_event,
                                       logger_name=self.logger.name,
                                       gui_type='ttk',
                                       tag_status=TagStatus
                                       ) if cloud_config['is_online'] else None

    def run(self):
        self.logger.info('start running sample test thread')
        sample_tester_handler = threading.Thread(target=self.sample_tester.run, args=())
        sample_tester_handler.start()
        if self.resolver is not None:
            self.logger.info('start running resolver thread')
            resolver_handler = threading.Thread(target=self.resolver.run, args=())
            resolver_handler.start()
        else:
            resolver_handler = None

        sample_tester_handler.join()
        self.logger.info('running sample test thread was done')
        if resolver_handler is not None:
            self.stop_event.set()
            resolver_handler.join(10)
            if resolver_handler.is_alive():
                raise Exception('could not stop the resolve thread, please re-run app')
            self.logger.info('running resolver thread was done')

        self.logger.info('end of run')

    def get_test_results(self, only_inside_test=False):
        if self.results_df is not None:
            return self.results_df
        test_results = self.sample_tester.test_results
        df = test_results.tests[-1].filtered_tags.get_df(add_sprinkler_info=True)
        if df.empty:
            self.results_df = df
            return df
        stat = test_results.tests[-1].filtered_tags.get_statistics()
        df_res = pd.merge(df, self.sample_tester.tags_status_df, how='outer', on='adv_address')
        df_res = pd.merge(df_res, stat, how='outer', on='adv_address')
        if only_inside_test or self.sample_tester.is_all_resolve():
            df_res = df_res[df_res['resolve_status'] == TagStatus.INSIDE_TEST]
        df_res.reset_index(inplace=True)
        self.results_df = df_res
        return df_res


if __name__ == '__main__':
    import os
    import json

    test_tags_in_test = ['(01)00850027865010(21)01t6T0080', '(01)00850027865010(21)01jvT5192']
    test_selected_test = 'TIKI_BLE'
    test_configs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs', '.default_test_configs.json')
    with open(test_configs_path, 'r') as f:
        test_configs = json.load(f)
    test_all_configs = {'run': {'rssiThresholdHW': 0,
                                'rssiThresholdSW': 100,
                                },
                        'test': test_configs
                        }
    test_cloud_config = {'is_online': True, 'owner_id': 'wiliot-ops', 'env': 'prod'}

    s_r = SampleRun(tags_in_test=test_tags_in_test,
                    selected_test=test_selected_test,
                    all_configs=test_all_configs,
                    cloud_config=test_cloud_config,
                    gw_obj=None,
                    stop_event=None,
                    inlay=None,
                    logger_name=None)
    s_r.run()
    res = s_r.get_test_results()
    print(res)
    print('done')
