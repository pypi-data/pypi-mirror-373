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
from os.path import join, abspath
import os
import time
from wiliot_api import ManufacturingClient
from wiliot_core import WiliotGateway, GetApiKey
from wiliot_testers.utils.upload_to_cloud_api import upload_to_cloud_api
from wiliot_testers.utils.get_version import get_version
from wiliot_testers.wiliot_tester_log import WiliotTesterLog, dict_to_csv
from wiliot_testers.wiliot_tester_tag_test import WiliotTesterTagTest
from wiliot_testers.wiliot_tester_tag_result import FailureCodes


class SimpleTest:

    def __init__(self,
                 owner_id='wiliot-ops',
                 output_path=None,
                 test_name=None,
                 test_time=None,
                 tester_type='sample',
                 test_env='test',
                 upload_to_cloud=False):
        """
                Initialize the SampleChamber object.

                Parameters: - mode (str): The mode of operation, either "online" or "offline". - external_id (str):
                The external ID of the tag. - test (str): The name of the test to perform according to the tests in
                .default_test_configs.json. - env (str): The environment for cloud connection, either "prod" or
                "test". - surface (str): The surface to simulate, default is 'no simulation' - data according to the
                .default_surfaces.json. - output_path (str): The path where output files will be stored,
                if not mentioned - it will be saved in <USER>/AppData/Local/wiliot/sample/logs directory.

                Initializes various instance variables and starts the test.
                """

        self.run_data_path = None
        self.packets_data_path = None
        self.name = test_name if test_name is not None else 'SimpleTest'
        self.output = output_path
        self.test_data = None
        self.runDataDict = None
        self.gw_version = None
        self.client = None
        self.tester_type = tester_type
        cur_time = time.strftime("_%d%m%y_%H%M%S")
        self.common_run_name = self.name + cur_time
        self.pywiliot_version = get_version()
        self.test = 'Simple Test'
        self.test_suite = None
        self.env = test_env
        self.owner_id = owner_id
        self.packets_csv = None

        self.logger = self.test_configs(test_time=test_time)  # Read all default values from JSONs
        self.gateway_obj = self.com_connect()  # Connect to all HW
        # Init Wiliot Tester SDK
        self.wiliot_tag_test = WiliotTesterTagTest(test_suite=self.test_suite,
                                                   selected_test=self.test,
                                                   logger_name=self.logger.logger.name,
                                                   logger_result_name=self.logger.results_logger.name,
                                                   logger_gw_name=self.logger.gw_logger.name,
                                                   gw_obj=self.gateway_obj)

        self.connect_to_cloud()

        result = self.start_test()

        if result and upload_to_cloud:
            self.logger.logger.info(f'Test done, \nData stored at {self.logger.log_path} \nStarting uploading to cloud')
            upload = self.cloud_upload()

            if not upload:
                self.logger.logger.warning('Failed to upload data to the cloud, please upload it manually')

        self.close_gw_port()

    def test_configs(self, test_time=None):
        """
        Configure the test environment.

        Reads configurations from JSON files and validates them.
        Also sets up logging and test suites according to the test provided.
        """

        logger = None
        try:

            logger = WiliotTesterLog()
            logger.set_common_run_name(reel_name='SimpleTest')
            logger.set_logger(log_path=self.output, tester_name='SimpleTest')
            self.run_data_path, self.packets_data_path = logger.create_data_dir(self.output,
                                                                                tester_name='SimpleTest',
                                                                                run_name=self.common_run_name)
            logger.set_console_handler_level(logger.logger, logging.DEBUG)
            logger.set_console_handler_level(logger.gw_logger, logging.WARNING)
            logger.set_console_handler_level(logger.results_logger, logging.DEBUG)
            sample_test_dir = os.getcwd()
            config_dir = abspath(join(sample_test_dir, 'configs'))

            with open(abspath(join(config_dir, 'test_suite_example.json')), 'r') as TestSuite:
                self.test_suite = json.load(TestSuite)
                if test_time is not None:
                    self.test_suite[self.test]['maxTtfp'] = int(test_time)
                    self.test_suite[self.test]['tests'][0]['maxTime'] = int(test_time)

        except Exception as e:
            if logger is not None:
                logger.logger.error(f'Could not read test suite: {e}')
            raise Exception(e)

        return logger

    def com_connect(self):
        """
                Connect to all hardware components.

                Parameters:
                - default_coms (dict): Dictionary containing default COM port configurations.

                Connects to the Gateway, Attenuators [BLE and LORA],
                Barcode Scanner (if available), and Temperature Sensors (if available).
                """
        gateway_obj = None
        try:
            # Connect to the GW
            gateway_obj = WiliotGateway(auto_connect=True,
                                        logger_name=self.logger.gw_logger.name)
            if gateway_obj.is_connected():
                self.gw_version = gateway_obj.get_gw_version()
                self.logger.logger.info('GW connected')

            else:
                raise Exception('GW is not connected')

        except Exception as e:
            self.logger.logger.error(
                f'Could not detect GW, {e}')
            exit()

        return gateway_obj

    def connect_to_cloud(self):
        """
        Establishes a secure connection to the cloud service for data storage and validation.

        Parameters: - env (str): Specifies the cloud environment to connect to. It can be either 'prod' for
        production or 'test' for testing.

        Steps:
        1. Reads the user's cloud configuration file to obtain API keys and owner IDs.
        2. Validates the owner ID against a predefined list of valid owner IDs.
        3. Initializes the cloud client using the API key and specified environment.
        4. Logs the successful establishment of the cloud connection.

        Note: If the connection fails or configurations are invalid, the function will raise an exception and close
        the Gateway port.
        """
        try:
            g = GetApiKey(gui_type='ttk', env=self.env, owner_id=self.owner_id)
            api_key = g.get_api_key()
            if not api_key:
                raise Exception(f'Could not found an api key for owner id {self.owner_id} and env {self.env}')

            self.client = ManufacturingClient(api_key=api_key, env=self.env, logger_=self.logger.logger.name)
            self.logger.logger.info('Connection to the cloud was established')

        except Exception as e:
            self.close_gw_port()
            raise Exception(f'Problem connecting to cloud {e}')

    def close_gw_port(self):
        """
                Close the connection to the Gateway.

                If the Gateway is connected, this function will close the port.
                """
        self.gateway_obj.close_port()
        self.gateway_obj.exit_gw_api()

    def start_test(self):
        """
        Initiates and executes the test sequence for Wiliot pixie.

        This function performs several key tasks:
        1. Initializes the data structures for storing test results in CSV format.
        2. Executes the test by calling the `run()` method on the `wiliot_tag_test` object.
        3. Collects statistics and summary information about the test.
        4. Populates the run data dictionary with test results and statistics.
        5. Updates the packets data CSV with packet-level information.
        6. If in 'online' mode, it also validates the test results by comparing them with cloud data.

        Returns:
        - True: If the test and optional validation are successful.
        - False: If the test or validation fails.

        Note: This function will also close the Gateway port in case of an exception.
        """
        try:
            self.initialize_csv_data()  # Init the run result dictionary
            res = self.wiliot_tag_test.run()  # Begin the run

            if res.is_results_empty():
                #   Failed
                self.logger.logger.error('Test failed')
                if self.tester_type == 'sample':
                    self.runDataDict['tested'] = 0
                else:
                    self.runDataDict['total_run_tested'] = 0
                self.runDataDict['responded'] = 0
                self.runDataDict['passed'] = 0
                raise Exception('something went wrong during test and test was not preformed')

            selected_tag_statistics = res.tests[0].selected_tag.get_statistics()  # Get all the statistics
            test_sum = res.tests[0].get_summary()

            if self.tester_type == 'sample':
                self.runDataDict['tested'] = 1
            else:
                self.runDataDict['total_run_tested'] = 1
            self.runDataDict['testTime'] = str(res.get_total_test_duration())
            self.runDataDict['passed'] = int(res.is_all_tests_passed())
            self.runDataDict['responded'] = int(1 if res.tests[0].all_packets.__len__() > 0 else 0)
            if self.tester_type == 'sample':
                self.runDataDict['responding[%]'] = str(
                    self.runDataDict['responded'] / self.runDataDict['tested'] * 100) + '%'
                self.runDataDict['passed[%]'] = str(self.runDataDict['passed'] / self.runDataDict['tested'] * 100) + '%'
            else:
                self.runDataDict['responding[%]'] = str(
                    self.runDataDict['responded'] / self.runDataDict['total_run_tested'] * 100) + '%'
                self.runDataDict['passed[%]'] = str(
                    self.runDataDict['passed'] / self.runDataDict['total_run_tested'] * 100) + '%'

            if self.runDataDict['passed']:
                self.logger.logger.info('Test passed')
            elif self.runDataDict['responded']:
                selected_tag_statistics = res.tests[0].all_packets.get_statistics()
                self.logger.logger.info('Test failed, tag responded but tbp could not be calculated')
            else:
                self.logger.logger.info('Test failed, tag did not respond')

            # save files:
            self.populate_run_data(selected_tag_statistics, test_sum)  # Fill run result dictionary
            self.update_packets_data(res, selected_tag_statistics)

            self.wiliot_tag_test.exit_tag_test()
            return True

        except Exception as e:
            self.close_gw_port()
            self.logger.logger.error(f'Problem starting the test {e}')
            return False

    def initialize_csv_data(self):
        """
                Initialize the CSV data structures.

                Sets up dictionaries for run data and packet data.
                """

        test_values = self.test_suite[self.test]['tests'][0]
        if self.tester_type == 'sample':
            self.runDataDict = {
                'testerStationName': 'WiliotSample',
                'commonRunName': self.common_run_name,
                'batchName': '',
                'testerType': self.tester_type,
                'comments': '',
                'errors': '',
                'timeProfile': test_values.get('timeProfile', ''),
                'txPower': test_values.get('absGwTxPowerIndex', ''),
                'energizingPattern': test_values.get('energizingPattern', ''),
                'tested': '0',
                'passed': '0',
                'yield': '0',
                'inlay': '',
                'responded': '0',
                'responding[%]': '0',
                'passed[%]': '0',
                'testStatus': 'False',
                'operator': 'Wiliot',
                'testTime': '',
                'runStartTime': '',
                'runEndTime': '',
                'antennaType': 'TIKI',
                'surface': '',
                'numChambers': '1',
                'gwVersion': self.gw_version,
                'pyWiliotVersion': self.pywiliot_version,
                'bleAttenuation': '',
                'loraAttenuation': '',
                'testTimeProfilePeriod': test_values.get('timeProfile'[1], ''),
                'testTimeProfileOnTime': test_values.get('timeProfile'[0], ''),
                'ttfpAvg': '',
                'tbpAvg': '',
                'tbpStd': '',
                'rssiAvg': '',
                'maxTtfp': '',
                'controlLimits': '',
                'hwVersion': '',
                'sub1gFrequency': '',
                'failBinStr': '',
                'failBin': ''
            }

            self.test_data = {
                'commonRunName': self.common_run_name,
                'encryptedPacket': '',
                'time': '',
                'reel': self.common_run_name,
                'ttfp': '',
                'tbp': '',
                'adv_address': '',
                'status': ''}
        else:
            self.runDataDict = {
                'testerStationName': 'WiliotSample',
                'commonRunName': self.common_run_name,
                'batchName': '',
                'testerType': self.tester_type,
                'comments': '',
                'errors': '',
                'timeProfile': test_values.get('timeProfile', ''),
                'txPower': test_values.get('absGwTxPowerIndex', ''),
                'energizingPattern': test_values.get('energizingPattern', ''),
                'total_run_tested': '0',
                'passed': '0',
                'yield': '0',
                'inlay': '',
                'responded': '0',
                'responding[%]': '0',
                'passed[%]': '0',
                'testStatus': 'False',
                'operator': 'Wiliot',
                'testTime': '',
                'runStartTime': '',
                'runEndTime': '',
                'antennaType': 'TIKI',
                'surface': '',
                'numChambers': '1',
                'gwVersion': self.gw_version,
                'pyWiliotVersion': self.pywiliot_version,
                'bleAttenuation': '',
                'loraAttenuation': '',
                'testTimeProfilePeriod': test_values.get('timeProfile'[1], ''),
                'testTimeProfileOnTime': test_values.get('timeProfile'[0], ''),
                'ttfpAvg': '',
                'test_suite_dict': self.test_suite[self.test],
                'owner_id': self.owner_id,
                'to_print': False,
                'qr_validation': False,
                'tbpAvg': '',
                'tbpStd': '',
                'rssiAvg': '',
                'maxTtfp': '',
                'controlLimits': '',
                'hwVersion': '',
                'sub1gFrequency': '',
                'failBinStr': '',
                'failBin': ''
            }

            self.test_data = {
                'common_run_name': self.common_run_name,
                'raw_packet': '',
                'adv_address': '',
                'time_from_start': '',
                'ttfp': '',
                'tbp_mean': '',
                'rssi': '',
                'gw_packet': '',
                'tag_run_location': '0',
                'external_id': '',
                'status_offline': '',
                'selected_tag': '',
                'fail_bin': '',
                'fail_bin_str': '',
                'test_num': 0,
                'is_test_pass': '',
                'packet_status': ''}

        dict_to_csv(dict_in=self.runDataDict, path=self.run_data_path, append=False, only_titles=True)
        dict_to_csv(dict_in=self.test_data, path=self.packets_data_path, append=False, only_titles=True)

    def populate_run_data(self, selected_tag_statistics, test_sum):
        """
                Populate the run data dictionary.

                Parameters:
                - selected_tag_statistics (dict): Statistics of the selected tag.
                - test_sum (dict): Summary of the test.

                Fills the run data dictionary with test results and statistics.
                """
        self.runDataDict['testStatus'] = bool(test_sum['is_test_pass'])
        self.runDataDict['runStartTime'] = test_sum['test_start_time'].strftime("%Y-%m-%d %H:%M:%S.%f")
        self.runDataDict['runEndTime'] = test_sum['test_end_time'].strftime("%Y-%m-%d %H:%M:%S.%f")
        self.runDataDict['ttfpAvg'] = str(selected_tag_statistics.get('ttfp', 'nan'))
        self.runDataDict['tbpAvg'] = str(selected_tag_statistics.get('tbp_mean', 'nan'))
        self.runDataDict['tbpStd'] = str(selected_tag_statistics.get('tbp_std', 'nan'))
        self.runDataDict['rssiAvg'] = str(selected_tag_statistics.get('rssi_mean', 'nan'))
        self.runDataDict['maxTtfp'] = str(selected_tag_statistics.get('ttfp', 'nan'))
        dict_to_csv(dict_in=self.runDataDict, path=self.run_data_path, append=True, only_titles=False)

    def update_packets_data(self, res=None, stats=None):
        """
                Update the packets data CSV.

                Parameters:
                - res (object): The result object containing test data.
                - stats (dict): Statistics of the selected tag.

                Updates the packets data CSV with packet information.
                """

        if res:
            r = res.tests[0]
            if r.selected_tag.__len__() > 0:  # pass
                tag_data = r.selected_tag
            elif r.all_packets.__len__() > 0:  # responded but did not pass
                tag_data = r.all_packets
            else:  # No response
                if self.tester_type == 'sample':
                    self.test_data.update({
                        'encryptedPacket': '',
                        'time': '',
                        'status': r.is_test_passed,
                        'ttfp': str(stats.get('ttfp', 'nan')),
                        'tbp': str(stats.get('tbp_min', 'nan')),
                        'adv_address': ''})
                else:
                    self.test_data.update({
                        'raw_packet': '',
                        'time_from_start': '',
                        'packet_status': r.is_test_passed,
                        'ttfp': str(stats.get('ttfp', 'nan')),
                        'tbp_mean': str(stats.get('tbp_min', 'nan')),
                        'rssi': str(stats.get('rssi', 'nan')),
                        'tag_run_location': '',
                        'status_offline': 0,
                        'gw_packet': '',
                        'fail_bin': FailureCodes.NO_RESPONSE.value,
                        'fail_bin_str': FailureCodes.NO_RESPONSE.name,
                        'is_test_pass': r.is_test_passed,
                        'adv_address': ''})
                return

            if self.tester_type == 'sample':
                for p in tag_data:
                    self.test_data.update({
                        'encryptedPacket': p.get_packet(),
                        'time': p.gw_data['time_from_start'][0] if p.gw_data['time_from_start'].size > 1 else p.gw_data[
                            'time_from_start'].item(),
                        'status': r.is_test_passed,
                        'ttfp': str(stats.get('ttfp', 'nan')),
                        'tbp': str(stats.get('tbp_min', 'nan')),
                        'adv_address': p.packet_data['adv_address']})
                    dict_to_csv(dict_in=self.test_data, path=self.packets_data_path, append=True, only_titles=False)
            else:
                for p in tag_data:
                    for i in range(p.gw_data['gw_packet'].size):
                        if p.gw_data["gw_packet"].size > 1:
                            gw_packet = p.gw_data["gw_packet"][i]
                            rssi = p.gw_data["rssi"][i]
                            time_from_start = p.gw_data["time_from_start"][i]
                        else:
                            gw_packet = p.gw_data["gw_packet"].item()
                            rssi = p.gw_data["rssi"].item()
                            time_from_start = p.gw_data["time_from_start"].item()
                        self.test_data.update({
                            'raw_packet': p.get_packet(),
                            'status_offline': 1,
                            'time_from_start': time_from_start,
                            'packet_status': r.is_test_passed,
                            'ttfp': str(stats.get('ttfp', 'nan')),
                            'tbp_mean': str(stats.get('tbp_min', 'nan')),
                            'rssi': rssi,
                            'gw_packet': gw_packet,
                            'fail_bin': FailureCodes.PASS.value,
                            'fail_bin_str': FailureCodes.PASS.name,
                            'is_test_pass': r.is_test_passed,
                            'selected_tag': p.packet_data['adv_address'],
                            'adv_address': p.packet_data['adv_address']})
                        dict_to_csv(dict_in=self.test_data, path=self.packets_data_path, append=True, only_titles=False)

    def cloud_upload(self):
        """
        Uploads the collected test data to the cloud for further analysis and storage.

        Parameters: - env (str): Specifies the cloud environment to upload to. It can be either 'prod' for production
        or 'test' for testing.

        The function performs the following tasks:
        1. Calls the `upload_to_cloud_api` function to upload both run data and packets data CSV files.
        2. Logs the status of the upload operation.

        Returns:
        - True: If the data upload to the cloud is successful.
        - False: If the data upload fails for any reason.

        Note: The function uses the owner ID and API key that were set during the cloud connection phase.
        """
        tester_type = self.tester_type + '-test'
        success = upload_to_cloud_api(batch_name='',
                                                  tester_type=tester_type,
                                                  run_data_csv_name=self.run_data_path,
                                                  packets_data_csv_name=self.packets_data_path,
                                                  is_path=True,
                                                  env=self.env,
                                                  owner_id=self.owner_id,
                                                  logger_=self.logger.logger.name)

        return success

    def get_common_run_name(self):
        return self.common_run_name

    def get_out_put_dir(self):
        return self.output


if __name__ == "__main__":
    Test = SimpleTest()
