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

import json
import os

from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui, popup_message
from wiliot_testers import ConversionTypes, SurfaceTypes


CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs', 'gui_input_do_not_delete.json')
MAND_FIELDS = ['wafer_lot', 'wafer_num', 'window_size', 'thermodes_col', 'lane_ids', 'assembled_reel',
               'q_size']  # mandatory fields in GUI before the run
DEFAULT_USER_INPUT = {
    'inlay_dict_inlay': '', 'number': '', 'received_channel': '',
    'energy_pattern_val': '', 'tester_station_name': '',
    'comments': '', 'operator': '', 'wafer_lot': '', 'wafer_num': '',
    'conversion_type': '', 'surface': '', 'matrix_tags': '',
    'thermodes_col': 1, 'gw_energy_pattern': '', 'gw_time_profile': '',
    'window_size': 1, 'assembled_reel': '', 'do_resolve': False, 'owner_id': '',
}

GUI_INPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs',
                              'gui_input_do_not_delete.json')


def setup_inlay_parameters(values_out, cols_or_rows, inlays):
    """
    Takes the values from the first window and saves it to code in order to use it in the application.
    @param values_out: Took from first window
    @return: Dictionary of constant values we need for run data csv file
    """
    selected = values_out.get('inlay_dict_inlay', '')
    selected_inlay = inlays.get(selected)
    if_rows = cols_or_rows == 'rows_num'
    first_gui_vals = {'owner_id': values_out['owner_id'], 'do_resolve': values_out['do_resolve'],
                      'thermodes_col': 1 if if_rows else values_out.get('thermodes_col', 1),
                      'rows_number': values_out.get('rows_num', 1) if if_rows else int(
                          selected_inlay['number_of_rows']),
                      'wafer_lot': values_out.get('wafer_lot', ''), 'lane_ids': values_out.get('lane_ids', ''),
                      'assembled_reel': values_out.get('assembled_reel', ''),
                      'wafer_number': values_out.get('wafer_num', ''),
                      'selected': selected,
                      'window_size': values_out.get('window_size', 1), 'comments': values_out['comments'],
                      'gw_energy_pattern': selected_inlay['energy_pattern_val'],
                      'gw_time_profile': selected_inlay['time_profile_val'],
                      'conversion_type': values_out.get('conversion_type','unknown'),
                      'surface': values_out['surface'], 'tester_station_name': values_out['tester_station_name'],
                      'operator': values_out['operator']}
    first_gui_vals['matrix_size'] = int(first_gui_vals['thermodes_col']) * int(first_gui_vals['rows_number'])
    if values_out.get('assembled_reel', '') != '':
        first_gui_vals['rows_number'] = values_out.get('rows_num', '')
        parts = []

        for i in range(1, int(int(first_gui_vals['rows_number'])) + 1):
            part_value = values_out[f'parts_row_part_{i}']
            if part_value:
                parts.append(part_value)
        lane_ids = ','.join(parts)
        first_gui_vals['lane_ids'] = lane_ids
    return first_gui_vals


def preparing_layout(inlays):
    if os.path.exists(GUI_INPUT_PATH):
        with open(GUI_INPUT_PATH, "r") as f:
            previous_input = json.load(f)
    else:
        previous_input = {}

    for k, v in DEFAULT_USER_INPUT.items():
        if k not in previous_input.keys():
            previous_input[k] = v

    selected = previous_input['inlay_dict_inlay']
    selected_inlay = inlays.get(selected, {})
    default_matrix_tags = int(previous_input.get('thermodes_col', 1))
    inlay_info_dict = {
        'inlay_info': ',   '.join(f"{key}: {value}" for key, value in selected_inlay.items() if key not in ['inlay', 'number', 'number_of_rows']),
        'default_matrix_tags': default_matrix_tags,
        'conv_opts': tuple([conv.value for conv in ConversionTypes]),
        'surfaces': tuple([surf.value for surf in SurfaceTypes])
    }

    if not selected:
        inlay_info_dict['inlay_info'] = ('received_channel: Invalid,   energy_pattern_val: Invalid,'
                                         '   time_profile_val: Invalid,   symbol_val: Invalid')
        inlay_info_dict['default_matrix_tags'] = 0

    return previous_input, inlay_info_dict


def on_inlay_change(gui_instance, inlays):
    """
    Updates the first GUI when the user changes the selected inlay
    @param gui_instance: First window we see
    @param inlays: Inlays' information from inlay_data file
    @return:
    """
    values = gui_instance.get_all_values()

    selected_inlay = inlays.get(values['inlay_dict_inlay'], {})
    if selected_inlay:
        info_string = ',   '.join(
            f"{key}: {value}" for key, value in selected_inlay.items() if
            key not in {'inlay', 'number', 'number_of_rows'}
        )
    else:
        info_string = 'Invalid Selection'
    gui_instance.update_widget('inlay_dict_inlay_info', info_string)

    if 'matrix_tags' in gui_instance.widgets:
        default_matrix_tags = int(values['thermodes_col']) * selected_inlay.get('number_of_rows', 1) if selected_inlay else 0
        gui_instance.update_widget('matrix_tags', f'Total Tags per Matrix: {str(default_matrix_tags)}')


def on_cols_change(gui_instance, inlays):
    """
    Updates the first GUI when the user changes the selected number of columns.
    @param gui_instance: First window we see
    @param inlays: Inlays' information from inlay_data file
    @return:
    """
    values = gui_instance.get_all_values()

    inlay = values['inlay_dict_inlay'] if values['inlay_dict_inlay'] in inlays else list(inlays.keys())[0]
    selected_inlay = inlays[inlay]
    rows_num = int(values.get('rows_num', selected_inlay.get('number_of_rows')))
    if 'matrix_tags' in gui_instance.widgets:
        cols_num = int(values.get('thermodes_col', 1))
        default_matrix_tags = cols_num * rows_num
        gui_instance.update_widget('matrix_tags', f'Total Tags per Matrix: {str(default_matrix_tags)}')
    if 'parts_row_part_1' in gui_instance.widgets:
        for i in range(1, 4):
            gui_instance.update_widget(f'parts_row_part_{i}', disabled=(i > rows_num))


def submit_open_session(open_session_gui):
    values = open_session_gui.get_all_values()

    missing_fields = []
    filling_missed_field = []
    for field in MAND_FIELDS:
        if open_session_gui.widgets.get(field) is not None:
            session_value = open_session_gui.widgets.get(field).get().strip()
            if not session_value:
                missing_fields.append(field)
                filling_missed_field.append(field)
    if missing_fields:
        error_msg = f"Please fill all the " \
                    f"mandatory fields {', '.join([f'[{field}]' for field in missing_fields])}"
        popup_message(msg=error_msg, tk_frame=open_session_gui.layout)
        return  # Skip the rest and prompt for missing fields again

    if values.get('wafer_num'):
        if not str(values['wafer_num']).isdigit() or len(str(values['wafer_num'])) > 2:
            popup_message(msg=f"Wafer Number must contains numbers Only, 2 digits max {values['wafer_num']}",
                          tk_frame=open_session_gui.layout)
            return

    if values.get('wafer_lot'):
        if len(values['wafer_lot']) > 10 or any([not s.isalnum() for s in values['wafer_lot']]):
            popup_message(msg=f"Wafer Lot must contains alphanumeric charachters Only, 10 charachters max\n{values['wafer_lot']}",
                          tk_frame=open_session_gui.layout)
            return
    
    columns = values.get('thermodes_col')
    if columns and int(columns) < 1:
        popup_message(msg='Number of columns should be positive', tk_frame=open_session_gui.layout)
        return
    
    open_session_gui.on_submit()


def open_session(open_session_layout=None, cols_or_rows='thermodes_col', inlays={}, gui_title='Yield Tester Run Settings'):
    open_session_gui = WiliotGui(params_dict=open_session_layout, do_button_config=False,
                                 title=gui_title)

    open_session_gui.button_configs(submit_command=lambda: submit_open_session(open_session_gui))
    open_session_gui.add_event(widget_key='inlay_dict_inlay',
                               command=lambda *args: on_inlay_change(open_session_gui, inlays),
                               event_type='<<ComboboxSelected>>')
    open_session_gui.add_event(widget_key=cols_or_rows,
                               command=lambda *args: on_cols_change(open_session_gui, inlays))
    on_cols_change(open_session_gui, inlays)
    values_out = open_session_gui.run(save_path=GUI_INPUT_PATH)

    if values_out:
        first_gui_vals = setup_inlay_parameters(values_out=values_out, cols_or_rows=cols_or_rows, inlays=inlays)
        return first_gui_vals
    raise Exception('open session gui was ended with outputs')
