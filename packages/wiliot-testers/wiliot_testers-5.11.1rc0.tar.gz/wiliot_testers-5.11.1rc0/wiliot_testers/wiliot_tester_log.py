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
from wiliot_core import WiliotDir

import time
import os
import logging
from csv import DictWriter
import datetime


class WiliotTesterLog(object):
    def __init__(self, run_name=''):
        """
        generates both log files and CSV output files
        :param run_name: the test run name. used as the folder name and the files prefix
        :type run_name: str
        """

        self.stream_handler = None
        self.stream_handler2 = None
        self.stream_handler_gw = None
        self.log_path = ''
        self.file_handler = None
        self.run_name = run_name
        self.logger = None
        self.file_formatter = None
        self.gw_logger = None
        self.results_logger = None
        self.run_data = {}
        self.run_header = []
        self.packets_header = []
        self.run_data_name = ''
        self.packets_data_name = ''
        self.run_data_path = ''
        self.packets_data_path = ''
        self.data_folder = ''
        self.run_start_time = ''
        self.tester_station_name = ''

    def set_logger(self, log_path=None, tester_name='tester'):
        ''' Sets the logger if doesn't exist from main code - INFO level
        3 loggers declared
        self.logger - our main for packet
        self.results_logger - for results
        self.gw_logger - for GW logging'''

        self.logger = logging.getLogger('WiliotLogger')
        formatter = logging.Formatter('\x1b[36;20m%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                                      '%H:%M:%S')
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)
        self.logger.setLevel(logging.DEBUG)
        # Set format - Check PixieLog by Dudan

        self.gw_logger = logging.getLogger('GWLogger')
        self.results_logger = logging.getLogger('Testing')

        formatter2 = logging.Formatter('\x1b[33;20m%(message)s')
        gw_formatter = logging.Formatter('\x1b[38;20m%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                                         '%H:%M:%S')

        self.stream_handler2 = logging.StreamHandler()
        self.stream_handler2.setLevel(logging.DEBUG)
        self.stream_handler2.setFormatter(formatter2)

        self.stream_handler_gw = logging.StreamHandler()
        self.stream_handler_gw.setLevel(logging.INFO)
        self.stream_handler_gw.setFormatter(gw_formatter)

        if log_path is None:
            wiliot_dir = WiliotDir()
            wiliot_dir.create_tester_dir(tester_name)
            self.log_path = os.path.join(wiliot_dir.get_tester_dir(tester_name), 'logs')
        else:
            self.log_path = os.path.join(log_path, self.run_name)

        try:
            if not os.path.isdir(self.log_path):
                os.mkdir(self.log_path)
            logger_name = self.run_name + '.log'
            logger_path = os.path.join(self.log_path, logger_name)
        except Exception as e:
            self.logger.critical('Params input is invalid')
            raise e

        self.file_handler = logging.FileHandler(logger_path, mode='a')
        self.file_formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s', '%H:%M:%S')
        self.file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(self.file_handler)
        self.results_logger.addHandler(self.file_handler)
        self.gw_logger.addHandler(self.file_handler)

        self.gw_logger.addHandler(self.stream_handler_gw)
        self.gw_logger.setLevel(logging.INFO)

        self.results_logger.addHandler(self.stream_handler2)
        self.results_logger.setLevel(logging.DEBUG)

        self.logger.info(
            'Log created, path : {}'.format(str(self.log_path)))
        time.sleep(0.3)

    def create_data_dir(self, data_path=None, tester_name='tester', run_name='test'):
        """
        create the data directory
        :param data_path: the directory path of the csv data
        :type data_path: str
        :param tester_name: the tester name such as offline teser. relevant only if data path is not specified
        :type tester_name: str
        :param run_name: the test run name. used as the folder name and the files prefix
        :type run_name: str
        :return: the data pth of the run file (configuration for the whole file) and the path of packets file
                 which contains all packets received during test
        :rtype: str, str
        """
        self.run_name = run_name
        if data_path is None:
            wiliot_dir = WiliotDir()
            wiliot_dir.create_tester_dir(tester_name)
            data_path = os.path.join(wiliot_dir.get_tester_dir(tester_name), 'logs')

        # create folders:
        data_folder = os.path.join(data_path, run_name)
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        self.data_folder = data_folder
        self.run_data_name = run_name + '@run_data.csv'
        self.packets_data_name = run_name + '@packets_data.csv'
        self.run_data_path = os.path.join(data_folder, self.run_data_name)
        self.packets_data_path = os.path.join(data_folder, self.packets_data_name)

        return self.run_data_path, self.packets_data_path

    def set_new_path(self, path, formatter=None):
        if self.file_handler is not None:
            self.logger.removeHandler(self.file_handler)
            self.results_logger.removeHandler(self.file_handler)
            self.gw_logger.removeHandler(self.file_handler)
        self.file_handler = logging.FileHandler(path, mode='a')
        if formatter is None and self.file_formatter is None:
            self.file_formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                                                    '%H:%M:%S')
        else:
            self.file_formatter = formatter

        self.file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(self.file_handler)
        self.results_logger.addHandler(self.file_handler)
        self.gw_logger.addHandler(self.file_handler)

    def set_common_run_name(self, reel_name=None, run_start_time=None, lane_str=''):
        if reel_name is None:
            reel_name = 'test'
        if run_start_time is None:
            run_start_time = datetime.datetime.now()
        
        lane_str = lane_str + '_' if lane_str != '' else lane_str
        common_run_name =  reel_name + '_' + lane_str + run_start_time.strftime("%Y%m%d_%H%M%S")

        self.run_name = common_run_name
        self.run_start_time = run_start_time

        return common_run_name

    def set_station_name(self, tester_station_name):
        self.tester_station_name = tester_station_name

    @staticmethod
    def set_console_handler_level(logger, level):
        for handler in logger.handlers:
            original_formatter = handler.formatter  # Store the original formatter
            handler.setLevel(level)
            handler.setFormatter(original_formatter)  # Re-apply the original formatter


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
