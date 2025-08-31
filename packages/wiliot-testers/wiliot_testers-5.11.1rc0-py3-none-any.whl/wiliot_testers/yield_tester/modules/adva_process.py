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
import time

from wiliot_core import CommandDetails, WiliotGateway, ActionType, DataType
from wiliot_core import Packet, PacketList


MAX_TIME_WITHOUT_PACKETS = 120
MAX_SUB1G_POWER = 29
MAX_BLE_POWER = 22


class AdvaProcess(object):
    """
    Counting the number of unique advas
    """

    def __init__(self, stop_event, logger, adva_process_inputs, packet_and_triggers_q, get_sensors_values, ignore_adva_before_triggers=True):

        self.unq_packets_new_triggers = packet_and_triggers_q
        self.seen_advas = set()
        self.adva_process_inputs = adva_process_inputs
        self.inlay = adva_process_inputs['selected_inlay']
        self.advas_before_tags = set() if ignore_adva_before_triggers else None
        self.stopped_by_user = False
        self.gw_error_connection = False
        self.second_without_packets = False  # This is only used to print no packets after one minute
        self.gw_instance = None
        self.logger = logger
        self.stop = stop_event
        self.last_change_time = 0
        self.n_triggers = 0
        self.needed_time_between_matrices = float(self.adva_process_inputs['user_inputs'].get('time_between_matrices_sec', 0))
        self.get_sensors_value = get_sensors_values

        self.init_gw(self.adva_process_inputs['listener_path'])
        self.gw_reset_config()

    def init_gw(self, listener_path=None):
        try:
            if self.gw_instance is None:
                self.gw_instance = WiliotGateway(auto_connect=True,
                                                 logger_name=self.logger.name,
                                                 log_dir_for_multi_processes=listener_path,
                                                 np_max_packet_in_buffer_before_error=10,
                                                 allow_reset_time=False)

            else:
                # reconnect
                is_connected = self.gw_instance.is_connected()
                if is_connected:
                    self.gw_instance.close_port()
                self.gw_instance.open_port(self.gw_instance.port, self.gw_instance.baud)

            is_connected = self.gw_instance.is_connected()
            if is_connected:
                self.gw_instance.start_continuous_listener()
            else:
                self.logger.warning("Couldn't connect to GW in main thread")
                raise Exception(f"Couldn't connect to GW in main thread")

        except Exception as ee:
            raise Exception(f"Couldn't connect to GW in main thread, error: {ee}")

    def get_gw_version(self):
        if self.gw_instance:
            return self.gw_instance.get_gw_version()[0]
        return ''

    def gw_reset_config(self, start_gw_app=False):
        """
        Configs the gateway
        """
        if self.gw_instance.connected:
            self.gw_instance.reset_gw()
            self.gw_instance.reset_listener()
            time.sleep(2)
            if not self.gw_instance.is_gw_alive():
                self.logger.warning('gw_reset_and_config: gw did not respond')
                raise Exception('gw_reset_and_config: gw did not respond after rest')

            gw_config = self.inlay

            cmds = {CommandDetails.scan_ch: gw_config['received_channel'],
                    CommandDetails.time_profile: gw_config['time_profile_val'],
                    CommandDetails.set_energizing_pattern: gw_config['energy_pattern_val'],
                    CommandDetails.set_sub_1_ghz_power: [MAX_SUB1G_POWER],
                    CommandDetails.set_scan_radio: self.gw_instance.get_cmd_symbol_params(
                        freq_str=gw_config['symbol_val']),
                    CommandDetails.set_rssi_th: self.adva_process_inputs['user_inputs'].get('rssi_threshold', 0),
                    }
            output_power_cmds = self.gw_instance.get_cmds_for_abs_output_power(abs_output_power=MAX_BLE_POWER)
            cmds = {**cmds, **output_power_cmds}
            self.gw_instance.set_configuration(cmds=cmds, start_gw_app=False, read_max_time=1)
            pin_num = self.adva_process_inputs['user_inputs'].get('pin_number')
            cmd = '!cmd_gpio CONTROL_IN P%s 0' % pin_num.zfill(3)
            self.gw_instance.write(cmd, must_get_ack=True)
            user_commands = self.adva_process_inputs['user_inputs'].get('gw_commands', [])
            for cmd in user_commands:
                self.gw_instance.write(cmd, must_get_ack=True)
            # start GW applicaion if needed
            self.gw_instance.set_configuration(start_gw_app=start_gw_app)
        else:
            raise Exception('Could NOT connect to GW')

    def set_stopped_by_user(self, stopped):
        self.stopped_by_user = stopped

    def check_new_tags(self):
        """
        Does the process of adding a new Packet to our collection
        """
        new_packet_list = PacketList()
        if not self.gw_instance.is_data_available():
            return new_packet_list, False
        
        raw_packets_in = self.gw_instance.get_packets(action_type=ActionType.ALL_SAMPLE, data_type=DataType.RAW,
                                                      tag_inlay=self.inlay['inlay'])
        for p in raw_packets_in:
            cur_p = Packet(p['raw'], time_from_start=p['time'],
                           inlay_type=self.inlay['inlay'])

            tag_id = cur_p.get_adva()

            if self.n_triggers == 0 and self.advas_before_tags is not None:
                self.advas_before_tags.add(tag_id)

            elif tag_id not in self.seen_advas and (self.advas_before_tags is None or tag_id not in self.advas_before_tags):
                self.seen_advas.add(tag_id)
                self.logger.info(f"New adva {tag_id}")
                new_packet_list.append(cur_p)

        return new_packet_list, len(raw_packets_in) > 0

    def check_new_trigger(self):
        triggers_out = []
        if not self.gw_instance.is_signals_available():
            return triggers_out
        
        gw_rsps = self.gw_instance.get_gw_signals()
        for gw_rsp in gw_rsps:
            if not gw_rsp:
                continue
            time_condition_met = (gw_rsp['time'] - self.last_change_time >= self.needed_time_between_matrices) or self.last_change_time == 0
            if time_condition_met:
                if 'Detected High-to-Low peak' in gw_rsp['raw']:
                    self.last_change_time = gw_rsp['time']
                    self.n_triggers += 1
                    self.logger.info(f'Got a Trigger.  Number of Triggers {self.n_triggers}')
                    triggers_out.append({'trigger_time': self.last_change_time, 
                                         'trigger_num': self.n_triggers})
        return triggers_out

    def gw_recovery_flow(self):
        try:
            if not self.gw_instance.is_connected():
                self.logger.info('Trying to reconnect to GW')
                self.init_gw()
            self.gw_reset_config(start_gw_app=True)
            self.gw_error_connection = False
        except Exception as e:
            self.gw_error_connection = True
            self.logger.warning(f"Couldn't reconnect GW, due to: {e}")


    def run(self):
        """
        Receives available data then counts and returns the number of unique advas.
        """
        self.gw_instance.set_configuration(start_gw_app=True)
        self.gw_instance.reset_start_time()
        is_running = True
        last_packet_time = time.time()
        while not self.stop.is_set():
            time.sleep(0)
            try:
                # check gw errors:
                if self.gw_instance.get_read_error_status() or not self.gw_instance.is_connected():
                    self.gw_recovery_flow()
                #  Pause / Start cases
                if not self.stopped_by_user and not is_running:  # user click on Start case
                    self.gw_reset_config(start_gw_app=True)
                    is_running = True
                    last_packet_time = time.time()
                elif self.stopped_by_user and is_running:  # user click on Stop
                    self.gw_instance.reset_gw()
                    is_running = False
                    last_packet_time = time.time()
                
                if not is_running:
                    continue
                #  Receiving triggers
                trigger_list = self.check_new_trigger()

                #  Receiving packets
                new_packet_list, got_packets = self.check_new_tags()
                new_sensors = {}

                if got_packets:
                    # received packets
                    last_packet_time = time.time()

                if len(new_packet_list) > 0:
                    # received new packets
                    new_sensors = self.get_sensors_value()
                    trigger_list += self.check_new_trigger()  # add triggers before and after packets
                elif time.time() - last_packet_time > MAX_TIME_WITHOUT_PACKETS:
                    # Not receiving packets for awhile
                    self.logger.warning(f'Gateway did not get packets for the last {MAX_TIME_WITHOUT_PACKETS} seconds, try to reset and re-config')
                    self.gw_recovery_flow()
                    last_packet_time = time.time()
                else:
                    # Not receiving packets
                    time.sleep(0.050)
                # add to queue:
                if trigger_list or new_packet_list:
                    if self.unq_packets_new_triggers.full():
                        element = self.unq_packets_new_triggers.get()
                        element['packet'] = f'n packets in list: {len(element["packet"])}'
                        self.logger.warning(f"unq_packets_new_triggers is full, dropping {element}")
                    self.unq_packets_new_triggers.put({'trigger': trigger_list, 'packet': new_packet_list, 'sensors': new_sensors})
            except Exception as e:
                self.logger.warning(f'got exception during adva process run: {e}')
        
        self.logger.info('Stop advaProcess run')
        self.gw_instance.reset_gw()
        self.gw_instance.exit_gw_api()
