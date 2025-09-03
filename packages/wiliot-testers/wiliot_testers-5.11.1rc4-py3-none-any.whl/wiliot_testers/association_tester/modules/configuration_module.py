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
import json

from wiliot_core import GetApiKey
from wiliot_tools.utils.wiliot_gui.wiliot_gui import *
from wiliot_testers.association_tester.hw_components.scanner_component import Scanner
from wiliot_testers.association_tester.hw_components.r2r_component import R2R

GUI_USER_INPUT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_NAME = 'association_and_verification_gui_user_inputs.json'
GUI_FILE = os.path.abspath(os.path.join(GUI_USER_INPUT_PATH, 'configs', FILE_NAME))
RUN_PARAMS_FILE = os.path.abspath(os.path.join(GUI_USER_INPUT_PATH, 'configs', 'last_run_params.json'))
DEFAULT_VALUES = {
    'min_test_time': '1.5',
    'max_test_time': '5',
    'time_to_move': '0.5',
    'do_association': 'no',
    'is_step_machine': 'yes',
    'r2r_type': 'arduino',
    'asset_location': 'none',
    'wiliot_num_codes': 1,
    'asset_num_codes': 1,
    'owner_id': 'wiliot-ops',
    'category_id': '86fd9f07-38b0-466f-b717-2e285b803f5c',
    'energy_pattern': '51',
    'time_profile': '5,15',
    'ble_power': '22', 'sub1g_power': '29', 'sub1g_freq': '925000',
    'scan_ch': '37',
    'is_listen_bridge': 'yes',
    'env': 'prod',
    'scanner_type': 'Cognex',
    'sc_min_location': '30',
    'sc_association': '90',
    'sc_scanning': '90',
    'sc_responding': '90',
    'sc_n_no_scan': '2',
    'run_name': 'test',
    'do_verification': True,
    'do_printing': False,
    'do_scan_verification': False,
    'scan_verification_offset': 1,
}

DEFAULT_RUN_PARAM = {"last_run_name": "test", "last_location": 0, "last_asset_id": "", "last_asset_location": 0}


def get_params(file_path, default_values):
    if os.path.isfile(file_path):
        out = json.load(open(file_path, "rb"))
        for k in default_values.keys():
            if k not in out.keys():
                out[k] = default_values[k]
    else:
        out = default_values
    return out


def get_user_inputs():
    """
    opens GUI for selecting a file and returns it
    """
    # upload config
    global is_valid_setup_out
    default_values = get_params(GUI_FILE, DEFAULT_VALUES)
    run_params = get_params(RUN_PARAMS_FILE, DEFAULT_RUN_PARAM)
    params_dict = {}
    params_dict['main'] = {

        # Setup Button
        'check_setup': {
            'text': 'Check Setup',
            'value': '',
            'widget_type': 'button',
            'tab': 'Label Location'
        },

        # Label Location Section
        'run_name': {
            'text': 'Run name',
            'value': default_values['run_name'],
            'widget_type': 'entry',
            'tab': 'Label Location'
        },
        'generate_run_name': {
            'text': 'Generate Run Name',
            'value': '',
            'widget_type': 'button',
            'tab': 'Label Location'
        },
        'first_location': {
            'text': 'Start label location',
            'value': 0,
            'widget_type': 'entry',
            'tab': 'Label Location'
        },
        'last_tested': {
            'value': f'last tested run name was: {run_params["last_run_name"]}\n'
                     f'last tested location was: {run_params["last_location"]}\n'
                     f'last scanned asset id was: {run_params["last_asset_id"]} '
                     f'at location: {run_params["last_asset_location"]}',
            'text': '',
            'widget_type': 'label',
            'tab': 'Label Location'
        },
        'move_r2r': {
            'text': 'Move to the next Label',
            'value': '',
            'widget_type': 'button',
            'tab': 'Label Location'
        },

        # Tag-GW Configuration Section
        'do_verification': {
            'text': 'Do RF Verification',
            'value': default_values['do_verification'],
            'widget_type': 'checkbox',
            'tab': 'Tag-GW Configuration'
        },
        'min_test_time': {
            'text': 'Minimal wait time per location [sec] (for RF test)',
            'value': default_values['min_test_time'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'energy_pattern': {
            'text': 'Energy Pattern',
            'value': default_values['energy_pattern'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'time_profile': {
            'text': 'Time Profile',
            'value': default_values['time_profile'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'scan_ch': {
            'text': 'Scan Channel',
            'value': default_values['scan_ch'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'ble_power': {
            'text': 'BLE Power[dBm]',
            'value': default_values['ble_power'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'sub1g_power': {
            'text': 'Sub1G Power[dBm]',
            'value': default_values['sub1g_power'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'sub1g_freq': {
            'text': 'Sub1G frequency[kHz]',
            'value': default_values['sub1g_freq'],
            'widget_type': 'entry',
            'tab': 'Tag-GW Configuration'
        },
        'is_listen_bridge': {
            'text': 'listen to Bridge?',
            'value': default_values['is_listen_bridge'],
            'options': ('yes', 'no'),
            'widget_type': 'combobox',
            'tab': 'Tag-GW Configuration'
        },

        # Scanner Section
        'scanner_type': {
            'text': 'Scanner Type',
            'value': default_values['scanner_type'],
            'options': ('Cognex', ''),
            'widget_type': 'combobox',
            'group': 'Scanner',
            'tab': 'Hardware'
        },
        'asset_location': {
            'text': 'Asset location with respect to Wiliot code',
            'value': default_values['asset_location'],
            'options': ('first', 'last', 'none'),
            'widget_type': 'combobox',
            'group': 'Scanner',
            'tab': 'Hardware'
        },
        'wiliot_num_codes': {
            'text': 'Number of Wiliot Pixels per label',
            'value': default_values['wiliot_num_codes'],
            'widget_type': 'entry',
            'group': 'Scanner',
            'tab': 'Hardware'
        },
        'asset_num_codes': {
            'text': 'Number of asset codes per label',
            'value': default_values['asset_num_codes'],
            'widget_type': 'entry',
            'group': 'Scanner',
            'tab': 'Hardware'
        },
        'max_test_time': {
            'text': 'Maximal wait time per location [sec]',
            'value': default_values['max_test_time'],
            'widget_type': 'entry',
            'group': 'Scanner',
            'tab': 'Hardware'
        },
        'do_printing': {
            'text': 'Print on Failed Labels?',
            'value': default_values['do_printing'],
            'widget_type': 'checkbox',
            'group': 'Printer',
            'tab': 'Hardware'
        },
        'do_scan_verification': {
            'text': 'Scan after printing?',
            'value': default_values['do_scan_verification'],
            'widget_type': 'checkbox',
            'group': 'Verification Scanner',
            'tab': 'Hardware'
        },
        'scan_verification_offset': {
            'text': 'Scanner offset',
            'value': default_values['scan_verification_offset'],
            'options': list(range(1, 10)),
            'widget_type': 'combobox',
            'group': 'Verification Scanner',
            'tab': 'Hardware'
        },

        # Reel-to-Reel Section
        'is_step_machine': {
            'text': 'Is step machine?',
            'value': default_values['is_step_machine'],
            'options': ('yes', 'no'),
            'widget_type': 'combobox',
            'tab': 'Reel-to-Reel'
        },
        'r2r_type': {
            'text': 'step machine type',
            'value': default_values['r2r_type'],
            'options': ('gateway', 'arduino'),
            'widget_type': 'combobox',
            'tab': 'Reel-to-Reel'
        },
        'time_to_move': {
            'text': 'Movement time [sec]',
            'value': default_values['time_to_move'],
            'widget_type': 'entry',
            'tab': 'Reel-to-Reel'
        },

        # Association Section
        'do_association': {
            'text': 'Do association?',
            'value': default_values['do_association'] if isinstance(default_values['do_association'], bool) else default_values['do_association'].lower()=='yes',
            'widget_type': 'checkbox',
            'tab': 'Association'
        },
        'owner_id': {
            'text': 'Owner id',
            'value': default_values['owner_id'],
            'widget_type': 'entry',
            'tab': 'Association'
        },
        'env': {
            'text': 'Environment',
            'value': default_values['env'],
            'widget_type': 'entry',
            'tab': 'Association'
        },
        'category_id': {
            'text': 'Asset category id',
            'value': default_values['category_id'],
            'widget_type': 'entry',
            'tab': 'Association'
        },

        # Stop Criteria Section
        'sc_min_location': {
            'text': 'Minimum tags to test before applying "yield-stop-criteria"',
            'value': default_values['sc_min_location'],
            'widget_type': 'entry',
            'tab': 'Stop Criteria'
        },
        'sc_association': {
            'text': 'Stop if association yield is lower than [%]',
            'value': default_values['sc_association'],
            'widget_type': 'entry',
            'tab': 'Stop Criteria'
        },
        'sc_scanning': {
            'text': 'Stop if scanning yield is lower than [%]',
            'value': default_values['sc_scanning'],
            'widget_type': 'entry',
            'tab': 'Stop Criteria'
        },
        'sc_responding': {
            'text': 'Stop if responding yield is lower than [%]',
            'value': default_values['sc_responding'],
            'widget_type': 'entry',
            'tab': 'Stop Criteria'
        },
        'sc_n_no_scan': {
            'text': 'Stop if N successive labels are failed to be scanned',
            'value': default_values['sc_n_no_scan'],
            'widget_type': 'entry',
            'tab': 'Stop Criteria'
        },
    }
    is_valid_setup_out = {'is_valid': False, 'scanner': None, 'scanned_codes': []}

    def on_check_setup():
        global is_valid_setup_out
        values = gui.get_all_values()
        is_valid_setup_out = is_valid_setup(values, is_valid_setup_out['scanner'], gui)

    def on_generate_run_name():
        global is_valid_setup_out
        is_valid_setup_out['scanned_codes'].sort(reverse=True)
        gui.update_widget(widget_key='main_run_name', new_value='_'.join(is_valid_setup_out['scanned_codes']))

    def on_do_verification():
        do_verification = gui.get_all_values()['main_do_verification']
        gw_tab = ['min_test_time', 'energy_pattern', 'time_profile', 'scan_ch', 'ble_power', 'sub1g_power', 'sub1g_freq', 'is_listen_bridge']
        for k in gw_tab:
            gui.update_widget(f'main_{k}', disabled=not do_verification)

    def on_move_r2r():
        values = gui.get_all_values()
        try:
            r2r = R2R(logger_config={'logger_name': 'root', 'logger_path': None}, r2r_type=values['main_r2r_type'])
            r2r.move_r2r() # TODO printer needs line selection
            r2r.is_r2r_move(timeout=10)
            r2r.exit_app()
        except Exception as e:
            popup_message(str(e))

    def on_run():
        global is_valid_setup_out
        values = gui.get_all_values()
        if not is_valid_setup_out['is_valid']:
            is_valid_setup_out = is_valid_setup(values, is_valid_setup_out['scanner'], gui)
            if not is_valid_setup_out['is_valid']:
                print('invalid setup - update configuration and run again')
                return
        for k, v in values.items():
            default_values[k] = v
        with open(GUI_FILE, 'w') as f:
            json.dump(default_values, f)
        with open(RUN_PARAMS_FILE, 'w') as f:
            json.dump(run_params, f)

        if is_valid_setup_out['scanner'] is not None:
            is_valid_setup_out['scanner'].disconnect()
        gui.on_submit()
        return default_values

    gui = WiliotGui(params_dict, do_button_config=False, title='Association and Verification tester',
                    height_offset=50 , disable_all_children_windows=False)
    gui.widgets['main_last_tested'].configure(anchor="w", justify='left')
    gui.add_event(widget_key='main_generate_run_name', command=on_generate_run_name, event_type='button')
    gui.add_event(widget_key='main_check_setup', command=on_check_setup, event_type='button')
    gui.add_event(widget_key='main_do_verification', event_type='button', command=lambda: on_do_verification())
    gui.add_event(widget_key='main_move_r2r', event_type='button', command=lambda: on_move_r2r())
    gui.button_configs(submit_command=on_run)
    on_do_verification()
    values_out = gui.run()
    values_out_clean = {k.replace('main_', ''): v for k, v in values_out.items()}
    values_out_clean['category_id'] = values_out_clean['category_id'].strip()
    with open(GUI_FILE, 'w') as f:
                json.dump(values_out_clean, f)
    return values_out_clean

def is_valid_setup(values, scanner, gui):
    # check scanner
    valid_output = {'is_valid': False, 'scanner': scanner, 'scanned_codes': []}
    if values['main_scanner_type'].lower() == 'cognex':
        try:
            if scanner is None:
                scanner = Scanner(max_test_time=values['main_max_test_time'], 
                                n_codes=int(values['main_asset_num_codes']) + int(values['main_wiliot_num_codes']))
            valid_output['scanned_codes'] = scanner.scan()
            valid_output['scanned_codes'].sort()
            yes_or_no_layout = {
                'question': {
                    'value': f'Starting location was set to: {values["main_first_location"]}\n'
                                f'The scanned codes are:\n{valid_output["scanned_codes"]}\n'
                                f'Is the starting location is correct?\n'
                                f'Are those the codes of the first label?\n\n'
                                f'If not, please click on No, try to re-position scanner and try again',
                    'text': '',
                    'widget_type': 'label',
                },
            }
        except Exception as e:
            popup_message(str(e))
            valid_output['is_valid'] = False
            return valid_output

    def on_no_button():
        print('re-positioning the scanner and try again')
        valid_output['is_valid'] = False
        yes_or_no_gui.on_cancel()

    def on_yes_button():
        client_types = ['asset', None]
        for client_type in client_types:
            g = GetApiKey(gui_type='ttk',
                            env=values['main_env'],
                            owner_id=values['main_owner_id'],
                            client_type=client_type
                            )
            api_key = g.get_api_key()
            if not api_key:
                file_path = g.get_config_path()
                popup_message(
                    f'Could not found an api key for owner id {values["main_owner_id"]} and env {values["main_env"]}'
                    f'at path: {file_path}', tk_frame=gui.layout)
                valid_output['is_valid'] = False
                yes_or_no_gui.on_submit()
        valid_output['is_valid'] = True
        yes_or_no_gui.on_submit()

    yes_or_no_gui = WiliotGui(params_dict=yes_or_no_layout, parent=gui.layout, do_button_config=False,
                                title='Valid Setup Association and Verification', exit_sys_upon_cancel=False,
                                disable_all_children_windows=False)
    yes_or_no_gui.button_configs(submit_button_text='Yes', submit_command=on_yes_button, cancel_button_text='No', cancel_command=on_no_button)
    yes_or_no_gui.run()
    print(f'is valid setup output: {valid_output}')
    return valid_output

if __name__ == '__main__':
    user_inputs = get_user_inputs()
    print(user_inputs)