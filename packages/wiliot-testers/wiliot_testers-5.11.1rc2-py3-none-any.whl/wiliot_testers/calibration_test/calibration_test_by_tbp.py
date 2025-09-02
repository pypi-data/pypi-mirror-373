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
from time import sleep
import pandas as pd
import numpy as np
import json
import os
import logging
from wiliot_core import WiliotGateway, ActionType, DataType
from os.path import join
from wiliot_core import TagCollection
from wiliot_tools.utils.wiliot_gui.wiliot_gui import *
from wiliot_tools.test_equipment.test_equipment import Attenuator, EquipmentError
from wiliot_core import WiliotDir

test_name = 'calibration_test'


def default_calibration():
    default_values = {
        "GW Config": {
            "2.4_energizing_patterns_row_EP18": True,
            "2.4_energizing_patterns_row_EP20": False,
            "2.4_energizing_patterns_row_EP24": False,
            "sub1G_energizing_patterns_row_EP50": False,
            "sub1G_energizing_patterns_row_EP51": True,
            "sub1G_energizing_patterns_row_EP52": False,
            "test_mode_row_EP27": False,
            "2.4_energizing_patterns_row_EP17": False,
            "2.4_energizing_patterns_row_EP25": False,
            "2.4_energizing_patterns_row_EP26": False,
            "2.4_energizing_patterns_row_EP28": False,
            "2.4_energizing_patterns_row_EP30": False,
            "2.4_energizing_patterns_row_EP31": False,
            "2.4_energizing_patterns_row_EP32": False,
            "2.4_energizing_patterns_row_EP33": False,
            "power_boundary_scan_row_minSwap": 14,
            "power_boundary_scan_row_maxSwap": 18,
            "time_profile_row_timeProfileOn": 5,
            "time_profile_row_timeProfilePeriod": 15,
        },
        "Setup Config": {
            "externalAttn": "No"
        }
    }
    return default_values


def open_calibration_config():
    WILIOT_DIR = WiliotDir()
    dir_wiliot = WILIOT_DIR.get_wiliot_root_app_dir()
    tester_dir = join(dir_wiliot, 'offline')
    dir_config = join(tester_dir, 'configs')
    configuration_dir = os.path.join(dir_config, 'calibration_config.json')
    additional_values = {}
    if os.path.exists(configuration_dir):
        with open(configuration_dir) as confile:
            configuration = json.load(confile)
    else:
        with open(configuration_dir, 'w') as output:
            configuration = default_calibration()
            json.dump(configuration, output, indent=2, separators=(", ", ": "), sort_keys=False)

    def on_open_energy_patterns_click():
        nonlocal additional_values
        additional_params_dict = {

            'add_patterns_row_1': [
                {'additional_2.4_pattern_label': {
                    'text': '',
                    'value': 'Additional 2.4 GHz Energizing Pattern:',
                    'widget_type': 'label'
                }},
                {'EP17': {
                    'text': '17',
                    'widget_type': 'checkbox',
                    'value': configuration["GW Config"].get('add_patterns_row_1_EP17', False)
                }},
                {'EP25': {
                    'widget_type': 'checkbox',
                    'text': '25',
                    'value': configuration["GW Config"].get('add_patterns_row_1_EP25', False)
                }},
                {'EP26': {
                    'widget_type': 'checkbox',
                    'text': '26',
                    'value': configuration["GW Config"].get('add_patterns_row_1_EP26', False)
                }},
                {'EP28': {
                    'widget_type': 'checkbox',
                    'text': '28',
                    'value': configuration["GW Config"].get('add_patterns_row_1_EP28', False)
                }}
            ],
            'add_patterns_row_2': [
                {'some_space': {
                    'text': '',
                    'value': ' ',
                    'widget_type': 'label'
                }},
                {'EP30': {
                    'widget_type': 'checkbox',
                    'text': '30',
                    'value': configuration["GW Config"].get('add_patterns_row_2_EP30', False)
                }},
                {'EP31': {
                    'widget_type': 'checkbox',
                    'text': '31',
                    'value': configuration["GW Config"].get('add_patterns_row_2_EP31', False)
                }},
                {'EP32': {
                    'widget_type': 'checkbox',
                    'text': '32',
                    'value': configuration["GW Config"].get('add_patterns_row_2_EP32', False)
                }},
                {'EP33': {
                    'widget_type': 'checkbox',
                    'text': '33',
                    'value': configuration["GW Config"].get('add_patterns_row_2_EP33', False)
                }}
            ],

            'additional_sub1g_pattern_row': [
                {'additional_sub1g_pattern_label': {
                    'text': '',
                    'value': 'Additional Sub1G Energizing Pattern:',
                    'widget_type': 'label'
                }},
                {'EP53': {
                    'text': '53',
                    'widget_type': 'checkbox',
                    'value': configuration["GW Config"].get('additional_sub1g_pattern_row_EP53', False)
                }},
                {'EP54': {
                    'widget_type': 'checkbox',
                    'text': '54',
                    'value': configuration["GW Config"].get('additional_sub1g_pattern_row_EP54', False)
                }},
                {'EP55': {
                    'widget_type': 'checkbox',
                    'text': '55',
                    'value': configuration["GW Config"].get('additional_sub1g_pattern_row_EP55', False),
                }},
                {'EP56': {
                    'widget_type': 'checkbox',
                    'text': '56',
                    'value': configuration["GW Config"].get('additional_sub1g_pattern_row_EP56', False),
                }},
                {'EP57': {
                    'widget_type': 'checkbox',
                    'text': '57',
                    'value': configuration["GW Config"].get('additional_sub1g_pattern_row_EP57', False),
                }}
            ],

        }
        additional_gui = WiliotGui(params_dict=additional_params_dict, parent=main_gui.layout,
                                   exit_sys_upon_cancel=False, title='Additional Parameters')
        additional_values = additional_gui.run()
    main_params_dict = {
        '2.4_energizing_patterns_row': [
            {'2.4_energizing_patterns_label': {
                'text': '',
                'value': '2.4 GHz Energizing Pattern:',
                'widget_type': 'label'
            }},
            {'EP18': {
                'text': '18',
                'widget_type': 'checkbox',
                'value': configuration["GW Config"]['2.4_energizing_patterns_row_EP18'],
            }},
            {'EP20': {
                'widget_type': 'checkbox',
                'text': '20',
                'value': configuration["GW Config"]['2.4_energizing_patterns_row_EP20'],
            }},
            {'EP24': {
                'widget_type': 'checkbox',
                'text': '24',
                'value': configuration["GW Config"]['2.4_energizing_patterns_row_EP24'],
            }}

        ],

        'sub1G_energizing_patterns_row': [
            {'sub1G_energizing_patterns_label': {
                'text': '',
                'value': 'Sub1G Energizing Pattern:',
                'widget_type': 'label'
            }},
            {'EP50': {
                'text': '50',
                'widget_type': 'checkbox',
                'value': configuration["GW Config"]['sub1G_energizing_patterns_row_EP50'],
            }},
            {'EP51': {
                'widget_type': 'checkbox',
                'text': '51',
                'value': configuration["GW Config"]['sub1G_energizing_patterns_row_EP51'],
            }},
            {'EP52': {
                'widget_type': 'checkbox',
                'text': '52',
                'value': configuration["GW Config"]['sub1G_energizing_patterns_row_EP52'],
            }}
        ],
        'test_mode_row': [
            {'test_mode_label': {
                'text': '',
                'value': 'Test Mode Energizing Pattern:',
                'widget_type': 'label'
            }},
            {'EP27': {
                'text': '27',
                'widget_type': 'checkbox',
                'value': configuration["GW Config"]['test_mode_row_EP27'],
            }}
        ],


        'Open_Energy_Patterns': {
            'text': 'Open Energy Patterns',
            'widget_type': 'button',
        },
        'power_boundary_scan_row': [
            {'power_boundary_scan_label': {
                'text': '',
                'value': 'Power boundary scan',
                'widget_type': 'label'
            }},
            {'minSwap': {
                'text': '',
                'widget_type': 'combobox',
                'options': list(range(0, 18)),
                'value': configuration["GW Config"]['power_boundary_scan_row_minSwap'],
            }},
            {'maxSwap': {
                'widget_type': 'combobox',
                'text': '',
                'options': list(range(1, 19)),
                'value': configuration["GW Config"]['power_boundary_scan_row_maxSwap'],
            }}
        ],

        'time_profile_row': [
            {'time_profile_label': {
                'text': '',
                'value': 'Time profile',
                'widget_type': 'label'
            }},
            {'timeProfileOn': {
                'text': '',
                'widget_type': 'combobox',
                'options': [5, 10],
                'value': configuration["GW Config"]['time_profile_row_timeProfileOn'],
            }},
            {'timeProfilePeriod': {
                'widget_type': 'combobox',
                'text': '',
                'options': [15, 25],
                'value': configuration["GW Config"]['time_profile_row_timeProfilePeriod'],
            }}
        ],

        'externalAttn': {
            'text': 'Is there external attenuator?',
            'widget_type': 'combobox',
            'options': ['Yes', 'No'],
            'value': configuration["Setup Config"]['externalAttn'],
        },
    }

    main_gui = WiliotGui(params_dict=main_params_dict, title='Calibration test by tbp')
    main_gui.add_event(widget_key='Open_Energy_Patterns', command=on_open_energy_patterns_click, event_type='button')
    main_values = main_gui.run()
    values = {**additional_values, **main_values}

    should_submit = False
    should_calibrate = False
    try:
        if values['power_boundary_scan_row_minSwap'] < values['power_boundary_scan_row_maxSwap']:
            if int(values['time_profile_row_timeProfileOn']) < int(values['time_profile_row_timeProfilePeriod']):
                should_submit = True
                should_calibrate = True
            else:
                logging.warning(
                    'Please make sure that Power boundary scan is legal.\n'
                    'First value for the Time Profile On and the second value for Time Profile Period ')
        else:
            logging.warning(
                'Please make sure that Power boundary scan is legal.\n'
                'First value for lower limit, Second value for upper limit ')
    except Exception:
        should_submit = False
        logging.warning('Please check all values are valid')

    Dict = {}
    if should_submit:
        Dict['GW Config'] = {}
        Dict['Setup Config'] = {}

        flag = False
        for key in values:
            if 'EP' in key:
                flag = True
            if not flag:
                Dict['Setup Config'][key] = values[key]
            else:
                Dict['GW Config'][key] = values[key]

        with open(configuration_dir, 'w') as output:
            json.dump(Dict, output, indent=2, separators=(", ", ": "), sort_keys=False)

    if should_calibrate:
        try:
            all_patterns = []
            for key in values:
                if 'EP' in key and values[key]:
                    all_patterns.append(key[-2:])

            logging.info('Will start calibration, When done program will end')
            logging.info('---------------------------------------------------------------\n'
                         'Please make sure the tags on and around the antenna are working\n'
                         '---------------------------------------------------------------')
            print('Will start calibration, When done program will end')
            print('---------------------------------------------------------------\n'
                  'Please make sure the tags on and around the antenna are working\n'
                  '---------------------------------------------------------------')
            top_score = start_calibration(
                sweep_scan=[Dict['GW Config']['power_boundary_scan_row_minSwap'], 1,
                            Dict['GW Config']['power_boundary_scan_row_maxSwap'] + 1],
                to_set=False, time_profiles_on=[Dict['GW Config']['time_profile_row_timeProfileOn']],
                time_profiles_period=[Dict['GW Config']['time_profile_row_timeProfilePeriod']],
                energy_pattern_custom=all_patterns)
            print('Best abs power to work with for tbp of 100ms is: {} with time profile of [{},{}]'.format(
                str(top_score['abs_power'].item()), str(top_score['time_profile_on'].item()),
                str(top_score['time_profile_period'].item())))

        except Exception:
            logging.warning(
                'Couldnt get calibration values - Please make sure the tags on and around the antenna are working ')
            exit()

    return values


def set_attn_power(external_attn, attn_obj, gw_obj, attn_power):
    """
    configure Attenuator to a specific value
    gets:
        attn_obj:       Attenuator obj
        attn_power:     value to set attn

    return:
        status if Attenuator is set correctly

    """
    status = True
    if not external_attn:
        try:
            gw_obj.set_gw_output_power_by_index(attn_power)
        except Exception as e:
            print('got error during set_attn_power: {}'.format(e))
            status = False
        if attn_obj is not None:
            attn_obj.Setattn(0)
    else:
        if gw_obj is not None:
            gw_obj.set_gw_output_power_by_index(8)
        print('Setting Attenuator to {attn_power}dB'.format(attn_power=attn_power))
        attn_obj.Setattn(attn_power)
        sleep(2)

        attn_current_config = attn_obj.Getattn()
        if (float(attn_current_config) - attn_power) != 0:
            print('Error setting ATTENUATOR')
            status = False
        print(
            "Attenuator is set to: {attn_current_config} dB".format(
                attn_current_config=attn_current_config.split('.')[0]))
    return status


def build_range(target_range):
    new_range = range(target_range[0], target_range[-1])
    if len(target_range) > 2:
        new_range = range(target_range[0], target_range[-1], target_range[1])
    return new_range


def get_statistics(gw_obj, external_attn, attn_obj, attn_power, energy_pattern_val, time_profile_on=5,
                   time_profile_period=15):
    multi_tag = TagCollection()
    gw_obj.config_gw(time_profile_val=[0, 6])
    set_attn_power(external_attn, attn_obj, gw_obj, attn_power)
    sleep(1)
    gw_obj.reset_buffer()
    gw_obj.reset_listener()
    gw_obj.config_gw(pacer_val=0, energy_pattern_val=energy_pattern_val,
                     time_profile_val=[time_profile_on, time_profile_period], received_channel=37,
                     beacons_backoff_val=0)

    gw_answer = gw_obj.get_packets(action_type=ActionType.FIRST_SAMPLES, num_of_packets=100, max_time=20)
    for packet in gw_answer.packet_list:
        multi_tag.append(packet)
    sleep(3)
    multi_tag_statistics = multi_tag.get_statistics()
    if multi_tag_statistics.empty:
        return multi_tag_statistics

    multi_tag_statistics['absGwTxPowerIndex'] = attn_power
    if not external_attn:
        multi_tag_statistics['abs_power'] = gw_obj.valid_output_power_vals[attn_power]['abs_power']
        multi_tag_statistics['gw_output_power'] = gw_obj.valid_output_power_vals[attn_power]['gw_output_power']
        multi_tag_statistics['bypass_pa'] = gw_obj.valid_output_power_vals[attn_power]['bypass_pa']
    else:
        multi_tag_statistics['abs_power'] = None
        multi_tag_statistics['gw_output_power'] = None
        multi_tag_statistics['bypass_pa'] = None
    multi_tag_statistics['time_profile_on'] = time_profile_on
    multi_tag_statistics['time_profile_period'] = time_profile_period
    multi_tag_statistics['energy_pattern'] = energy_pattern_val

    optimal_tag_statistics = multi_tag_statistics[
        multi_tag_statistics.rssi_mean == multi_tag_statistics.rssi_mean.min()]
    return optimal_tag_statistics


def start_calibration(target_tbp=100, sweep_scan=[12, 1, 18], time_profiles_on=[5],
                      time_profiles_period=[15],
                      external_attn=False, inlay_type='Single Band', energy_pattern_custom=None, to_set=False):
    """
    calibration process
    :type inlay_type: string
    :param inlay_type: will determine the energizing patterns we will use

    return:
        df with closest tbp value to target
    """

    wiliot_dir = WiliotDir()
    wiliot_dir.create_tester_dir(test_name)
    calibration_dir = wiliot_dir.get_tester_dir(test_name)
    if energy_pattern_custom is None:
        if inlay_type.startswith('Single'):
            energy_pattern_values = [18]
        else:
            energy_pattern_values = [18, 51]
    else:
        energy_pattern_values = energy_pattern_custom

    # create equipment objects
    attn_obj = None
    if external_attn:
        try:
            attn_obj = Attenuator('API').GetActiveTE()
            current_attn = attn_obj.Getattn()
        except Exception as e:
            raise EquipmentError('Attenuator Error - Verify Attenuator connection')
    gw_obj = None
    try:
        gw_obj = WiliotGateway(auto_connect=True, logger_name='root', verbose=False)
        gw_obj.write('!set_tester_mode 1')
        gw_obj.write('!listen_to_tag_only 1')

        if not gw_obj.get_connection_status()[0]:
            raise EquipmentError('Gateway Error - Verify WiliotGateway connection')
    except Exception as e:
        if gw_obj is not None:
            gw_obj.close_port()
        raise EquipmentError('Gateway Error - Verify WiliotGateway connection')

    statistics_df = pd.DataFrame()
    for energy_pattern_val in energy_pattern_values:
        attn_range = build_range(sweep_scan)
        gw_obj.start_continuous_listener()
        gw_obj.config_gw(pacer_val=0, energy_pattern_val=energy_pattern_val, time_profile_val=[5, 15],
                         received_channel=37, beacons_backoff_val=0)
        sleep(2)
        # gw_obj.start_continuous_listener()
        for attn_power in attn_range:
            print('attn_power: ' + str(attn_power))
            optimal_tag_statistics = get_statistics(gw_obj, external_attn, attn_obj, attn_power, energy_pattern_val,
                                                    time_profile_on=int(
                                                        (time_profiles_on[0] + time_profiles_on[-1]) / 2),
                                                    time_profile_period=int(
                                                        (time_profiles_period[0] + time_profiles_period[-1]) / 2))
            if optimal_tag_statistics.empty:
                print('skipped')
                continue
            statistics_df = pd.concat([statistics_df, optimal_tag_statistics], axis=0)

        print(statistics_df)

        top_score = statistics_df.iloc[(statistics_df['tbp_mean'] - target_tbp).abs().argsort()[1:3]]

        if time_profiles_on != [5] and len(time_profiles_on) > 1 or time_profiles_period != [15] and len(
                time_profiles_period) > 1:
            if time_profiles_on != [5]:
                time_profiles_on = build_range(time_profiles_on)
            if time_profiles_period != [15]:
                time_profiles_period = build_range(time_profiles_period)
            for index, row in top_score.iterrows():
                attn_power = row['absGwTxPowerIndex']
                for tpo in time_profiles_on:
                    for tpp in time_profiles_period:
                        print('time_profiles_on: ' + str(tpo) + '/time_profiles_period: ' + str(tpp))
                        optimal_tag_statistics = get_statistics(gw_obj, external_attn, attn_obj, attn_power,
                                                                energy_pattern_val, time_profile_on=tpo,
                                                                time_profile_period=tpp)
                        if optimal_tag_statistics.empty:
                            print('skipped')
                            continue
                        statistics_df = pd.concat([statistics_df, optimal_tag_statistics], axis=0)

        top_score = statistics_df.iloc[(statistics_df['tbp_mean'] - target_tbp).abs().argsort()[:1]]

    gw_obj.stop_continuous_listener()
    gw_obj.close_port()

    statistics_df.to_csv(calibration_dir + '/results/' + 'results.csv')
    # statistics_df.to_csv('top_score.csv')

    if to_set:
        set_attn_power(external_attn, attn_obj, gw_obj, top_score['absGwTxPowerIndex'])
        print('Calibration success, power set to: {}'.format(top_score['absGwTxPowerIndex']))

    return top_score


def get_calibration_results(target_tbp=100, energy_pattern=None):
    """target_tbp=0 will return knee point"""
    wiliot_dir = WiliotDir()
    calibration_dir = wiliot_dir.get_tester_dir(test_name)

    statistics_df = pd.read_csv(calibration_dir + '/results/' + 'results.csv')

    if energy_pattern is not None:
        if not isinstance(energy_pattern, list):
            energy_pattern = list(energy_pattern)
        statistics_df = statistics_df.loc[(statistics_df["energy_pattern"].isin(energy_pattern))]

    if target_tbp == 0:
        tbp_df = statistics_df['tbp_mean'].to_list()
        tbp_df_a = tbp_df.copy()[:-1]
        tbp_df_b = tbp_df.copy()[1:]

        tbp_df.pop(0)

        sub_list = [i - j for i, j in zip(tbp_df_a, tbp_df_b)]

        fraction_list = [s < tbp * 0.1 for s, tbp in zip(sub_list, tbp_df)]
        if any(fraction_list):
            knee_index = np.where(fraction_list)[0][0] + 1
        else:
            knee_index = -1

        top_score = statistics_df.iloc[knee_index].to_frame().transpose()
    else:
        top_score = statistics_df.iloc[(statistics_df['tbp_mean'] - target_tbp).abs().argsort()[:1]]

    return top_score


def set_calibration_attn(set_optimal_attn=True, config_path=None):
    """
    setting attn value
    :type set_optimal_attn: Bool
    :param set_optimal_attn: A flag to decide if set attn to optimal value
    :type config_path: string
    :param config_path: path to config file

    return:
        attenuation set to attenuator or None if set is failed
    """
    # create equipment objects
    try:
        attn_obj = Attenuator('API').GetActiveTE()
        current_attn = attn_obj.Getattn()
    except Exception as e:
        raise EquipmentError('Attenuator Error - Verify Attenuator connection')

    if config_path is None:
        parent_path = os.path.dirname(__file__)
        offline_path = os.path.join(parent_path, 'offline')
        offline_config_path = os.path.join((offline_path, 'configs'))
        path = os.path.join(offline_config_path, 'test_configs.json')
        # path = '{parent_path}\\offline\\configs\\test_configs.json'.format(parent_path=parent_path)
    else:
        path = config_path

    key = "equipment"

    key = "AttenuationEnergy"
    optimal_attenuation_value = None
    if set_optimal_attn:
        try:
            with open(path, "r+") as jsonFile:
                config_data = json.load(jsonFile)
                optimal_attenuation_value = config_data.get(key)
        except Exception as e:
            raise

    if set_optimal_attn and optimal_attenuation_value is not None:
        print('Setting ATTN to {value} dB'.format(value=optimal_attenuation_value))
        # set_attn_status = set_attn_power(True, attn_obj, None, optimal_attenuation_value)
        set_attn_status = attn_obj.Setattn(optimal_attenuation_value)
        if set_attn_status:
            return optimal_attenuation_value
    else:
        print('Setting ATTN to 0 dB')
        # set_attn_status = set_attn_power(False, attn_obj, None, 0)
        set_attn_status = attn_obj.Setattn(0)
        if set_attn_status:
            return 0
    return None


# main
if __name__ == '__main__':
    vals = open_calibration_config()
    start_calibration(inlay_type='Dual')
    calibration_results = get_calibration_results(energy_pattern=[20])
    print(calibration_results['absGwTxPowerIndex'].item())
