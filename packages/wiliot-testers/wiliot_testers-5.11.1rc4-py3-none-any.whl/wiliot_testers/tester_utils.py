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
import copy
from yoctopuce.yocto_temperature import *
import threading
import logging
import json
import time
import os
from csv import writer, DictWriter
import numpy as np
import sys
from os.path import dirname
import pathlib
from wiliot_testers.wiliot_tester_tag_result import *
from wiliot_tools.utils.wiliot_gui.wiliot_gui import popup_message


###########################################
#            Tester Management            #
###########################################

class TesterName(Enum):
    """
    determines tester type (affects output file format set in class CsvLog)
    """
    OFFLINE = 'offline'
    TAL15K = 'tal15k'
    CONVERSION = 'conversion'
    SAMPLE = 'sample'
    NONE = ''


class HeaderType(Enum):
    """
    determines which output file is generated in class CsvLog (run data or tags data)
    """
    TAG = 'tag'
    RUN = 'run'
    PACKETS = 'packets'
    NONE = ''



def dict_to_csv(dict_in, path, append=False, only_titles=False):
    if append:
        method = 'a'
    else:
        method = 'w'
    with open(path, method, newline='') as f:
        dict_writer = DictWriter(f, fieldnames=dict_in.keys())
        if not append:
            dict_writer.writeheader()
        if not only_titles:
            dict_writer.writerow(dict_in)
        f.close()


def get_temperature():
    """
    initialize yocto temperature sensor
    :return: current temperature
    """
    # object tenp sens
    errmsg = YRefParam()
    if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
        sys.exit("init error :" + errmsg.value)
    cur_temp = YTemperature.FirstTemperature()
    return cur_temp.get_currentValue()


def open_json(folder_path, file_path, default_values=None):
    """
    opens config json
    :type folder_path: string
    :param folder_path: the folder path which contains the desired file
    :type file_path: string
    :param file_path: the file path which contains the json
            (including the folder [file_path = folder_path+"json_file.json"])
    :type default_values: dictionary
    :param default_values: default values for the case of empty json
    :return: the desired json object
    """
    if not os.path.exists(folder_path):
        pathlib.Path(folder_path).mkdir(parents=True, exist_ok=True)
    
    file_exists = os.path.isfile(file_path)
    if not file_exists or os.stat(file_path).st_size == 0:
        # save the default values to json
        with open(file_path, "w") as out_file:
            json.dump(default_values, out_file)
        
        return json.load(open(file_path, "rb"))
    else:
        with open(file_path) as f:
            json_content = f.read()
        if len(json_content) == 0:
            with open(file_path, "w") as out_file:
                json.dump(default_values, out_file)
            json_content = json.load(open(file_path, "rb"))
        else:
            json_content = json.loads(json_content)
        return json_content


def open_json_cache(folder_path, file_path, default_values=None):
    """
    opens config json - for test/sgtin mode only
    :type folder_path: string
    :param folder_path: the folder path which contains the desired file
    :type file_path: string
    :param file_path: the file path which contains the json
            (including the folder [file_path = folder_path+"json_file.json"])
    :type default_values: dictionary
    :param default_values: default values for the case of empty json
    :return: the desired json object
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    file_exists = os.path.isfile(file_path)
    if not file_exists:
        # save the default values to json
        with open(file_path, "w") as out_file:
            json.dump(default_values, out_file)
        with open(file_path, 'r') as f:
            json_content = json.load(f)
        return json_content
    else:
        with open(file_path, 'r') as f:
            json_content = json.load(f)

        for k, v in default_values.items():
            if k not in json_content.keys():
                json_content[k] = v
        with open(file_path, "w") as out_file:
            json.dump(json_content, out_file)
        return json_content


def printing_func(str_to_print, logging_entity, lock_print=None, do_log=True, logger_type='info', logger_name=None):
    """
    print and log
    :type str_to_print: string
    :param str_to_print: string to print
    :type logging_entity: string
    :param logging_entity: what thread is asking to log
    :type lock_print: threading.Lock
    :param lock_print: lock to prevent cutting printing in the middle
    :type do_log: bool
    :param do_log: if True log the data, do not log otherwise
    :type logger_type: string (info, debug, warning)
    :param logger_type: how to log the str_to_print
    """
    
    msg = str(logging_entity) + ':\t' + str(str_to_print)
    # if lock_print is not None:
    #     with lock_print:
    #         print(msg)
    # else:
    #     print(msg)
    # if do_log:
    #     if logger_type == 'info':
    #         logging.info(msg)
    #     elif logger_type == 'debug':
    #         logging.debug(msg)
    #     elif logger_type == 'warning':
    #         logging.warning(msg)
    if logger_name is None:
        if do_log:
            if lock_print is not None:
                with lock_print:
                    if logger_type == 'info':
                        logging.info(msg)
                    elif logger_type == 'debug':
                        logging.debug(msg)
                    elif logger_type == 'warning':
                        logging.warning(msg)
            else:
                if logger_type == 'info':
                    logging.info(msg)
                elif logger_type == 'debug':
                    logging.debug(msg)
                elif logger_type == 'warning':
                    logging.warning(msg)
        
        else:
            if lock_print is not None:
                with lock_print:
                    print(msg)
            else:
                print(msg)
    else:
        my_logger = logging.getLogger(logger_name)
        if do_log:
            if lock_print is not None:
                with lock_print:
                    if logger_type == 'info':
                        my_logger.info(msg)
                    elif logger_type == 'debug':
                        my_logger.debug(msg)
                    elif logger_type == 'warning':
                        my_logger.warning(msg)
            else:
                if logger_type == 'info':
                    my_logger.info(msg)
                elif logger_type == 'debug':
                    my_logger.debug(msg)
                elif logger_type == 'warning':
                    my_logger.warning(msg)
        
        else:
            if lock_print is not None:
                with lock_print:
                    print(msg)
            else:
                print(msg)


###########################################
#              Tester Classes             #
###########################################
class TagsHandling:
    """
    controls the tags adv_address seen in the run, filtering bad packets, duplications etc.
    """
    
    def __init__(self, tags_list_len, lock_print=None, rssi_threshold=None, logging_thread=None,
                 only_add_tags_after_location_ends=False, add_to_black_list_after_locations=2):
        """
        :type tags_list_len: int
        :param tags_list_len: how long back to look for duplications
        :type lock_print: threading.lock
        :param lock_print: printing lock
        :type rssi_threshold: int
        :param rssi_threshold: max rssi value allowed for a packet
        :type logging_thread: string
        :param logging_thread: name of thread that will log the data
        :type only_add_tags_after_location_ends: bool
        :param only_add_tags_after_location_ends: if True will add the adv_addresses to
                                                  self.adv_addresses_in_current_location when calling to
                                                  self.set_new_location()
        :type add_to_black_list_after_locations: int (minimum is 2)
        :param add_to_black_list_after_locations: amount of locations a tag should appear in until
                                                  it will be added to black list
        """
        self.lock_print = lock_print
        self.rssi_threshold = int(rssi_threshold)
        self.only_add_tags_after_location_ends = only_add_tags_after_location_ends
        self.tags_list = []
        self.tags_list_len = tags_list_len
        self.cur_tag_adv_addr = None
        self.cur_tag_location = -1  # to make the first location be 0 (when calling set_new_location())
        self.cur_tag_min_rssi = np.inf  # big value, any real value will be much smaller
        self.group_id_hist = {}  # histogram of the group_id in this run
        self.black_list = []  # tags to ignore during the run
        self.black_list_candidates_hist = {}  # holds tags that will be added to black list if will reach to threshold
        self.add_to_black_list_after_locations = add_to_black_list_after_locations
        self.packets_in_current_location = []  # list of dictionaries (raw_data) of packets in this location
        self.adv_addresses_in_current_location = []  # list of adv_address from this location
        self.logging_thread = logging_thread
        self.problem_in_locations_hist = {'tag from black list': 0, 'bad group id': 0, 'above rssi threshold': 0,
                                          'packet from bridge': 0, 'duplication': 0, 'no singularization': 0}
        self.prev_location_problem_in_locations_hist = copy.copy(self.problem_in_locations_hist)
    
    def encrypted_packet_filter(self, raw_data, is_test_mode_packet=False):
        """
        checks if the packet is good in terms of RSSI, tag UID
        :type raw_data: dictionary (return value from gw_api.packet_listener (PROCESSED))
        :param raw_data: raw data of the tags
        :type is_test_mode_packet: bool
        :param is_test_mode_packet: is it a test mode packet (will only use the filtering by rssi)
        :return: is_good_packet - is the packet relevant for this run,
                 need_to_check_TBP - you should open wide window for catching more packets (using get_rates())
                                     due to Duplication/ non singularity issue (TBP =  time between packets)
                 reason_to_fail - string with reason for failing the packet (for logging in debug mode)
        """
        try:
            time.sleep(0)
            if is_test_mode_packet:
                if self.rssi_threshold is not None:
                    if int(raw_data['rssi']) > self.rssi_threshold:
                        msg = str(raw_data['packet']) + " - Packet rssi is too high"
                        printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                        reason_to_fail = 'rssi'
                        self.add_hist_val('above rssi threshold')
                        return False, False, reason_to_fail
                reason_to_fail = 'good'
                return True, False, reason_to_fail
            # check if the tag is in the black list
            if raw_data['adv_address'] in self.black_list:
                msg = str(raw_data['packet']) + " - tag that is in the black list (will be ignored)"
                printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                reason_to_fail = 'blackList'
                self.add_hist_val('tag from black list')
                return False, False, reason_to_fail
            
            else:
                self.packets_in_current_location.append(raw_data)
                
                # check if it is a bridge packet
                if self.is_packet_from_bridge(raw_data):
                    self.add_tag_to_black_list(raw_data['adv_address'])
                    msg = str(raw_data['packet']) + " - packet generated by Wiliot bridge found, " \
                                                    "will add it to the black list"
                    printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                    reason_to_fail = 'bridge'
                    self.add_hist_val('packet from bridge')
                    return False, False, reason_to_fail
                
                # check if the tag group_id is the same as the rest of the tags
                bad_group_id = False
                if raw_data['group_id'] is not None:
                    if raw_data['group_id'] not in self.group_id_hist.keys():
                        if len(self.group_id_hist) > 0:
                            max_group_id = max(self.group_id_hist.values())
                            for i, (group, group_val) in enumerate(self.group_id_hist.items()):
                                if group_val == max_group_id and not raw_data['group_id'] == group:
                                    bad_group_id = True
                        self.group_id_hist[raw_data['group_id']] = 1
                    else:
                        if len(self.group_id_hist) > 0:
                            max_group_id = max(self.group_id_hist.values())
                            for i, (group, group_val) in enumerate(self.group_id_hist.items()):
                                if group_val == max_group_id and not raw_data['group_id'] == group:
                                    bad_group_id = True
                        self.group_id_hist[raw_data['group_id']] += 1
                    if bad_group_id:
                        msg = str(raw_data['packet']) + " - packet with wrong group_id found (group_id = " + \
                              str(raw_data['group_id']) + ', group_id seen so far (from all packets) = ' + \
                              str(self.group_id_hist) + ')'
                        printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                        reason_to_fail = 'group_id'
                        self.add_hist_val('bad group id')
                        return False, False, reason_to_fail
                
                # check if the RSSI is good
                if self.rssi_threshold is not None:
                    if int(raw_data['rssi']) > self.rssi_threshold:
                        msg = str(raw_data['packet']) + " - Packet rssi is too high"
                        printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                        reason_to_fail = 'rssi'
                        self.add_hist_val('above rssi threshold')
                        return False, False, reason_to_fail
                
                is_new_tag = self.add_new_tag_to_tags_list(raw_data)
                
                # check if the tag was already caught in the GW
                if not is_new_tag:
                    msg = str(raw_data['packet']) + " - Duplication from a tag we have seen before (advAddress = " \
                          + raw_data['adv_address'] + ")"
                    printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                    reason_to_fail = 'duplication'
                    self.add_hist_val('duplication')
                    return True, True, reason_to_fail
                
                # check if this packet is from new tag
                if is_new_tag and self.cur_tag_adv_addr != raw_data['adv_address'] and \
                        self.cur_tag_adv_addr is not None:
                    msg = str(raw_data['packet']) + " - no singularity issue (did not see this tag before), " \
                                                    "new tag advAddress = " + str(raw_data['adv_address']) \
                          + ", new tag rssi = " + str(raw_data['rssi']) \
                          + ', current tag rssi = ' + str(self.cur_tag_min_rssi)
                    printing_func(msg, self.logging_thread, self.lock_print, logger_type='debug')
                    reason_to_fail = 'no singularity'
                    self.add_hist_val('no singularization')
                    return True, True, reason_to_fail
                
                self.cur_tag_adv_addr = raw_data['adv_address']
                if self.cur_tag_min_rssi > int(raw_data['rssi']):
                    self.cur_tag_min_rssi = int(raw_data['rssi'])
                
                reason_to_fail = 'good'
                return True, False, reason_to_fail
        
        except Exception as e:
            printing_func('Exception during encrypted_packet_filter: ' + str(e), self.logging_thread,
                          self.lock_print, logger_type='debug')
            return False, False, 'exception'
    
    def is_packet_from_bridge(self, raw_data):
        """
        check if the packet generated by Wiliot bridge
        :type raw_data: dictionary (return value from gw_api.packet_listener)
        :param raw_data: raw data of the tags
        :return: True if the tag is bridge packet, False otherwise
        """
        chars_starts_with10_bits = ['8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        if str(raw_data['packet'])[0].upper() in chars_starts_with10_bits and 'AFFD' in str(raw_data['packet']):
            return True
    
    def add_new_tag_to_tags_list(self, raw_data):
        """
        adds a new tag's adv_address to the list of the tags we have seen before
        :type raw_data: dictionary (return value from gw_api.packet_listener)
        :param raw_data: raw data of the tags
        :return: True if the tag is a new tag, False otherwise
        """
        if self.only_add_tags_after_location_ends:
            if raw_data['adv_address'] not in self.adv_addresses_in_current_location:
                self.adv_addresses_in_current_location.append(raw_data['adv_address'])
            if raw_data['adv_address'] not in self.tags_list:
                return True
            else:
                return False
        
        elif raw_data['adv_address'] not in self.tags_list:
            if len(self.tags_list) <= self.tags_list_len:
                self.tags_list.append(str(raw_data['adv_address']))
            else:
                del self.tags_list[0]
                self.tags_list.append(str(raw_data['adv_address']))
            return True
        else:
            return False
    
    def add_tag_to_black_list(self, adv_address):
        """
        adds a tag's adv_address to the black list (tags to ignore during the run)
        :type adv_address: string
        :param adv_address: adv_address of the tag to add to black list
        :return: True if the tag is a new tag, False otherwise
        """
        if adv_address not in self.black_list:
            self.black_list.append(adv_address)
            return True
        else:
            return False
    
    def add_hist_val(self, key):
        """
        :type key: string
        :param key: one of the keys in self.problem_in_locations_hist
        """
        if key not in self.prev_location_problem_in_locations_hist.keys() or \
                key not in self.problem_in_locations_hist.keys():
            return
        
        if self.prev_location_problem_in_locations_hist[key] == self.problem_in_locations_hist[key]:
            self.problem_in_locations_hist[key] += 1
    
    def set_new_location(self):
        """
        reset all packet rates from previous tags, will start rates comparison with tags received from now
        until this function will be called again
        """
        for adv_address in self.adv_addresses_in_current_location:
            if adv_address not in self.tags_list:
                if self.only_add_tags_after_location_ends:
                    if len(self.tags_list) <= self.tags_list_len:
                        self.tags_list.append(str(adv_address))
                    else:
                        del self.tags_list[0]
                        self.tags_list.append(str(adv_address))
            else:
                if adv_address not in self.black_list_candidates_hist.keys():
                    self.black_list_candidates_hist[adv_address] = 2  # already appeared in previous location
                else:
                    self.black_list_candidates_hist[adv_address] += 1
                if self.black_list_candidates_hist[adv_address] >= self.add_to_black_list_after_locations:
                    self.add_tag_to_black_list(adv_address)
        
        self.adv_addresses_in_current_location = []
        self.packets_in_current_location = []
        self.cur_tag_location += 1
        self.cur_tag_adv_addr = None
        self.prev_location_problem_in_locations_hist = copy.copy(self.problem_in_locations_hist)
    
    def is_tag_appeared_before(self, adv_addr):
        return adv_addr in self.tags_list
    
    def get_black_list_size(self):
        return len(self.black_list)


###########################################
#              Tester GUI             #
###########################################
def upload_conclusion(succeeded_csv_uploads=None):
    """
    :type failed_tags: list or None
    :param failed_tags: list of dictionaries ({'tag_id': XXX, 'status': YYY}) of tags that failed in serialization
    :type succeeded_csv_uploads: bool or None
    :param succeeded_csv_uploads: if True - upload of csv has succeeded
    """
    if succeeded_csv_uploads is None or succeeded_csv_uploads:
        msg = "Upload CSVs succeeded"
        bg = 'green'
    else:
        msg = "Upload CSVs Failed!\nPlease check log file for more details"
        bg = 'red'
    popup_message(msg=msg, bg=bg)


###########################################
#                   Log                   #
###########################################
def update_json_field(path, key, value):
    """
    update json config file value
    :type path: string
    :param path: json config file path
    :type key: string
    :param key: key to change in json file
    :type value: string
    :param value: value to change @key to
    :return:
    """
    with open(path, "r+") as jsonFile:
        config_data = json.load(jsonFile)
        
        config_data[key] = value
        
        jsonFile.seek(0)
        json.dump(config_data, jsonFile)
        jsonFile.truncate()


class CsvLog:
    """
    Class for csv logs
    """
    
    def __init__(self, header_type, path, headers=None, tester_type=TesterName.NONE, temperature_sensor=False,
                 is_debug_mode=False):
        """
        :type header_type: HeaderType
        :param header_type:
        :param path:
        :param headers:
        :param tester_type:
        :type temperature_sensor: bool
        :param temperature_sensor: if True -> temperature sensor enabled -> add header. else: sensor is disabled
        :type is_debug_mode: bool
        :param is_debug_mode: if True adds more columns to tags_data, if False will not add anything
                              (only in offline tester)
        """
        self.tags_header = ['advAddress', 'tagLocation', 'status', 'commonRunName', 'rawData']
        
        self.run_header = ['testerStationName', 'commonRunName', 'batchName', 'testerType',
                           'comments', 'errors',
                           'timeProfile', 'txPower', 'energizingPattern',
                           'tested', 'passed', 'yield', 'inlay']
        
        self.packets_header = ['commonRunName', 'encryptedPacket', 'time']
        
        if header_type.value == HeaderType.TAG.value:
            self.header = self.tags_header
        elif header_type.value == HeaderType.RUN.value:
            self.header = self.run_header
        elif header_type.value == HeaderType.PACKETS.value:
            self.header = self.packets_header
        else:
            self.header = []
        self.path = path
        
        # add additional columns per tester:
        self.temperature_sensor_enable = temperature_sensor
        self.add_headers(headers, header_type, tester_type, is_debug_mode)
    
    def add_headers(self, headers=None, header_type=HeaderType.RUN, tester_type=TesterName.NONE, is_debug_mode=False):
        """
        added additional headers to output file according to file type and tester type
        :type headers:
        :param headers: additional headers for output file (determined by user)
        :type header_type: HeaderType
        :param header_type: determines if the file generated stores run data or tags data
        :type tester_type: TesterName
        :param tester_type: determines unique headers to add according to tester type
        :type is_debug_mode: bool
        :param is_debug_mode: if True adds more columns to tags_data, if False will not add anything
                              (only in offline tester)
        """
        if headers is None:
            if header_type.value == HeaderType.RUN.value:
                if tester_type.value == TesterName.OFFLINE.value:
                    added_headers = ['testTime', 'maxTtfp', 'converted', 'surface', 'tagGen',
                                     'toPrint', 'passJobName', 'printingFormat', 'stringBeforeCounter',
                                     'digitsInCounter', 'gwVersion', 'desiredPass',
                                     'desiredTags', 'firstPrintingValue', 'missingLabel', 'maxMissingLabels']
                    # TODO - add this list instead af the previous when cloud supports it
                    # added_headers = ['testTime', 'maxTtfp', 'converted', 'surface', 'tagGen',
                    #                  'toPrint', 'passJobName', 'printingFormat', 'stringBeforeCounter',
                    #                  'digitsInCounter', 'gwVersion', 'secondEnergizingPattern', 'desiredPass',
                    #                  'desiredTags', 'firstPrintingValue', 'missingLabel', 'maxMissingLabels',
                    #                  'temperatureSensorEnable', 'wiliotPackageVersion']
                
                elif tester_type.value == TesterName.TAL15K.value:
                    added_headers = ['testersGwVersion', 'chargerGwVersion', 'rowsNum', 'columnsNum',
                                     'numOfTesters', 'chargingTime', 'timePerTag']
                elif tester_type.value == TesterName.CONVERSION.value:
                    added_headers = []
                elif tester_type.value == TesterName.SAMPLE.value:
                    added_headers = ['responded', 'responding[%]', 'passed[%]', 'validTbp[%]', 'testStatus',
                                     'operator', 'testTime', 'runStartTime', 'runEndTime', 'antennaType',
                                     'surface', 'numChambers', 'gwVersion', 'pyWiliotVersion',
                                     'bleAttenuation', 'loraAttenuation', 'testTimeProfilePeriod',
                                     'testTimeProfileOnTime', 'ttfpAvg', 'tbpAvg', 'tbpStd', 'rssiAvg', 'maxTtfp',
                                     'controlLimits', 'hwVersion', 'sub1gFrequency', 'failBinStr', 'failBin',
                                     'uploadToCloud']
                else:
                    added_headers = []
            elif header_type.value == HeaderType.TAG.value:
                if tester_type.value == TesterName.OFFLINE.value:
                    added_headers = ['externalId']
                    if self.temperature_sensor_enable:
                        added_headers.append('temperatureFromSensor')
                    if is_debug_mode:
                        added_headers.append('AdvAddressesInLocation')
                        added_headers.append('packetsTimeDiff')
                        added_headers.append('Ttfgp')
                elif tester_type.value == TesterName.SAMPLE.value:
                    added_headers = ['externalId', 'temperature_from_sensor']
                else:
                    added_headers = []
            elif header_type.value == HeaderType.PACKETS.value:
                added_headers = []
                if tester_type.value == TesterName.OFFLINE.value:
                    added_headers = ['externalId', 'tagLocation', 'packetStatus', 'chosenTagInLocation',
                                     'chosenTagStatus', 'rssi', 'advAddr', 'gw_tx_power', 'attenuation', 'gw_time',
                                     'packet_data', 'tbp', 'test_num', 'test_duration']
                    if self.temperature_sensor_enable:
                        added_headers.append('temperatureFromSensor')
                elif tester_type.value == TesterName.SAMPLE.value:
                    added_headers = ['externalId', 'chamber', 'status',
                                     'state(tbp_exists:0,no_tbp:-1,no_ttfp:-2,dup_adv_address:-3)', 'fail_bin',
                                     'reel', 'ttfp', 'tbp', 'adv_address', 'temperature_from_sensor']
            else:
                added_headers = []
        else:
            added_headers = headers
        self.header += added_headers
    
    def open_csv(self):
        """
        create csv file if not exist
        """
        # dir_path = self.path[:(len(self.path) - (len(self.path.split('/')[-1])+1))]
        dir_path = dirname(self.path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if not os.path.isfile(self.path):
            with open(self.path, 'w', newline='') as write_obj:
                csv_writer = writer(write_obj)
                csv_writer.writerow(self.header)
    
    def append_dict_as_row(self, data_to_append):
        """
        append data list to existing csv
        @type data_to_append: list
        @param data_to_append: dictionary for each new row
        """
        # Open file in append mode
        with open(self.path, 'a+', newline='') as write_obj:
            # Create a dict writer object from csv module
            csv_writer = DictWriter(write_obj, fieldnames=self.header)
            # Add contents of list as last rows in the csv file
            csv_writer.writerows(data_to_append)
    
    def append_list_as_row(self, data_to_append):
        """
        append data list to existing csv
        @type data_to_append: list
        @param data_to_append: values to append to csv
        """
        # Open file in append mode
        with open(self.path, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(data_to_append)
    
    def append_table(self, data_table):
        """
        append data table to existing csv (using append_list_as_row)
        @type: data_table: list (list of lists)
        @param data_table: values to append to csv
        """
        col = 0  # the table has only 1 column
        for i in range(len(data_table)):
            self.append_list_as_row(self.dict_to_list(data_table[i][col]))
    
    def dict_to_list(self, data):
        """
        convert dict to list
        @type data: dict
        @param data:
        @rtype: list
        """
        res_list = []
        for title in self.header:
            if title in data.keys():
                res_list.append(data[title])
            else:
                res_list.append('')
        return res_list
    
    def override_run_data(self, run_data, path_=None):
        """
        override run_data.csv at the end of run
        @type run_data: dict
        @param run_data: run configurations and results such as passed, tested, yield, etc.
        """
        if path_ is None:
            path_ = self.path
        
        with open(path_, 'w', newline='') as write_obj:
            csv_writer = writer(write_obj)
            csv_writer.writerow(self.header)
            # self.append_list_as_row(self.path, self.dict_to_list(run_data))
            csv_writer.writerow(self.dict_to_list(run_data))


if __name__ == '__main__':
    upload_conclusion(False)
