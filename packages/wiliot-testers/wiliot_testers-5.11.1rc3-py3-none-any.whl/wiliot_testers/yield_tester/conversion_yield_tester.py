#  """
#    Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.
#
#    Redistribution and use of the Software in source and binary forms, with or without modification,
#     are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#       2. Redistributions in binary form, except as used in conjunction with
#       Wiliot's Pixel in a product or a Software update for such product, must reproduce
#       the above copyright notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution.
#
#       3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
#       may be used to endorse or promote products or services derived from this Software,
#       without specific prior written permission.
#
#       4. This Software, with or without modification, must only be used in conjunction
#       with Wiliot's Pixel or with Wiliot's cloud service.
#
#       5. If any Software is provided in binary form under this license, you must not
#       do any of the following:
#       (a) modify, adapt, translate, or create a derivative work of the Software; or
#       (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
#       discover the source code or non-literal aspects (such as the underlying structure,
#       sequence, organization, ideas, or algorithms) of the Software.
#
#       6. If you create a derivative work and/or improvement of any Software, you hereby
#       irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
#       royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
#       right and license to reproduce, use, make, have made, import, distribute, sell,
#       offer for sale, create derivative works of, modify, translate, publicly perform
#       and display, and otherwise commercially exploit such derivative works and improvements
#       (as applicable) in conjunction with Wiliot's products and services.
#
#       7. You represent and warrant that you are not a resident of (and will not use the
#       Software in) a country that the U.S. government has embargoed for use of the Software,
#       nor are you named on the U.S. Treasury Department’s list of Specially Designated
#       Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
#       You must not transfer, export, re-export, import, re-import or divert the Software
#       in violation of any export or re-export control laws and regulations (such as the
#       United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
#       and use restrictions, all as then in effect
#
#     THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
#     OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
#     WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
#     QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
#     IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
#     ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
#     OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
#     FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
#     (SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
#     (A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
#     CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
#     (B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
#     (C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
#  """

from assembly_yield_tester import MainWindow as BaseMainWindow
from assembly_yield_tester import *

INLAY_INFO_COLUMNSPAN = 200
CONV_SENSORS_TYPE = ['temperature', 'humidity']


class MainWindow(BaseMainWindow):

    def __init__(self, ):
        super().__init__(do_init_app_config=False)
        self.machine_type = 'conversion_yield_tester'
        self.tester_type = 'conversion_yield'

        self.init_app_configuration()
    
    def init_user_inputs(self, default_values=DEFAULT_USER_INPUTS):
        default_values['rssi_threshold'] = 50
        default_values['time_between_matrices_sec'] = 0
        user_inputs = super().init_user_inputs(default_values=default_values)
        return user_inputs

    def init_processes(self, sensors_type=CONV_SENSORS_TYPE):
        super().init_processes(sensors_type=sensors_type)

    def get_cmn(self, time_str):
        return '_'.join([self.first_gui_vals['assembled_reel'], time_str])

    def get_folder_name(self):
        return self.first_gui_vals['assembled_reel']

    def open_session_layout(self, previous_input, inlay_info):
        cols_or_rows = 'rows_num'
        open_session_layout = {
            'assembled_reel': {'text': 'Assembled Reel:', 'value': previous_input.get('assembled_reel', ''),
                               'widget_type': 'entry'},
            'rows_num': {'text': 'Number of lanes:', 'value': previous_input.get('rows_num', 1),
                         'widget_type': 'combobox', 'options': [1, 2, 3]},
            'parts_row': [
                {'part_1': {'text': 'PART 1', 'value': previous_input.get('parts_row_part_1', '')}},
                {'part_2': {'text': 'PART 2', 'value': previous_input.get('parts_row_part_2', '')}},
                {'part_3': {'text': 'PART 3', 'value': previous_input.get('parts_row_part_3', '')}},
            ],
            'inlay_dict': [
                {'inlay': {'text': 'Inlay:', 'value': previous_input.get('inlay_dict_inlay', ''),
                           'widget_type': 'combobox',
                           'options': list(self.inlays.keys())}},
                {'inlay_info': {'widget_type': 'label', 'value': inlay_info['inlay_info'],
                                'columnspan': INLAY_INFO_COLUMNSPAN}},
            ],
            'tester_station_name': {'text': 'Tester Station:', 'value': previous_input.get('tester_station_name', ''),
                                    'widget_type': 'entry'},
            'comments': {'text': 'Comments:', 'value': previous_input.get('comments', ''), 'widget_type': 'entry'},
            'operator': {'text': 'Operator:', 'value': previous_input.get('operator', ''), 'widget_type': 'entry'},
            'conversion_type': {'text': 'Conversion:', 'value': previous_input.get('conversion_type', ''),
                                'widget_type': 'combobox', 'options': inlay_info["conv_opts"]},
            'surface': {'text': 'Surface:', 'value': previous_input.get('surface', ''), 'widget_type': 'combobox',
                        'options': inlay_info["surfaces"]},
            'window_size': {'text': 'Window Size for Analysis:', 'value': previous_input['window_size'],
                            'widget_type': 'entry'},
            'do_resolve': {'text': 'Get External Id from Cloud', 'value': previous_input['do_resolve']},
            'owner_id': {'text': 'Owner Id for Cloud Connection', 'value': previous_input['owner_id']},

        }

        return open_session_layout, cols_or_rows


if __name__ == '__main__':
    m = MainWindow()
    m.run()
