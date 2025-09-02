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

from wiliot_testers.offline.modules.offline_r2r_controller import R2R
from wiliot_testers.offline.configs.global_vars_and_enums import ASTERISK


class R2RBendurance(R2R):
    def __init__(self, logger_name, gw_obj=None, exc_obj=Exception):
        """
        @param logger_name:
        @type logger_name: str
        """
        super().__init__(logger_name=logger_name, gw_obj=gw_obj, exc_obj=exc_obj)

    def send_start_to_r2r(self):
        self.logger.info('R2R Bendurance: R2R starts automatically')
        self.is_running = True

    def send_stop_to_r2r(self):
        try:
            self.gpio.gpio_state(self.constant_obj.BENDURANCE_START_STOP_GPIO, "OFF")
            self.logger.info('R2R Bendurance: PC send stop to R2R')
            self.is_running = False
        except Exception as e:
            raise self.exc_obj(f'send_stop_to_r2r: could not stop r2r due to {e}')

    def move_r2r(self, is_pass=False):
        try:
            self.gpio.gpio_state(self.constant_obj.BENDURANCE_START_STOP_GPIO, "ON")
            self.logger.info(f'{ASTERISK} R2R: PC send signal to move to the next tag {ASTERISK}')
            self.counter += 1
        except Exception as e:
            raise self.exc_obj(f'move_r2r: could not move r2r due to {e}')

    def enable_missing_label(self, is_enable):
        pass


if __name__ == '__main__':
    from queue import Queue
    from wiliot_core import WiliotGateway

    N_STEPS = 32

    logger_name = 'root'
    gw_obj = WiliotGateway(auto_connect=True)

    r2r = R2RBendurance(logger_name, gw_obj=gw_obj, exc_obj=Exception)

    r2r.send_start_to_r2r()
    time.sleep(1)
    for i in range(N_STEPS):
        r2r.move_r2r()
        time.sleep(1)
        print(f'move step {i}')
    r2r.send_stop_to_r2r()
    gw_obj.exit_gw_api()
