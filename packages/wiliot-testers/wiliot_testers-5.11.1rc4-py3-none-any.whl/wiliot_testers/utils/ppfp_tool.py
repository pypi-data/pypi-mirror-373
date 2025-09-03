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
from wiliot_core import GetApiKey
from wiliot_api import ManufacturingClient
from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui, popup_message


class DataPullGUI:
    """
    To create .exe file for this script use the next line:
    pywiliot-testers> pyinstaller --onefile --windowed --add-data "./wiliot_testers/docs/wiliot_logo.png;./docs" ./wiliot_testers/utils/ppfp_tool.py
    """

    def __init__(self, owner_id='', single_crn='', output_dir=None):
        current_script = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_script)
        os.chdir(current_dir)

        self.params_dict = {
            # Owner ID Section
            'owner_id': {
                'text': 'Owner ID',
                'value': owner_id,  # Assuming owner_id is predefined
                'widget_type': 'entry',
            },

            # Environment Section
            'env': {
                'text': 'Environment',
                'value': 'Production',
                'options': ['Production', 'Test'],
                'widget_type': 'combobox',
            },

            # Tester Type Section
            'tester_type': {
                'text': 'Tester Type',
                'value': 'Offline',
                'options': ['Offline', 'Sample'],
                'widget_type': 'combobox',
            },

            # Common Run Name Insert Mode Section
            'select_mode': {
                'text': 'Select mode for Common Run Name Insert',
                'value': '',
                'widget_type': 'label',
            },
            'crn_mode': {
                'text': 'Select mode for Common Run Name Insert',
                'value': 'Single CRN',
                'widget_type': 'combobox',
                'options': ['Single CRN', 'CRN List (CSV)'],
            },

            # CRN and CSV File Section
            'crn_col': {
                'text': 'CRN',
                'value': single_crn,
                'widget_type': 'entry',
            },
            'csv_file_col': {
                'text': 'CSV File',
                'value': '',
                'widget_type': 'file_input',
            },

            # Target Directory Section
            'target_dir': {
                'text': 'select_target_directory',
                'value': output_dir if output_dir is not None else '',
                'widget_type': 'file_input',
                'options': 'folder',
            },
        }

    def run(self):

        def on_combobox_change(*args):
            selected_value = ppfp_gui.widgets_vals['crn_mode'].get()
            if selected_value == 'Single CRN':
                ppfp_gui.update_widget('crn_col', disabled=False)
                ppfp_gui.update_widget('csv_file_col', disabled=True)
            elif selected_value == 'CRN List (CSV)':
                ppfp_gui.update_widget('crn_col', disabled=True)
                ppfp_gui.update_widget('csv_file_col', disabled=False)

        ppfp_gui = WiliotGui(params_dict=self.params_dict)
        ppfp_gui.add_event(widget_key='crn_mode', command=on_combobox_change)
        on_combobox_change()
        values = ppfp_gui.run()

        try:
            tester_type = 'offline-test' if values['tester_type'] == 'Offline' else 'sample-test'
            g = GetApiKey(gui_type='ttk', env=values['env'][0:4].lower(), owner_id=values['owner_id'])
            api_key = g.get_api_key()
            if not api_key:
                raise Exception('User configuration check failed')
            client = ManufacturingClient(api_key=api_key, env=values['env'][0:4].lower())
            rsp = None

            if values['crn_mode'] == 'Single CRN':
                common_run_name_list = [values['crn_col'].strip()]
            else:
                common_run_name_list = []
                with open(values['csv_file_col'], 'r') as f:
                    for line in f:
                        common_run_name_list.append(line.strip())
            try:
                for common_run_name in common_run_name_list:
                    out_file_path = os.path.join(values['target_dir'], f'{common_run_name}.zip')
                    with open(out_file_path, 'wb') as out_file:
                        rsp = client.get_file_for_ppfp(common_run_name, tester_type, out_file)
            except Exception as e:
                print(f'problem get file from cloud due to {e}')
                popup_message(f'An error occurred while loading CSV file - please check it')

            if rsp:
                print('Job Success')
                done_layout = {
                    'done': {
                        'text': '',
                        'value': 'Job Succeeded',
                        'widget_type': 'label'
                    }
                }
                popup_message(f'Job Succeeded!\nzip file is saved under {values["target_dir"]}', title='Success')

            else:
                popup_message(f'An error occurred while getting data from cloud')

        except Exception as e:
            print(e)
            popup_message(f'An error occurred: {e}')


if __name__ == '__main__':
    gui = DataPullGUI()
    gui.run()
