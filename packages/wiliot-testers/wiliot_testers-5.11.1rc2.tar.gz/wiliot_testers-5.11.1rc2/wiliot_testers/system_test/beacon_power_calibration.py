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
import os
import pathlib
import time
from datetime import datetime
try:
    from tkinter import messagebox
except Exception as e:
    print(f'could not import tkinter: {e}')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from wiliot_core import WiliotGateway, set_logger, PacketList, DataType, ActionType
from wiliot_tools.utils.wiliot_gui.wiliot_gui import *

from wiliot_tools.test_equipment.test_equipment import EquipmentError, Attenuator
from wiliot_testers.wiliot_tester_log import WiliotTesterLog

# global vars go here :)
global LORA_ATTN_COM
global BLE_ATTN_COM
global STABILIZATION_RANGE_MODIFIER  # Max differance between points that fit the criteria
global MIN_CONSECUTIVE_POINTS_MODIFIER  # How many points in a row should be in order to recommend a value
global OPTIMAL_ATTENUATION_MODIFIER  # By how much attenuation to increase after finding stabilisation point

LORA_ATTN_COM = "COM3"
BLE_ATTN_COM = "COM6"
STABILIZATION_RANGE_MODIFIER = 1
MIN_CONSECUTIVE_POINTS_MODIFIER = 5
OPTIMAL_ATTENUATION_MODIFIER = 2

run_default_values = {
    'time_profile_on': '5',
    'time_profile_period': '15',
    'lora_value': '20',
    'iter_length': '90',
    'energy_pattern_value': '50',
    'ble_sweep_start': 0,
    'ble_sweep_end': 30,
}

multiprocessing = True
now = datetime.now()
run_start_time = now.strftime("%m-%d-%Y_%H-%M-%S")


class BeaconCalibration:

    def __init__(self):
        # Initialises logger and GUI
        self.init_name_path()
        self.init_gui()
        self.gw_logger = WiliotTesterLog(run_name="beacon_calibration_testing")
        self.gw_logger.set_logger(self.gw_log_path, tester_name="Wiliot tester")

        # Initialises the hardware
        self.attn_enable = True
        self.gw_obj = None
        self.attn_obj_lora = None
        self.attn_obj_ble = None
        self.init_hw()
        self.all_results = pd.DataFrame({'Adva': [], 'Frequency': [], 'TBP': [], 'Atten': []})
        self.gw_config()
        self.run_sweep()
        self.process_result()
        self.analysis_plot()

    def init_name_path(self):
        self.results_path = os.path.join('', 'Beacon_calibration_runs',
                                         ('Beacon_calibration_run_{}'.format(run_start_time)))
        if not os.path.exists(self.results_path):
            pathlib.Path(self.results_path).mkdir(parents=True, exist_ok=True)

        self.gw_log_path = os.path.join('', 'Beacon_calibration_logs')  # Gateway log location

        logger_path, self.logger = set_logger(app_name='BeaconCalibration', dir_name='Beacon_calibration_logs',
                                              file_name='Beacon_calibration_test_log')
        self.logger.critical("I love you, unassuming user")

    def init_hw(self):

        self.gw_obj = WiliotGateway(auto_connect=True, logger_name=self.gw_logger.gw_logger.name, verbose=False)
        try:
            time.sleep(1)
            if self.gw_obj.connected:
                self.gw_obj.reset_gw()
                self.gw_obj.reset_buffer()
                self.gw_obj.is_gw_alive()
                self.gw_obj.start_continuous_listener()

                self.gw_logger.gw_logger.info('GW config finished')
            else:
                raise EquipmentError('Gateway Error - Verify WiliotGateway connection')
        except Exception as e:
            self.gw_logger.gw_logger.warning(e)
            self.gw_obj.close_port()
            raise EquipmentError('Gateway Error - Verify WiliotGateway connection')

        if self.attn_enable:
            self.attn_obj_lora = Attenuator(ATTN_type='API', comport=LORA_ATTN_COM).GetActiveTE()
            attn = self.lora_value
            value = self.attn_obj_lora.Setattn(attn=attn)
            if value != attn:
                raise Exception(f'Error setting attenuation: new : {attn} current: {value}')

    def gw_config(self):
        self.gw_obj.config_gw(energy_pattern_val=self.energy_pattern_val,
                              time_profile_val=[self.time_profile_on_val, self.time_profile_period_val])

    def run_sweep(self):
        self.attn_obj_ble = Attenuator(ATTN_type="API", comport=BLE_ATTN_COM).GetActiveTE()
        self.gw_obj.start_continuous_listener()
        sweep_attns = range(self.ble_sweep_start, self.ble_sweep_end, 1)
        self.attenuation_list = []
        self.all_results = PacketList()
        for attn in sweep_attns:
            # set atten
            self.attn_val = self.attn_obj_ble.Getattn()
            self.attn_val = int(self.attn_obj_ble.Setattn(attn=attn))
            self.attenuation_list.append(attn)
            self.logger.info(f'Current setting attenuation: new : {attn} current: {self.attn_val}')

            self.gw_obj.reset_listener()
            self.gw_obj.config_gw(start_gw_app=True)
            self.daq()
            is_stopped = self.gw_obj.stop_gw_app()
            if not is_stopped:
                raise Exception('could not send stop to GW')
        return self.attenuation_list, self.attn_val

    def daq(self):
        time.sleep(2)  # possibly useless, check
        start_time = time.time()  # Records starting time
        max_duration = self.iter_duration
        while True:
            time.sleep(0)

            if self.gw_obj.is_data_available():
                cur_packet_list = self.gw_obj.get_packets(action_type=ActionType.ALL_SAMPLE,
                                                          data_type=DataType.PACKET_LIST)

                if len(cur_packet_list) > 0:
                    for p in cur_packet_list:
                        p.add_custom_data({'attenuation': self.attn_val})
                        self.logger.info("Would you look at that! , i found this packet: {}"
                                         .format(p.packet_data['raw_packet']))
                        # self.logger.info('got packet {}'.format(p.packet_data['raw_packet']))
                        self.all_results.append(p)
            if time.time() - start_time > max_duration:
                break
        self.logger.info('Iteration ended!')

    def process_result(self):
        self.tbp_df = pd.DataFrame()  # creates an empty dataframe

        df = self.all_results.get_df(add_sprinkler_info=True)  # makes a dataframe from the data so far
        df_packet = df.drop_duplicates(subset=['raw_packet'])  # drops duplicates of packets
        self.group_tbp = df_packet.groupby(by=['attenuation', 'adv_address']).agg(
            tbp_mean=('tbp', lambda x: np.ceil(np.mean(x[x > 0]))),  # Calculates mean, then applies ceiling
            tbp_min=('tbp', lambda x: np.ceil(np.min(x[x > 0]))),
            tbp_median=('tbp', lambda x: np.ceil(np.median(x[x > 0])))  # Calculates min, then applies ceiling
        ).reset_index()

        self.group_tbp = self.group_tbp.sort_values(by=['adv_address', 'attenuation'])

        self.group_tbp['Difference'] = self.group_tbp.groupby('adv_address')['tbp_min'].diff().fillna(0)
        self.group_tbp = self.group_tbp.dropna()

        # Various calculations on the TBP packets
        self.group_tbp.to_csv(os.path.join(self.results_path, "tbp_calculated_{}.csv".format(run_start_time)))
        # Saves packets with TBP only
        df_packet.to_csv(os.path.join(self.results_path, "filtered_tbp_packets_{}.csv".format(run_start_time)))
        # Saves all the results
        df.to_csv(os.path.join(self.results_path, "full_Test_results_{}.csv".format(run_start_time)))

    def analysis_plot(self):
        self.optimal_value_calculation()
        for adva in self.group_tbp['adv_address'].unique():
            group_data = self.group_tbp[self.group_tbp['adv_address'] == adva]
            y1 = self.group_tbp['tbp_min']
            y2 = self.group_tbp['tbp_mean']
            y3 = self.group_tbp['tbp_median']
            plt.plot(group_data['attenuation'], y1, marker='o', label="tbp_min")

            # Used for debugging and comparing results
            # plt.plot(group_data['attenuation'], y2, marker='o', label="tbp_mean")
            # plt.plot(group_data['attenuation'], y3, marker='o', label="tbp_median")

        plt.draw()
        plt.xlabel("Attenuation")
        plt.ylabel('TBP')
        if self.recommended_stabilization:
            plt.title(f"Recommended attenuation: {self.recommended_stabilization}")
        else:
            plt.title("No recommended attenuation based on criteria")
        plt.legend()
        # TODO: add recommended attenuation to graph
        plt.savefig((os.path.join(self.results_path, "beacon_calibration_plot_{}.png".format(run_start_time))))
        plt.show()

    def optimal_value_calculation(self):
        self.group_tbp['Incremental_Difference'] = self.group_tbp['tbp_min'].diff()

        stabilization_range = 1  # Max differance between points that fit the criteria
        min_consecutive_points = 5  # How many points in a row should be in order to recommend a value

        streak_count = 0  # Tracks the longest streak of values within the stabilization range
        stabilization_start_index = None
        try:
            for index, row in self.group_tbp.iterrows():
                if abs(row['Incremental_Difference']) <= stabilization_range:
                    streak_count += 1
                    if streak_count == min_consecutive_points:
                        stabilization_start_index = index - min_consecutive_points + 1
                        stabilization_start_value = self.group_tbp.loc[stabilization_start_index, 'attenuation']
                        break
                else:
                    streak_count = 0  # Resets said counter if conditions are not met

        except KeyError:
            pass

        if stabilization_start_index is not None:
            self.logger.critical(
                f"Stabilization starts at Attenuation: {stabilization_start_index}, tbp_min: {int(self.group_tbp.loc[stabilization_start_index, 'tbp_min'])}")
            self.recommended_stabilization = stabilization_start_value + OPTIMAL_ATTENUATION_MODIFIER
            messagebox.showinfo(message=f"Recommended Attenuation: {int(stabilization_start_value) + 2}")

        else:
            print("No stabilization detected based on the criteria :(")

    # GUI
    def init_gui(self):

        json_params_path = os.path.join(os.path.dirname(__file__), 'beacon_power_calibration_params.json')

        def load_params_from_json(json_params_path):
            if os.path.exists(json_params_path):
                try:
                    with open(json_params_path, 'r') as json_file:
                        return json.load(json_file)
                except json.JSONDecodeError:
                    print("Error decoding JSON from file")
            return {}

        used_values = load_params_from_json(json_params_path)

        # TODO
        # add the attenuation ports to the GUI

        params_dict = {
            'time_profile_on': {
                'text': 'On',
                'value': used_values.get('time_profile_on', '5'),
                'widget_type': 'entry',
                'group': 'Time profile'
            },
            'time_profile_period': {
                'text': 'Period',
                'value': used_values.get('time_profile_period', '15'),
                'widget_type': 'entry',
                'group': 'Time profile'
            },
            'lora_value': {
                'text': 'LoRa Value',
                'value': used_values.get('lora_value', '20'),
                'widget_type': 'entry',
                'options': {'font': ('Helvetica', 10, 'bold')},
            },
            'iter_length': {
                'text': 'Iteration length (in seconds)',
                'value': used_values.get('iter_length', '90'),
                'widget_type': 'entry',
                'options': {'font': ('Helvetica', 10, 'bold')},
            },
            'energy_pattern_value': {
                'text': 'Energy pattern',
                'value': used_values.get('energy_pattern_value', '50'),
                'widget_type': 'entry',
                'options': {'font': ('Helvetica', 10, 'bold')},
            },
            'sweep_row': [
                {'ble_sweep_start': {
                    'text': 'BLE Sweep Start',
                    'value': '0',
                    'widget_type': 'spinbox',
                    'options': list(range(0, 31)),
                },
                },
                {'ble_sweep_end': {
                    'text': 'to',
                    'value': '30',
                    'widget_type': 'spinbox',
                    'options': list(range(0, 31)),
                },
                }
            ],

            'LORA_ATTN_COM': {
                'text': 'LoRa COM Port',
                'value': used_values.get('LORA_ATTN_COM', 'COM3'),
                'widget_type': 'entry',
                'options': {'font': ('Helvetica', 10, 'bold')},
                'group': 'COM Port Configuration'
            },
            'BLE_ATTN_COM': {
                'text': 'BLE COM Port',
                'value': used_values.get('BLE_ATTN_COM', 'COM6'),
                'widget_type': 'entry',
                'options': {'font': ('Helvetica', 10, 'bold')},
                'group': 'COM Port Configuration'
            },
        }

        beacon_power_calib_gui = WiliotGui(params_dict=params_dict, title='Beacon Power Calibration')
        values = beacon_power_calib_gui.run()
        print(values)
        try:
            form_values = {
                'iter_duration': int(values['iter_length']),
                'lora_value': int(values['lora_value']),
                'sweep_row_ble_sweep_start': values['sweep_row_ble_sweep_start'],
                'sweep_row_ble_sweep_end': values['sweep_row_ble_sweep_end'],
                'energy_pattern_value': int(values['energy_pattern_value']),
                'time_profile_on': int(values['time_profile_on']),
                'time_profile_period': int(values['time_profile_period']),
                'LORA_ATTN_COM': values['LORA_ATTN_COM'],
                'BLE_ATTN_COM': values['BLE_ATTN_COM'],
            }

            # Serialize form values to JSON and write to a file
            with open('beacon_power_calibration_params.json', 'w') as json_file:
                json.dump(form_values, json_file, indent=4)

        except ValueError:
            popup_message('Value must be an integer.', logger=self.logger)


if __name__ == '__main__':
    inst = BeaconCalibration()
    SystemExit("We're done here, get on with your day mate")
