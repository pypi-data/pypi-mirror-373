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

from shutil import copyfile
from os import makedirs
try:
    import pygubu
    from tkinter import Tk, Toplevel
    from os.path import join, abspath, dirname, isfile, isdir
except Exception as e:
    print(f'could not import tkinter or pygubu: {e}')
from json import dump, load
from wiliot_core import WiliotDir
from wiliot_testers.utils.get_version import get_version

TESTER_NAME = 'sample'
VER = get_version()
MEASURED = {'button': 'Measured', 'label': '[meter]'}
MANUAL = {'button': 'Manual', 'label': '[db]'}
DEFAULT_EMULATED_SURFACE = 'no simulation'

wiliot_dir = WiliotDir()
wiliot_dir.create_tester_dir(TESTER_NAME)
sample_test_dir = wiliot_dir.get_tester_dir(TESTER_NAME)
OUTPUT_DIR = abspath(join(sample_test_dir, 'logs'))
CONFIGS_DIR = abspath(join(sample_test_dir, 'configs'))
if not isdir(abspath(join(OUTPUT_DIR))):
    makedirs(abspath(join(OUTPUT_DIR)))
if not isdir(abspath(join(CONFIGS_DIR))):
    makedirs(abspath(join(CONFIGS_DIR)))


class ConfigsGui(object):
    is_gui = False
    atten_cur_mode = MANUAL
    test_config = ''
    config = ''
    configs_test = {}
    paramDict = {}
    defaultConfigsDict = {}
    default_surfaces = {}
    all_configs_fields = []
    builder = None
    ttk = None
    mainwindow = None
    
    def __init__(self, top_builder=None, tk_frame=None):
        self.top_builder = top_builder
        self.tk_frame = tk_frame
        self.config_path = abspath(join(dirname(__file__), 'configs', '.default_test_configs.json'))
        if isfile(self.config_path):
            with open(self.config_path, 'r') as jsonFile:
                self.configs_test = load(jsonFile)
                if len(self.configs_test):
                    self.all_configs_fields = list(self.configs_test[next(iter(self.configs_test))].keys())
            self.fix_antenna_type()

        with open(abspath(join(dirname(__file__), 'configs', '.default_surfaces.json')), 'r') as jsonFile:
            self.default_surfaces = load(jsonFile)

        tests_suites_path = abspath(join(dirname(__file__), 'configs', 'tests_suites.json'))
        if isfile(tests_suites_path):
            with open(tests_suites_path, 'r') as jsonFile:
                tests_suites = load(jsonFile)
                for k in tests_suites.keys():
                    test_time = 0
                    for t in tests_suites[k]['tests']:
                        test_time += (t.get('maxTime', 0) + t.get('delayBeforeNextTest', 0))
                    tests_suites[k] = {**tests_suites[k], **{'isTestSuite': True, 'testTime': test_time}}
                self.configs_test = {**self.configs_test, **tests_suites}

        self.copy_config_file()

    def copy_config_file(self):
        copyfile(self.config_path, abspath(join(CONFIGS_DIR, f'.default_test_configs(ViewOnly)_{VER}.json')))

    def gui(self):
        self.builder = builder = pygubu.Builder()
        ui_file = abspath(join(abspath(dirname(__file__)), 'utils', 'configs.ui'))
        self.builder.add_from_file(ui_file)
        
        img_path = abspath(join(abspath(dirname(__file__)), ''))
        builder.add_resource_path(img_path)
        img_path = abspath(join(abspath(dirname(__file__)), 'utils'))
        builder.add_resource_path(img_path)

        if self.tk_frame is not None:
            self.ttk = Toplevel(self.tk_frame)
        else:
            self.ttk = Tk()

        self.ttk.title("Sample Test Configs")
        
        self.mainwindow = self.builder.get_object('mainwindow', self.ttk)
        
        self.builder.connect_callbacks(self)
        
        self.ttk.protocol("WM_DELETE_WINDOW", self.close_cb)
        self.ttk.lift()
        self.ttk.attributes("-topmost", True)
        self.ttk.attributes("-topmost", False)
        
        self.set_gui_defaults()
        
        self.is_gui = True
        self.ttk.mainloop()
    
    def set_gui_defaults(self):
        temp_dict = self.configs_test
        self.builder.get_object('configsList')['values'] = [key for key, item in temp_dict.items()
                                                            if isinstance(item, dict) and not item.get('isTestSuite', False)]
        if temp_dict.get(self.config) and not temp_dict[self.config].get('isTestSuite', False):
            self.builder.get_object('configsList').set(self.config)
            self.top_builder.tkvariables.get('testTime').set(temp_dict[self.config]['testTime'])
            self.builder.get_object('EmulateSurface')['values'] = tuple(
                self.default_surfaces['EmulateSurface'].keys())
            self.builder.get_object('EmulateSurface').set(DEFAULT_EMULATED_SURFACE)
            self.builder.get_object('antennaType')['values'] = ['TEO', 'TIKI']
            for param, value in temp_dict[self.config].items():
                if self.builder.tkvariables.get(param) is not None:
                    self.builder.tkvariables.get(param).set(value)
                else:
                    pass
        self.builder.get_object('save')['state'] = 'normal'
    
    def fix_antenna_type(self):
        tempDict = self.configs_test
        for config, params in tempDict.items():
            if 'antennaType' in params.keys() and params['antennaType']:
                fixedAntenna = 'TIKI' if params['antennaType'].lower() in ['dual', 'tiki'] else 'TEO'
                self.configs_test[config]['antennaType'] = fixedAntenna

    def is_gui_opened(self):
        return self.is_gui
    
    def get_params(self):
        return self.paramDict
    
    def get_configs(self):
        return self.configs_test
    
    def set_params(self, test_config):
        if test_config not in self.configs_test.keys():
            config_options = list(self.configs_test.keys())
            test_config = config_options[0]
        self.paramDict = self.configs_test[test_config].copy()
        if 'EmulateSurface' in self.configs_test[test_config].keys():
            surface = self.configs_test[test_config]['EmulateSurface']
            self.paramDict['EmulateSurfaceValue'] = self.configs_test[test_config]['EmulateSurfaceValue'] = \
                self.default_surfaces['EmulateSurface'][surface]
        self.top_builder.tkvariables.get('testTime').set(self.paramDict['testTime'])
    
    def set_default_config(self, test_config):
        self.test_config = test_config
        self.config = test_config

    def config_set(self, config):
        self.config = config
        self.set_params(config)
        if self.is_gui:
            self.builder.get_object('configsList').set(config)
            self.set_gui_defaults()
        # except BaseException:
        #     pass

    # ############## GUI Callbacks  #######################

    def choose_antenna_type_cb(self, *args):
        antenna = self.builder.tkvariables.get('antennaType').get()
        antenna = 'TIKI' if antenna.lower() in ['dual', 'tiki'] else 'TEO'
        self.builder.tkvariables.get('antennaType').set(antenna)

    def reset_cb(self):
        self.configs_test.update(self.defaultConfigsDict)
        self.set_gui_defaults()

    def atten_mode_cb(self):
        self.atten_cur_mode = MEASURED if self.atten_cur_mode == MANUAL else MANUAL
        self.builder.tkvariables.get('atten_mode').set(self.atten_cur_mode['button'])
        ble_label = self.builder.tkvariables.get('attenBleLabel')
        ble_label.set(ble_label.get().split()[0] + ' ' + self.atten_cur_mode['label'])
        lora_label = self.builder.tkvariables.get('attenLoRaLabel')
        lora_label.set(lora_label.get().split()[0] + ' ' + self.atten_cur_mode['label'])

    def close_cb(self):
        self.is_gui = False
        self.ttk.destroy()

    def save_cb(self):
        self.config = config = self.builder.get_object('configsList').get()
        if config == '':
            return

        if config not in self.configs_test.keys():
            self.configs_test[config] = {}
        
        if self.configs_test[config].get('isTestSuite', False):
            print('please edit test suite parameters using the json file directly')
            return
        
        for param in self.all_configs_fields:
            value = self.builder.tkvariables.get(param)
            if value is not None:
                self.configs_test[config][param] = value.get()
        self.builder.get_object('configsList')['values'] = [key for key, item in self.configs_test.items()
                                                            if isinstance(item, dict)]
        self.top_builder.get_object('test_config')['values'] = [key for key, item in self.configs_test.items()
                                                                if isinstance(item, dict)]
        self.top_builder.get_object('test_config').set(config)

        with open(self.config_path, 'w+') as jsonFile:
            dump(self.configs_test, jsonFile, indent=4)
        self.copy_config_file()

        self.set_params(config)
        print(f'{config} configuration saved successfully.')

    def config_select_cb(self, *args):
        self.config = config = self.builder.get_object('configsList').get()
        self.builder.get_object('save')['state'] = 'normal'
        if config and self.configs_test[config].get('isTestSuite', False):
            self.builder.get_object('save')['state'] = 'disabled'
        self.top_builder.get_object('test_config').set(config)
        self.reset_cb()
