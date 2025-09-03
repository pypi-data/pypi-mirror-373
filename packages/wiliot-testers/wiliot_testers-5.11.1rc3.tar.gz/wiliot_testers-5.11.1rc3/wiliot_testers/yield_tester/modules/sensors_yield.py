"""
Copyright (c) 2016- 2024, Wiliot Ltd. All rights reserved.

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
import time

from wiliot_tools.test_equipment.test_equipment import YoctoSensor


SENSORS_MEAS_TIME = 0.300
ALL_SENSORS = ['temperature', 'humidity', 'light_intensity']


class SensorsYield(object):
    def __init__(self, stop_event, logger, sensors_type=None):

        self.main_sensor = None
        self.logger = logger
        self.stop = stop_event
        sensors_type = ALL_SENSORS if sensors_type is None else sensors_type
        self.sensor_vals = {k: float('nan') for k in sensors_type}
        self.setup_sensors()

    def read_sensors_values(self):
        if not self.main_sensor:
            return
        for k in self.sensor_vals.keys():
            if k == 'temperature':
                val = self.main_sensor.get_temperature()
            elif k == 'humidity':
                val = self.main_sensor.get_humidity()
            elif k == 'light_intensity':
                val = self.main_sensor.get_light()
            else:
                raise Exception(f'unsupported sensors type: {k}')
            self.sensor_vals[k] = val

    def setup_sensors(self):
        try:
            self.main_sensor = YoctoSensor(self.logger)
            self.logger.info('sensors are connected')
        except Exception as ee:
            self.main_sensor = None
            self.logger.info(f'No sensor is connected ({ee})')

    def is_sensor_enable(self):
        return self.main_sensor is not None

    def run(self):
        """
        Receives available data then counts and returns the number of unique advas.
        """
        while not self.stop.is_set():
            try:
                self.read_sensors_values()
                time.sleep(SENSORS_MEAS_TIME)
            except Exception as e:
                self.logger.warning(f'got exception during sensors run: {e}')
        
        self.logger.info('Stop SensorYield run')
        self.stop_sensors()

    def get_sensors_data(self):
        return self.sensor_vals
    
    def stop_sensors(self):
        if self.main_sensor:
            self.main_sensor.exit_app()
