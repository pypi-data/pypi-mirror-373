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
import os
from wiliot_core import InlayTypes
from wiliot_tools.utils.wiliot_gui.wiliot_gui import popup_message, WiliotGui
from wiliot_testers.wiliot_tester_tag_test import load_test_suite_file
from wiliot_testers.wiliot_tester_tag_result import FailureCodes
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_testers.offline.offline_main import MainDefaults, upload_conclusion


class ConvertLogToTesters(object):
    def __init__(self, path, tester_station_name, inlay, owner_id):
        df = pd.read_csv(path)
        test_suite = load_test_suite_file(tester_name='offline')
        test_suite_name, test_suite_dict = '', ''
        for k, v in test_suite.items():
            test_suite_name = k
            test_suite_dict = v
            break

        # create run data file
        common_run_name = os.path.basename(path).replace('.csv', '')
        self.common_run_name = common_run_name
        print(f'common_run_name: {common_run_name}')
        self.owner_id = owner_id
        n_tags = df['adv_address'].nunique()
        run_data = {
            'common_run_name': [common_run_name],
            'tester_station_name': [tester_station_name],
            'tester_type': ['offline'],
            'total_run_tested': [n_tags],
            'inlay': [inlay],
            'test_suite': [test_suite_name],
            'test_suite_dict': [test_suite_dict],
            'to_print': ['No'],
            'owner_id': [owner_id],
        }
        run_data_df = pd.DataFrame(run_data)
        self.run_data_path = os.path.join(os.path.dirname(path), f'{common_run_name}@run_data.csv')
        run_data_df.to_csv(self.run_data_path, index=False)

        # create packet data file
        location_map = {adv: i for i, adv in enumerate(df['adv_address'].unique())}
        df = df[['raw_packet', 'gw_packet', 'time_from_start', 'adv_address']]
        df.insert(loc=0, column='common_run_name', value=common_run_name)
        df.insert(loc=0, column='test_num', value=0)
        df.insert(loc=0, column='packet_status', value='good')
        df.insert(loc=0, column='selected_tag', value=df['adv_address'])
        df.insert(loc=0, column='is_test_pass', value=1)
        df.insert(loc=0, column='status_offline', value=1)
        df.insert(loc=0, column='fail_bin', value=FailureCodes.PASS.value)
        df.insert(loc=0, column='fail_bin_str', value=FailureCodes.PASS.name)

        df.insert(loc=0, column='tag_run_location', value=df['adv_address'].map(location_map))
        if 'external_id' not in df.keys():
            df.insert(loc=0, column='external_id', value='')

        self.packets_data_path = os.path.join(os.path.dirname(path), f'{common_run_name}@packets_data.csv')
        df.to_csv(self.packets_data_path, index=False)

    def upload_to_cloud(self, env):
        file_size = os.stat(self.packets_data_path).st_size
        if file_size < MainDefaults.MAX_FILE_SIZE:
            try:
                res = upload_to_cloud_api(batch_name=self.common_run_name,
                                          tester_type='offline-test',
                                          run_data_csv_name=self.run_data_path,
                                          packets_data_csv_name=self.packets_data_path,
                                          env=env,
                                          owner_id=self.owner_id,
                                          is_path=True)
            except Exception as e:
                print(f'WARNING: upload_to_cloud: {e}')
                res = False

            upload_conclusion(succeeded_csv_uploads=res)
        else:
            e_msg = 'Test files are too large, please upload using manual upload app'
            popup_message(msg=e_msg, bg='red')
            print(f'WARNING: upload_to_cloud: {e_msg}')


if __name__ == '__main__':
    params_dict = {
        'path': {'text': 'Please select the csv file to convert (_plot.csv)', 'value': '', 'widget_type': 'file_input'},
        'tester_station_name': {'value': ''},
        'owner_id': {'value': ''},
        'environment': {'value': ['prod', 'test']},
    }
    wg = WiliotGui(params_dict=params_dict, title='Convert LOG to offline')
    values = wg.run()
    ct = ConvertLogToTesters(path=values['path'],
                             tester_station_name=values['tester_station_name'],
                             inlay=InlayTypes.TIKI_169,
                             owner_id=values['owner_id'],
                             )
    ct.upload_to_cloud(env=values['environment'])
    print('done')
