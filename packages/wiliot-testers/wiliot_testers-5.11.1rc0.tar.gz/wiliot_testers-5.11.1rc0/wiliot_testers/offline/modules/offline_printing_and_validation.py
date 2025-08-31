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

from wiliot_testers.tester_utils import open_json_cache
from wiliot_testers.offline.modules.offline_utils import ConfigDefaults, get_printed_value, \
    get_print_user_config_file, DefaultGUIValues
from wiliot_tools.test_equipment.test_equipment import BarcodeScanner, CognexDataMan
from wiliot_testers.wiliot_tester_tag_result import FailureCodes, WiliotTesterTagResultList
from wiliot_testers.offline.configs.global_vars_and_enums import PrintingAndValidationDefaults, ASTERISK
from wiliot_testers.offline.modules.offline_r2r_controller import R2R
from wiliot_testers.offline.modules.offline_bendurance_r2r_controller import R2RBendurance

import os
import json
import time
import logging
from threading import Event
import datetime
from enum import Enum
from queue import Queue
import socket
import pandas as pd
from typing import Union


class PrintingAndValidationException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(f'PrintingAndValidation Exception: {self.message}')


class PrinterException(PrintingAndValidationException):
    def __init__(self, msg):
        super().__init__(f'Printer: {msg}')


class ScannerException(PrintingAndValidationException):
    def __init__(self, msg):
        super().__init__(f'Scanner: {msg}')


class R2RException(PrintingAndValidationException):
    def __init__(self, msg):
        super().__init__(f'R2R: {msg}')


class ValidationStates(Enum):
    IDLE = 0
    STOP = 99
    WAIT_MOH = 88
    WAIT_START = 81
    WAIT_END = 82
    START_TEST = 1
    PRE_VALIDATION = 2
    VALIDATION = 3
    PRINTER_ACK = 4
    SET_NEXT_PRINT = 5
    END_TEST = 6
    NEXT_TAG = 7
    LOG_DATA = 8
    PRINTER_CART_READY = 9


class ValidatedBin(Enum):
    # even values are good
    UNTESTED = 0  # not tested by the scanner
    PRINT_ACK_ONLY = 2  # got acknowledgement from printer
    MATCH = 4  # ext. id/black square as expected
    # odd values are bad
    REEL_ID_LIMIT_EXCEEDED = 5  # too many reel id changes
    MISMATCH = 3  # ex id/black square not as expected (should be a different ex.id or black square)
    NO_READ = 1  # expect to read ex id, but no success reading it
    ERROR = 99


class PrintingAndValidation(object):
    def __init__(self, test_start_event, test_end_event, validation_end_event, stop_app_event, moh_object, test_object,
                 exception_queue, tag_results_queue, log_obj=None, user_config=None, gw_version='',
                 get_duplicated_tags=None, scanning_data=None, get_gw_signal=None):
        """

        @param test_start_event: event is set when tag is under test
        @type test_start_event: Event
        @param test_end_event: event is set when tag test was completed
        @type validation_end_event: Event
        @param validation_end_event: event is set when validation ends if GW move R2R
        @type test_end_event: Event
        @param moh_object: an object contains all functions related to MOH event, Manual Operation Handling
        @type moh_object: Object
        @param test_object: an object contains all functions related to test parameters
        @type test_object: TestParameters
        @param exception_queue: queue for all exceptions, handled in the main class
        @type exception_queue: Queue
        @param tag_results_queue: queue for tag test results, sent from the tag test class
        @type tag_results_queue: Queue
        @param user_config: all user configuration inputs
        @type user_config: dict or None
        """
        self.test_start_event = test_start_event
        self.test_end_event = test_end_event
        self.validation_end_event = validation_end_event
        self.stop_app_event = stop_app_event
        self.exception_q = exception_queue
        self.tag_results_q = tag_results_queue
        self.end_of_test_tags = []
        self.moh = moh_object
        self.test = test_object
        self.logger = logging.getLogger(log_obj.get_logger_name())
        self.is_print = user_config['toPrint'].lower() == 'yes'
        self.is_preprint = user_config['printingFormat'].lower() == 'preprint'
        self.print_calib = user_config['printingFormat'].lower() == 'test' and user_config['toPrint'].lower() == 'yes'
        self.is_scanner = user_config['QRRead'].lower() == 'yes'
        self.user_config = user_config
        self.is_r2r = user_config['isR2R'].lower() == 'yes' and user_config['typeR2R'].lower() == 'arduino'
        self.get_duplicated_tags = get_duplicated_tags
        self.get_gw_signal = get_gw_signal
        self.change_tag_to_duplicated = []
        self.scanning_data = scanning_data
        self.printer_cart_is_ready = False

        self.last_state = ValidationStates.IDLE
        self.tag_run_location = PrintingAndValidationDefaults.FIRST_TAG_RUN_LOCATION - 1
        self.external_id_counter = 0
        self.printed_pass_counter = 0
        self.tag_result_to_validate = None

        self.is_init = False
        self.r2r = None
        self.r2r_counter_func = None
        try:
            if self.is_r2r:
                if 'bendurance' in user_config.keys() and user_config['bendurance'].lower() == 'yes':
                    self.r2r = R2RBendurance(logger_name=log_obj.get_logger_name(),
                                             exc_obj=R2RException)
                else:
                    self.r2r = R2R(logger_name=log_obj.get_logger_name(),
                                   exc_obj=R2RException)
                self.r2r_counter_func = self.r2r.get_counter
            
            self.printer = Printer(is_print=self.is_print,
                                   exception_queue=exception_queue,
                                   logger_name=log_obj.get_logger_name(),
                                   printing_config=log_obj.get_log_config(),
                                   is_calib=self.print_calib)
            if self.is_print and self.printer.bi_directional:
                self.init_printer_cart()

            self.scanner = Scanner(is_scanner=self.is_scanner,
                                   exception_queue=exception_queue,
                                   logger_name=log_obj.get_logger_name(),
                                   scanning_config=user_config,
                                   is_print=self.is_print,
                                   is_preprint=self.is_preprint)

            self.data_logging = log_obj
            self.data_logging.run_data_init(is_printing=self.is_print, gw_version=gw_version,
                                            test_suite_dict=test_object.get_selected_test_suite())

            self.is_init = True
        except Exception as e:
            if isinstance(e, PrintingAndValidationException):
                self.exception_q.put(f'init: {e}', block=False)
            else:
                self.exception_q.put(PrintingAndValidationException(f'{e}').__str__(), block=False)
            return

        # init Queues
        try:
            self.validation_q = None
            self.init_validation_q()
            self.printing_type_q = None
            self.init_printing_type_q()
        except Exception as e:
            if isinstance(e, PrintingAndValidationException):
                self.exception_q.put(f'init: queues: {e}', block=False)
            else:
                self.exception_q.put(PrintingAndValidationException(f'init: queues: {e}').__str__(), block=False)
            return

        # move to the first tag:
        try:
            if self.is_print:
                if self.printer.bi_directional:
                    gw_signals = self.get_gw_signal()
                    if gw_signals:
                        self.logger.info(f'clean the following gw signals during init: {gw_signals}')
                self.set_next_printing_type(False)
            if self.is_r2r:
                self.r2r.move_to_the_first_tag()
        except Exception as e:
            if isinstance(e, PrintingAndValidationException):
                self.exception_q.put(f'init: move to the first tag: {e}', block=False)
            else:
                self.exception_q.put(PrintingAndValidationException(f'init: move to the first tag: {e}').__str__(),
                                     block=False)
            return

    def get_r2r_counter(self):
        if self.r2r_counter_func is None:
            return 0
        return self.r2r_counter_func()

    def set_r2r_counter_func(self, r2r_counter_func=None):
        self.r2r_counter_func = r2r_counter_func

    def init_validation_q(self):
        if self.is_scanner:
            q_size = self.scanner.scanning_config['QRoffset']
        elif self.is_print:
            q_size = int(self.printer.printing_config['printOffset']) - 1 + \
                     PrintingAndValidationDefaults.QUEUE_VALIDATION_OFFSET
        else:
            q_size = 1  # No validation is needed
        self.validation_q = Queue(maxsize=int(q_size))

    def init_printing_type_q(self):
        offset_printing = 0
        if self.is_print:
            q_size = int(self.printer.printing_config['printOffset']) - 1
            # Since when using gpio and not line selection the pulse selects the next print
            offset_printing = 0 if self.printer.printing_config['enableLineSelection'].lower() == 'yes' else 1
        else:
            q_size = 0  # No Printing is needed
        self.printing_type_q = Queue(maxsize=q_size)
        if q_size == 0:
            return

        status = self.print_calib
        for _ in range(q_size - offset_printing):
            self.printing_type_q.put({'adva': '', 'status': status}, block=False)

    def run(self):
        state = ValidationStates.IDLE
        next_tag_status = False
        self.printer.reset_printer_ack()
        start_test_time = time.time()
        n_skip_location = None
        self.printer_cart_is_ready = False

        while True:
            time.sleep(0)
            try:
                state = self.update_state(state)
                self.logger.info(f'PrintingAndValidation: start state {state}')
                if state == ValidationStates.STOP:
                    self.logger.info('Stop running PrintingAndValidation main loop')
                    break

                elif state == ValidationStates.WAIT_MOH:
                    # wait if Manual Operation Handling is needed:
                    self.wait_for_moh()

                elif state == ValidationStates.WAIT_START:
                    # wait till event start_testing is set
                    self.wait_for_new_event(event=self.test_start_event,
                                            time_to_wait=PrintingAndValidationDefaults.EVENT_WAIT_TIME)

                elif state == ValidationStates.START_TEST:
                    start_test_time = time.time()

                    self.tag_run_location += 1
                    self.logger.info(f'{ASTERISK} PrintingAndValidation: START_TEST: '
                                     f'new tag location {self.tag_run_location} {ASTERISK}')
                    # Stop R2R if long test
                    if self.is_r2r:
                        if self.test.get_total_test_time() > PrintingAndValidationDefaults.MAX_R2R_WAIT_TIME:
                            self.r2r.send_stop_to_r2r()

                elif state == ValidationStates.PRE_VALIDATION:
                    # Validation
                    self.tag_result_to_validate = None
                    if self.validation_q.full() or self.stop_app_event.is_set():
                        n_skip_location, do_skip = self.check_test_end_before_start_validation(n_skip_location)
                        if do_skip:
                            self.logger.info('PrintingAndValidation: PRE_VALIDATION: skip on validation')
                        else:
                            self.tag_result_to_validate = self.validation_q.get(block=False)
                            self.handle_duplication_before_validation()
                            self.add_external_id_to_tag_results()
                    else:
                        self.logger.info('PrintingAndValidation: PRE_VALIDATION: '
                                         'Waiting for the first tag to arrive')
                        if self.is_print and not self.is_scanner and not self.printer.printing_during_movement:
                            is_ack = self.printer.get_printing_ack()
                            if not is_ack:
                                self.logger.warning('pre-validation: printing-only: '
                                                    'did not get printing acknowledgement (PRC), continue anyway')

                elif state == ValidationStates.VALIDATION:
                    if self.tag_result_to_validate is not None:
                        self.validation(self.tag_result_to_validate)
                    elif self.is_preprint:
                        self.validation(None)

                elif state == ValidationStates.PRINTER_ACK:
                    if self.need_to_check_printer_ack():
                        is_ack = self.printer.get_printing_ack()
                        if not is_ack:
                            status = self.printer.get_printer_status(counter=self.get_r2r_counter(), 
                                                                     is_pass=next_tag_status,
                                                                     timeout=0.1)
                            if not status:
                                raise PrinterException('did not get printing acknowledgement (PRC)')

                elif state == ValidationStates.SET_NEXT_PRINT:  # if bi-directional happens only after test end
                    # select next printing type
                    if self.is_print:
                        if self.printing_type_q.empty():
                            self.logger.info(
                                'PrintingAndValidation: SET_NEXT_PRINT: set next printing to False since queue empty')
                            next_tag_status = False if not self.print_calib else True
                            self.logger.info('PrintingAndValidation: SET_NEXT_PRINT: '
                                             'set printing type to false since queue is empty')
                        else:
                            next_tag_to_print = self.printing_type_q.get(block=False)
                            next_tag_status = self.handle_duplication_before_printing(next_tag_to_print)
                        if self.is_print and not self.printer.bi_directional:
                            self.set_next_printing_type(next_tag_status)

                elif state == ValidationStates.WAIT_END:
                    # wait till event end_of_testing is set
                    self.wait_for_new_event(
                        event=self.test_end_event,
                        time_to_wait=self.test.get_total_test_time() + PrintingAndValidationDefaults.EVENT_WAIT_TIME)

                elif state == ValidationStates.END_TEST:
                    # update class queue:
                    if self.tag_results_q.empty():
                        if self.is_print:
                            self.logger.info(f'Empty tag_results_q during {state}')
                            self.add_end_of_test_tags()

                    else:
                        cur_tag_to_print = self.tag_results_q.get(timeout=0.1, block=False)
                        cur_tag_to_print.set_test_info({'tag_run_location': self.tag_run_location,
                                                        'tag_reel_location': self.get_tag_reel_location()})
                        self.validation_q.put(cur_tag_to_print, block=False)
                        if self.is_print:
                            self.printing_type_q.put({'adva': cur_tag_to_print.check_and_get_selected_tag_id(),
                                                      'status': cur_tag_to_print.get_total_test_status()}, block=False)

                elif state == ValidationStates.PRINTER_CART_READY:
                    self.printer_cart_ready_timeout(start_test_time=start_test_time)
                    if self.is_print and self.printer.bi_directional:
                        self.set_next_printing_type(next_tag_status)

                elif state == ValidationStates.NEXT_TAG:
                    # send signal to the r2r to move
                    self.printer.reset_printer_ack()
                    self.printer_cart_is_ready = False
                    if self.is_r2r:
                        self.r2r.move_r2r(is_pass=next_tag_status)
                    else:
                        self.validation_end_event.set()

                elif state == ValidationStates.LOG_DATA:
                    # log data
                    if self.tag_result_to_validate is not None:
                        self.log_data(self.tag_result_to_validate)
                        self.tag_result_to_validate = None

                self.logger.info(f'PrintingAndValidation: end state {state}')
            except Exception as e:
                if isinstance(e, PrintingAndValidationException):
                    self.exception_q.put(f'run: state{state.name}: {e}', block=False)
                else:
                    self.exception_q.put(PrintingAndValidationException(f'run: state{state.name}: {e}').__str__(),
                                         block=False)
                if state == ValidationStates.VALIDATION:
                    if self.tag_result_to_validate is not None:
                        tag_info = self.tag_result_to_validate.get_test_info()
                        if 'validated' not in tag_info or ValidatedBin[tag_info['validated']].value % 2 == 0:
                            self.tag_result_to_validate.set_test_info({'validated': ValidatedBin.ERROR.name})
                            self.tag_result_to_validate.set_total_fail_bin(fail_code=FailureCodes.SOFTWARE_GENERAL_ERROR,
                                                                        overwrite=True)
                            self.logger.warning(f'PrintingAndValidation: run: state{state.name}: '
                                                f'Error during validation: {tag_info}')
                        else:
                            self.tag_result_to_validate.set_total_fail_bin(fail_code=FailureCodes.BAD_PRINTING)

        self.stop()

    def update_state(self, state):
        # after MOH was done, continue to the next state
        if state == ValidationStates.WAIT_MOH:
            state = self.last_state

        # when event occurred
        if self.stop_app_event.is_set():
            if self.validation_q.empty() and self.tag_results_q.empty():
                if state == ValidationStates.LOG_DATA:
                    state = ValidationStates.STOP
                if state == ValidationStates.END_TEST:
                    state = ValidationStates.NEXT_TAG  # skip NEXT_TAG stage since this is the last iteration
        elif self.moh.get_manual_operation_is_needed():
            self.last_state = state
            state = ValidationStates.WAIT_MOH

        # main flow
        if state == ValidationStates.IDLE:
            state = ValidationStates.WAIT_START
        elif state == ValidationStates.WAIT_START:
            state = ValidationStates.START_TEST
        elif state == ValidationStates.START_TEST:
            state = ValidationStates.PRE_VALIDATION
        elif state == ValidationStates.PRE_VALIDATION:
            state = ValidationStates.VALIDATION
        elif state == ValidationStates.VALIDATION:
            state = ValidationStates.PRINTER_ACK
        elif state == ValidationStates.PRINTER_ACK:
            state = ValidationStates.SET_NEXT_PRINT
        elif state == ValidationStates.SET_NEXT_PRINT:
            state = ValidationStates.WAIT_END
        elif state == ValidationStates.WAIT_END:
            state = ValidationStates.END_TEST
        elif state == ValidationStates.END_TEST:
            state = ValidationStates.PRINTER_CART_READY
        elif state == ValidationStates.PRINTER_CART_READY:
            state = ValidationStates.NEXT_TAG
        elif state == ValidationStates.NEXT_TAG:
            state = ValidationStates.LOG_DATA
        elif state == ValidationStates.LOG_DATA:
            state = ValidationStates.WAIT_START
        return state

    def restart_printer_after_moh(self):
        self.printer.init_printer_hw_connection()
        if self.printer.bi_directional:
            self.init_printer_cart()
    
    def init_printer_cart(self):
        if not self.is_print or not self.printer.bi_directional:
            return
        self.printer_cart_is_ready = False
        t_start = time.time()
        dt = 0
        while not self.printer_cart_is_ready and dt < PrintingAndValidationDefaults.PRINTER_90_DEG_WAIT_TIME:
            try:
                self.check_if_printer_cart_ready(t_start)
            except Exception as e:
                self.logger.info(f'init_printer_cart: check_if_printer_cart_ready failed due to {e}, try again')
            self.printer_cart_is_ready = self.printer.current_direction == 'forward'
            dt = time.time() - t_start
        if self.printer.current_direction == 'backward':
            raise PrinterException('restart_printer_after_moh: printer cart is set to the backward direction instead of forward')
        self.printer_cart_is_ready = True
        self.printer.set_printer_direction('forward')
        self.logger.info(f'init_printer_cart: completed successfully')

    def printer_cart_ready_timeout(self, start_test_time):
        dt = 0
        while dt < PrintingAndValidationDefaults.PRINTER_90_DEG_WAIT_TIME:
            try:
                self.check_if_printer_cart_ready(start_test_time)
                break
            except Exception as e:
                self.logger.info(f'init_printer_cart: check_if_printer_cart_ready failed due to {e}, try again')
            dt = time.time() - start_test_time


    def check_if_printer_cart_ready(self, start_test_time):
        if not self.is_print:
            return

        if self.printer.printing_during_movement:
            return

        if self.printer.bi_directional:
            if self.printer_cart_is_ready:
                return
            
            if self.get_gw_signal is None:
                raise PrinterException('check_if_printer_cart_ready: printer is bi-directional but \
                                       get_gw_signal function is not set ')
            
            gw_signals = self.get_gw_signal()

            if len(gw_signals) == 0:
                raise PrinterException('check_if_printer_cart_ready: no signal was received from gateway')
                
            if PrintingAndValidationDefaults.PRINTER_FORWARD_MSG in gw_signals[-1].lower():
                current_gw_signal = 'forward'
            elif PrintingAndValidationDefaults.PRINTER_BACKWARD_MSG in gw_signals[-1].lower():
                current_gw_signal = 'backward'
            else:
                raise PrinterException(f'check_if_printer_cart_ready: invalid gw signal: {gw_signals[-1]}')
            
            if self.printer.current_direction is not None and self.printer.current_direction == current_gw_signal:
                raise PrinterException(f'check_if_printer_cart_ready: cart signal was not toggled in between '
                                       f'locations. still {current_gw_signal}')
            self.printer.set_printer_direction(current_gw_signal)
            self.printer_cart_is_ready = True
            return
        dt = time.time() - start_test_time
        if dt < PrintingAndValidationDefaults.PRINTER_90_DEG_WAIT_TIME:
            time.sleep(PrintingAndValidationDefaults.PRINTER_90_DEG_WAIT_TIME - dt)

    def check_test_end_before_start_validation(self, n_skip_location):
        if self.stop_app_event.is_set():
            if self.validation_q.full():
                n_skip_location = 0
            elif n_skip_location is None:
                n_skip_location = self.validation_q.maxsize - self.validation_q.qsize()

            if n_skip_location > 0:
                n_skip_location -= 1
                return n_skip_location, True
        return n_skip_location, False

    def handle_duplication_before_printing(self, next_tag):
        is_tag_passed = False
        if not next_tag['status']:
            return is_tag_passed

        duplication_list = self.get_duplicated_tags()
        if next_tag['adva'] != '' and next_tag['adva'] in duplication_list:
            self.change_tag_to_duplicated.append(next_tag['adva'])
            self.logger.info(f'changing printing tag {next_tag["adva"]} to fail due to duplication')
            return is_tag_passed

        is_tag_passed = True
        return is_tag_passed

    def handle_duplication_before_validation(self):
        selected_tag = self.tag_result_to_validate.check_and_get_selected_tag_id()
        if selected_tag in self.change_tag_to_duplicated:
            self.tag_result_to_validate.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
            self.logger.info(f'changing tag {selected_tag} to duplication fail bin')

    def need_to_check_printer_ack(self):
        return self.is_print and self.is_scanner and self.printer.printing_config['enablePrinterAck'].lower() == 'yes'

    def add_external_id_to_tag_results(self):
        expected_external_id = ''
        if self.is_preprint:
            expected_external_id = self.scanner.update_reel_counter()
            if not self.tag_result_to_validate.get_total_test_status():
                expected_external_id = ''

        elif self.is_print:
            if self.tag_result_to_validate.get_total_test_status():
                expected_external_id = self.printer.get_expected_external_id(counter=self.external_id_counter)
                self.external_id_counter += 1
        
        if self.is_print:
            self.tag_result_to_validate.set_test_info({'external_id': expected_external_id})
            self.logger.info(f'PrintingAndValidation: assigned external id {expected_external_id}')
        
        return expected_external_id

    def get_validation_q_size(self):
        return self.validation_q.qsize()

    def get_validation_q_maxsize(self):
        return self.validation_q.maxsize

    def get_tag_reel_location(self):
        configs = self.data_logging.get_log_config()
        offset = int(configs['tag_reel_location']) if 'tag_reel_location' in configs.keys() else 0
        return self.tag_run_location + offset

    def update_scanning_results_after_exception(self):
        if not self.is_scanner:
            return ''
        test_info = {'external_id': 'unknown'}
        try:
            test_info = self.tag_result_to_validate.get_test_info() if self.tag_result_to_validate is not None else {'external_id': None}
            self.validation(self.tag_result_to_validate)
            if self.tag_result_to_validate is not None:
                if self.tag_result_to_validate.get_total_fail_bin() == FailureCodes.BAD_PRINTING.value:
                    self.tag_result_to_validate.set_total_fail_bin(fail_code=FailureCodes.PASS, overwrite=True)
        except Exception as e:
            self.logger.warning(f'update_scanning_results_after_exception: {e}')
            return f"Re-Validation for external id {test_info.get('external_id', 'unknown')} Failed: {e}"
        success_str = f"Re-Validation for external id {test_info.get('external_id', 'unknown')} was successful"
        self.logger.info(success_str)
        return success_str

    def set_next_printing_type(self, is_pass):
        """

        @param is_pass:
        @type is_pass: bool or None
        @return:
        @rtype:
        """
        if is_pass is None:
            is_pass = False
        if self.is_print:
            if self.printer.enable_line_selection:
                try:
                    self.printer.set_printing_type(is_tag_passed=is_pass)
                    self.printed_pass_counter += int(is_pass)
                except Exception as e:
                    raise PrinterException(f'set_next_printing_type: {e}')
                self.update_printer_configs()

    def wait_for_new_event(self, event, time_to_wait):
        t_start = datetime.datetime.now()
        while not event.is_set():
            if not self.is_r2r and self.stop_app_event.is_set() and self.user_config['isR2R'].lower() == 'yes':
                self.logger.info('stop application during waiting for event while r2r is controlled by gateway')
            elif self.stop_app_event.is_set():
                self.logger.info('stop application during waiting for event')
                time.sleep(PrintingAndValidationDefaults.MIN_WAIT_TIME)
                break
            elif self.moh.get_manual_operation_is_needed():
                self.wait_for_moh()
                t_start = datetime.datetime.now()
                self.first_cycle_after_moh = True
            event.wait(0.1)
            dt = (datetime.datetime.now() - t_start).total_seconds()

            if dt > time_to_wait and not self.moh.get_manual_operation_is_needed():
                raise PrintingAndValidationException('wait_for_new_event: did not receive ack for '
                                                     'starting/ending tag test')
        event.clear()

    def wait_for_moh(self):
        try:
            if self.is_r2r:
                self.r2r.send_stop_to_r2r()
        except Exception as e:
            self.logger.warning(f'Could not stop R2R during wait for manual operation handling due to {e}')
        self.logger.info('PrintingAndValidation: wait for manual operation handling')
        while True:
            time.sleep(1)
            if not self.moh.get_manual_operation_is_needed():
                break
            if self.stop_app_event.is_set():
                break

    def get_estimated_external_id(self):
        validation_loc = self.tag_run_location - self.get_validation_q_maxsize()
        if validation_loc >= len(self.scanning_data):
            raise Exception('tag location does not exist in the specified file for scanning without printing')
        expected_value = self.scanning_data.iloc[validation_loc]['external_id']
        expected_value = expected_value if not pd.isnull(expected_value) else ''
        return expected_value

    def validation(self, expected_result: Union[WiliotTesterTagResultList, None] = None):
        """

        @param expected_result:
        @type expected_result: WiliotTesterTagResultList
        @return:
        @rtype:
        """
        is_validated = ValidatedBin.UNTESTED
        test_info = {"external_id": ''}
        hw_exc = ''

        if self.is_print and self.is_scanner:
            # scan and compare
            test_info = expected_result.get_test_info() if expected_result is not None else {'external_id': None}
            try:
                is_validated, res_str = self.scanner.validated_scan_data(expected_value=test_info['external_id'], expected_result=expected_result)
                hw_exc = f' [{res_str}]'
            except Exception as e:
                is_validated = ValidatedBin.NO_READ
                hw_exc = f' [{e}]'

        elif self.is_print and not self.is_scanner:
            # get_status from printer
            if not self.printer.printing_during_movement:
                is_ack = self.printer.get_printing_ack()
                if not is_ack:
                    self.logger.warning('printing only - did not get printing acknowledgement (PRC), '
                                        'try to get status anyway')
            assert expected_result is not None, 'expected_result must be provided when printing only'
            status = self.printer.get_printer_status(counter=self.get_r2r_counter(),
                                                     is_pass=expected_result.get_total_test_status())
            if status:
                is_validated = ValidatedBin.PRINT_ACK_ONLY
            else:
                is_validated = ValidatedBin.MISMATCH

        elif not self.is_print and self.is_scanner:
            try:
                expected_value = self.get_estimated_external_id()
                expected_result.set_test_info({'external_id': expected_value})
                test_info["external_id"] = expected_value
                is_validated, res_str = self.scanner.validated_scan_data(expected_value=expected_value)
                hw_exc = f' [{res_str}]'
            except Exception as e:
                is_validated = ValidatedBin.NO_READ
                hw_exc = f' [{e}]'

        else:  # no print and no scanner
            pass
        
        if expected_result is not None:
            expected_result.set_test_info({'validated': is_validated.name})
        if is_validated.value % 2 == 1:
            id_str = f'id: {test_info["external_id"]}' if test_info["external_id"] is not None and test_info["external_id"] != '' else 'black square'
            raise PrintingAndValidationException(
                f'Validation Failed due to: {is_validated} for {id_str}\n{hw_exc}')

    def log_data(self, new_tag_results):
        # update packet data
        self.data_logging.update_packets_data(res=new_tag_results)
        # update run data
        self.data_logging.update_run_data(res=new_tag_results)

    def add_end_of_test_tags(self):
        if self.is_print:
            dummy_dict = {'tag_run_location': self.tag_run_location,
                          'tag_reel_location': self.get_tag_reel_location(),
                          'fail_bin': FailureCodes.END_OF_TEST.value,
                          'fail_bin_str': FailureCodes.END_OF_TEST.name,
                          'trigger_time': None, 
                          'total_test_duration': None,
                          'crc_environment_previous': None,
                          'label_validated': 'UNTESTED'}
            self.end_of_test_tags.append(dummy_dict)

    def add_end_of_test_to_log(self):
        for dummy_tag in self.end_of_test_tags:
            # Update only packet data
            self.data_logging.update_default_test_data(dummy_tag)
            self.data_logging.update_packets_data()

    def update_printer_configs(self):
        if not self.is_print:
            return
        # update printing config:
        configs = self.data_logging.get_log_config()
        file_name = get_print_user_config_file(configs['printingFormat'])
        config_path = os.path.join(self.test.dir_config, file_name)
        data = open_json_cache(folder_path=self.test.dir_config,
                               file_path=config_path,
                               default_values=DefaultGUIValues(configs['printingFormat']).default_gui_values)
        data['firstPrintingValue'] = self.printer.get_expected_external_id(
            counter=self.printed_pass_counter)[-PrintingAndValidationDefaults.TAG_COUNT_SIZE:]
        data['tagLocation'] = str(self.tag_run_location)
        data['tag_reel_location'] = str(self.get_tag_reel_location() +
                                        PrintingAndValidationDefaults.R2R_START_OFFSET)
        with open(config_path, "w") as f:
            json.dump(data, f)

    def stop(self):
        if self.end_of_test_tags:
            self.add_end_of_test_to_log()
        if self.printer.enable:
            self.update_printer_configs()
            self.printer.exit()
        if self.scanner.enable:
            self.scanner.exit()
        if self.is_r2r:
            self.r2r.exit()


class Printer(object):
    def __init__(self, is_print, exception_queue, logger_name, printing_config=None, is_calib=False):
        """

        @param exception_queue:
        @type exception_queue: Queue
        @param logger_name:
        @type logger_name: str
        @param printing_config:
        @type printing_config: dict
        """
        self.exception_queue = exception_queue
        self.logger = logging.getLogger(logger_name)
        self.printing_config = printing_config
        self.got_printer_ack = False
        self.printer_socket = None
        self.enable = True
        if printing_config is None or not is_print:
            self.logger.info('Printer is disable')
            self.enable = False
            return

        self.enable_line_selection = self.printing_config['enableLineSelection'].lower() == 'yes'
        self.printing_during_movement = self.printing_config['printingDuringMovement'].lower() == 'yes'
        self.bi_directional = self.printing_config['printingBidirectionalMovement'].lower() == 'yes'
        self.printing_calib = is_calib
        self.printed_id = 0
        self.current_direction = None
        self.cur_value = 0

        try:
            self.init_printer_hw_connection()
            self.init_printing_protocols()
            self.logger.info('PRINTER: printer is ready after initialization')
        except Exception as e:
            raise PrinterException(f'init: {e}')

    def init_printer_hw_connection(self):
        self.open_printer_socket()
        self.logger.info('PRINTER: printer is connected')
        self.set_printer_to_running()
        self.logger.info('PRINTER: printer is running')
        self.current_direction = None

    def get_expected_external_id(self, counter=0):
        if self.enable:
            tag_counter = counter + int(self.printing_config['firstPrintingValue']
                                        if 'firstPrintingValue' in self.printing_config.keys() else 0)
            printed_external_id, is_ok = get_printed_value(
                self.printing_config['stringBeforeCounter'],
                str(tag_counter))
            if not is_ok:
                raise PrinterException('get_expected_external_id: failed to get a valid printed value')
            return printed_external_id

    def set_printer_direction(self, direction):
        self.current_direction = direction

    @staticmethod
    def set_printer_config():
        try:
            defaults = ConfigDefaults()
            dir_config = os.path.abspath(os.path.join(os.path.dirname(__file__), '../configs'))
            file_config = os.path.abspath(os.path.join(dir_config, 'configs_for_printer_values.json'))
            printer_configs = open_json_cache(dir_config, file_config, defaults.get_printer_defaults())
        except Exception as e:
            raise PrinterException(f'init: set_printer_config: {e}')
        return printer_configs

    def is_connected(self):
        try:
            if self.printer_socket is None:
                return False
            self.query(self.get_state_request())
            return True
        except Exception as e:
            return False

    def open_printer_socket(self):
        """
        opens the printer socket
        """
        try:
            if not self.is_connected():
                self.printer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.printer_socket.settimeout(PrintingAndValidationDefaults.PRINTER_SOCKET_TIMEOUT)
                self.printer_socket.connect((self.printing_config['TCP_IP'],
                                             int(self.printing_config['TCP_PORT'])))
        except Exception as e:
            raise PrinterException(f'could not open_printer_socket: {e}')

    def exit(self):
        try:
            time.sleep(4)  # wait for printer to finish last print
            self.query(self.set_state_command('2'))  # for regular closure (not when connection error happens)
            self.printer_socket.close()
        except Exception as e:
            self.logger.warning(f'Could not exit printer due to: {e}')

    def set_printer_to_running(self):
        """
        sets the printer to running mode
        Zipher Text Communications Protocol
        printer state machine:
           0 -> 1                      shutdown
           1 -> 4 (automatically)      starting-up
           2 -> 0 (automatically)      shutting-down
           3 -> 2, 4                   running
           4 -> 2, 3                   offline
        @except: PrinterNeedsResetException('Printer failed to switch to running mode')
        @return: None
        """
        res = self.query(self.get_state_request())
        parts = res.split('|')
        if len(parts) < 2:
            raise PrinterException(f'set_printer_to_running: got unexpected results {res}')
        if parts[1] == '0':  # (Shut down)
            res = self.query(self.set_state_command('1'))
            if res == 'ACK':
                counter = 0
                while counter < 10:
                    time.sleep(1)
                    res = self.query(self.set_state_command('3'))
                    if res == 'ACK':
                        return
                    counter += 1
        elif parts[1] == '3':  # (Running)
            return
        elif parts[1] == '4':  # (Offline)
            res = self.query(self.set_state_command('3'))
            if res == 'ACK':
                return
        e = 'Printer failed to switch to running mode'
        raise PrinterException(f'set_printer_to_running: {e}')

    def query(self, cmd):
        """Send the input cmd string via TCP/IP Socket
        @type cmd: str
        @param cmd: command to send to printer
        @return: the reply string
        """
        cmd_str = cmd.strip('\r\n')
        self.logger.info(f'Sent command to printer: {cmd_str}')
        self.printer_socket.send(cmd.encode())
        values = self.read(cmd=cmd)
        if 'PRC' in values:
            self.got_printer_ack = True
            if len(set(values)) == 1:  # only PRC was received
                values = self.read(cmd=cmd)
        for value in values:
            if value != 'PRC' and value != '':
                return value

        raise Exception(f'Printer: query: did not ack to the following cmd :{cmd}')

    def read(self, cmd=''):
        data = self.printer_socket.recv(int(self.printing_config['TCP_BUFFER']))
        self.logger.info(f'Received RAW answer from printer: {data}')
        if len(data) == 0:
            raise PrinterException(f'query: did not ack to the following cmd :{cmd}' if cmd else '')
        value = data.decode("utf-8")
        str_split = '\r\n'
        if str_split not in value:
            str_split = '\r' if '\r' in value else '\n'

        values = value.split(str_split)[:-1]
        self.logger.info(f'Received answer from printer: {values}')
        return values

    def reset_printer_ack(self):
        self.got_printer_ack = False

    def get_printing_ack(self, timeout=PrintingAndValidationDefaults.PRINTER_ACK_TIMEOUT):
        if not self.enable:
            return True
        if self.got_printer_ack:
            self.got_printer_ack = False
            return True
        t_i = datetime.datetime.now()
        dt = 0.0
        while dt < timeout:
            try:
                values = self.read()
                if 'PRC' in values:
                    return True
                raise PrinterException(f'while waiting for ack, received a different response: {values}')
            except Exception as e:
                self.logger.info(f'Printer got exception, try again ({e})')
                dt = (datetime.datetime.now() - t_i).total_seconds()
                time.sleep(PrintingAndValidationDefaults.TIME_BTWN_PRINTER_REQUESTS)
        return False

    def get_printer_status(self, counter, is_pass, timeout=PrintingAndValidationDefaults.PRINTER_ACK_TIMEOUT):
        t_i = datetime.datetime.now()
        dt = 0.0
        while dt < timeout:
            try:
                status = self.printer_status(counter=self.cur_value + counter, is_pass=is_pass)
                if status:
                    return True
                dt = (datetime.datetime.now() - t_i).total_seconds()
                time.sleep(PrintingAndValidationDefaults.TIME_BTWN_PRINTER_REQUESTS)
            except Exception as e:
                raise PrinterException(f'get_printer_status: exception:({e})')

        return False

    @staticmethod
    def get_state_request():
        """
        gets the situation of the printer
        @return: the situation in the printer in the following format:
            STS|<overall state>|<error state>|<current job>|<batchcount>|<total count>|<
        """
        cmd = 'GST\r\n'
        return cmd

    @staticmethod
    def set_state_command(desired_state):
        """
        builds the command to send to printer for setting a printer state
        @param desired_state: the state to enter to, according to the following description
        0 Shut down
        1 Starting up
        2 Shutting down
        3 Running
        4 Offline
        @return: the cmd to send to printer
        """
        cmd = 'SST|' + str(desired_state) + '|\r\n'
        return cmd

    def get_line_assignment_cmd(self, line, tag_counter):
        job_name = self.printing_config['passJobName']
        if 'SGTIN' in job_name.upper():
            raise Exception('bi-directional mirror printing is not supported for SGTIN')
        job_name += '_M' if line == PrintingAndValidationDefaults.PASS_MIRROR_JOB_NUM else ''
        reel_id = self.printing_config["stringBeforeCounter"]
        return f'LAS|{job_name}|{line}|reel_num={reel_id}T|tag_number={str(tag_counter).zfill(4)}|\r\n'

    def get_line_number(self, is_pass):
        if is_pass:
            if self.current_direction is None or self.current_direction == 'forward':
                line = PrintingAndValidationDefaults.PASS_JOB_NUM
            elif self.current_direction == 'backward':
                line = PrintingAndValidationDefaults.PASS_MIRROR_JOB_NUM
            else:
                raise Exception(f'invalid printer direction: {self.current_direction}')
        else:
            line = PrintingAndValidationDefaults.FAIL_JOB_NUM
        return line
    
    @staticmethod
    def get_line_selection_cmd(line):
        return f"LSL|{line}|\r\n"

    def set_job_fields(self, tag_num_offset=0):
        pass_job_name = self.printing_config['passJobName']
        fail_job_name = self.printing_config['failJobName']
        reel_id = self.printing_config["stringBeforeCounter"]

        if 'BARCODE' in pass_job_name.upper():
            job_fields = [f'reel_num={reel_id}T']
        elif 'SGTIN' in pass_job_name.upper():
            job_fields = [f'sgtin={reel_id[:18]}',
                          f'reel_num={reel_id[18:26]}T']
        elif 'BLANK' in pass_job_name.upper():
            job_fields = []
        else:
            raise PrinterException('Job Name inserted is not supported at the moment')

        if pass_job_name != 'BLANK':
            tag_num_int = int(self.printing_config["firstPrintingValue"]) + tag_num_offset
            tag_num_str = str(tag_num_int).zfill(4)
            job_fields.append(f'tag_number={tag_num_str}')
        job_fields.append('\r\n')
        job_fields_str = '|'.join(job_fields)

        pass_job_fields_cmd = f'LAS|{pass_job_name}|{PrintingAndValidationDefaults.PASS_JOB_NUM}|' + job_fields_str
        fail_job_fields_str = '\r\n' if fail_job_name != pass_job_name else job_fields_str
        fail_job_fields_cmd = f'LAS|{fail_job_name}|{PrintingAndValidationDefaults.FAIL_JOB_NUM}|' + fail_job_fields_str
        all_cmds = [pass_job_fields_cmd, fail_job_fields_cmd]
        if self.bi_directional:
            all_cmds.append(
                f'LAS|{pass_job_name}_M|{PrintingAndValidationDefaults.PASS_MIRROR_JOB_NUM}|' + job_fields_str)

        return all_cmds

    def init_printing_protocols(self, tag_num_offset=0):

        try:
            job_fields_cmds = self.set_job_fields(tag_num_offset=tag_num_offset)

            cmds = ['CAF\r\n',
                    'CQI\r\n',
                    f'CLN|{PrintingAndValidationDefaults.PASS_JOB_NUM}|\r\n',
                    f'CLN|{PrintingAndValidationDefaults.FAIL_JOB_NUM}|\r\n',
                    ]
            if self.bi_directional:
                cmds += [f'CLN|{PrintingAndValidationDefaults.PASS_MIRROR_JOB_NUM}|\r\n']
            cmds += job_fields_cmds

            for cmd in cmds:
                value = self.query(cmd)
                time.sleep(0.1)
                # check if the return value is good, if not retry again for 10 times
                counter = 0
                while counter < 10:
                    # 'CQI' fails if the queue is empty
                    if value == 'ERR' and 'CQI' not in cmd:
                        counter += 1
                        time.sleep(0.1)
                        value = self.query(cmd)
                    else:
                        break
                if counter >= 10:
                    raise PrinterException('initialization process has failed in command: ' + cmd)
            # get the current counter value
            value = self.query(self.get_state_request())
            if value == 'ERR':
                raise PrinterException('initialization process has failed in command: ' + self.get_state_request())
            else:
                parts = [p for p in value.split("|")]
                if len(parts) < 6:
                    raise PrinterException(f'init_printing_protocols: got unexpected results {value}')
                self.cur_value = int(parts[5])

        except Exception as e:
            raise PrinterException(f'init_printing_protocols: {e}')

    def set_line_selection(self, line_number):
        """
        line selection
        @return:
        @rtype:
        """
        try:
            line_selection_msg = self.get_line_selection_cmd(line_number)
            rsp = ''
            t_0 = datetime.datetime.now()
            dt = 0
            timeout_ack = 1
            while rsp != 'ACK' and dt < timeout_ack:
                rsp = self.query(line_selection_msg)
                if rsp == 'ACK':
                    return
                dt = (datetime.datetime.now() - t_0).total_seconds()
            raise Exception('getting ERR from printer')
        except Exception as e:
            raise PrinterException(f'set_line_selection: Did not get ACK for Line Selection: {e}')
    
    def set_update_line_data(self, line):
        """
        line selection
        @return:
        @rtype:
        """
        try:
            update_line_msg = self.get_line_assignment_cmd(line=line, tag_counter=int(self.printing_config["firstPrintingValue"]) + self.printed_id)
            rsp = ''
            t_0 = datetime.datetime.now()
            dt = 0
            timeout_ack = 1
            while dt < timeout_ack:
                rsp = self.query(update_line_msg)
                if rsp and rsp != 'ERR':
                    return
                dt = (datetime.datetime.now() - t_0).total_seconds()
            raise Exception('getting ERR from printer')
        except Exception as e:
            raise PrinterException(f'set_update_line_data: Did not get ACK for Update Line Data: {e}')
    
    def set_printing_type(self, is_tag_passed):
        """
        line selection
        @return:
        @rtype:
        """
        if not self.enable:
            return
        line_number = self.get_line_number(is_tag_passed)
        if self.bi_directional and (is_tag_passed or self.printing_calib):
            self.set_update_line_data(line_number)
        self.set_line_selection(line_number)
        self.printed_id += int(is_tag_passed)

    def printer_status(self, counter, is_pass):
        """
        checks if the printing value matches the values registered to the logs
        should be called only after self.events.r2r_ready was set
        Exceptions:
            @except Exception('The printer printed Pass to the previous tag'):
                    printer printed pass while it should have been print fail
            @except Exception('The printer printed Fail to the previous tag')
                    printer printed fail while it should have been print pass
            @except Exception('The printer have not printed on the last tag')
                    printer did not print while it should have been
        """
        res = self.query(
            self.get_state_request())  # STS|<overall state>|<error state>|<current job>|<batchcount>|<total count>
        parts = [p for p in res.split("|")]
        if len(parts) < 6:
            raise PrinterException(f'printer_status: got unexpected results {res}')
        if parts[1] == '3':
            if parts[2] == '0':
                if int(parts[5]) == counter:
                    if not self.printing_config['printingFormat'] != 'Test':
                        job_name = self.printing_config['passJobName'] if is_pass else \
                            self.printing_config['failJobName']

                        if job_name in parts[3]:
                            self.logger.debug(f'Compare success with type {job_name} and counter {counter}')
                            return True
                        else:
                            self.logger.info(f'Printer type was not right (expected: {job_name}, got: {parts[3]}')
                            return False
                    else:
                        self.logger.debug(f'Compare success with counter {counter}')
                        return True
                else:
                    self.logger.info(f'The printer counter is not synced (expected: {counter}, got: {parts[5]}'
                                     f', trying again')
                    return False
            else:
                if parts[2] == '1':
                    raise PrinterException('error-state is Warnings present')
                if parts[2] == '2':
                    raise PrinterException('error-state is Faults present')
        else:
            if parts[1] == '0':
                raise PrinterException('over-all-state is Shutdown')
            if parts[1] == '1':
                raise PrinterException('over-all-state is Starting up')
            if parts[1] == '2':
                raise PrinterException('over-all-state is Shutting down')
            if parts[1] == '4':
                raise PrinterException('over-all-state is Offline')
            if parts[2] == '1':
                raise PrinterException('error-state is Warnings present')
            if parts[2] == '2':
                raise PrinterException('error-state is Faults present')


class Scanner(object):
    def __init__(self, is_scanner, exception_queue, logger_name, scanning_config, is_print=False, is_preprint=False):
        """

        @param exception_queue:
        @type exception_queue:
        @param logger_name:
        @type logger_name:
        @param scanning_config: all scanner configuration
        @type scanning_config: dict
        @param is_print: True if run with printing
        @type is_print: bool
        """
        self.exception_queue = exception_queue
        self.logger = logging.getLogger(logger_name)
        self.scanning_config = scanning_config
        self.enable = True
        if scanning_config is None or not is_scanner:
            self.logger.info('Scanner is disable')
            self.enable = False
            return
        
        # pre-print parameters:
        self.is_preprint = is_preprint
        self.reel_id = None
        self.tag_dir = None
        self.offset = -1
        self.expected_value, _ = get_printed_value(self.scanning_config['stringBeforeCounter'], self.scanning_config.get('firstPrintingValue', '0000'))
        self.tag_counter = int(self.expected_value.split('T')[1])
        self.num_reel_ids = 1

        scanner_port = f'COM{scanning_config["QRcomport"]}'
        try:
            if self.scanning_config["scannerType"].lower() == 'rtscan':
                self.scanner = BarcodeScanner(com_port=scanner_port, log_type='LOG', write_to_log=not is_print,
                                              timeout=str(self.scanning_config['QRtimeout']),
                                              is_flash=self.scanning_config['scannerFlash'])
            elif self.scanning_config["scannerType"].lower() == 'cognex':
                self.scanner = CognexDataMan(port=scanner_port, timeout=self.scanning_config['QRtimeout'])
            else:
                raise Exception('scanner type is not supported. Please use rtscan or cognex')
            self.logger.info('Connected to scanner at port {}'.format(scanner_port))
        except Exception as e:
            raise ScannerException(f'init: could not connect to barcode scanner {e}')

    def reconnect(self):
        try:
            if not self.scanner.is_open():
                self.scanner.open_port(com_port=self.scanner.com_port, timeout=str(self.scanning_config['QRtimeout']))
        except Exception as e:
            raise ScannerException(f'reconnect: could not connect to barcode scanner {e}')

    def update_first_tag_reel_id_and_counter(self, scanned_data):
        if self.reel_id is None and self.is_preprint:
            self.expected_value = scanned_data
            self.reel_id = scanned_data.split('T')[0]
            self.tag_counter = int(scanned_data.split('T')[1])
            self.offset = 0
    
    def update_reel_counter(self):       
        if self.tag_dir is not None:
            self.tag_counter = self.tag_counter + self.tag_dir  # here we update the tag counter according to the tag direction
            self.expected_value = self.reel_id + 'T' + str(self.tag_counter).zfill(4)
        else:
            self.offset += 1
            reel_id = self.get_reel_id()
            tag_counter = self.get_tag_counter()
            if self.offset > 0:
                self.expected_value = f'{reel_id}T{str(tag_counter+self.offset).zfill(4)} or {reel_id}T{str(tag_counter-self.offset).zfill(4)}'

        return self.expected_value

    def handle_reel_change(self, scanned_data, expected_result):
        if not self.is_preprint:
            return
        
        self.num_reel_ids += 1
        self.expected_value = scanned_data
        if expected_result is not None:
            expected_result.set_test_info({'external_id': self.expected_value})
        
        self.logger.info(f"{ASTERISK} SCANNING: reel id changed from {self.reel_id} to {scanned_data.split('T')[0]}, num_reel_ids: {self.num_reel_ids} {ASTERISK}")
        self.reel_id = scanned_data.split('T')[0]
        self.tag_counter = int(scanned_data.split('T')[1])
        self.tag_dir = None
        self.offset = 0

    def calculate_reel_direction(self, scanned_data, expected_result):
        if not self.is_preprint:
            return
        tag_counter = int(scanned_data.split('T')[1])
        if abs(tag_counter - self.tag_counter) == self.offset:
            self.tag_dir = 1 if tag_counter > self.tag_counter else -1
            self.tag_counter += (self.tag_dir * self.offset)
            self.expected_value = self.reel_id + 'T' + str(self.tag_counter).zfill(4)
            self.offset = 0
            if expected_result is not None:
                expected_result.set_test_info({'external_id': self.expected_value})
                self.logger.info(f'{ASTERISK} SCANNING: detected {"increasing" if self.tag_dir > 0 else "decreasing"} sequence, hence expected is {self.expected_value} {ASTERISK}')
                            
    def handle_mismatch(self, scanned_data, expected_result):

        if not self.is_preprint:
            validated_bin = ValidatedBin.MISMATCH
        
        elif self.reel_id is None:  
            # first passed tag
            if scanned_data in self.expected_value or scanned_data.split('T')[0] != self.expected_value.split('T')[0]:
                validated_bin = ValidatedBin.MATCH
                if scanned_data in self.expected_value:  # the first tags failed so now need to check the direction
                    self.tag_dir = 1 if scanned_data == self.expected_value.split(' or ')[0] else -1
                    self.logger.info(f'{ASTERISK} SCANNING: first passed tag scanned, detected {"increasing" if self.tag_dir > 0 else "decreasing"} sequence, expected is {self.expected_value} {ASTERISK}')
                elif scanned_data.split('T')[0] != self.expected_value.split('T')[0]:
                    self.num_reel_ids += 1
                    self.tag_dir = None
                    
                    self.logger.info(f'{ASTERISK} SCANNING: first passed tag scanned, detected new reel, expected is {self.expected_value} {ASTERISK}')
                
                self.update_first_tag_reel_id_and_counter(scanned_data)
                if expected_result is not None:
                    expected_result.set_test_info({'external_id': self.expected_value})
            else:
                validated_bin = ValidatedBin.MISMATCH
        
        elif scanned_data.split('T')[0] != self.reel_id:
            # reel id change
            self.handle_reel_change(scanned_data, expected_result)
            if self.num_reel_ids <= PrintingAndValidationDefaults.MAX_REEL_ID:
                validated_bin = ValidatedBin.MATCH
            else:
                validated_bin = ValidatedBin.REEL_ID_LIMIT_EXCEEDED
        
        elif self.tag_dir is None:
            # the second tag after reel id change to identify if it is increasing/decreasing sequence
            self.calculate_reel_direction(scanned_data, expected_result)
            validated_bin = ValidatedBin.MATCH if self.tag_dir is not None else ValidatedBin.MISMATCH
        
        else:
            validated_bin = ValidatedBin.MISMATCH  # mismatch during the same reel
        
        return validated_bin

    def get_tag_counter(self):
        return self.tag_counter

    def get_reel_id(self):
        return self.reel_id if self.reel_id is not None else self.expected_value.split('T')[0]

    def get_expected_value(self):
        return self.expected_value

    def validated_scan_data(self, expected_value:Union[str, None] = None, expected_result:Union[WiliotTesterTagResultList, None] = None):
        validated_status = ValidatedBin.UNTESTED
        t_i = datetime.datetime.now()
        dt = 0.0
        is_first = True
        res_str = ''
        black_square_readings = 0
        
        while dt < PrintingAndValidationDefaults.SCANNER_GOOD_READ_TIMEOUT:
            try:
                if self.num_reel_ids > PrintingAndValidationDefaults.MAX_REEL_ID:
                    return ValidatedBin.REEL_ID_LIMIT_EXCEEDED, 'MAX REEL ID LIMIT EXCEEDED'

                scanned_data, _, _, _ = \
                    self.scanner.scan_ext_id(
                        need_to_trigger=is_first or PrintingAndValidationDefaults.TRIGGER_TYPE == 0)
                res_str = f'expected:{expected_value}, scanned:{scanned_data}'
                self.logger.info(f'{ASTERISK} SCANNING: {res_str} {ASTERISK}')
                if expected_value is None:
                    # scanning before the first tag was reached to the scanner
                    if scanned_data is None:
                        black_square_readings += 1
                        validated_status = ValidatedBin.MATCH if black_square_readings >= PrintingAndValidationDefaults.BLACK_SQUARE_TOLERANCE else ValidatedBin.MISMATCH

                    else:
                        validated_status = ValidatedBin.MISMATCH

                elif expected_value == '' and scanned_data is None:  # failed tag and no code was read
                    black_square_readings += 1
                    validated_status = ValidatedBin.MATCH if black_square_readings >= PrintingAndValidationDefaults.BLACK_SQUARE_TOLERANCE else ValidatedBin.MISMATCH
                
                elif scanned_data is None:  # nothing was scanned but the expected value is not None not empty string
                    validated_status = ValidatedBin.NO_READ
                
                elif expected_value == '':  # expected fail but something was scanned
                    validated_status = ValidatedBin.MISMATCH
                
                elif scanned_data == expected_value:  # same read codes
                    self.update_first_tag_reel_id_and_counter(scanned_data)
                    return ValidatedBin.MATCH, res_str
                
                else:
                    # cases where the expected value is not None (can be failed or pass) and scanned_data is not None
                    validated_status = self.handle_mismatch(scanned_data, expected_result)
                    if validated_status != ValidatedBin.MISMATCH:
                        return validated_status, res_str

                if black_square_readings >= PrintingAndValidationDefaults.BLACK_SQUARE_TOLERANCE:
                    break  # after several black square readings we can assume it is a black square
                
                dt = (datetime.datetime.now() - t_i).total_seconds()
                time.sleep(PrintingAndValidationDefaults.TIME_BTWN_PRINTER_REQUESTS)
                is_first = False
            except Exception as e:
                self.scanner.trigger_off()
                raise ScannerException(f'get_scan_data: got exception from scanner ({e})')
        self.scanner.trigger_off()
        return validated_status, res_str

    def exit(self):
        try:
            self.scanner.close_port()
        except Exception as e:
            self.logger.warning(f'Could not exit scanner due to: {e}')