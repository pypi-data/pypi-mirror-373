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

from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui, popup_message
from wiliot_testers.utils.ppfp_tool import DataPullGUI
from wiliot_testers.partners.simple_test.simple_test import SimpleTest

OWNER_ID = ''


def run_simple_test(owner_id, test_name, output_path, window, test_time, shared_status):
    try:
        test = SimpleTest(owner_id=owner_id,
                          test_name=test_name,
                          output_path=output_path,
                          test_time=test_time,
                          tester_type='offline',
                          test_env='prod')
    except Exception:
        popup_message(msg='Problem initializing the test', tk_frame=window)
        return
    shared_status['test'] = test
    shared_status['test_complete'] = True


def upload_to_cloud(shared_status):
    if shared_status.get('test'):
        shared_status['test'].cloud_upload()
        shared_status['upload_complete'] = True


def create_gui():
    params_dict = {
        'test_name': {'text': 'Test Name', 'value': 'SimpleTest', 'group': 'Test Run'},
        'test_time': {'text': 'Time to Test', 'value': '10', 'group': 'Test Run'},
        'target_dir': {'text': 'Output', 'value': '', 'group': 'Test Run', 'widget_type': 'file_input', 'options': 'folder'},
        'start_test_btn': {'value': 'Start Test', 'group': 'Test Run', 'widget_type': 'button'},
        'upload_btn': {'value': 'Upload data to cloud', 'group': 'Upload to Cloud', 'widget_type': 'button'},
        'cloud_test_name': {'text': 'Test Name', 'value': '', 'group': 'Extract Data from Cloud'},
        'cloud_output_dir': {'text': 'Output Directory', 'value': '', 'group': 'Extract Data from Cloud'},
        'get_results_btn': {'value': 'Get Results', 'group': 'Extract Data from Cloud', 'widget_type': 'button'},
    }
    shared_status = {'test_complete': False, 'test': None, 'upload_complete': False}

    def on_start_test():
        values = wg.get_all_values()
        run_simple_test(OWNER_ID, values['test_name'], values['target_dir'], wg.layout, values['test_time'], shared_status)

    def on_get_results():
        values = wg.get_all_values()
        DataPullGUI(owner_id=OWNER_ID, single_crn=values['cloud_test_name'], output_dir=values['cloud_output_dir'])

    wg = WiliotGui(params_dict=params_dict, title='Simple Test GUI')
    wg.add_event(widget_key='start_test_btn', command=lambda: on_start_test())
    wg.add_event(widget_key='upload_btn', command=lambda: upload_to_cloud(shared_status))
    wg.add_event(widget_key='get_results_btn', command=lambda: on_get_results(wg.layout, shared_status))

    wg.run()


if __name__ == '__main__':
    create_gui()
