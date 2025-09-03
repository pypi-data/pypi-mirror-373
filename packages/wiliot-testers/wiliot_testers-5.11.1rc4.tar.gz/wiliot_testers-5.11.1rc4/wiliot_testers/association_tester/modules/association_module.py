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

import json
import logging
import os
import multiprocessing
from queue import Queue
import time
import datetime
import pandas as pd
import traceback

from wiliot_core.utils.utils import QueueHandler
from wiliot_tools.association_tool.association_configs import is_asset_code, is_wiliot_code, \
    WILIOT_MIN_NUM_CODE, ASSET_NUM_CODES
from wiliot_tools.association_tool.send_association_to_cloud import CloudAssociation
from wiliot_tools.test_equipment.test_equipment import BarcodeScanner
from wiliot_testers.association_tester.hw_components.r2r_component import R2R, R2RException
from wiliot_testers.association_tester.hw_components.scanner_component import Scanner
from wiliot_testers.offline.modules.offline_printing_and_validation import Printer
pd.options.mode.chained_assignment = None  # default='warn'


ASSOCIATION_Q_SIZE = 200


class AssociatorProcess(CloudAssociation):
    def __init__(self, associate_q=None, associated_status_q=None, stop_event=None, owner_id='', category_id='', time_btwn_request=1,
                 initiator_name=None, common_run_name=''):
        self.associated_status_q = associated_status_q
        super().__init__(associate_q=associate_q, stop_event=stop_event, owner_id=owner_id,
                         is_gcp=False, category_id=category_id, time_btwn_request=time_btwn_request,
                         initiator_name=initiator_name,
                         logger_config={'dir_name': 'association_and_verification_tester',
                                        'folder_name': common_run_name})

    def handle_results(self, message, asset_id, pixel_dict, bad_association):
        bad_association = super().handle_results(message, asset_id, pixel_dict, bad_association)
        element = {'is_associated': int(message['status_code'] // 100) == 2,
                   'associate_status_code': message['status_code'],
                   'asset_code': [asset_id],
                   'wiliot_code': pixel_dict['pixel_id']}
        if self.associated_status_q.full():
            self.logger.warning(f'associated_status_q queue is full. discard {element}')
        else:
            self.associated_status_q.put(element)
        return bad_association


class TagAssociation(object):
    def __init__(self, user_input, stop_event, is_app_running, logger_config, exception_q, run_param_file):
        self.logger = logging.getLogger(logger_config['logger_name'])
        self.user_inputs = user_input
        self.stop_event = stop_event
        self.exception_q = exception_q
        self.is_running = False
        self.is_main_app_running = is_app_running
        self.run_param_file = run_param_file

        self.need_to_check_printer_ack = False
        self.r2r = None
        self.scanner = None
        self.verification_scanner = None
        self.init_hw(logger_config=logger_config)

        # init data:
        self.locations_df = pd.DataFrame()
        # start app
        self.associator_handler = None

        try:
            queue_handler = QueueHandler()
            self.do_association_q = queue_handler.get_multiprocess_queue(queue_max_size=ASSOCIATION_Q_SIZE)
            self.associated_q = queue_handler.get_multiprocess_queue(queue_max_size=ASSOCIATION_Q_SIZE)
            self.scan_verification_q = Queue(maxsize=int(self.user_inputs['scan_verification_offset'])+1)

            if self.user_inputs['do_association']:
                initiator_name = os.environ.get('testerStationName')
                kwargs = {'associate_q': self.do_association_q,
                          'associated_status_q': self.associated_q,
                          'stop_event': stop_event,
                          'owner_id': self.user_inputs['owner_id'],
                          'category_id': self.user_inputs['category_id'],
                          'initiator_name': initiator_name,
                          'common_run_name': os.path.basename(logger_config['logger_path'])}
                # check cloud connection:
                AssociatorProcess(owner_id=kwargs['owner_id'])
                self.associator_handler = multiprocessing.Process(target=AssociatorProcess,
                                                                  kwargs=kwargs)

        except Exception as e:
            self.logger.warning(f'exception during TagAssociation init: {e}')
            raise e

    def init_hw(self, logger_config=None):
        # connect to the r2r:
        self.r2r = R2R(logger_config=logger_config, counter_start_idx=self.user_inputs['first_location'], r2r_type=self.user_inputs['r2r_type'])
        # connect to scanner
        self.scanner = Scanner(logger_name=self.logger.name, max_test_time=self.user_inputs['max_test_time'], 
                               n_codes=int(self.user_inputs['asset_num_codes']) + int(self.user_inputs['wiliot_num_codes']))
        if self.user_inputs['do_scan_verification']:
            self.verification_scanner = BarcodeScanner(timeout='500', is_flash=True)

        # connect to printer
        printing_config = Printer.set_printer_config()
        printing_config['passJobName'] = 'BLANK'
        printing_config['failJobName'] = 'line_'
        printing_config["stringBeforeCounter"] = ''
        self.printing = Printer(is_print=self.user_inputs['do_printing'],
                                exception_queue=self.exception_q,
                                logger_name=self.logger.name,
                                printing_config=printing_config)

    def run_app(self):
        try:
            if self.associator_handler is not None:
                self.associator_handler.start()
        except Exception as e:
            self.logger.warning(f'exception during TagAssociation run_app: {e}')
            raise e
        self.run()

    def run(self):
        self.logger.info('MoveAndScan Start')
        self.is_running = True
        end_of_reel = 0
        max_steps_after_end_of_reel = 2
        while True:
            time.sleep(0)
            cur_time = time.time()
            try:
                if self.stop_event.is_set():
                    self.logger.info('MoveAndScan Stop')
                    self.exit_app()
                    return
                elif self.is_running != self.is_main_app_running():
                    self.is_running = not self.is_running
                    if self.is_running:
                        self.continue_app()
                    else:
                        self.pause_app()
                elif not self.exception_q.empty():
                    time.sleep(0.1)
                    continue

                if self.is_running:
                    # scan
                    time.sleep(0.1)  # wait for r2r to finish moving
                    res = self.scan()
                    if self.need_to_check_printer_ack and not self.printing.get_printing_ack(timeout=3):
                        raise Exception('Did not get ack from printer')
                    self.printing.set_printing_type(res['scan_status'])
                    # print here

                    # add data to dataframe:
                    self.add_data(new_result=res)

                    # add data to scanner verification
                    if self.user_inputs['do_scan_verification']:
                        self.check_scan_verification(res)

                    # wait
                    time_to_wait = max([0, float(self.user_inputs['min_test_time']) - (time.time() - cur_time)])
                    time.sleep(time_to_wait)

                    # move
                    if self.user_inputs['is_step_machine'].lower() == 'yes':
                        if end_of_reel >= max_steps_after_end_of_reel:
                            raise R2RException('End of reel reached')
                        if self.r2r.is_r2r_move_during_test():
                            raise R2RException('R2R moved during test!')
                        self.r2r.move_r2r()
                        if self.r2r.is_r2r_move(timeout=float(self.user_inputs['time_to_move'])):
                            end_of_reel = 0
                        else:
                            end_of_reel += 1
                            self.logger.info(f'End of reel reached: continue step number {end_of_reel} out of {max_steps_after_end_of_reel}')

                    if not self.associated_q.empty():
                        self.merge_associated_data()

                    self.need_to_check_printer_ack = True
                else:
                    time.sleep(1)
                

            except Exception as e:
                self.logger.warning(f'MoveAndScan got exception: {e}')
                if not self.exception_q.full():
                    self.exception_q.put(f'MoveAndScan: {e}')
                    self.logger.warning(f'Main: {(traceback.format_exc())}')

    def add_data(self, new_result):
        new_result['wiliot_code'] = new_result['wiliot_code'] if len(new_result['wiliot_code']) > 0 else ['']
        new_result['asset_code'] = new_result['asset_code'] if len(new_result['asset_code']) > 0 else ['']
        added_data = []
        for wiliot_code in new_result['wiliot_code']:
            for asset_code in new_result['asset_code']:
                new_row = {k: v for k, v in new_result.items()}
                new_row['wiliot_code'] = wiliot_code
                new_row['asset_code'] = asset_code
                added_data.append(new_row)

        self.update_last_run_params(added_data[-1])
        self.locations_df = pd.concat([self.locations_df, pd.DataFrame(added_data)], ignore_index=True)

    def update_last_run_params(self, new_data):
        with open(self.run_param_file, 'rb') as f:
            last_run_params = json.load(f)
        last_run_params['last_location'] = new_data['location']
        last_run_params['last_run_name'] = self.user_inputs['run_name']
        if new_data['asset_code']:
            last_run_params['last_asset_id'] = new_data['asset_code']
            last_run_params['last_asset_location'] = new_data['location']
        with open(self.run_param_file, 'w') as f:
            json.dump(last_run_params, f)

    def scan(self):
        complete_label_read = {'location': self.r2r.get_counter(),
                               'wiliot_code': [], 'asset_code': [], 'timestamp': 0,
                               'scan_status': False,
                               'is_associated': False, 'associate_status_code': ''}

        scanned_codes = self.scanner.scan()

        self.check_scanned_codes_and_update_result(scanned_codes, complete_label_read)

        # send data to cloud
        if self.user_inputs['do_association'] and complete_label_read['scan_status']:
            if self.do_association_q.full():
                self.logger.warning(f'do_association_q queue is full. discard  {complete_label_read}')
            else:
                self.do_association_q.put(complete_label_read)

        # end of label scanning:
        self.check_end_of_label(complete_label_read)
        return complete_label_read
    
    def check_scan_verification(self, res):
        # put the asset code in the queue
        if not self.scan_verification_q.full():
            self.scan_verification_q.put(res['asset_code'][0] if res['scan_status'] else None)
        else:
            self.logger.warning(f'scan_verification_q queue is full. discarded {res["asset_code"][0]}')
            raise Exception('scan_verification_q is full')

        # if queue is full, scan code and compare
        if self.scan_verification_q.full():
            exp_code = self.scan_verification_q.get()
            get_code = self.verification_scanner.scan_and_flush()[0]
            self.logger.info(f'Validation Scanner: expected {exp_code}, got {get_code}')
            if exp_code is not None:
                if not exp_code == get_code:
                    if not self.exception_q.full():
                        self.exception_q.put(f'Validation Scanner: expected {exp_code}, but no asset code scanned')
            else:
                if get_code:
                    if not self.exception_q.full():
                        self.exception_q.put(f'Validation Scanner: expected no asset code, got {get_code}')

    def check_scanned_codes_and_update_result(self, codes_in, complete_label_read):
        time_now = datetime.datetime.now().timestamp()
        for code in codes_in:
            if is_wiliot_code(code):
                complete_label_read['wiliot_code'].append(code)
                complete_label_read['timestamp'] = time_now
            elif is_asset_code(code):
                complete_label_read['asset_code'].append(code)
                complete_label_read['timestamp'] = time_now

        if len(complete_label_read['asset_code']) == 0:
            raise Exception(f'No asset code in scan')

        pass_criteria = len(complete_label_read['wiliot_code']) >= int(self.user_inputs['wiliot_num_codes']) \
                and len(complete_label_read['asset_code']) == int(self.user_inputs['asset_num_codes'])
        if self.user_inputs['asset_location'] == 'none':
            complete_label_read['scan_status'] = pass_criteria
        else:
            if (self.user_inputs['asset_location'] == 'first' and is_wiliot_code(codes_in[-1])) or (
                    self.user_inputs['asset_location'] == 'last' and is_wiliot_code(codes_in[0])):
                complete_label_read['scan_status'] = True
                self.logger.info(f'Found all codes for association! '
                                 f'Wiliot:{complete_label_read["wiliot_code"]}, '
                                 f'Asset: {complete_label_read["asset_code"]}')
            else:
                complete_label_read['scan_status'] = False
                raise Exception(f'Scanned codes from different labels '
                                f'Wiliot:{complete_label_read["wiliot_code"]}, '
                                f'Asset: {complete_label_read["asset_code"]}')

    def check_end_of_label(self, label_read):
        if label_read is None:
            return
        if len(label_read['asset_code']) == 0 and len(label_read['wiliot_code']) == 0:
            self.logger.info(f"No codes were read")
        if len(label_read['asset_code']) < ASSET_NUM_CODES:
            self.logger.info(f"Not enough Asset codes were scanned: {label_read['asset_code']}")
        elif len(label_read['asset_code']) > ASSET_NUM_CODES:
            self.logger.info(f"Too many Asset codes were scanned: {label_read['asset_code']}")
        elif len(label_read['wiliot_code']) < WILIOT_MIN_NUM_CODE:
            self.logger.info(f"Not enough Wiliot codes were scanned: {label_read['wiliot_code']}")

    def merge_associated_data(self):
        n = self.associated_q.qsize()
        for _ in range(n):
            associated = self.associated_q.get(block=False)
            print(f'associated: {associated}')
            self.locations_df.loc[(self.locations_df['asset_code'].isin(associated['asset_code'])) & (
                    self.locations_df['wiliot_code'].isin(associated['wiliot_code'])),
                                  ['is_associated', 'associate_status_code']] = [associated['is_associated'],
                                                                                 associated['associate_status_code']]

    def pause_app(self):
        self.need_to_check_printer_ack = False
        self.r2r.pause_app()
        self.scanner.disconnect()

    def continue_app(self):
        self.r2r.continue_app()
        self.scanner.reconnect()

    def exit_app(self):
        try:
            time.sleep(2)
            self.r2r.exit_app()
            self.scanner.disconnect()
            if self.associator_handler is not None:
                self.associator_handler.join(10)
                if self.associator_handler.is_alive():
                    self.logger.warning('associator process is still running')
            if not self.associated_q.empty():
                self.merge_associated_data()
        except Exception as e:
            self.logger.warning(f'MoveAndScan: exit_app: got exception: {e}')
            if not self.exception_q.full():
                self.exception_q.put(f'MoveAndScan: exit_app: {e}')
                self.logger.warning(f'Main: {(traceback.format_exc())}')


    def get_locations_df(self):
        return self.locations_df


if __name__ == '__main__':
    from wiliot_core import set_logger
    RUN_TIME = 60

    tag_assoc_logger_path, tag_assoc_logger = set_logger(app_name='TagAssociation', dir_name='tag_association',
                                                         file_name='association_log')
    stop_event = multiprocessing.Event()
    user_input = {
        'min_test_time': '1.5',
        'max_test_time': '5',
        'time_to_move': '0.5',
        'do_association': 'no',
        'is_step_machine': 'yes',
        'asset_location': 'last',
        'owner_id': 'wiliot-ops',
        'category_id': '86fd9f07-38b0-466f-b717-2e285b803f5c'
    }
    ta = TagAssociation(user_input=user_input, stop_event=stop_event,
                        logger_config={'logger_name': tag_assoc_logger.name, 'logger_path': tag_assoc_logger_path})

    t_i = time.time()
    while time.time() - t_i < RUN_TIME:
        time.sleep(1)
        df = ta.get_locations_df()
        print(f'n unique locations: {len(df)}')
    # stop run
    stop_event.set()

    df = ta.get_locations_df()
    df_path = tag_assoc_logger_path.replace('.log', '_locations_df.csv')
    print(f'saving data at: {df_path}')
    df.to_csv(df_path, index=False)

    print('done')
