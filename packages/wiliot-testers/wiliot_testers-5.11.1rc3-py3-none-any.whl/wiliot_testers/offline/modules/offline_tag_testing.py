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
import datetime
import numpy as np
from enum import Enum
import pandas as pd

from wiliot_api import WiliotCloudError
from wiliot_core import InlayTypes
from wiliot_tools.test_equipment.test_equipment import Attenuator, YoctoSensor
from wiliot_testers.wiliot_tester_tag_test import WiliotTesterTagTest
from wiliot_testers.wiliot_tester_tag_result import FailureCodes, WiliotTesterTagResultList
from wiliot_testers.offline.configs.global_vars_and_enums import TagTestingDefaults
from wiliot_testers.offline.modules.offline_r2r_controller import R2R
from wiliot_testers.offline.modules.offline_utils import connect_to_cloud


class TagTestingException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(f'TagTesting Exception: {self.message}')


class R2RException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'R2R: {msg}')


class MissingLabelException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'Missing Label: {msg}')


class AttenuatorException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'Attenuator: {msg}')


class SensorException(TagTestingException):
    def __init__(self, msg):
        super().__init__(f'Sensor: {msg}')


MAX_MAIN_STATES = 5


class TagStates(Enum):
    IDLE = 0
    STOP = 99
    WAIT_MOH = 88
    GET_TRIGGER = 1
    START_TEST = 2
    TAG_TEST = 3
    PROCESS_TEST = 4
    END_TEST = 5
    WAIT_END = 6
    NEXT_TAG = 7


class TagTesting(object):
    def __init__(self, test_start_event, test_end_event, validation_end_event, stop_app_event, moh_object,
                 exception_queue, tag_results_queue, log_obj, test_object, user_config=None, hw_config=None):
        self.test_start_event = test_start_event
        self.test_end_event = test_end_event
        self.validation_end_event = validation_end_event
        self.stop_app_event = stop_app_event
        self.exception_q = exception_queue
        self.tag_results_q = tag_results_queue
        self.moh = moh_object
        self.test = test_object
        self.logger = logging.getLogger(log_obj.get_logger_name())
        self.user_config = user_config
        self.tested = 0
        self.missing_labels = 0
        self.missing_label_locations = []
        self.need_to_manual_trigger = False
        self.tag_test_running = False
        self.all_selected_tags = pd.DataFrame()
        self.duplicated_adva_diff_tags = 0
        self.all_duplicated_tags = []
        self.all_tags = []
        self.is_passed_list = []
        self.ttfp_list = []
        self.last_state = TagStates.IDLE
        self.is_gen_checked = False
        self.is_r2r = user_config['isR2R'].lower() == 'yes' and user_config['typeR2R'].lower() == 'gateway'
        prod_owner_id = self.user_config.get('defaultClient', self.user_config['OwnerId'])
        self.client = connect_to_cloud(env='prod', owner_id=prod_owner_id,
                                        logger=self.logger)

        self.is_init = False
        self.r2r = None
        try:
            # init tester class
            self.wiliot_tester = WiliotTesterTagTest(
                selected_test=self.user_config['testName'],
                logger_name=self.logger.name,
                logger_result_name=log_obj.get_results_logger_name(),
                logger_gw_name=log_obj.get_gw_logger_name(),
                stop_event_trig=self.stop_app_event,
                inlay=InlayTypes(self.user_config['inlay']),
                dir_for_gw_log=log_obj.get_test_folder(),
                gw_test_cmds=self.get_additional_gw_cmds(hw_config=hw_config),
                client=self.client,
            )
            self.gw_obj = self.wiliot_tester.get_gw_object()

            # init timeout for trigger:
            self.logger.info(f'Maximum time for gw trigger (i.e. missing label) '
                             f'is {TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL}')

            # init r2r if relevant:
            if self.is_r2r:
                self.r2r = R2R(logger_name=log_obj.get_logger_name(),
                               exc_obj=R2RException,
                               gw_obj=self.gw_obj)

            # init external hw
            self.attenuator_handle = AttenuatorHandle(logger_name=self.logger.name, exception_q=exception_queue,
                                                      attenuator_configs=hw_config)
            self.sensors_handle = ExternalSensorHandle(logger_name=self.logger.name,
                                                       exception_q=exception_queue,
                                                       sensor_configs=hw_config)
            self.is_init = True

        except Exception as e:
            if isinstance(e, TagTestingException):
                self.exception_q.put(f'init: {e}', block=False)
            else:
                self.exception_q.put(TagTestingException(f'init: {e}').__str__(), block=False)

    @staticmethod
    def get_additional_gw_cmds(hw_config):
        if hw_config is None:
            return None
        if hw_config.get('printingBidirectionalMovement', 'No').lower() == 'yes':
            gpio = TagTestingDefaults.PRINTER_DIRECTION_GPIO.replace('.', '').upper()
            return [f'!cmd_gpio CONTROL_IN {gpio} 0']  # to get ack from printer cart

    def run(self):
        tester_res = WiliotTesterTagResultList()  # Empty list
        state = TagStates.IDLE
        if self.is_r2r:
            self.r2r.move_to_the_first_tag()

        while True:
            time.sleep(0)
            try:
                state = self.update_state(state)
                self.logger.info(f'TagTesting: start state {state}')
                if state == TagStates.GET_TRIGGER:
                    self.get_trigger()

                elif state == TagStates.START_TEST:
                    self.start_test()

                elif state == TagStates.TAG_TEST:
                    tester_res = self.tag_test()
                    self.need_to_manual_trigger = False

                elif state == TagStates.PROCESS_TEST:
                    self.process_test(tester_res=tester_res)

                elif state == TagStates.END_TEST:
                    self.end_test(tester_res=tester_res)

                elif state == TagStates.WAIT_END:
                    if self.is_r2r:
                        # wait till event end_of_validation is set
                        self.wait_for_new_event(
                            event=self.validation_end_event,
                            time_to_wait=TagTestingDefaults.EVENT_WAIT_TIME)
                        self.gw_obj.clear_rsp_str_input_q()

                elif state == TagStates.NEXT_TAG:
                    if self.is_r2r:
                        # send signal to the r2r to move
                        self.r2r.move_r2r()

                elif state == TagStates.STOP:
                    self.logger.info('Stop running TagTesting main loop')
                    break

                elif state == TagStates.WAIT_MOH:
                    self.wait_for_moh()

                self.logger.info(f'TagTesting: end state {state}')

            except Exception as e:
                if isinstance(e, TagTestingException):
                    self.exception_q.put(f'run: state{state.name}: {e}', block=False)
                elif isinstance(e, WiliotCloudError):
                    self.exception_q.put(TagTestingException(f'run: state{state.name}: server: {e}').__str__(), block=False)
                else:
                    self.exception_q.put(TagTestingException(f'run: state{state.name}: {e}').__str__(), block=False)

                if state == TagStates.GET_TRIGGER:
                    self.need_to_manual_trigger = True
                elif state == TagStates.TAG_TEST:
                    tester_res = WiliotTesterTagResultList()
                    tester_res.set_total_fail_bin(fail_code=FailureCodes.GW_ERROR, overwrite=True)
                    self.tag_test_running = False

                elif state == TagStates.PROCESS_TEST:
                    tester_res.set_total_fail_bin(fail_code=FailureCodes.SOFTWARE_GENERAL_ERROR, overwrite=True)
                elif state == TagStates.END_TEST or state == TagStates.WAIT_MOH:
                    self.logger.warning(f'TagTesting Got exception during {state}: {e}')
                elif state == TagStates.NEXT_TAG:
                    state = TagStates.WAIT_END

        self.stop()

    def update_state(self, state):
        # after MOH was done, continue to the next state
        if state == TagStates.WAIT_MOH:
            state = self.last_state

        # when event occurred
        if self.stop_app_event.is_set():
            if state == TagStates.TAG_TEST or state == TagStates.PROCESS_TEST:
                pass  # finish the cycle
            else:
                self.last_state = state
                state = TagStates.STOP
        elif self.moh.get_manual_operation_is_needed():
            self.last_state = state
            state = TagStates.WAIT_MOH

        # main flow
        if state == TagStates.IDLE:
            state = TagStates.GET_TRIGGER
        elif state == TagStates.GET_TRIGGER:
            state = TagStates.START_TEST
        elif state == TagStates.START_TEST:
            state = TagStates.TAG_TEST
        elif state == TagStates.TAG_TEST:
            state = TagStates.PROCESS_TEST
        elif state == TagStates.PROCESS_TEST:
            state = TagStates.END_TEST
        elif state == TagStates.END_TEST:
            state = TagStates.WAIT_END
        elif state == TagStates.WAIT_END:
            state = TagStates.NEXT_TAG
        elif state == TagStates.NEXT_TAG:
            state = TagStates.GET_TRIGGER

        return state

    def wait_for_new_event(self, event, time_to_wait=TagTestingDefaults.POST_RUN_WAIT_TIME):
        t_start = time.time()
        while not event.is_set():
            if self.stop_app_event.is_set():
                self.logger.info('Tag Testing: stop application during waiting for event')
                time.sleep(TagTestingDefaults.POST_RUN_WAIT_TIME)
                break
            elif self.moh.get_manual_operation_is_needed():
                self.wait_for_moh()
                t_start = time.time()
            event.wait(0.1)
            dt = time.time() - t_start

            if dt > time_to_wait and not self.moh.get_manual_operation_is_needed():
                raise TagTestingException('wait_for_new_event: did not receive ack for '
                                          'starting/ending tag test')
        event.clear()

    def update_missing_label_parameters(self):
        self.missing_labels += 1
        if self.user_config['sensorOffset'] != '':
            self.missing_label_locations.append(self.tested + int(self.user_config['sensorOffset']) + 1)
            self.logger.info(f'TagTesting: update_missing_label_parameters: '
                             f'estimate Missing Label at location: {self.missing_label_locations[-1]}')

    def get_trigger(self):
        pulse_received = self.wiliot_tester.wait_for_trigger(
            wait_for_gw_trigger=TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL)
        if not pulse_received:
            while self.moh.get_manual_operation_is_needed():
                self.wait_for_moh()
                if self.stop_app_event.is_set():
                    return
                pulse_received = self.wiliot_tester.wait_for_trigger(
                    wait_for_gw_trigger=TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL)
                if pulse_received:
                    break
            if not pulse_received:
                self.update_missing_label_parameters()
                if TagTestingDefaults.ENABLE_MISSING_LABEL and \
                        self.missing_labels < TagTestingDefaults.MAX_MISSING_LABEL_ENGINEERING + 1:
                    self.need_to_manual_trigger = True
                    self.logger.info((f'MISSING LABEL. no trigger was received for '
                                      f'{TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL} seconds. Continue to test.'))
                    if self.is_r2r:
                        self.r2r.send_stop_to_r2r()
                    return
                if not self.stop_app_event.is_set():
                    raise MissingLabelException(f'MISSING LABEL. no trigger was received for '
                                                f'{TagTestingDefaults.TIMEOUT_FOR_MISSING_LABEL} seconds')

    def start_test(self):
        self.test_start_event.set()
        if self.attenuator_handle.enable:
            self.attenuator_handle.set_dynamic_value()
        if self.is_r2r:
            if self.test.get_total_test_time() > TagTestingDefaults.MAX_R2R_WAIT_TIME:
                self.r2r.send_stop_to_r2r()

    def gw_reset_and_config(self):
        if not self.tag_test_running:
            self.wiliot_tester.gw_reset_and_config()
            self.wiliot_tester.init_gw_test(is_start_gw_app=False)

    def tag_test(self):
        self.tested += 1
        self.tag_test_running = True
        if not self.is_printing_calibration():
            tester_res = self.wiliot_tester.run(wait_for_gw_trigger=None,
                                                need_to_manual_trigger=self.need_to_manual_trigger)
        else:
            tester_res = WiliotTesterTagResultList()
            self.gw_obj.stop_gw_app()
            time.sleep(TagTestingDefaults.TIME_BETWEEN_TEST_PRINTING)
        self.tag_test_running = False

        return tester_res

    def is_test_running(self):
        return self.tag_test_running

    def is_correct_tag_gen(self, adva_in):
        self.is_gen_checked = True
        if len(adva_in) < 2:
            return True
        if adva_in.lower()[:2] >= '06':
            return self.user_config['gen'].lower() == 'gen3'
        return self.user_config['gen'].lower() == 'gen2'   # adva_in.lower()[:2] < '06'

    def duplication_process(self, tester_res, selected_tag):
        prod_owner_id = self.user_config.get('defaultClient', self.user_config['OwnerId'])
        payload = ''
        try:
            payload_cur = tester_res.get_payload()
            ex_id_cur = self.client.resolve_payload(payload=payload_cur,
                                                    owner_id=prod_owner_id, 
                                                    verbose=True)
            self.logger.info(f'resolve for current {selected_tag} the external id: {ex_id_cur}')
            if self.all_selected_tags.loc[selected_tag, 'external_ids'] != '':
                duplicated = ex_id_cur['externalId'] in self.all_selected_tags.loc[selected_tag, 'external_ids']
            else:
                payload_pre = self.all_selected_tags.loc[selected_tag, 'payload']
                ex_id_prev = self.client.resolve_payload(payload=payload_pre,
                                                        owner_id=prod_owner_id, 
                                                        verbose=True)
                duplicated = ex_id_prev['externalId'] == ex_id_cur['externalId']
                self.all_selected_tags.loc[selected_tag, 'external_ids'] += f"{ex_id_prev['externalId']},"
                self.logger.info(f'resolve for previous {selected_tag} the external id: {ex_id_prev}')
            
            if not duplicated:
                self.all_selected_tags.loc[selected_tag, 'external_ids'] += f"{ex_id_cur['externalId']},"
                self.logger.info(f'found two tags with the same adv_address but different external ids: {self.all_selected_tags.loc[selected_tag, "external_ids"]}')
                return False
        except WiliotCloudError as e:
            self.logger.warning(f'could not resolve duplication payload for {selected_tag}, {payload} due to {e}')
        
        return True
        

    def process_test(self, tester_res):
        is_pass = False
        tag_current_location = self.tested - 1
        if self.is_printing_calibration():
            tester_res.set_total_test_status(True)
            is_pass = True
        elif tester_res.get_total_test_status():
            selected_tag = tester_res.check_and_get_selected_tag_id()
            if selected_tag == '':
                if not self.wiliot_tester.run_all and not self.is_printing_calibration():
                    raise TagTestingException("run: ANALYSIS TEST: Test Status is PASS but could not select tag")
                else:
                    is_pass = True

            elif selected_tag in self.all_selected_tags.index:
                # Duplication
                self.logger.info(f'start to analyze duplication case for location: {tag_current_location}')
                is_duplicated = self.duplication_process(tester_res=tester_res, selected_tag=selected_tag)
                if is_duplicated:
                    # found duplication:
                    tester_res.set_total_fail_bin(FailureCodes.DUPLICATION_OFFLINE)
                    tester_res.set_packet_status(adv_address=selected_tag, status='duplication')
                    self.all_duplicated_tags.append(selected_tag)
                    self.logger.warning(f'DUPLICATION for Adva: {selected_tag}')
                else:
                    # PASS
                    is_pass = True
                    self.duplicated_adva_diff_tags += 1
            else:
                # PASS
                self.all_selected_tags = pd.concat([self.all_selected_tags, pd.DataFrame({'payload': tester_res.get_payload(), 'external_ids': ''}, index=[selected_tag])])
                is_pass = True

            if not self.is_gen_checked and not self.is_correct_tag_gen(selected_tag):
                raise Exception(f'Mismatch between tag gen: {selected_tag} and '
                                f'specified gen: {self.user_config["gen"]}')
        else:
            if tester_res.get_total_fail_bin() == FailureCodes.NO_RESPONSE.value:
                self.logger.info(f'TagTesting: process_test: got NO_RESPONSE at location: {tag_current_location}')
                if self.tested in self.missing_label_locations:
                    tester_res.set_total_fail_bin(FailureCodes.MISSING_LABEL, overwrite=True)
                    self.logger.info(f'set tag location {tag_current_location} to MISSING lABEL fail bin')
        if not is_pass:
            self.logger.warning(f'Tag {tag_current_location} Failed - {tester_res.get_total_fail_bin(as_name=True)}')
        if self.tested in self.missing_label_locations and tester_res.get_total_fail_bin() != FailureCodes.MISSING_LABEL.value:
            self.missing_labels -= 1
        self.all_tags += tester_res.get_test_unique_adva()
        self.all_tags = list(set(self.all_tags))
        self.is_passed_list.append(is_pass)

    def get_all_duplicated_tags(self):
        return self.all_duplicated_tags

    def is_printing_calibration(self):
        return self.user_config['printingFormat'].lower() == 'test' and self.user_config['toPrint'].lower() == 'yes'

    @staticmethod
    def calculating_ttfp_avg(ttfp_list):
        ttfp_list_no_nan = [x for x in ttfp_list if not np.isnan(x)]
        if ttfp_list_no_nan:
            return np.mean(ttfp_list_no_nan)
        return float(-1)

    def end_test(self, tester_res):
        sensor_warning = None
        self.ttfp_list.append(tester_res.get_total_ttfp())
        test_data = {'tested': self.get_tested(),
                     'passed': self.get_passed(),
                     'responded': self.get_responded(),
                     'missing_label': self.get_missing_label_count(),
                     'ttfp_avg': self.calculating_ttfp_avg(self.ttfp_list),
                     'crc_environment_previous': self.wiliot_tester.get_wrong_crc()
                     }
        if self.sensors_handle.enable:
            try:
                sensors_out = self.sensors_handle.get_measurement()
                test_data = {**test_data, **sensors_out}
            except Exception as e:
                self.logger.warning(f'end test: could not read from sensor due to {e}')
                sensor_warning = e
        tester_res.set_test_info(test_info=test_data)
        if self.tag_results_q.full():
            raise TagTestingException('end_test: tag results queue is full - error in offset definition')
        self.tag_results_q.put(tester_res, block=False)
        self.test_end_event.set()
        if sensor_warning is not None:
            raise sensor_warning

    def wait_for_moh(self):
        self.logger.info('TagTesting: wait for manual operation handling')
        try:
            if self.is_r2r:
                self.r2r.send_stop_to_r2r()
        except Exception as e:
            self.logger.warning(f'Could not stop R2R during wait for manual operation handling due to {e}')
        while True:
            time.sleep(1)
            if not self.moh.get_manual_operation_is_needed():
                break
            if self.stop_app_event.is_set():
                break

    def get_tested(self):
        return self.tested

    def get_responded(self):
        return len(self.all_tags) + self.duplicated_adva_diff_tags

    def get_passed(self):
        return len(self.all_selected_tags) + self.duplicated_adva_diff_tags

    def get_missing_label_count(self):
        return self.missing_labels

    def get_is_passed_list(self):
        return self.is_passed_list.copy()

    def get_ttfp_list(self):
        return self.ttfp_list

    def stop(self):
        if self.is_r2r:
            self.post_run_validation()
            self.r2r.exit()
        self.wiliot_tester.exit_tag_test()
        self.logger.info('TagTesting Thread is done')

    def post_run_validation(self):
        self.logger.info('TagTesting: start post run validation...')
        if self.last_state == TagStates.WAIT_END:
            stage = 'move'  # wait, move, trigger
        elif self.last_state in [TagStates.NEXT_TAG, TagStates.GET_TRIGGER, TagStates.STOP]:
            stage = 'trigger'  # wait, move, trigger
        else:
            stage = 'wait'  # wait, move, trigger
        while True:
            if stage == 'wait':
                time.sleep(TagTestingDefaults.TIME_BETWEEN_TEST_PRINTING)
                self.validation_end_event.wait(TagTestingDefaults.POST_RUN_WAIT_TIME)
                if not self.validation_end_event.is_set():
                    break
                stage = 'move'
            elif stage == 'move':
                self.validation_end_event.clear()
                try:
                    self.r2r.move_r2r()
                    gw_answer = self.gw_obj.read_specific_message(msg="Start Production Line GW",
                                                                read_timeout=TagTestingDefaults.EVENT_WAIT_TIME)
                    self.logger.info(f'TagTesting: post_run_validation: gw rsp: {gw_answer}')
                except Exception as e:
                    self.logger.warning(f'TagTesting: post_run_validation: error during moving to the next tag: {e}')
                stage = 'trigger'
            elif stage == 'trigger':
                self.test_start_event.set()
                try:
                    self.gw_obj.stop_gw_app()
                except Exception as e:
                    self.logger.warning(f'TagTesting: post_run_validation: error during trigger test start/end events: {e}')
                self.test_end_event.set()
                stage = 'wait'

            else:
                raise Exception(f'TagTesting: post_run_validation: stage is not supported: {stage}')

        self.logger.info('TagTesting: end post run validation')

    def get_gw_version(self):
        return self.wiliot_tester.get_gw_version()

    def get_gw_gpio_signal(self):
        signals_out = []
        t_i = datetime.datetime.now()
        dt = 0.0
        while dt < TagTestingDefaults.PRINTER_SIGNAL_TIMEOUT:
            try:
                time.sleep(TagTestingDefaults.PRINTER_SIGNAL_SLEEP_TIME)
                all_signals = self.gw_obj.get_gw_signals()
                if all_signals:
                    signals_out = [sig['raw'] for sig in all_signals]
                    self.logger.info(f'got the following signals: {signals_out}')
                    break
            except Exception as e:
                self.logger.warning(f'get_gw_gpio_signal got exception, try again ({e})')
                time.sleep(TagTestingDefaults.PRINTER_SIGNAL_SLEEP_TIME)
            dt = (datetime.datetime.now() - t_i).total_seconds()
        return signals_out


class AttenuatorHandle(object):
    def __init__(self, logger_name, exception_q, attenuator_configs=None):
        self.logger = logging.getLogger(logger_name)
        self.exception_q = exception_q
        self.enable = True
        if attenuator_configs is None or attenuator_configs['AutoAttenuatorEnable'].lower() == 'no':
            self.logger.info('Attenuator is disable')
            self.enable = False
            return

        self.attenuator_configs = attenuator_configs
        if self.attenuator_configs['attnComport'].upper() == 'AUTO':
            self.attenuator = Attenuator('API').GetActiveTE()
        else:
            self.attenuator = Attenuator('API', comport=f'COM{self.attenuator_configs["attnComport"]}').GetActiveTE()
        current_attn = self.attenuator.Getattn()
        self.logger.info(f'Attenuator is connected at port {self.attenuator.comport} and set to: {current_attn}')
        self.set_value()

    def set_value(self, attenuator_val=None):
        if attenuator_val is None:
            attenuator_val = self.attenuator_configs['attnval']
        try:
            set_attn_status = self.attenuator.Setattn(int(attenuator_val))
        except Exception as e:
            raise AttenuatorException(f'AttenuatorHandle Exception: set_value: {e}')
        if set_attn_status == attenuator_val:
            self.logger.info(f'Attenuation is set to {attenuator_val} dB')
        else:
            raise AttenuatorException(f'AttenuatorHandle Exception: set_value: failed to set attenuation value '
                                      f'(expected: {attenuator_val}, current: {set_attn_status})')

    def set_dynamic_value(self):
        pass


class ExternalSensorHandle(object):
    def __init__(self, logger_name, exception_q, sensor_configs=None):
        self.logger = logging.getLogger(logger_name)
        self.exception_q = exception_q
        self.sensor_configs = sensor_configs

        self.enable = True
        if sensor_configs is None or self.sensor_configs['sensorsEnable'].lower() == 'no':
            self.logger.info('External Sensors measurement is disable')
            self.enable = False
            return

        self.sensor = None
        self.sensor_measurements = []
        try:
            self.connect()
        except Exception as e:
            raise SensorException(f'ExternalSensorHandle Exception: init: {e}')

    def connect(self):
        self.sensor = YoctoSensor(self.logger)
        if self.sensor.temperature_sensor is not None:
            self.logger.info(f'Connected to temperature sensor')
            self.sensor_measurements.append({'name': 'temperature', 'func': self.sensor.get_temperature})
        if self.sensor.humidity_sensor is not None:
            self.logger.info(f'Connected to humidity sensor')
            self.sensor_measurements.append({'name': 'humidity', 'func': self.sensor.get_humidity})
        if self.sensor.light_sensor is not None:
            self.logger.info(f'Connected to light sensor')
            self.sensor_measurements.append({'name': 'light', 'func': self.sensor.get_light})

    def get_measurement(self):
        meas_out = {}
        for meas in self.sensor_measurements:
            try:
                cur_value = meas['func']()
                if cur_value == float('nan') or (isinstance(cur_value, int) and cur_value == 0):
                    raise SensorException(f'ExternalSensorHandle: Could not measure {meas["name"]} from sensor')
                else:
                    self.logger.info(f'Measured {meas["name"]} from sensor: {cur_value}')
                    meas_out[f'{meas["name"]}_sensor'] = cur_value
            except Exception as e:
                raise SensorException(f'ExternalSensorHandle: get_measurement: {e}')
        return meas_out
