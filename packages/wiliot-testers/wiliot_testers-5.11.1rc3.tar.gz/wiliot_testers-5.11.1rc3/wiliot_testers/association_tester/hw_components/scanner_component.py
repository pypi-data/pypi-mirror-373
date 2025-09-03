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

import logging
import time

from wiliot_tools.test_equipment.test_equipment import CognexDataMan
from wiliot_core.utils.utils import enable_class_method

MIN_TIME_TO_READ = 0.200  # seconds

class Scanner(object):
    def __init__(self, max_test_time=10.0, logger_name=None, n_codes=0, enable=True):
        self.max_test_time = float(max_test_time)
        self.n_codes = n_codes
        self.enable = enable
        # connect to scanner
        self.scanner = CognexDataMan(log_name=logger_name, enable=enable)
        self.logger = logging.getLogger(self.scanner.logger.name)
        if not self.scanner.connected:
            raise Exception('Could not connect to Cognex. please check connection and other app usage')
        self.scanner.reset()
        # TODO add here config to upload cognex file
        self.logger.info(f'Scanner init with max time: {self.max_test_time}, n codes: {self.n_codes}')

    @enable_class_method()
    def scan(self) -> list:
        self.scanner.send_command('TRIGGER ON')
        scanned_codes = self.scanner.read_batch(n_msg=self.n_codes, wait_time=self.max_test_time)
        if not scanned_codes:
            self.scanner.send_command('TRIGGER OFF')
            time.sleep(0.200)
            scanned_codes = self.scanner.read_batch(n_msg=self.n_codes, wait_time=MIN_TIME_TO_READ)

        for new_scanned in scanned_codes:
            self.logger.info(f'scanned new code: {new_scanned}')
        self.scanner.reset()
        return scanned_codes

    @enable_class_method()
    def disconnect(self) -> None:
        if self.scanner.is_open():
            self.scanner.trigger_off()
            time.sleep(MIN_TIME_TO_READ)
            self.scanner.close_port()

    @enable_class_method()
    def reconnect(self) -> None:
        self.scanner.reconnect()
