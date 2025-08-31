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
import threading
import time
from queue import Queue
from enum import Enum
import os
import json
import pandas as pd
from PyQt5.QtCore import pyqtSignal, QSize, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor, QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QPushButton, QPlainTextEdit, QWidget
import pyqtgraph as pg
try:
    from tkinter import Tk, ttk, Toplevel, Label
except Exception as e:
    print(f'could not import tkinter: {e}')

from wiliot_tools.utils.wiliot_gui.wiliot_gui import WiliotGui, popup_message, FONT_BUTTONS
from wiliot_testers.wiliot_tester_tag_test import load_test_suite_file, TesterName
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_testers.offline.modules.offline_utils import ConfigDefaults, open_session, save_screen
from wiliot_testers.offline.modules.offline_utils import printing_test_window, printing_sgtin_window
from wiliot_testers.offline.modules.offline_utils import get_validation_data_for_scanning
from wiliot_testers.tester_utils import open_json_cache, upload_conclusion

from wiliot_testers.offline.modules.offline_tag_testing import TagTesting, TagStates
from wiliot_testers.offline.modules.offline_printing_and_validation import PrintingAndValidation, ValidationStates
from wiliot_testers.offline.configs.moh_instruction import moh_instruction, lang_map
from wiliot_testers.offline.configs.global_vars_and_enums import MainDefaults, ASTERISK

from wiliot_testers.offline.modules.offline_log import DataLogging


class ErrorCode(Enum):
    Main = 100
    TagTesting = 200
    PrintingAndValidation = 300


class HwErrors(Enum):
    R2R = 10
    PRINTER = 20
    SCANNER = 30
    ATTENUATOR = 50
    SENSOR = 60
    GATEWAY = 70
    SERVER = 80


class MohType(Enum):
    MISSING_LABEL = 'Missing Label'
    STOP_CRITERIA = 'stop Criteria'
    VALIDATION_FAILED = 'Validation Failed'
    FILES_ERROR = 'Files Error'
    PRINTER_ERROR = 'Printer Error'
    SCANNER_ERROR = 'Scanner Error'
    ARDUINO_ERROR = 'Arduino Error'
    NO_PRINTER_ACK = 'Missed Printing'
    GENERAL_ERROR = 'General Error'
    GATEWAY_ERROR = 'Gateway Error'
    SERVER_ERROR = 'Server Error'


class MainStates(Enum):
    STOP_CRITERIA = 1
    UPDATE_PLOT = 2
    RESTART_AFTER_MOH = 3


class TestParametersException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)


class Main(QMainWindow):
    sig = pyqtSignal(str)

    def __init__(self, test_config_path=None, *args, **kwargs):

        # init communication between classes
        self.test_start_event = threading.Event()
        self.test_end_event = threading.Event()
        self.validation_end_event = threading.Event()
        self.stop_app_event = threading.Event()
        self.exception_q = Queue(maxsize=MainDefaults.MAX_QUEUE_SIZE)
        self.tag_results_queue = Queue(maxsize=MainDefaults.MAX_QUEUE_SIZE)

        # init test parameters including tests suites
        self.test_parameters = TestParameters()

        # init user inputs
        self.is_gui = test_config_path is None
        self.user_config = None
        tag_print_config = self.run_main_gui(test_config_path)

        # init log
        self.test_logger = DataLogging(exception_queue=self.exception_q, log_config=self.user_config)
        self.logger = logging.getLogger(self.test_logger.get_logger_name())
        self.logger.info(f"Wiliot's package version = {get_version()}")

        # init test parameters including tests suites
        self.test_parameters.set_logger_name(logger_name=self.test_logger.get_logger_name())

        # init printer config:
        self.external_hw_config = self.test_parameters.init_external_hw_config()

        # select test suites
        self.test_parameters.set_specific_test(user_inputs=self.user_config)

        # open printing GUI
        self.print_config = self.run_printing_gui(tag_print_config)
        self.test_logger.update_log_config({**self.external_hw_config, **self.print_config})
        self.scan_validation_df = self.run_scanning_gui()

        # run application
        self.tag_testing = None
        self.print_log_validation = None
        self.tag_testing_thread = None
        self.print_log_validation_thread = None
        self.r2r_obj = None
        self.moh_obj = ManualOperationHandle(exception_queue=self.exception_q, logger_name=self.logger.name,
                                             is_gw_r2r=False)
        self.gw_version = ''
        self.run_app()

        # run GUI:
        self.tested = None
        self.text_box = None
        self.data_line = None
        self.reel_label = None
        self.update_timer = None
        self.last_tested_num = 0
        self.last_passed_num = 0
        super(Main, self).__init__(*args, **kwargs)
        self.open_ui(wiliot_ver=get_version(), gw_version=self.gw_version)

    def run_main_gui(self, test_config_path):
        tag_print_config = {}
        if self.is_gui:
            self.user_config, tag_print_config = open_session(
                test_suite_list=self.test_parameters.get_tests_suites_names())
        else:
            try:
                with open(test_config_path, 'r') as f:
                    self.user_config = json.load(f)
            except Exception as e:
                raise Exception(f'Main: init: error while running without gui: '
                                f'could not read user inputs from the following path: {test_config_path}, due to: {e}')
        return tag_print_config

    def check_conversation_label_error(self, new_reel, tag_print_config):
        need_conv_label = self.user_config['gen'].lower() == 'gen3' and self.user_config['Environment'].lower() == 'prod'
        conv_label_not_changed = not tag_print_config.get('conversion_label_changed', False)
        not_allow_same_label = not self.user_config['sameConversionLabel']
        need_warning = new_reel and need_conv_label and conv_label_not_changed and not_allow_same_label
        return need_warning

    def run_printing_gui(self, tag_print_config=None):
        tag_print_config = tag_print_config if tag_print_config is not None else {}
        is_valid = True
        msg = ''
        if self.user_config['toPrint'] == 'Yes' and not tag_print_config.get('run_printing_gui', False):
            new_tag_print_config = {}
            if self.user_config['printingFormat'] == 'Test':
                new_tag_print_config, is_valid = printing_test_window()
                if not is_valid:
                    msg = 'Impossible printing values entered by the user, the program will exit now'

            elif self.user_config['printingFormat'] in MainDefaults.PRINTING_GUI_TYPE:
                new_tag_print_config, is_valid, new_reel = \
                    printing_sgtin_window(env=self.user_config['Environment'],
                                          owner_id=self.user_config['OwnerId'],
                                          printing_format=self.user_config['printingFormat'],
                                          gen=self.user_config['gen'],
                                          is_new_batch_name=tag_print_config['batch_name_change'])
                if not is_valid:
                    msg = 'user exited the program'

                if self.check_conversation_label_error(new_reel=new_reel, tag_print_config=tag_print_config):
                    msg += '\nConversion label was not updated although NEW reel was assembled'
                    is_valid = False

            else:
                msg = 'user chose unsupported printing format!!!'

            for k, v in new_tag_print_config.items():
                tag_print_config[k] = v

        if not is_valid:
            raise Exception(f'Main: run_printing_gui: {msg}')

        return tag_print_config

    def run_scanning_gui(self):
        df = pd.DataFrame()
        if self.user_config['toPrint'].lower() == 'no' and self.user_config['QRRead'].lower() == 'yes':
            df = get_validation_data_for_scanning()
        return df

    def run_app(self):
        # init all classes
        self.tag_testing = TagTesting(test_start_event=self.test_start_event,
                                      test_end_event=self.test_end_event,
                                      validation_end_event=self.validation_end_event,
                                      stop_app_event=self.stop_app_event,
                                      moh_object=self.moh_obj,
                                      exception_queue=self.exception_q,
                                      tag_results_queue=self.tag_results_queue,
                                      log_obj=self.test_logger,
                                      test_object=self.test_parameters,
                                      user_config=self.user_config,
                                      hw_config=self.external_hw_config)
        if not self.tag_testing.is_init:
            err = self.moh_obj.get_all_exceptions()
            raise Exception(f'Got the following errors during TagTesting init:\n{err}')
        self.moh_obj.set_is_gw_r2r(self.tag_testing.is_r2r)
        self.print_log_validation = PrintingAndValidation(test_start_event=self.test_start_event,
                                                          test_end_event=self.test_end_event,
                                                          validation_end_event=self.validation_end_event,
                                                          stop_app_event=self.stop_app_event,
                                                          moh_object=self.moh_obj,
                                                          exception_queue=self.exception_q,
                                                          tag_results_queue=self.tag_results_queue,
                                                          log_obj=self.test_logger,
                                                          test_object=self.test_parameters,
                                                          user_config=self.user_config,
                                                          gw_version=self.tag_testing.get_gw_version(),
                                                          get_duplicated_tags=self.tag_testing.get_all_duplicated_tags,
                                                          scanning_data=self.scan_validation_df,
                                                          get_gw_signal=self.tag_testing.get_gw_gpio_signal)
        if not self.print_log_validation.is_init:
            err = self.moh_obj.get_all_exceptions()
            raise Exception(f'Got the following errors during PrintingAndValidation init:\n{err}')
        # set r2r counter:
        self.r2r_obj = self.tag_testing.r2r if self.tag_testing.is_r2r else self.print_log_validation.r2r
        self.set_r2r_configuration()

        # open threads for all classes
        self.tag_testing_thread = threading.Thread(target=self.tag_testing.run)
        self.print_log_validation_thread = threading.Thread(target=self.print_log_validation.run)

        self.tag_testing_thread.start()
        self.print_log_validation_thread.start()

        self.gw_version = self.tag_testing.get_gw_version()

    def set_r2r_configuration(self):
        if self.tag_testing.is_r2r:
            self.print_log_validation.set_r2r_counter_func(self.tag_testing.r2r.get_counter)
            # update instruction strings
            for lan in moh_instruction[MohType.ARDUINO_ERROR.value].keys():
                moh_instruction[MohType.ARDUINO_ERROR.value][lan] = \
                    [s.replace('Arduino', 'Gateway') for s in moh_instruction[MohType.ARDUINO_ERROR.value][lan]]
            self.logger.info('Gateway working instead of Arduino')

    @pyqtSlot(str)
    def append_debug(self, string):
        self.text_box.appendPlainText(string)  # +'\n')

    def open_ui(self, wiliot_ver, gw_version):
        """
        opens the run main GUI that will present the run data and gives to the user ability to Stop/Continue/Pause
        """
        stop_label = QLabel("If you want to stop this run, press stop")
        stop_label.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE))
        self.reel_label = QLabel("Reel Name: ")
        self.reel_label.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE))
        self.reel_label.setStyleSheet('.QLabel {padding-top: 10px; font-weight: bold; font-size: 25px; color:#ff5e5e;}')
        self.reel_label.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE))
        self.tested = QLabel("Tested = 0, Passed = 0, Yield = -1%")
        self.tested.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE))
        last_tag_str = QLabel("Last Tag Passed: ")
        last_tag_str.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE, weight=QFont.Bold))
        layout = QVBoxLayout()

        stop = QPushButton("Stop")
        stop.setStyleSheet("background-color: #FD4B4B")
        stop.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE))
        stop.setFixedSize(QSize(300, 22))
        stop.pressed.connect(self.stop_app_event.set)

        c = ConsolePanelHandlerGUI(self.sig)
        c.setLevel(logging.WARNING)
        self.text_box = QPlainTextEdit()
        self.text_box.setPlaceholderText("Warnings will be printed here")
        self.text_box.setMaximumBlockCount(1000)
        self.text_box.setReadOnly(True)

        self.logger.addHandler(c)
        self.sig.connect(self.append_debug)
        self.text_box.moveCursor(QTextCursor.End)

        graphWidget = pg.PlotWidget()
        graphWidget.setBackground('w')
        # Add Title
        graphWidget.setTitle("Yield over time", color=QColor("56C2FF"), size="20pt")
        styles = {"color": "#f00", "font-size": "14px"}
        graphWidget.setLabel("left", "Yield for the last 50 tags [%]", **styles)
        graphWidget.setLabel("bottom",
                             f"Last tag location [x*{MainDefaults.CALCULATE_INTERVAL}+{MainDefaults.CALCULATE_ON}]",
                             **styles)
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = graphWidget.plot([], [], pen=pen)
        versions = QLabel("PyWiliot Version: {}\nGW Version: {}".format(wiliot_ver, gw_version))
        versions.setFont(QFont(MainDefaults.FONT_NAME, MainDefaults.FONT_SIZE, weight=QFont.Bold))

        layout.addWidget(self.reel_label)
        layout.addWidget(stop_label)
        layout.addWidget(stop)
        layout.addWidget(last_tag_str)
        layout.addWidget(self.tested)
        # layout.addWidget(self.debug)
        layout.addWidget(self.text_box)
        layout.addWidget(graphWidget)
        layout.addWidget(versions)

        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)
        self.show()

        # updates the GUI and stops all if exception happened
        self.update_timer = QTimer()
        self.update_timer.setInterval(MainDefaults.GUI_UPDATE_TIME)
        self.update_timer.timeout.connect(self.gui_run)
        self.update_timer.start()

    def check_stop_criteria(self, tested, responded, passed, is_passed_list, yield_over_time):
        # check Stop Conditions:
        need_to_stop = False
        messages = []
        if not self.user_config['ignoreStop']:

            # check max fail in a row:
            max_failed = int(self.user_config['maxFailStop'])
            if len(is_passed_list) > max_failed:
                max_fail_in_a_row = not any(is_passed_list[-max_failed:])
                if max_fail_in_a_row:
                    msg = str('*' * 100) + f'\nThere are {self.user_config["maxFailStop"]} fails in a row, ' \
                                           f'Run will stop\n' + str('*' * 100)
                    self.logger.warning(msg)
                    messages.append('max failed in a row happened')
                    need_to_stop = True

            # check yield drop:
            if len(yield_over_time) >= MainDefaults.N_YIELD_SAMPLES_UNDER_THRESHOLD:
                yield_drop_happened = True
                for ii in range(1, MainDefaults.N_YIELD_SAMPLES_UNDER_THRESHOLD):
                    if yield_over_time[-ii] > int(self.user_config['maxYieldStop']):
                        yield_drop_happened = False
                        break
                if yield_drop_happened:
                    msg = str('*' * 100) + f'\nThe yield-over-time of the last tags is below ' \
                                           f'{self.user_config["maxYieldStop"]}%, Run will stop\n' + str('*' * 100)
                    self.logger.warning(msg)
                    messages.append('yield drop happened')
                    need_to_stop = True

            # check responding vs pass:
            high_responded_vs_passed = \
                responded > int(self.user_config['pass_response_diff_offset']) and \
                (responded - passed) / tested > int(self.user_config['pass_response_diff']) / 100
            if high_responded_vs_passed:
                msg = str('*' * 100) + f'\nThere is a significant differences between passed yield ' \
                                       f'and responded yield:{self.user_config["pass_response_diff"]}%, ' \
                                       f'Run will stop\n' + str('*' * 100)
                self.logger.warning(msg)
                messages.append('High difference between passed and responding happened')
                need_to_stop = True

        return need_to_stop, messages

    def timed_popup(self):
        params_dict = {
            'space': {'value': '', 'widget_type': 'label'},
            'msg': {'value': 'Please wait until the Post-Run-Validation is completed\n',
                    'widget_type': 'label', 'options': {'font': ("Gudea", 20, 'bold')}},
            'progress': {'value': '', 'widget_type': 'label'}
        }
        wg = WiliotGui(params_dict=params_dict, do_button_config=False, parent=None, exit_sys_upon_cancel=False,
                       title='Wait Post-Run-Validation')
        max_length = self.print_log_validation.get_validation_q_maxsize()

        def update_progress():
            current_length = self.print_log_validation.get_validation_q_size()
            progress = round(100 * (1 - (current_length / max_length)), 2)
            wg.update_widget('progress', f'{progress}%')

            if current_length <= 0:
                wg.exit_gui()

        update_progress()
        wg.add_recurrent_function(cycle_ms=1000, function=update_progress)
        wg.run()

    def wait_for_tag_test_end(self):
        t_start = time.time()
        while self.tag_testing.is_test_running() and \
                time.time() - t_start <= self.test_parameters.get_total_test_time():
            time.sleep(0.200)

    def check_end_of_test(self, tested, passed):
        # check end of test according to number of tested:
        if tested >= int(self.user_config['desiredTags']):
            self.wait_for_tag_test_end()
            msg = f'---------------------------Desired tags have reached ({tested})---------------------------'
            self.logger.warning(msg)
            return True

        # check end of test according to number of passed:
        if passed >= int(self.user_config['desiredPass']):
            self.wait_for_tag_test_end()
            msg = f'---------------------------Desired passed tags have reached ({passed})---------------------------'
            self.logger.warning(msg)
            return True
        return False

    @staticmethod
    def calculate_yield_over_time(is_passed_list):
        yield_over_time = \
            [sum(is_passed_list[x - MainDefaults.CALCULATE_ON:x]) / MainDefaults.CALCULATE_ON * 100
             for x in range(MainDefaults.CALCULATE_ON, len(is_passed_list), MainDefaults.CALCULATE_INTERVAL)]
        return yield_over_time

    def gui_run(self):

        try:

            if self.stop_app_event.is_set():
                self.exit()
                return

            tested = self.tag_testing.get_tested() - int(self.tag_testing.is_test_running())
            passed = self.tag_testing.get_passed()
            is_passed_list = self.tag_testing.get_is_passed_list()
            responded = self.tag_testing.get_responded()
            missing_labels = self.tag_testing.get_missing_label_count()
            self.reel_label.setText("Reel Name: " + self.test_logger.get_reel_name())

            if tested == 0:
                passed_yield = -1.0
                responded_yield = -1
            else:
                passed_yield = passed / tested * 100
                responded_yield = responded / tested * 100
            if self.test_logger.get_reel_name() == '':
                raise ValueError('REEL NAME PROBLEM')
            self.tested.setText(f'Tested = {tested}, Passed = {passed}, '
                                f'Responded Yield = {round(responded_yield, 2)}%, '
                                f'Yield = {round(passed_yield, 2)}%\n Tag reel location:'
                                f' {self.print_log_validation.get_tag_reel_location() + 1},'
                                f' Missing labels = {missing_labels}')

            # update plot:
            yield_over_time = self.calculate_yield_over_time(is_passed_list)
            x = list(range(len(yield_over_time)))
            self.data_line.setData(x, yield_over_time)

            # check end of test:
            end_of_test = None if self.user_config['ignoreStop'] else self.check_end_of_test(tested=tested,
                                                                                             passed=passed)
            if end_of_test:
                self.exit()
                return

            # check Stop Conditions:
            need_to_stop, messages = self.check_stop_criteria(tested=tested, responded=responded, passed=passed,
                                                              is_passed_list=is_passed_list,
                                                              yield_over_time=yield_over_time)
            if need_to_stop:
                for msg in messages:
                    self.exception_q.put(f'Main Exception: run: state{MainStates.STOP_CRITERIA.name}: {msg}',
                                         block=False)
        except Exception as e:
            self.exception_q.put(f'Main Exception: run: state{MainStates.UPDATE_PLOT.name}: {e}', block=False)
        # check manual operation handling:
        self.wait_for_tag_test_end()
        exceptions_status = self.moh_obj.handle_exceptions()
        while exceptions_status['pause_run']:
            self.moh_obj.set_moh_is_needed(True)
            # open moh GUI:
            self.update_timer.stop()
            is_end_of_run = False
            continue_run = False
            if exceptions_status['moh_type'] == MohType.MISSING_LABEL:
                is_end_of_run = self.end_of_run_pop_up() if self.is_gui else True
            if not is_end_of_run:
                continue_run = \
                    self.moh_obj.moh_pop_up(
                        moh_type=exceptions_status['moh_type'],
                        error_code=exceptions_status['error_code'],
                        msg=exceptions_status['exception_str'],
                        scan_again_func=self.print_log_validation.update_scanning_results_after_exception
                        if self.print_log_validation.is_scanner else None)
            self.restart_run_after_moh(continue_run)
            exceptions_status = self.moh_obj.handle_exceptions()

            if not continue_run:
                self.exit()
                break
        self.update_state_machines()
        self.moh_obj.set_moh_is_needed(False)
        self.update_timer.start()

    def restart_run_after_moh(self, continue_run):
        self.logger.info('Start the run after MOH')
        is_print = self.user_config['toPrint'].lower() == 'yes'
        is_scanner = self.user_config['QRRead'].lower() == 'yes'
        is_r2r = self.user_config['isR2R'].lower() == 'yes'
        try:
            self.tag_testing.gw_reset_and_config()
            if is_r2r:
                self.r2r_obj.reconnect()
                self.r2r_obj.send_start_to_r2r()
                if not continue_run:
                    self.r2r_obj.end_of_run()
            if is_print:
                self.print_log_validation.restart_printer_after_moh()
            if is_scanner:
                self.print_log_validation.scanner.reconnect()

        except Exception as e:
            self.exception_q.put(f'Main Exception: run: state{MainStates.RESTART_AFTER_MOH.name}: {e}', block=False)

    def update_state_machines(self):
        # to re-do WAIT_END, since results are not yet ready:
        if self.print_log_validation.last_state == ValidationStates.WAIT_END and \
                self.tag_testing.last_state in [TagStates.TAG_TEST, TagStates.PROCESS_TEST]:
            self.print_log_validation.last_state = ValidationStates.SET_NEXT_PRINT
        return

    @staticmethod
    def end_of_run_pop_up():
        params_dict = {
            'space': {'value': '', 'widget_type': 'label'},
            'is_new': {'value': '         End of Run?    \n',
                       'widget_type': 'label', 'options': {'font': ("Gudea", 20, 'bold')}}}
        wg = WiliotGui(params_dict=params_dict, do_button_config=False, parent=None, exit_sys_upon_cancel=False,
                       title='End Run')
        wg.button_configs(submit_button_text='Yes', cancel_button_text='No')
        out = wg.run()
        return out is not None

    def upload_data_to_cloud_and_summary(self):
        # upload data to cloud and present summary
        tested = self.tag_testing.get_tested()
        passed = self.tag_testing.get_passed()
        responded = self.tag_testing.get_responded()
        is_passed_list = self.tag_testing.get_is_passed_list()
        missing_labels = self.tag_testing.get_missing_label_count()

        if tested == 0:
            return

        if not self.is_gui and 'upload_to_cloud' in self.user_config.keys():
            values = {'upload': self.user_config['upload_to_cloud'], 'comments': ''}
        else:
            ttfp_list = self.tag_testing.get_ttfp_list()
            ttfp_avg = self.tag_testing.calculating_ttfp_avg(ttfp_list)
            values = save_screen(tested=tested,
                                 passed=passed,
                                 responded=responded,
                                 yield_=passed / tested * 100 if tested > 0 else -1,
                                 missing_labels=self.tag_testing.get_missing_label_count(),
                                 ttfp_avg=ttfp_avg,
                                 ttfp_max_error=MainDefaults.MAX_TTFP_ERROR)

        if values['upload'].lower() == 'yes':
            file_size = os.stat(self.test_logger.get_packets_data_path()).st_size
            if file_size < MainDefaults.MAX_FILE_SIZE:
                try:
                    res = upload_to_cloud_api(batch_name=self.test_logger.get_reel_name(),
                                              tester_type='offline-test',
                                              run_data_csv_name=self.test_logger.get_run_data_path(),
                                              packets_data_csv_name=self.test_logger.get_packets_data_path(),
                                              env=self.user_config['Environment'],
                                              owner_id=self.user_config['OwnerId'],
                                              logger_=self.logger.name, is_path=True)
                except Exception as e:
                    self.logger.warning(f'Main: upload_data_to_cloud_and_summary: {e}')
                    res = False

                if self.is_gui:
                    upload_conclusion(succeeded_csv_uploads=res)
            else:
                e_msg = 'Test files are too large, please upload using manual upload app'
                popup_message(msg=e_msg, bg='red')
                self.logger.warning(f'Main: upload_data_to_cloud_and_summary: {e_msg}')
        else:
            self.logger.info('Data was not Uploaded to cloud, due to user selection')

        # summary message:
        yield_over_time = self.calculate_yield_over_time(is_passed_list)
        responded_yield = responded / tested * 100 if tested > 0 else -1
        passed_yield = passed / tested * 100 if tested > 0 else -1
        msg = f"Stopped by the operator.\nReels yield_over_time is: |{yield_over_time}" \
              f"| interval: |{MainDefaults.CALCULATE_INTERVAL}|, on: |{MainDefaults.CALCULATE_ON}\n" \
              f"User comments: {values['comments']}\n" \
              f"Tested = {tested}, Passed = {passed}, " \
              f"Responded Yield = {responded_yield}%, Yield = {passed_yield}%, Missing labels = {missing_labels}"
        self.logger.info(msg)

    def stop_app(self):
        if self.tag_testing_thread.is_alive():
            self.logger.info('Waiting for Tag Testing thread to stop all processes...')
            self.tag_testing_thread.join()
            self.logger.info('Tag Testing thread was done')
        if self.print_log_validation_thread.is_alive():
            self.logger.info('Waiting for Printing Log and Validation thread to stop all processes...')
            self.print_log_validation_thread.join()
            self.logger.info('Printing Log and Validation thread was done')

    def exit(self):
        self.stop_app_event.set()
        try:
            offset_size = self.print_log_validation.get_validation_q_maxsize()
            if offset_size > 1:
                self.timed_popup()
            self.stop_app()
            if self.is_gui:
                self.moh_obj.get_all_exceptions()
            self.upload_data_to_cloud_and_summary()
        except Exception as e:
            self.logger.warning(f'Main: exit: Got Exception during upload data: [{e}]\n'
                                f'please make sure data was uploaded')
        self.update_timer.stop()
        self.close()


class TestParameters(object):
    def __init__(self, logger_name=None):
        self.logger = None
        if logger_name is not None:
            self.logger = logging.getLogger(logger_name)
        # set config folder
        app_dir = os.path.abspath(os.path.dirname(__file__))
        self.dir_config = os.path.join(app_dir, 'configs')
        # set test suite:
        self.tests_suite = None
        self.all_tests_suites = load_test_suite_file(TesterName.OFFLINE.value)
        self.total_time = 0
        self.user_inputs = None
        self.stop_criteria = None

    def get_tests_suites_names(self):
        return list(self.all_tests_suites.keys())

    def set_logger_name(self, logger_name):
        self.logger = logging.getLogger(logger_name)

    def set_specific_test(self, user_inputs):
        self.user_inputs = user_inputs
        self.set_test_suite()
        calculated_time = self.calculate_total_test_time()
        self.set_total_test_time(total_time=calculated_time)

        self.stop_criteria = self.set_stop_criteria()

    def set_stop_criteria(self):
        stop_criteria = {}
        if 'pass_response_diff' in self.user_inputs.keys():
            max_diff_btwn_pass_and_response = {}
            try:
                max_diff_btwn_pass_and_response['value'] = int(self.user_inputs['pass_response_diff'])
            except Exception as e:
                raise TestParametersException(f'set_stop_criteria: Could not convert the pass_response_diff to number:'
                                              f' {e}')
            if 'pass_response_diff_offset' in self.user_inputs.keys():
                try:
                    max_diff_btwn_pass_and_response['offset'] = int(self.user_inputs['pass_response_diff_offset'])
                except Exception as e:
                    raise TestParametersException(f'set_stop_criteria: Could not convert the pass_response_diff_offset '
                                                  f'to number: {e}')
            stop_criteria['max_diff_btwn_pass_and_response'] = max_diff_btwn_pass_and_response

        fields = {'desiredTags': 'max_tested_tags', 'desiredPass': 'max_pass_tags'}
        for f_user, f_stop in fields.items():
            if f_user in self.user_inputs.keys():
                stop_criteria[f_stop] = self.user_inputs[f_user]
            else:
                raise TestParametersException(f'set_stop_criteria: could not find {f_user} in '
                                              f'the user inputs: {self.user_inputs.keys()}')
        return stop_criteria

    def calculate_total_test_time(self):
        total_time = 0
        for stage in self.tests_suite['tests']:
            if 'maxTime' in stage.keys():
                total_time += stage['maxTime']
            if 'delayBeforeNextTest' in stage.keys():
                total_time += stage['delayBeforeNextTest']
            if 'DelayAfterTest' in stage.keys():
                total_time += stage['DelayAfterTest']
        total_time *= int(self.tests_suite.get('n_cycles', 1))
        return total_time

    def set_total_test_time(self, total_time):
        self.total_time = total_time

    def get_total_test_time(self):
        return self.total_time

    def set_test_suite(self):
        # read file:
        if self.user_inputs['testName'] in self.all_tests_suites.keys():
            self.tests_suite = self.all_tests_suites[self.user_inputs['testName']]
        else:
            raise TestParametersException(f'set_test_suite: specified test, {self.user_inputs["testName"]}, '
                                          f'is not part of test suit file: {self.all_tests_suites.keys()}')

    def get_selected_test_suite(self):
        return self.tests_suite

    def init_external_hw_config(self):
        config_defaults = ConfigDefaults()
        printer_config_path = os.path.join(self.dir_config, 'configs_for_printer_values.json')
        printer_config_values = open_json_cache(self.dir_config, printer_config_path,
                                                config_defaults.get_printer_defaults())
        if 'printingFormat' in printer_config_values.keys():
            del printer_config_values['printingFormat']
        external_hw_config_path = os.path.join(self.dir_config, 'test_configs.json')
        external_hw_config_values = open_json_cache(self.dir_config, external_hw_config_path,
                                                    config_defaults.get_external_hw_defaults())
        return {**printer_config_values, **external_hw_config_values}


class ManualOperationHandle(object):
    def __init__(self, exception_queue, logger_name, is_gw_r2r):
        """

        @param exception_queue:
        @type exception_queue: Queue
        """
        self.exception_q = exception_queue
        self.logger = logging.getLogger(logger_name)
        self.is_moh_needed = False
        self.is_gw_r2r = is_gw_r2r
        self.critical_moh_types = []
        self.set_critical_errors()

    def set_critical_errors(self):
        self.critical_moh_types = [MohType.GENERAL_ERROR, MohType.FILES_ERROR, MohType.STOP_CRITERIA,
                                   MohType.NO_PRINTER_ACK]

    def get_manual_operation_is_needed(self):
        return self.is_moh_needed or not self.exception_q.empty()

    def set_moh_is_needed(self, is_needed):
        self.is_moh_needed = is_needed

    def set_is_gw_r2r(self, is_r2r):
        self.is_gw_r2r = is_r2r

    @staticmethod
    def error_code_to_moh(error_code):
        if compare_error_code(error_code, ErrorCode.TagTesting.value, 0) and \
                compare_error_code(error_code, TagStates.GET_TRIGGER.value, 2):
            moh_type = MohType.MISSING_LABEL
        elif compare_error_code(error_code, ErrorCode.Main.value, 0) and \
                compare_error_code(error_code, MainStates.STOP_CRITERIA.value, 2):
            moh_type = MohType.STOP_CRITERIA
        elif compare_error_code(error_code, ErrorCode.PrintingAndValidation.value, 0) and \
                compare_error_code(error_code, ValidationStates.VALIDATION.value, 2):
            moh_type = MohType.VALIDATION_FAILED
        elif compare_error_code(error_code, ErrorCode.PrintingAndValidation.value, 0) and \
                compare_error_code(error_code, ValidationStates.PRINTER_ACK.value, 2):
            moh_type = MohType.NO_PRINTER_ACK
        elif compare_error_code(error_code, ErrorCode.PrintingAndValidation.value, 0) and \
                compare_error_code(error_code, ValidationStates.LOG_DATA.value, 2):
            moh_type = MohType.FILES_ERROR
        elif compare_error_code(error_code, HwErrors.PRINTER.value, 1):
            moh_type = MohType.PRINTER_ERROR
        elif compare_error_code(error_code, HwErrors.SCANNER.value, 1):
            moh_type = MohType.SCANNER_ERROR
        elif compare_error_code(error_code, HwErrors.R2R.value, 1):
            moh_type = MohType.ARDUINO_ERROR
        elif compare_error_code(error_code, HwErrors.GATEWAY.value, 1):
            moh_type = MohType.GATEWAY_ERROR
        elif compare_error_code(error_code, HwErrors.SERVER.value, 1):
            moh_type = MohType.SERVER_ERROR
        else:  # any error will pop up a msg
            moh_type = MohType.GENERAL_ERROR
        return moh_type

    def get_all_exceptions(self):

        def show_exceptions(exceptions):
            instructions_str = moh_instruction[MohType.GENERAL_ERROR.value][MainDefaults.DEFAULT_LANGUAGE]
            param_dict_ex = {f'exc{i}': {'value': exc, 'widget_type': 'label', 'columnspan': 3}
                             for i, exc in enumerate(exceptions)}
            param_dict_ins = {
                'space': {'value': '', 'widget_type': 'label'},
                'language': {'text': 'select language', 'value': [lang_code for lang_code in lang_map.keys()]},
                '-INSTRUCTIONS-': {'value': '\n'.join(instructions_str), 'widget_type': 'label', 'columnspan': 3,
                                   'options': {'font': FONT_BUTTONS}},
                'quit': [{'space': {'value': '', 'widget_type': 'label'}},
                         {'quit': {'value': 'Quit', 'widget_type': 'button', 'options': {'bg': 'white', 'fg': 'red'}}}]
            }
            param_dict = {**param_dict_ex, **param_dict_ins}
            wg = WiliotGui(params_dict=param_dict, do_button_config=False, exit_sys_upon_cancel=False, theme='warning',
                           title='Exception')

            wg.add_event(widget_key='language',
                         event_type='<<ComboboxSelected>>',  # need to add args for this event_type
                         command=lambda args: self.update_instruction(app_in=wg, moh_type=MohType.GENERAL_ERROR))
            self.update_instruction(app_in=wg, moh_type=MohType.GENERAL_ERROR)
            wg.add_event(widget_key='quit_quit', event_type='button', command=wg.on_cancel)
            wg.run()

        n_exceptions = self.exception_q.qsize()
        err = []
        for _ in range(n_exceptions):
            exception_str = self.exception_q.get(block=False)
            err.append(exception_str)
            self.logger.warning(exception_str)
        if len(err) > 0:
            show_exceptions(err)

        return err

    def handle_exceptions(self):
        exceptions_status = {'pause_run': False}
        n_exceptions = self.exception_q.qsize()
        for _ in range(n_exceptions):
            exception_str = self.exception_q.get(block=False)
            error_code = get_error_code(exception_str)
            self.logger.warning(f'{ASTERISK} ErrorCode:{error_code} - {exception_str} {ASTERISK}')

            moh_type = self.error_code_to_moh(error_code=error_code)
            exceptions_status = {'pause_run': True, 'exception_str': exception_str,
                                 'error_code': error_code, 'moh_type': moh_type}
            return exceptions_status

        return exceptions_status

    def moh_pop_up(self, error_code, moh_type, msg, scan_again_func=None):
        language_code = MainDefaults.DEFAULT_LANGUAGE  # Default to English
        instructions_str = moh_instruction[moh_type.value][language_code] \
            if moh_type.value in moh_instruction and language_code in moh_instruction[moh_type.value] \
            else ['error instructions are not available']

        moh_name = moh_type.value
        nice_msg = msg.replace(': ', '\n')
        if self.is_gw_r2r:
            moh_name = moh_name.replace('Arduino', 'Gateway')
            nice_msg = nice_msg.replace('Arduino', 'Gateway')

        param_dict = {
            'title': {'value': 'Manual Handling is Needed!', 'widget_type': 'label',
                      'options': {'font': ("Gudea", 18, "bold")}, 'columnspan': 3},
            'moh_name': {'value': moh_name, 'widget_type': 'label', 'options': {'font': FONT_BUTTONS}, 'columnspan': 3},
            'instructions_title': {'value': 'Instructions:', 'widget_type': 'label', 'columnspan': 3,
                                   'options': {'font': ("Gudea", 12, "underline")}},
            'language': {'text': 'select language', 'value': [lang_code for lang_code in lang_map.keys()]},
            '-INSTRUCTIONS-': {'value': '\n'.join(instructions_str), 'widget_type': 'label', 'columnspan': 3,
                               'options': {'font': FONT_BUTTONS}},
            'error_code': {'value': f'ErrorCode:{error_code}', 'widget_type': 'label', 'columnspan': 3},
            'msg': {'value': f'{nice_msg}', 'widget_type': 'label', 'columnspan': 3},
        }

        if self.must_end_run(moh_type):
            param_dict['stop'] = [{'space': {'value': '', 'widget_type': 'label'}},
                                  {'stop': {'value': 'Stop', 'widget_type': 'button'}}]
        elif moh_type == MohType.VALIDATION_FAILED and scan_again_func is not None:
            param_dict['rescan'] = {'value': 'Scan Again', 'widget_type': 'button'}
            param_dict['scan_output'] = {'value': '', 'widget_type': 'label'}

        wg = WiliotGui(params_dict=param_dict, do_button_config=False, exit_sys_upon_cancel=False, theme='warning',
                       height_offset=10, width_offset=0, title='Ask For Handling')

        wg.add_event(widget_key='language',
                     event_type='<<ComboboxSelected>>',  # need to add args for this event_type
                     command=lambda args: self.update_instruction(app_in=wg, moh_type=moh_type))
        self.update_instruction(app_in=wg, moh_type=moh_type)
        if self.must_end_run(moh_type):
            wg.add_event(widget_key='stop_stop', event_type='button', command=wg.on_cancel)
        else:
            if 'rescan' in param_dict:
                wg.add_event(widget_key='rescan', event_type='button',
                             command=lambda: wg.update_widget(widget_key='scan_output', new_value=scan_again_func()))
            wg.button_configs(submit_button_text='Continue', cancel_button_text='Stop')

        values = wg.run()
        return values is not None

    @staticmethod
    def update_instruction(app_in, moh_type):
        values = app_in.get_all_values()
        language_code = lang_map[values['language']]  # Update the language code
        new_instructions = moh_instruction[moh_type.value][language_code] \
            if moh_type.value in moh_instruction and language_code in moh_instruction[moh_type.value] \
            else ['error instructions are not available']
        app_in.update_widget(widget_key='-INSTRUCTIONS-', new_value='\n'.join(new_instructions))

        if values['language'] == 'Hebrew':
            app_in.widgets['-INSTRUCTIONS-'].configure(anchor="e", justify='right')
        else:
            app_in.widgets['-INSTRUCTIONS-'].configure(anchor="w", justify='left')

    def must_end_run(self, moh_type):
        return moh_type in self.critical_moh_types


def get_error_code(msg):
    error_code = 0
    for m in ErrorCode.__members__:
        if f'{m} Exception'.lower() in msg.lower():
            error_code += ErrorCode[m].value
            break

    for h in HwErrors.__members__:
        if f'{h}:'.lower() in msg.lower():
            error_code += HwErrors[h].value
            break

    if 'run:' in msg.lower():
        if compare_error_code(error_code, ErrorCode.Main.value, 0):
            states = MainStates
        elif compare_error_code(error_code, ErrorCode.TagTesting.value, 0):
            states = TagStates
            gws_strs = ['gateway', 'gw ', ' gw', 'did not get ack for !']
            for gw_str in gws_strs:
                if gw_str in msg.lower():
                    error_code_str = str(error_code).zfill(3)
                    error_code = int(error_code_str[0] + str(HwErrors.GATEWAY.value // 10) + error_code_str[2])  #overwrite the second digit
                    break
        elif compare_error_code(error_code, ErrorCode.PrintingAndValidation.value, 0):
            states = ValidationStates
        else:
            return error_code

        for m in states:
            if f'state{m.name}'.lower() in msg.lower():
                error_code += m.value
                break

    return error_code


def compare_error_code(error_code1, error_code2, char_num):
    error_code1_str = str(error_code1).zfill(3)
    error_code2_str = str(error_code2).zfill(3)
    return error_code1_str[char_num] == error_code2_str[char_num]


class ConsolePanelHandlerGUI(logging.Handler):

    def __init__(self, sig):
        logging.Handler.__init__(self)
        self.stream = sig

    def handle(self, record):
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                self.emit(record)
            finally:
                self.release()
        return rv

    def emit(self, record):
        try:
            self.stream.emit(self.format(record))
        except RecursionError:
            raise
        except Exception as e:
            self.handleError(record)


if __name__ == '__main__':
    import argparse
    from PyQt5.QtWidgets import QApplication

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_name', action='store', dest='file_name',
                        help='file_name - Test Configuration File Name (Json Format, *.json)')
    args = vars(parser.parse_args())
    config_file_name = args['file_name']

    app = QApplication([])
    window = Main(test_config_path=config_file_name)
    app.exec_()
