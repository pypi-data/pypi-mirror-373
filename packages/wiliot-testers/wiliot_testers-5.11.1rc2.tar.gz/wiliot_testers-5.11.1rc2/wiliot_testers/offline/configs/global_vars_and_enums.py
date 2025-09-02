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

ASTERISK = ''.join(['*'] * 10)


# Configurations and Enums for offline_main.py
class MainDefaults:
    # GUI
    FONT_NAME = 'SansSerif'
    FONT_SIZE = 10
    GUI_UPDATE_TIME = 500  # ms
    DEFAULT_LANGUAGE = 'En'  # Default to English
    PRINTING_GUI_TYPE = ['SGTIN', 'Barcode', 'prePrint']

    # Modules handler
    MAX_QUEUE_SIZE = 100

    # calculation
    CALCULATE_INTERVAL = 10
    CALCULATE_ON = 50
    N_YIELD_SAMPLES_UNDER_THRESHOLD = 15
    MAX_TTFP_ERROR = 2  # if ttfp avg is more than MAX_TTFP_ERROR, the summary window will be red
    MAX_FILE_SIZE = 12 * 10 ** 6  # 12 Mb


# Configurations for offline_printing_and_validation.py
class PrintingAndValidationDefaults:
    # module handlers
    FIRST_TAG_RUN_LOCATION = 0  # first tag run location
    QUEUE_VALIDATION_OFFSET = 1  # queue size offset when no scanner is connected
    EVENT_WAIT_TIME = 20  # the max time to wait for an event
    MIN_WAIT_TIME = 2  # time to wait for post run validation validation if stop is set
    MAX_MAIN_STATES = 80

    # Printer and printing
    PRINTER_SOCKET_TIMEOUT = 1  # seconds
    PRINTER_ACK_TIMEOUT = 1.5  # seconds max time we allow to get ack from printer
    TIME_BTWN_PRINTER_REQUESTS = 0.25  # seconds
    FAIL_JOB_NUM = 1  # line number for fail job
    PASS_JOB_NUM = 2  # line number for pass job
    PASS_MIRROR_JOB_NUM = 3  # line number for pass mirrored job
    TAG_COUNT_SIZE = 4  # number of characters per tag count inside the external id

    # Printer Cart:
    PRINTER_90_DEG_WAIT_TIME = 2  # time to wait for the printer if NOT printing during movement
    PRINTER_FORWARD_MSG = 'high-to-low'
    PRINTER_BACKWARD_MSG = 'low-to-high'

    # scanner
    SCANNER_GOOD_READ_TIMEOUT = 1.5  # seconds max time we allow to validate scanner
    TRIGGER_TYPE = 5  # relevant only for Cognex, 5: Continuous (external)
    MAX_REEL_ID = 2 # relevant only for preprint
    BLACK_SQUARE_TOLERANCE = 3  # number of black square readings to assume it is a black square

    # r2r
    ARDUINO_BAUD_RATE = 1000000
    PASS_PULSE_GPIO = 1
    FAIL_PULSE_GPIO = 2
    START_STOP_GPIO = 3
    DIRECTION_GPIO = 5  # 0 regular run (left to right) 1 rewind (right to left)
    MISSING_LABEL_GPIO = 4
    R2R_PULSE_DURATION = 50  # ms
    MAX_R2R_WAIT_TIME = 90  # being on the safe side since r2r can wait max 99 seconds
    R2R_START_OFFSET = 1  # When starting run then its starting from 1 and not 0

    # Bendurance
    BENDURANCE_START_STOP_GPIO = 4
    BENDURANCE_GW_TRIGGER = 3


# Configurations for offline_tag_testing.py
class TagTestingDefaults:
    # missing label:
    TIMEOUT_FOR_MISSING_LABEL = 5
    ENABLE_MISSING_LABEL = False
    MAX_MISSING_LABEL_ENGINEERING = 30

    # unique testing modes:
    TIME_BETWEEN_TEST_PRINTING = 3  # timeout when do printing calibration with no RF testing
    POST_RUN_WAIT_TIME = 5  # relevant only if GW control R2R: timeout for post run validation validation if stop is set

    # GPIO and R2R
    R2R_PULSE_DURATION = 50  # relevant only if GW control R2R: milliseconds
    MAX_R2R_WAIT_TIME = PrintingAndValidationDefaults.MAX_R2R_WAIT_TIME
    EVENT_WAIT_TIME = 5  # relevant only if GW control R2R: time to wait till printing and validation are done
    START_STOP_GPIO = 'P0.31'  # relevant only if GW control R2R
    PASS_PULSE_GPIO = 'P0.29'  # relevant only if GW control R2R
    FAIL_PULSE_GPIO = 'P0.30'  # relevant only if GW control R2R
    MISSING_LABEL_GPIO = 'P1.00'  # relevant only if GW control R2R
    PRINTER_DIRECTION_GPIO = 'P1.09'  # relevant only if GW control R2R
    DIRECTION_GPIO = ''  # relevant only if GW control R2R - unsupported pin

    # Printer Cart
    PRINTER_SIGNAL_TIMEOUT = 1  # sec, max time to get ack from the printer cart that it completed its movement
    PRINTER_SIGNAL_SLEEP_TIME = 0.100  # sec, time between gw responses check
