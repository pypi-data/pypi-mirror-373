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

from wiliot_testers.offline.configs.global_vars_and_enums import TagTestingDefaults
from wiliot_core import WiliotGateway


class TadbikR2rController():
    def __init__(self, gw_name=None):
        """Initialize the controller and its components."""
        self.cleanup_done = False
        self.GwObj = WiliotGateway(auto_connect=True, logger_name='root', device_name=gw_name)
        self.configure_gateway()
        logging.info("tadbikR2rController initialized.")

    def configure_gateway(self):
        """Configure the gateway with initial settings."""
        try:
            self.GwObj.reset_gw()
            if not self.GwObj.is_gw_alive():
                time.sleep(5)
            self.GwObj.config_gw(energy_pattern_val=18, time_profile_val=[0, 15],
                                 pl_delay_val=0, start_gw_app=False, with_ack=True)
            self.GwObj.write('!pl_gw_config 1')  # Enable production line trigger
        except Exception as e:
            logging.error(f"Error configuring gateway: {e}")
            raise

    def __enter__(self):
        """Enter method for context management."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Cleanup resources on exit."""
        if not self.cleanup_done:
            self.cleanup()
        if exc_type:
            logging.error(f"Exception occurred: {exc_value}")
        return False  # To propagate exceptions, if any

    def cleanup(self):
        """Clean up resources."""
        self.stop()
        self.GwObj.exit_gw_api()
        self.cleanup_done = True
        logging.info("Resources cleaned up.")

    def stop(self):
        self.GwObj.gpio_state(gpio=TagTestingDefaults.START_STOP_GPIO, state='OFF')

    def start(self):
        self.GwObj.gpio_state(gpio=TagTestingDefaults.START_STOP_GPIO, state="ON")

    def failed(self):
        self.GwObj.pulse(gpio=TagTestingDefaults.FAIL_PULSE_GPIO, pulse_duration_ms=50)

    def passed(self):
        self.GwObj.pulse(gpio=TagTestingDefaults.PASS_PULSE_GPIO, pulse_duration_ms=50)

    def set_missing_label_state(self, state="ON"):
        self.GwObj.gpio_state(gpio=TagTestingDefaults.MISSING_LABEL_GPIO, state=state)

    def toggle_direction(self, direction='backward'):
        state = 'ON' if direction == 'backward' else 'OFF'
        self.GwObj.gpio_state(gpio=TagTestingDefaults.PRINTER_DIRECTION_GPIO, state=state)

    def restart(self):
        self.stop()
        self.start()

    def is_r2r_moved(self):
        gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW", read_timeout=1)
        if gw_answer == '':
            return False
        else:
            self.GwObj.write('!cancel', with_ack=True)
            return True

    def rewind(self, max_missing_labels=6, num_tags=0):
        """
        Rewind the reel with given parameters.

        :param max_missing_labels: Maximum number of missing labels before stopping the rewind.
        :param num_tags: The number of tags to rewind through.
        :raises ValueError: If max_missing_labels is not positive.
        """
        if max_missing_labels <= 0:
            raise ValueError(f"max missing labels must be bigger than zero, got {max_missing_labels}")

        self._start_rewind_process()
        try:
            missing_labels_stop = self._process_rewind_loop(max_missing_labels, num_tags)
            if missing_labels_stop:
                self._handle_missing_labels_stop()
        finally:
            self.cleanup()

    def _start_rewind_process(self):
        """Initialize the rewind process."""
        self.GwObj.start_continuous_listener()
        self.restart()
        self.toggle_direction()

    def _process_rewind_loop(self, max_missing_labels, num_tags):
        """Process the main rewind loop."""
        missing_label_counter, tags_counter = 0, 0
        while True:
            self.passed()
            if not self.is_r2r_moved():
                missing_label_counter += 1
                print(f"Missing labels: {missing_label_counter}")
                if missing_label_counter >= max_missing_labels:
                    print(f"Rewind finished after {missing_label_counter} missing labels")
                    return True  # Indicates missing labels stop condition
            else:
                tags_counter += 1
                missing_label_counter = 0
                if num_tags and tags_counter >= num_tags:
                    print(f"Rewind finished after {tags_counter} tags")
                    break
                if tags_counter % 100 == 0:
                    print(f'Rewinding {tags_counter} tags')

    def _handle_missing_labels_stop(self):
        """Handle additional steps if the missing labels stop condition was met."""
        print("Start searching for first tag")
        self.stop()
        self.toggle_direction('forward')
        self.start()
        for _ in range(100):
            if self.is_r2r_moved():
                print("Roll to first tag")
                return
            self.restart()
            self.passed()
        print("Start of reel wasn't found for 100 tags!")


if __name__ == '__main__':
    tadbik_r2r_controller = TadbikR2rController()
    tadbik_r2r_controller.rewind(max_missing_labels=10, num_tags=1000)
    print("Done!")
