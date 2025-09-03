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
import json
from pathlib import Path

from wiliot_core import WiliotDir
from wiliot_testers.utils.get_version import get_version

TESTER_NAME = 'failure_analysis'
VER = get_version()

wiliot_dir = WiliotDir()
wiliot_dir.create_tester_dir(TESTER_NAME)
FA_TEST_DIR = Path(wiliot_dir.get_tester_dir(TESTER_NAME))
TIME_NOW = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
CONFIGS_DIR = FA_TEST_DIR / 'configs'
CONFIGS_DIR.mkdir(exist_ok=True)
CONFIG_FILE = CONFIGS_DIR / 'config.json'
RELAY_CONFIG = {
    'LORA': '0000',
    'BLE': '0100',
    'TX': '1100',
    'VDD_CAP': '1110',
    # 'LC': '1111',
}
single_config = {'start_current_uA': -200,
                 'stop_current_uA': 200,
                 'voltage_limit_V': 2,
                 'delay_us': 10000,
                 'samp_interval_us': 100000,
                 'num_points': 81}

default_config = {field: single_config.copy()
                  for field in RELAY_CONFIG.keys()}
default_config['visa_addr'] = 'USB0::10893::46081::MY61390379::0::INSTR'
default_config['reference_path'] = ''
default_config['compare_threshold_percent'] = 10
default_config['VDD_CAP']['stop_current_uA'] = 0


def load_config():
    if CONFIG_FILE.is_file():
        with open(CONFIG_FILE, 'r') as jsonFile:
            test_config = json.load(jsonFile)
        for key in default_config.keys():
            if key not in test_config:
                test_config[key] = default_config[key]
            if isinstance(test_config[key], dict):
                for inner_key in default_config[key].keys():
                    if inner_key not in test_config[key]:
                        test_config[key][inner_key] = default_config[key][inner_key]

    else:
        test_config = default_config

    save_config(test_config)
    return test_config

def save_config(test_config):
    with open(CONFIG_FILE, 'w') as jsonFile:
        json.dump(test_config, jsonFile, indent=4)
