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
import os
from wiliot_api import ManufacturingClient, TesterType
from wiliot_core import GetApiKey


def upload_to_cloud_api(batch_name, tester_type, run_data_csv_name=None, packets_data_csv_name=None,
                        env='', is_batch_name_inside_logs_folder=True, logger_=None, is_path=False,
                        client=None, owner_id='wiliot-ops'):
    """
    uploads a tester log to Wiliot cloud
    :type batch_name: string
    :param batch_name: folder name of the relevant log
    :type run_data_csv_name: string
    :param run_data_csv_name: name of desired run_data log to upload,
                              should contain 'run_data' and end with .csv
    :type packets_data_csv_name: string
    :param packets_data_csv_name: name of desired packets_data log to upload,
                               should contain 'packets_data' and end with .csv
    :type tester_type: string or TesterType
    :param tester_type: name of the tester the run was made on (offline, tal15k, conversion, yield)
    :type env: string (prod, dev, test)
    :param env: to what cloud environment should we upload the files
    :type is_batch_name_inside_logs_folder: bool
    :param is_batch_name_inside_logs_folder: flag to indicate if the batch_name is the regular run folder (logs) or
                                             this function is being used in a way we will need the full path
    :return: True for successful upload, False otherwise
    """
    # Logger setup
    if logger_ is None:
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(logger_)

    # Check tester type
    if not isinstance(tester_type, TesterType):
        is_tester_type_valid = len([t for t in TesterType if t.value == tester_type])
        if is_tester_type_valid:
            tester_type = TesterType(tester_type)
        else:
            logger.warning('Unsupported tester_type inserted to upload_to_cloud_api()\nPlease change it and retry')
            return False

    # Check file names
    if run_data_csv_name and 'run_data' not in run_data_csv_name:
        logger.warning('Unsupported run_data_csv_name inserted to upload_to_cloud_api()\nPlease change it and retry')
        return False
    if packets_data_csv_name and 'packets_data' not in packets_data_csv_name:
        logger.warning('Unsupported packets_data_csv_name inserted to upload_to_cloud_api()\nPlease change it and retry')
        return False

    # Environment validation
    if env == 'production' or env == '':
        env = 'prod'
    env = env.strip('/')
    if env not in {'prod', 'test', 'dev'}:
        logger.warning(f'Unsupported env value was inserted (env = {env})')
        return False

    # Check user credentials and client setup
    g = GetApiKey(gui_type='ttk', env=env, owner_id=owner_id)
    api_key = g.get_api_key()
    if not api_key:
        logger.warning('could not extract user credentials. please check warnings')
        return False
    client = ManufacturingClient(api_key=api_key, env=env, logger_=logger.name) if client is None else client

    # Upload process
    run_upload_status = False
    packet_upload_status = False

    try:
        if run_data_csv_name is not None:
            run_data_file_path = os.path.join("logs" if is_batch_name_inside_logs_folder
                                              else "", batch_name, run_data_csv_name) if not is_path \
                                              else run_data_csv_name
            run_upload_status = client.upload_testers_data(tester_type=tester_type,
                                                           file_path=run_data_file_path)
    except Exception as e:
        logger.warning(f'A problem occurred in upload_to_cloud_api: {e}')

    try:
        if packets_data_csv_name is not None:
            packets_data_file_path = os.path.join("logs" if is_batch_name_inside_logs_folder
                                                  else "", batch_name, packets_data_csv_name) if not is_path \
                                                  else packets_data_csv_name
            packet_upload_status = client.upload_testers_data(tester_type=tester_type,
                                                              file_path=packets_data_file_path)
    except Exception as e:
        logger.warning(f'A problem occurred in upload_to_cloud_api: {e}')

    merged_status = run_upload_status and packet_upload_status
    if merged_status:
        logger.info('\n-----------------------------------------------------------------------\n'
                    'upload to cloud is finished successfully\n'
                    '-----------------------------------------------------------------------')
    return merged_status
