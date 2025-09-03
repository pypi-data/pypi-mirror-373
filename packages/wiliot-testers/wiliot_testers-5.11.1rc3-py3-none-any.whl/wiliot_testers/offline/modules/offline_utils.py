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

from wiliot_api import ManufacturingClient
from wiliot_core import GetApiKey, InlayTypes
from wiliot_tools.utils.wiliot_gui.wiliot_gui import *
from wiliot_testers.config.unusable_inlays import UnusableInlayTypes
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.tester_utils import open_json, open_json_cache
from wiliot_testers.wiliot_tester_tag_result import *
from wiliot_tools.test_equipment.test_equipment import serial_ports
import serial # type: ignore
import logging
import re
import time
import pandas as pd

PRINT_FORMAT_TO_PASS_JOB_NAME = {'SGTIN': 'SGTIN_QR', 'Barcode': 'BARCODE_8', 'prePrint': 'BLANK'}
PRINT_JOB_OPTIONS = tuple(PRINT_FORMAT_TO_PASS_JOB_NAME.values())
PASS_JOB_NUM = 2
TAG_COUNTER_DIGITS = 4
SGTIN_PREFIX = '(01)00850027865010(21)'
CONFIGS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'configs')


class ConfigDefaults(object):
    """
    contains the default values for the configuration json
    """

    def __init__(self):
        self.printer_defaults = {'TCP_IP': '192.168.6.61', 'TCP_PORT': '3003', 'TCP_BUFFER': '128',
                                 'enableLineSelection': 'Yes', 'enablePrinterAck': 'Yes',
                                 'printingDuringMovement': 'No',
                                 'printingBidirectionalMovement': 'No'}
        self.single_band_gw_defaults = {'energizingPattern': '18', 'timeProfile': '3,7', 'txPower': '3',
                                        'rssiThreshold': '90', 'plDelay': '150'}
        self.dual_band_gw_defaults = {'energizingPattern': '18', 'secondEnergizingPattern': '52', 'timeProfile': '5,10',
                                      'txPower': '3', 'rssiThreshold': '90', 'plDelay': '100'}
        self.external_hw = {"sensorsEnable": "Yes",
                            "AutoAttenuatorEnable": "No", "attnComport": "AUTO", "attnval": "0",
                            "scannerType": "rtscan", "scannerFlash": False,
                            "isR2R": "yes", "typeR2R": "gateway"}

    def get_printer_defaults(self):
        return self.printer_defaults

    def get_single_band_gw_defaults(self):
        return self.single_band_gw_defaults

    def get_dual_band_gw_defaults(self):
        return self.dual_band_gw_defaults

    def get_external_hw_defaults(self):
        return self.external_hw


class DefaultGUIValues:
    def __init__(self, gui_type):
        if gui_type == 'Main':
            self.default_gui_values = {
                'toPrint': 'No', 'printOffset': '1', 'printingFormat': 'SGTIN',
                'batchName': 'test_reel',
                'testName': 'Ble_Test_Only', 'inlay': InlayTypes.TIKI_099.value, 'product_config': 'Pixels',
                'tag_sensor_type': 'Default',
                'gen': 'Gen2',
                'desiredTags': '9999999', 'desiredPass': '9999999',
                'surface': SurfaceTypes.AIR.value,
                'conversion': ConversionTypes.STANDARD.value,
                'Environment': 'production', 'OwnerId': 'wiliot-ops', 'operator': '', 'conversionLabel': '',
                'QRRead': 'No', 'QRcomport': 'COM3', 'QRoffset': '2',
                'QRtimeout': '200',
                'sensorOffset': '',
                'comments': '', 'maxFailStop': '50', 'maxYieldStop': '40',
                'pass_response_diff': '100', 'pass_response_diff_offset': '9999'}
        elif gui_type == 'Test':
            self.default_gui_values = {'passJobName': 'BARCODE_8', 'passJobNum': 2, 'sgtin': '',
                                       'stringBeforeCounter': '',
                                       'reelNumManually': 'test', 'firstPrintingValue': '0', 'tagLocation': '0',
                                       'tag_reel_location': '0'}
        elif gui_type == 'SGTIN':
            self.default_gui_values = {'passJobName': 'SGTIN_QR', 'passJobNum': 2, 'sgtin': '(01)00850027865010(21)',
                                       'stringBeforeCounter': '',
                                       'reelNumManually': '', 'firstPrintingValue': '0', 'tagLocation': '0',
                                       'tag_reel_location': '0'}
        elif gui_type == 'Barcode':
            self.default_gui_values = {'passJobName': 'BARCODE_8', 'passJobNum': 2, 'sgtin': '',
                                       'stringBeforeCounter': '',
                                       'reelNumManually': '', 'firstPrintingValue': '0', 'tagLocation': '0',
                                       'tag_reel_location': '0'}
        elif gui_type == 'prePrint':
            self.default_gui_values = {'passJobName': 'BLANK', 'passJobNum': 2, 'sgtin': '',
                                       'stringBeforeCounter': '',
                                       'reelNumManually': '', 'firstPrintingValue': '0', 'tagLocation': '0',
                                       'tag_reel_location': '0'}
        else:
            self.default_gui_values = {}


def connect_to_cloud(env, owner_id, logger):
    try:
        k = GetApiKey(env=env, owner_id=owner_id)
        api_key = k.get_api_key()
        if api_key == '':
            raise Exception(f'Could not found an api key for owner id {owner_id} and env {env}')

        client = ManufacturingClient(api_key=api_key, env=env, logger_=logger.name, owner_id=owner_id)
        logger.info('Connection to the cloud was established')
        return client
    except Exception as e:
        raise Exception(f'Problem connecting to cloud {e}')


def open_session(test_suite_list):
    """
    gets the user inputs from first GUI
    :return: dictionary of the values
    """

    def check_structure(input_str: str, gen_in: str, printing_format: str, job_name: str) -> str:
        if printing_format == 'prePrint':
            pattern = re.compile(r"^[A-Z]{4}$")
            if not pattern.match(input_str):
                return 'Reel name error \n Reel name should be: \n 4 upper case alphabetic chars\n'
        elif gen_in.lower() == 'gen2':
            pattern = re.compile(r"^[A-Z0-9]{6}\.[0-9]{2}_[A-F]$")
            if not pattern.match(input_str):
                return 'Reel name error \n Reel name should be: \n <6 uppercase alphanumeric chars>.<2 integers minimum 01 maximum 25>_<upper case char minimum A maximum F>\n'
        elif gen_in.lower() == 'gen3':
            if 'SGTIN' in printing_format.upper() or (job_name is not None and 'SGTIN' in job_name.upper()):
                reel_name_length = 4
            else:
                reel_name_length = 3
            pattern = re.compile(rf"^[a-z0-9]{{{reel_name_length}}}_[A-E]$")
            if not pattern.match(input_str):
                return f'Reel name error \n Reel name should be: \n <reel id: {reel_name_length} alphanumeric chars>_<upper case char minimum A maximum E>\n'
        else:
            raise Exception('check_structure: gen must be gen2 or gen3')
        return ''

    def check_is_gen3_prod(values_in):
        return values_in['main_gen'].lower() == 'gen3' and 'prod' in values_in['main_Environment'].lower() and \
            values_in['main_toPrint'].lower() == 'yes'

    def check_is_preprint_prod(values_in):
        return values_in['main_printingFormat'].lower() == 'preprint' and 'prod' in values_in['main_Environment'].lower() and \
            values_in['main_toPrint'].lower() == 'yes'

    folder_name = CONFIGS_FOLDER
    file_name = 'gui_inputs_do_not_delete.json'
    gui_inputs_values = open_json(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                  default_values=DefaultGUIValues(gui_type='Main').default_gui_values)
    for key in DefaultGUIValues(gui_type='Main').default_gui_values.keys():
        if key not in gui_inputs_values.keys():
            gui_inputs_values[key] = DefaultGUIValues(gui_type='Main').default_gui_values[key]

    inlay_group = tuple(x.value for x in InlayTypes if x.name not in UnusableInlayTypes.__members__)
    conversion_group = tuple([conv.value for conv in ConversionTypes])
    surface_group = tuple([surf.value for surf in SurfaceTypes])
    im_path = os.path.join(CONFIGS_FOLDER, 'offline_offset.png')
    param_dict = {
        'main': {
            'batchName': {'text': 'Reel Name:', 'value': gui_inputs_values['batchName'], 'tab': 'Main',
                          'group': 'Name'},
            'conversionLabel': {'text': 'conversion Label:', 'value': gui_inputs_values['conversionLabel'],
                                'tab': 'Main', 'group': 'Name'},
            'sameConversionLabel': {'text': 'allow same conversion label for new reel', 'value': False,
                                    'tab': 'Main', 'group': 'Name'},
            'get_reel_id': {'value': 'Get Reel Id', 'widget_type': 'button', 'tab': 'Main', 'group': 'Name'},
            'testName': {'text': 'Test Suite:', 'value': gui_inputs_values['testName'],
                         'widget_type': 'combobox', 'options': tuple(test_suite_list), 'tab': 'Main', 'group': 'test'},
            'toPrint': {'text': 'Printing?', 'value': gui_inputs_values['toPrint'],
                        'widget_type': 'combobox', 'options': ('Yes', 'No'), 'tab': 'Main', 'group': 'test'},
            'QRRead': {'text': 'Scanning?', 'value': gui_inputs_values['QRRead'],
                       'widget_type': 'combobox', 'options': ('Yes', 'No'), 'tab': 'Main', 'group': 'test'},
            'Environment': {'text': 'Environment:', 'value': gui_inputs_values['Environment'], 'group': 'Cloud',
                            'widget_type': 'combobox', 'options': ('test', 'production'), 'tab': 'Main'},
            'OwnerId': {'text': 'Owner Id:', 'value': gui_inputs_values['OwnerId'], 'group': 'Cloud',
                        'widget_type': 'combobox', 'options': ('wiliot-ops', '852213717688'), 'tab': 'Main'},
            'operator': {'text': 'Operator:', 'value': gui_inputs_values['operator'], 'tab': 'Main'},
            'comments': {'text': 'Comments:', 'value': gui_inputs_values['comments'], 'tab': 'Main'},

            'gen': {'text': 'Tag Generation:', 'value': gui_inputs_values['gen'],
                    'widget_type': 'combobox', 'options': ('Gen2', 'Gen3'), 'tab': 'Reel', 'group': 'tag'},
            'inlay': {'text': 'Inlay Type:', 'value': gui_inputs_values['inlay'],
                      'widget_type': 'combobox', 'options': inlay_group, 'tab': 'Reel', 'group': 'tag'},
            'product_config': {'text': 'Product configuration:', 'value': gui_inputs_values['product_config'],
                      'widget_type': 'combobox', 'options': ('Pixels', 'Labels'), 'tab': 'Reel', 'group': 'tag'},
            'tag_sensor_type': {'text': 'Tag sensor type:', 'value': gui_inputs_values['tag_sensor_type'],
                                'widget_type': 'combobox', 'options': ('Default', 'Humidity', 'Light'), 'tab': 'Reel', 'group': 'tag'},
            'surface': {'text': 'Surface:', 'value': gui_inputs_values['surface'], 'group': 'setup',
                        'widget_type': 'combobox', 'options': surface_group, 'tab': 'Reel'},
            'conversion': {'text': 'Conversion:', 'value': gui_inputs_values['conversion'], 'group': 'setup',
                           'widget_type': 'combobox', 'options': conversion_group, 'tab': 'Reel'},

            'ignoreStop': {'text': 'Ignore Stop Conditions', 'value': False, 'tab': 'Stop Conditions'},
            'maxFailStop': {'text': 'Max failed tags in a row:', 'value': int(gui_inputs_values['maxFailStop']),
                            'tab': 'Stop Conditions'},
            'maxYieldStop': {'text': 'Minimum yield [%]:', 'value': int(gui_inputs_values['maxYieldStop']),
                             'tab': 'Stop Conditions'},
            'desiredTags': {'text': 'Desired amount of tags:', 'value': int(gui_inputs_values['desiredTags']),
                            'tab': 'Stop Conditions'},
            'desiredPass': {'text': 'Desired amount of passed tags:', 'value': int(gui_inputs_values['desiredPass']),
                            'tab': 'Stop Conditions'},

            'printingFormat': {'text': 'Printing Job Format:',
                               'value': gui_inputs_values['printingFormat']
                               if gui_inputs_values['printingFormat'] != 'Test' else 'Barcode',
                               'widget_type': 'combobox', 'options': ('Test', 'SGTIN', 'Barcode', 'prePrint'),
                               'tab': 'Hardware', 'group': 'Printer'},
            'printOffset': {'text': 'Printing Offset:', 'value': int(gui_inputs_values['printOffset']),
                            'widget_type': 'combobox', 'options': tuple(range(1, 6)), 'tab': 'Hardware',
                            'group': 'Printer'},
            'QRcomport': {'text': 'Scanner COM port:',
                          'value': int(gui_inputs_values['QRcomport'])
                          if str(gui_inputs_values['QRcomport']).isdigit() else 0, 'group': 'Scanner',
                          'widget_type': 'combobox', 'options': tuple(range(15)), 'tab': 'Hardware'},
            'QRoffset': {'text': 'Scanner Offset:', 'value': int(gui_inputs_values['QRoffset']),
                         'widget_type': 'combobox', 'options': tuple(range(15)), 'tab': 'Hardware', 'group': 'Scanner'},
            'QRtimeout': {'text': 'Scanner Read Time [ms]:', 'value': int(gui_inputs_values['QRtimeout']),
                          'widget_type': 'combobox', 'options': tuple(range(100, 1000, 100)), 'tab': 'Hardware',
                          'group': 'Scanner'},
            'sensorOffset': {'text': 'Label Detector Sensor Offset:',
                             'value': int(gui_inputs_values['sensorOffset'])
                             if gui_inputs_values['sensorOffset'] else '',
                             'widget_type': 'combobox', 'options': tuple([''] + list(range(15))), 'tab': 'Hardware'},
            "offline_offset_image": {
                "widget_type": "image", "value": im_path, "options": {"width": 550, "height": 300},
                "text": "", 'tab': 'Hardware', 'columnspan': 2},
        },
        'version': {'value': 'Version: {}'.format(get_version()), 'widget_type': 'label'}
    }

    wg = WiliotGui(params_dict=param_dict, do_button_config=False, height_offset=50, title='Offline tester')

    def update_reel_name_state():
        values_in = wg.get_all_values()
        if check_is_preprint_prod(values_in=values_in):
            wg.update_widget(widget_key='main_batchName', disabled=False)
            wg.update_widget(widget_key='main_conversionLabel', disabled=False)
            wg.update_widget(widget_key='main_get_reel_id', disabled=True)
        else:
            is_gen3_prod = check_is_gen3_prod(values_in=values_in)
            for widget_key in ['batchName']:
                wg.update_widget(widget_key=f'main_{widget_key}', disabled=is_gen3_prod)
            for widget_key in ['conversionLabel', 'get_reel_id']:
                wg.update_widget(widget_key=f'main_{widget_key}', disabled=not is_gen3_prod)

    tag_print_config = {}

    def update_conversion_label():
        values_in = wg.get_all_values()
        tag_print_config['conversion_label_changed'] = (values_in["main_conversionLabel"] != gui_inputs_values['conversionLabel']) or values_in["main_sameConversionLabel"]
        if tag_print_config['conversion_label_changed']:
            update_reel_name_str(values_in["main_conversionLabel"])

    def check_conversion_label(label):
        label_parts = label.split('_')
        if len(label_parts) != 5:
            str_out = '\nconversion label must contain 5 fields: inlay, sequence assembly reel, lane id (letter), ' \
                      'conversion date, serial number: (e.g., 169_1_A_22082024_2)'
            return False, str_out
        for i, k in enumerate(['inlay', 'seq_ass_reel', 'lane', 'date', 'sn']):
            tag_print_config[k] = label_parts[i]
        tag_print_config['lane'] = tag_print_config['lane'].upper()
        if not 'A' <= tag_print_config['lane'] <= 'F':
            return False, f'specified lane was: {tag_print_config["lane"]} but labe must be A - F'
        return True, ''

    def update_reel_name_str(user_conversion_label):
        check_conversion_label(user_conversion_label)
        values_in = wg.get_all_values()
        if not check_is_preprint_prod(values_in=values_in):
            reel_id = tag_print_config.get("stringBeforeCounter", "")
            reel_id = reel_id[-4:] if SGTIN_PREFIX in reel_id else reel_id
            new_str = f'{reel_id}_{tag_print_config.get("lane", "")}'
            wg.update_widget(widget_key='main_batchName', disabled=False)
            wg.update_widget(widget_key='main_batchName', new_value=new_str)
            wg.update_widget(widget_key='main_batchName', disabled=True)

    def update_print_config(print_config):
        print_config['run_printing_gui'] = True
        values_in = wg.get_all_values()
        print_config_out, is_valid, new_run = \
            printing_sgtin_window(env=values_in['main_Environment'], owner_id=values_in['main_OwnerId'],
                                  printing_format=values_in['main_printingFormat'], gen=values_in['main_gen'],
                                  parent=wg.layout)
        tag_print_config['is_new_run'] = new_run
        if is_valid:
            for k, v in print_config_out.items():
                print_config[k] = v
        else:
            print('Generating invalid reel id')
            tag_print_config['stringBeforeCounter'] = 'invalid reel id'
        update_reel_name_str(values_in["main_conversionLabel"])

    def update_production_config():
        values_in = wg.get_all_values()
        if values_in['main_product_config'].lower() == 'labels' and str(values_in['main_QRoffset']).lower() > '3':
            popup_message(msg='Production Configuration was set to LABELS with LARGE scanner offset!\nPlease make sure it is the correct configuration',
                          bg='yellow', tk_frame=wg.layout)
        elif values_in['main_product_config'].lower() == 'pixels' and str(values_in['main_QRoffset']).lower() <= '3':
            popup_message(msg='Production Configuration was set to PIXELS with SMALL scanner offset!\nPlease make sure it is the correct configuration',
                          bg='yellow', tk_frame=wg.layout)

    def print_offset_change():
        values_in = wg.get_all_values()
        if int(values_in['main_printOffset']) == 0:
            popup_message(msg='Printing offset MUST be larger than 0', bg='red', tk_frame=wg.layout)
            wg.update_widget(widget_key='main_printOffset', new_value=1)
        else:
            popup_message(msg='Printing offset was changed!\nPlease make sure it is the correct offset',
                          bg='yellow', tk_frame=wg.layout)

    def update_stop_conditions_state():
        values_in = wg.get_all_values()
        for widget_key in ['maxFailStop', 'maxYieldStop', 'desiredTags', 'desiredPass']:
            wg.update_widget(widget_key=f'main_{widget_key}', disabled=values_in['main_ignoreStop'])

    def on_submit():
        values_in = wg.get_all_values()
        # check values validity
        err_str = ''
        if not str(values_in['main_desiredTags']).isdigit():
            err_str += f'desiredTags must be a number! {values_in["main_desiredTags"]} is not supported\n'
        if not str(values_in['main_desiredPass']).isdigit():
            err_str += f'desiredPass must be a number! {values_in["main_desiredPass"]} is not supported\n'
        if values_in['main_Environment'] == 'production' and values_in['main_toPrint'].lower() == 'yes':
            err_str += check_structure(values_in['main_batchName'], values_in['main_gen'],
                                    values_in['main_printingFormat'], tag_print_config.get('passJobName'))

            if values_in['main_printingFormat'].lower() == 'preprint' and values_in['main_QRRead'].lower() != 'yes':
                err_str += 'scanning must be enabled for preprint\n'
            if values_in['main_gen'].lower() == 'gen3':
                is_label_valid, err_conv = check_conversion_label(values_in["main_conversionLabel"])
                if not is_label_valid:
                    err_str += err_conv
                elif tag_print_config.get('is_new_run', False) and \
                        not tag_print_config.get('conversion_label_changed', False) and not values_in["main_sameConversionLabel"]:
                    err_str += f'\nConversion label was not updated although NEW reel was assembled'
                elif tag_print_config.get('inlay', '') != values_in['main_inlay']:
                    err_str += f'\nUser specified inlay: {values_in["main_inlay"]} is different from the scanned ' \
                                f'conversion label: {values_in["main_conversionLabel"]}'
        if values_in['main_tag_sensor_type'].lower() != 'default':
            p_dict = {
                'space': {'value': '', 'widget_type': 'label'},
                'is_new': {'value': f"Are you sure tag sensor type is {values_in['main_tag_sensor_type']}?\n", 'widget_type': 'label', 'options': {'font': ("Gudea", 20)}}}
            wg_tag_sens = WiliotGui(params_dict=p_dict, do_button_config=False, exit_sys_upon_cancel=False, title='Tag Sensor Type?')
            wg_tag_sens.button_configs(submit_button_text='Yes', cancel_button_text='No')
            correct_sensor_type = wg_tag_sens.run() is not None
            if not correct_sensor_type:
                err_str += f'\nPlease change the Tag Sensor Type on the Reel Tab'
        if err_str:
            popup_message(msg=err_str, bg='red')
            return

        tag_print_config['batch_name_change'] = values_in["main_batchName"] != gui_inputs_values['batchName']

        wg.on_submit()

    update_reel_name_state()
    for widget_event_key in ['gen', 'Environment', 'toPrint']:
        wg.add_event(widget_key=f'main_{widget_event_key}',
                     event_type='<<ComboboxSelected>>', command=lambda args: update_reel_name_state())
    wg.add_event(widget_key='main_conversionLabel',
                 event_type='<FocusOut>', command=lambda args: update_conversion_label())
    wg.add_event(widget_key='main_get_reel_id',
                 event_type='button', command=lambda: update_print_config(print_config=tag_print_config))
    wg.add_event(widget_key='main_printOffset',
                 event_type='<<ComboboxSelected>>', command=lambda args: print_offset_change())
    wg.add_event(widget_key='main_ignoreStop',
                 event_type='button', command=lambda: update_stop_conditions_state())
    for widget_event_key in ['product_config', 'QRoffset']:
        wg.add_event(widget_key=f'main_{widget_event_key}',
                     event_type='<<ComboboxSelected>>', command=lambda args: update_production_config())
    
    wg.button_configs(submit_command=on_submit)
    user_input = wg.run()
    if user_input is None:
        print('User exited the program')
        exit()

    # remove prefix from user input dict
    values = {}
    for k, v in user_input.items():
        values[k.replace('main_', '')] = v

    for key in gui_inputs_values.keys():
        if key not in values.keys():
            values[key] = gui_inputs_values[key]

    # save user input
    with open(os.path.join(folder_name, file_name), 'w') as f:
        json.dump(values, f, indent=2, separators=(", ", ": "), sort_keys=False)

    return values, tag_print_config


def get_printed_value(string_before_the_counter: str, first_counter: str, digits_in_counter=TAG_COUNTER_DIGITS):
    """
    builds the printed value
    :type string_before_the_counter: string
    :param string_before_the_counter: the sg1 Id of the tested reel
    :type digits_in_counter: int
    :param digits_in_counter: amount of digits in the tag counter field (usually 4)
    :type first_counter: string
    :param first_counter: counter of the run first tag
    """
    first_print = str(string_before_the_counter)
    first_print += 'T'
    first_print += str(first_counter).zfill(digits_in_counter)
    is_ok = len(first_counter) <= digits_in_counter
    return first_print, is_ok


def update_tag_counter(current_tag_counter: str, value_to_add: int):
    return str(int(current_tag_counter) + int(value_to_add)).zfill(TAG_COUNTER_DIGITS)


def get_gui_inputs_values(printing_format):
    """
    A function that sends the GUI's input
    """
    folder_name = CONFIGS_FOLDER
    file_name = get_print_user_config_file(printing_format)
    gui_inputs_values = open_json_cache(folder_path=folder_name, file_path=os.path.join(folder_name, file_name),
                                        default_values=DefaultGUIValues(printing_format).default_gui_values)
    return gui_inputs_values


def printing_process_of_test_and_sgtin(window, printing_format, gui_inputs_values, is_new_reel=True):
    """
    A function that does all the work of the printing process
    """
    reel_number = ''
    pass_job_name = None
    is_ok = True
    original_p_format = printing_format
    printing_config = {'pass_job_name': pass_job_name, 'reel_number': reel_number, 'printing_format': printing_format}
    printing_values = {'firstPrintingValue': '', 'reelNumManually': ''}

    def check_first_print(values_in=None, printing_config_in=None):
        if values_in is None:
            values_in = window.get_all_values()
        if printing_config_in is None:
            printing_config_in = printing_config
        printing_config_in['pass_job_name'] = values_in['passJobName']
        try:
            if original_p_format == 'Test':
                printing_config_in["printing_format"] = printing_config_in['pass_job_name']

            if printing_config_in["printing_format"] == 'prePrint':
                if 'T' not in values_in['firstFullExternalId']:
                    window.update_widget(widget_key='-OUTPUT-',
                                         new_value='scanned external id must contains the char T')
                    return
                external_id_list = values_in['firstFullExternalId'].split('T')
                if len(external_id_list) != 2:
                    window.update_widget(widget_key='-OUTPUT-',
                                         new_value='scanned external id must be: <REEL ID>T<TAG COUNT>')
                    return
                if len(external_id_list[1]) != 4:
                    window.update_widget(widget_key='-OUTPUT-',
                                         new_value='Counter should be equal to 4 digits')
                    return
                values_in['firstPrintingValue'] = external_id_list[1]
                values_in['reelNumManually'] = external_id_list[0]
                printing_values['firstPrintingValue'] = values_in['firstPrintingValue']
                printing_values['reelNumManually'] = values_in['reelNumManually']

            if len(str(values_in['firstPrintingValue'])) > TAG_COUNTER_DIGITS:
                window.update_widget(widget_key='-OUTPUT-',
                                     new_value=f"you entered: {values_in['firstPrintingValue']} but length "
                                               f"must be {TAG_COUNTER_DIGITS}")
                return
            if printing_config_in['printing_format'] == 'SGTIN' or 'SGTIN' in values_in['passJobName']:
                printing_config_in['reel_number'] = str(values_in['sgtinNumManually'])
                if not len(str(values_in['sgtinNumManually'])) == 22:
                    window.update_widget(
                        widget_key='-OUTPUT-',
                        new_value=f'SGTIN number is not equal to 22 chars!!\n'
                                  f'The current SGTIN length is: {len(values_in["sgtinNumManually"])}')
                    return
                if not len(str(values_in['reelNumManually'])) == 4:
                    window.update_widget(widget_key='-OUTPUT-',
                                         new_value='Reel number is not equal to 4 chars!!\n'
                                                   'Please enter correct Reel number')
                    return

            if (printing_config_in['printing_format'] == 'Barcode' or 'Barcode' in values_in['passJobName']) and \
                    len(values_in['reelNumManually']) != 3:
                window.update_widget(widget_key='-OUTPUT-',
                                     new_value='Reel number is not equal to 3 chars!!\n'
                                               'Please enter correct Reel number')
                return

            printing_config_in['pass_job_name'] = values_in['passJobName']

            if printing_config_in['printing_format'] == 'SGTIN' or 'SGTIN' in values_in['passJobName']:
                printing_config_in['reel_number'] += str(values_in['reelNumManually'])
            else:
                printing_config_in['reel_number'] = str(values_in['reelNumManually'])
            printing_config_in['first_counter'] = values_in['firstPrintingValue']
            first_print, is_ok = get_printed_value(printing_config_in['reel_number'],
                                                   printing_config_in['first_counter'])
            window.update_widget(widget_key='-OUTPUT-',
                                 new_value='The first tag printing value will be:\n' + first_print)
        except Exception as e:
            window.update_widget(widget_key='-OUTPUT-',
                                 new_value=f'got exception during parsing, please try again: {e}')
            return

        if printing_config_in['printing_format'] == 'prePrint':
            printing_config_in['reel_number'] = str(values_in['reelNumManually'])
            first_print, is_ok = get_printed_value(printing_config_in['reel_number'], values_in['firstPrintingValue'])
            msg = f'Are you sure the tag BEFORE the coupler is:\n\n' \
                    f'      {first_print}\n'
            wg_preprint = WiliotGui(params_dict={'sure': {'value': msg, 'widget_type': 'label'}}, parent=window.layout,
                                exit_sys_upon_cancel=False, title='Offline Setup')
                
            out = wg_preprint.run()
            sure_to_submit = out is not None
            if sure_to_submit:
                window.update_widget(widget_key='-OUTPUT-',
                                     new_value='The first tag printing value will be:\n' + first_print)
            else:
                window.update_widget(widget_key='-OUTPUT-',
                                     new_value='')
                return

        return True

    def submit_func(values_in=None, printing_config_in=None):
        if check_first_print(values_in=values_in, printing_config_in=printing_config_in):
            window.on_submit()

    window.button_configs(submit_command=lambda: submit_func(printing_config_in=printing_config))
    window.add_event(widget_key='check_first_print', event_type='button',
                     command=lambda: check_first_print(printing_config_in=printing_config))
    values = window.run()
    if values is None:
        is_ok = False

    v = {}
    pass_job_name = printing_config['pass_job_name']
    reel_number = printing_config['reel_number']

    if is_ok:
        for k, new_v in printing_values.items():
            if new_v:
                values[k] = new_v
        v = {'passJobName': pass_job_name, 'digitsInCounter': TAG_COUNTER_DIGITS, 'passJobNum': PASS_JOB_NUM,
             'firstPrintingValue': values['firstPrintingValue'], 'tagLocation': values['firstPrintingValue'],
             'tag_reel_location': gui_inputs_values['tag_reel_location'],
             'stringBeforeCounter': reel_number}

        data_to_save = {'passJobName': pass_job_name,
                        'passJobNum': PASS_JOB_NUM,
                        'sgtin': values['sgtinNumManually'] if 'sgtinNumManually' in values else '',
                        'reelNumManually': values['reelNumManually'],
                        'firstPrintingValue': values['firstPrintingValue'],
                        'tagLocation': values['firstPrintingValue'],
                        'tag_reel_location': gui_inputs_values['tag_reel_location'],
                        'stringBeforeCounter': reel_number}

        if original_p_format == 'Test':
            v['failJobName'] = pass_job_name
        else:
            v['failJobName'] = 'line_'
            v['printingFormat'] = original_p_format
            data_to_save['printingFormat'] = original_p_format

        folder_name = CONFIGS_FOLDER
        file_name = get_print_user_config_file(original_p_format)
        f = open(os.path.join(folder_name, file_name), "w")
        json.dump(data_to_save, f)
        f.close()
    return v, is_ok


def get_print_user_config_file(printing_format):
    if printing_format.lower() == 'test':
        filename = 'gui_printer_inputs_4_Test_do_not_delete.json'
    elif printing_format in PRINT_FORMAT_TO_PASS_JOB_NAME.keys():
        filename = 'gui_printer_inputs_4_SGTIN_do_not_delete.json'
    else:
        raise Exception(f'unsupported printing format: {printing_format}, valid formats are: sgtin, barcode, test')
    return filename


def printing_test_window(parent=None):
    """
    opens the GUI for user input for test print
    :return: dictionary of user inputs
    """
    printing_format = 'Test'
    gui_inputs_values = get_gui_inputs_values(printing_format)

    if gui_inputs_values['reelNumManually'] == "":
        reel_num = 'test_test_test_test_X_test'
        gui_inputs_values['sgtin'] = reel_num[:22]
        gui_inputs_values['reelNumManually'] = reel_num[22:]
        gui_inputs_values['firstPrintingValue'] = '0'
        gui_inputs_values['tagLocation'] = '0'
        gui_inputs_values['tag_reel_location'] = '0'

    param_dict = {
        'passJobName': {'text': 'Job to print for pass:', 'value': gui_inputs_values['passJobName'],
                        'widget_type': 'combobox', 'options': PRINT_JOB_OPTIONS},
        'firstPrintingValue': {'text': 'What is the first counter number?',
                               'value': gui_inputs_values['firstPrintingValue']},
        'sgtinNumManually': {'text': 'For QR code - what is the SGTIN number?',
                             'value': gui_inputs_values['sgtin']},
        'reelNumManually': {'text': 'For Barcode code - what is the reel number?',
                            'value': gui_inputs_values['reelNumManually']},
        '-OUTPUT-': {'value': '', 'widget_type': 'label', 'options': {'font': FONT_TXT_WARNING}, 'columnspan': 2},
        'check_first_print': {'text': 'Check first print', 'value': '', 'widget_type': 'button'}
    }
    wg = WiliotGui(params_dict=param_dict, parent=parent, do_button_config=False, title='Printing Test Window')

    wanted_v, wanted_is_ok = printing_process_of_test_and_sgtin(wg, printing_format, gui_inputs_values)

    return wanted_v, wanted_is_ok


def printing_sgtin_window(env='', owner_id='wiliot-ops', printing_format='SGTIN', gen='Gen2', parent=None, is_new_batch_name=False):
    """
    opens the GUI for user input for SGTIN print
    :return: dictionary of user inputs
    """
    read_only = False
    gui_inputs_values = get_gui_inputs_values(printing_format)

    # Checking if it's a new reel run and updating the GUI inputs according to this
    params_dict = {
        'space': {'value': '', 'widget_type': 'label'},
        'is_new': {'value': '    New Reel?    \n', 'widget_type': 'label', 'options': {'font': ("Gudea", 20)}}}
    wg_new_run = WiliotGui(params_dict=params_dict, parent=parent, do_button_config=False, exit_sys_upon_cancel=False,
                           title='New run?')
    wg_new_run.button_configs(submit_button_text='Yes', cancel_button_text='No')
    new_run = wg_new_run.run() is not None
    if env == 'production' or env == '':
        env = 'prod'
        # verify batch name changed if new run, and didn't change if not new run
        if printing_format.lower() == 'preprint' and not new_run == is_new_batch_name:
            err_msg = 'reel name must be changed for new reel run, and not changed for existing reel run\n'
            popup_message(msg=err_msg, bg='red')
            raise Exception(err_msg)
    if new_run:
        gui_inputs_values['tagLocation'] = '0'
        gui_inputs_values['tag_reel_location'] = '0'
        if printing_format != 'prePrint':
            try:
                logging.info('Receiving data from the cloud, please wait')
                reel_num = get_reel_name_from_cloud_api(env, owner_id, printing_format, gen)
                print(reel_num)
            except Exception:
                logging.warning('Problem with receiving data from cloud')
                raise Exception
        else:
            reel_num = {}
        gui_inputs_values['firstPrintingValue'] = '0000'
        if 'data' in reel_num:
            reel_number = reel_num['data']
            if printing_format == 'SGTIN':
                if len(reel_number) < len(SGTIN_PREFIX):
                    reel_number = SGTIN_PREFIX + reel_number
                gui_inputs_values['sgtin'] = reel_number[:22]
                gui_inputs_values['reelNumManually'] = reel_number[22:26]
            elif printing_format == 'Barcode':
                gui_inputs_values['sgtin'] = ''
                gui_inputs_values['reelNumManually'] = reel_number
            else:
                raise Exception(f'printing_format is not supported: {printing_format}')
            read_only = True
        else:
            gui_inputs_values['sgtin'] = ''
            gui_inputs_values['reelNumManually'] = ''
            read_only = False

    param_dict = {
        'p_format_txt': {'value': str(printing_format), 'widget_type': 'label'},
        'passJobName': {'text': 'Job to print for pass:', 'value': PRINT_FORMAT_TO_PASS_JOB_NAME[printing_format],
                        'widget_type': 'combobox', 'options': PRINT_JOB_OPTIONS},
    }

    if printing_format == 'prePrint':
        scan_str = 'place the first tag BEFORE the coupler and scan it'
        param_dict['firstFullExternalId'] = {'text': scan_str, 'value': ''}
    else:
        param_dict['firstPrintingValue'] = {'text': 'First counter number',
                                            'value': 0000 if read_only else gui_inputs_values['firstPrintingValue']}
        param_dict['reelNumManually'] = {'text': 'Reel number', 'value': gui_inputs_values['reelNumManually']}

    if printing_format == 'SGTIN':
        param_dict['sgtinNumManually'] = {'text': 'SGTIN number', 'value': gui_inputs_values['sgtin']}

    param_dict['-OUTPUT-'] = {'value': '', 'widget_type': 'label', 'options': {'font': FONT_TXT_WARNING},
                              'columnspan': 2}
    param_dict['check_first_print'] = {'value': 'Check first print', 'widget_type': 'button'}
    param_dict['reel_location'] = {'value': 'Tag Reel Location: {}'.format(gui_inputs_values['tag_reel_location']),
                                   'widget_type': 'label'}

    wg = WiliotGui(params_dict=param_dict, parent=parent, do_button_config=False, title='Printing SGTIN Window')
    if read_only:
        wg.update_widget(widget_key='firstPrintingValue',
                         disabled=True)
        if 'sgtinNumManually' in param_dict:
            wg.update_widget(widget_key='sgtinNumManually', disabled=True)

    wanted_v, wanted_is_ok = printing_process_of_test_and_sgtin(wg, printing_format, gui_inputs_values, new_run)

    return wanted_v, wanted_is_ok, new_run


def get_validation_data_for_scanning(parent=None):
    params_dict = {'file_path': {'text': 'You selected scanning without printing.\n'
                                         'Please select a file for scanning validation',
                                 'value': '', 'widget_type': 'file_input'}}
    wg = WiliotGui(params_dict=params_dict, parent=parent, title='Scanning Validation File')
    user_out = wg.run()
    file_path = user_out['file_path']
    if not file_path:
        raise Exception('no file was selected for scanning without printing')
    if not os.path.isfile(file_path):
        raise Exception(f'The specified file does not exist: {file_path} for scanning without printing')
    df = pd.read_csv(file_path)
    if not {'tag_run_location', 'external_id'}.issubset(df.keys()):
        raise Exception(f'The specified file: {file_path} for scanning without printing '
                        f'MUST contains the following columns: tag_run_location, external_id')
    df = df[['tag_run_location', 'external_id']]
    df.drop_duplicates('tag_run_location', inplace=True)
    df.reset_index(inplace=True)
    if pd.isnull(df['external_id']).all():
        raise Exception(f'The specified file: {file_path} for scanning without printing has empty external_id column')
    if pd.Series(df['tag_run_location'] - df.index != df['tag_run_location'].iloc[0]).any():
        raise Exception(f'The specified file: {file_path} for scanning without printing has missing locations, '
                        f'please select a file with one external id per location')
    return df


def save_screen(tested, passed, yield_, missing_labels, ttfp_avg, ttfp_max_error=1, responded=None):
    """
    open last GUI
    :type tested: int
    :param tested: amount of tested tags
    :type passed: int
    :param passed: amount of passed tags
    :type yield_: float
    :param yield_: yield in the run
    :type missing_labels: int
    :param missing_labels: amount of missing_labels tags
    :type ttfp_avg: float or None
    :param ttfp_avg: average of ttfp (time to first good packet) in this run
    :return dictionary with the user inputs (should upload, last comments)
    """

    if ttfp_avg is None or str(ttfp_avg) == 'nan':
        ttfp_avg_str = ''
        ttfp_avg_color = 'black'
    elif ttfp_avg < ttfp_max_error:
        ttfp_avg_str = f'Average time to first good packet is OK ({round(ttfp_avg, 4)} secs)'
        ttfp_avg_color = 'green'
    else:
        ttfp_avg_str = f'Average time to first good packet is too high ({round(ttfp_avg, 4)} secs)'
        ttfp_avg_color = 'red'

    params_dict = {
        'tested': {'value': f'Tags tested = {tested}', 'widget_type': 'label', 'group': 'Run Statistics'},
        'responded': {'value': f'Tags responded = {responded if responded is not None else 0}', 'widget_type': 'label',
                      'group': 'Run Statistics'},
        'passed': {'value': f'Tags passed = {passed}', 'widget_type': 'label', 'group': 'Run Statistics'},
        'yield': {'value': f'Yield = {round(yield_, 2)}%', 'widget_type': 'label', 'group': 'Run Statistics'},
        'missing': {'value': f'Missing labels = {missing_labels}', 'widget_type': 'label', 'group': 'Run Statistics'},
        'ttfp_avg': {'value': ttfp_avg_str, 'widget_type': 'label', 'group': 'Run Statistics'},
        'upload': {'text': 'Would you like to upload this log to the cloud?', 'value': ('Yes', 'No')},
        'comments': {'text': 'Post run comments:', 'value': ''},
    }

    wg = WiliotGui(params_dict=params_dict, exit_sys_upon_cancel=False, title='Offline Run')
    wg.update_widget(widget_key='ttfp_avg', color=ttfp_avg_color)
    wg.layout.attributes('-topmost', True)  # pop window up
    wg.layout.attributes('-topmost', False)  # allow user to move wind if needed
    values = wg.run()
    if values is None:
        print("user exited the program, upload did not happen")
        values = {'upload': 'No', 'comments': ''}

    return values


def get_reel_name_from_cloud_api(env, owner_id, printing_format='SGTIN', gen='Gen2'):
    """
    API to receive reel number from cloud (should use it to avoid duplications).
    :return: the reel number (in 0x)
    """
    assert ('testerStationName' in os.environ), 'testerStationName is missing from PC environment variables'
    tester_station_name = os.environ['testerStationName']

    try:
        g = GetApiKey(gui_type='ttk', env=env, owner_id=owner_id)
        api_key = g.get_api_key()
        client = ManufacturingClient(api_key=api_key, logger_=logging.getLogger().name, env=env)
        payload = {"printerId": tester_station_name}
        reel_id_3_char = printing_format == "Barcode"
        n_tries = 0
        while True:
            n_tries += 1
            try:
                reel_id = client.get_reel_id(owner_id, payload, reel_id_3_char, gen)
                return reel_id
            except Exception as e:
                if '409' in e.__str__() and n_tries < 3:
                    print(f'got reel id cloud error 409 - internal conflict, trying again {n_tries}/3...')
                    time.sleep(1)
                else:
                    raise e

    except Exception as e:
        raise Exception(f"An exception occurred at get_reel_name_from_cloud_API: {e}")


"""
    R2R Arduino
"""

ARDUINO_BAUD_RATE = 1000000


class R2rGpio(object):
    """
    class to open and use communication to Arduino on R2R machine
    """

    def __init__(self, logger_name=None):
        """
        initialize params and port
        """
        self.baud_rate = ARDUINO_BAUD_RATE
        self.comport = ''
        self.s = None
        self.connected = False
        self.logger = logging.getLogger(logger_name) if logger_name is not None else None
        ports_list = serial_ports()
        if len(ports_list) == 0:
            raise Exception("no serial ports were found. please check your connections")
        self.connect(ports_list)

    def is_connected(self):
        if self.s is None:
            return False

        if not self.s.isOpen():
            return False

        response = self.query("*IDN?")

        if "Williot R2R GPIO" in response:
            self.connected = True
            if self.logger is None:
                print('R2R: Found ' + response + " Serial Number " + self.query("SER?"))
            else:
                self.logger.info('R2R: Found ' + response + " Serial Number " + self.query("SER?"))
            self.s.flushInput()
            return True
        else:
            self.s.close()
            return False

    def connect(self, ports_list):
        for port in ports_list:
            try:
                self.comport = port
                self.s = serial.Serial(self.comport, self.baud_rate, timeout=0, write_timeout=0)

                if self.is_connected():
                    break

            except (OSError, serial.SerialException):
                pass
            except Exception as e:
                if self.logger is None:
                    print(e)
                else:
                    self.logger.warning(f'R2R: connect: {e}')
        if not self.connected:
            raise Exception('Could NOT connect to the Arduino, please check connections')

    def __del__(self):
        if self.s is not None:
            self.s.close()

    def write(self, cmd):
        """
        Send the input cmd string via COM Socket
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()

        try:
            self.s.flushInput()
            self.s.write(str.encode(cmd))
        except Exception:
            pass

    def query(self, cmd):
        """
        Send the input cmd string via COM Socket and return the reply string
        :return: massage from arduino (w/o the '\t\n')
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()
            time.sleep(1)
        self.s.flushInput()
        time.sleep(1)
        try:
            self.s.write(str.encode(cmd))
            time.sleep(2)
            data = self.s.readlines()
            value = data[0].decode("utf-8")
            # Cut the last character as the device returns a null terminated string
            value = value[:-2]
        except Exception:
            value = ''
        return value

    def read(self):
        """
        Send the input cmd string via COM Socket and return the reply string
        :return: massage from arduino (w/o the '\t\n')
        """
        if self.s.isOpen():
            pass
        else:
            self.s.open()
        try:
            timeout = time.time() + 5  # 5 second to receive arduino pulse
            while self.s.in_waiting == 0 and time.time() < timeout:
                pass
            if time.time() > timeout:
                logging.warning('No data received from Arduino')
                self.reconnect()

            data = self.s.readlines()
            self.s.flushInput()
            value = data[0].decode("utf-8")
            # Cut the last character as the device returns a null terminated string
            value = value[:-2]
        except Exception:
            value = ''
        return value

    def gpio_state(self, gpio, state):
        """
        gets the gpio state:
            my_gpio.gpio_state(3, "ON")
               start"on"/stop"off"
            my_gpio.gpio_state(4, "ON")
               enable missing label
        :param gpio: what gpio to write to
        :param state: to what state to transfer (ON / OFF)
        :return: reply from Arduino
        """
        cmd = 'GPIO' + str(gpio) + "_" + state
        replay = self.query(cmd)
        return replay

    def pulse(self, gpio, pulse_duration_ms):
        """
        send a pulse to the r2r machine:
            my_gpio.pulse(1, 1000)
               Pass
            my_gpio.pulse(2, 1000)
               fail
        :param gpio: what gpio to write to
        :param pulse_duration_ms: how long is the pulse
        :return: True if succeeded, False otherwise
        """
        cmd = 'GPIO' + str(gpio) + '_PULSE ' + str(pulse_duration_ms)
        self.write(cmd)
        time.sleep(pulse_duration_ms * 2 / 1000)
        replay = self.read()
        if replay == "Completed Successfully":
            return True
        else:
            return False

    def reconnect(self):
        if self.is_connected():
            logging.info(f'Already connected to Arduino on {self.comport}')
            return True
        try:
            # Attempt to open a connection to the specified comport
            self.s = serial.Serial(self.comport, self.baud_rate, timeout=0, write_timeout=0)
            logging.info(f'Connection to Arduino on {self.comport} reestablished.')
            reconnect_success = True

        except serial.serialutil.SerialException:
            logging.warning(
                f'Connection to {self.comport} failed. Attempting to close the connection and detect Arduino...')
            try:
                self.s.close()
                time.sleep(1)
                self.s = serial.Serial(self.comport, self.baud_rate, timeout=0, write_timeout=0)
                logging.info(f'Connection to Arduino on {self.comport} reestablished.')
                reconnect_success = True

            except Exception as e:
                logging.warning(f"Failed to close connection to {self.comport} {e} - Please restart connection")
                return False

        if reconnect_success:

            if self.is_connected():
                logging.info(
                    'Connection was reestablished on COM{} with version {}'.format(self.comport, self.query("SER?")))
                self.s.flushInput()
            else:
                self.s.close()
                logging.warning(f"Failed to close connection to {self.comport} - Please restart connection")
                reconnect_success = False
        return reconnect_success


if __name__ == '__main__':
    # vals = save_screen(tested=100, passed=99, responded=102, yield_=99.54682, ttfp_avg=1.23, missing_labels=0)
    # open_session(['Hi', 'Bye'])
    # f = get_validation_data_for_scanning()
    # s = printing_test_window()
    # a = printing_sgtin_window(env='test', owner_id='wiliot-ops', printing_format='SGTIN', gen='gen3')
    # rsp = get_reel_name_from_cloud_api(env='test', owner_id='wiliot-ops', printing_format='SGTIN', gen='Gen3')

    v = open_session(['Single Band', 'Dual Band'])
    b = printing_test_window()
    c = printing_sgtin_window(env='test', printing_format='Barcode')
    d = printing_sgtin_window(env='test', printing_format='SGTIN')

    r = R2rGpio()
    open_session(['Single Band', 'Dual Band'])
    pass
