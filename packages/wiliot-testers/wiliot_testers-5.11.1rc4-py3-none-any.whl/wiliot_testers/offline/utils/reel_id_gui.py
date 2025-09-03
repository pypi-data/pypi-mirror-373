"""
  Copyright (c) 2016 - 2025, Wiliot Ltd. All rights reserved.

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
import argparse

from wiliot_api import ManufacturingClient
from wiliot_core import GetApiKey
from wiliot_core.utils.utils import set_logger

from datetime import datetime
from tkinter import simpledialog
import shutil
import requests
import csv
import time
import os

logger_path, logger = set_logger('reel_id_gui', 'reel_id_gui_files')
logger.info("Started logger")


def open_reel_id_request_gui(env='test', owner_id='wiliot-ops'):
    """
    API to receive reel number from cloud (should use it to avoid duplications).
    :return: the reel number (in 0x)
    """
    assert ('testerStationName' in os.environ), 'testerStationName is missing from PC environment variables'
    tester_station_name = os.environ['testerStationName']

    assert ('teams_url' in os.environ), 'teams_url is missing from PC environment variables'
    logger.info(f"Using env: {env}")
    logger.info(f"Using owner_id: {owner_id}")
    try:
        g = GetApiKey(gui_type='ttk', env=env, owner_id=owner_id)
        api_key = g.get_api_key()
        client = ManufacturingClient(api_key=api_key, logger_=logger.name, env=env)
        payload = {"printerId": tester_station_name}
    except Exception as e:
        raise Exception('Problem with authentication') from e

    try:
        operator = simpledialog.askstring("Input", "Enter operator name:")
        num_reels = simpledialog.askinteger("Input", "Enter number of reels:")
        if not operator or not num_reels:
            print("Cancelled or invalid input")
            return
        if num_reels > 100:
            raise Exception("Please request 100 reels or less and try again")

    except Exception as e:
        raise Exception(f'Problem with one or more parameters {e}')
    try:
        csv_filename = os.path.join(os.path.dirname(logger_path),
                                f"reel_ids_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        os.makedirs(os.path.dirname(csv_filename), exist_ok=True)  # checks if the csv folder exists, if not, creates it

        # Creation of "archive" folders
        csv_dir = os.path.join(os.path.dirname(logger_path))
        csv_archive_dir = os.path.join(csv_dir, 'csv_archive')
        log_archive_dir = os.path.join(csv_dir, 'log_archive')

        os.makedirs(csv_archive_dir, exist_ok=True)
        os.makedirs(log_archive_dir, exist_ok=True)


        send_teams_message(message =f"Request `{os.path.basename(csv_filename)}` with {num_reels} reels requested by {operator}.")  # Message we want to send in teams

        # Move existing CSVs to said archive
        for f in os.listdir(csv_dir):
            full_path = os.path.join(csv_dir, f)
            if f.endswith(".csv") and os.path.isfile(full_path):
                try:
                    shutil.move(full_path, os.path.join(csv_archive_dir, f))
                except PermissionError: pass

        with open(csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["reel_id", "First Ext. ID#", "Last Ext. ID#", "timestamp", "Requester"])
                # start process here with requester name and num of reels
                logger.info(f"Starting process, Reels requested: {num_reels}, Requester: {operator}")
                reel_ids_list = []
                for i in range(num_reels):
                    for attempt in range(1, 4):
                        try:
                            reel_id = client.get_reel_id(owner_id, payload, reel_id_3_char=True, gen_type='Gen3')
                            logger.info(f"Reel {i + 1}: {reel_id}")
                            reel_ids_list.append(reel_id)
                            writer.writerow([
                                reel_id['data'],
                                0,
                                9999,
                                datetime.now().strftime("%d/%m/%Y %H:%M"),
                                operator
                            ])
                            break
                        except Exception as e:
                            if  attempt < 3:
                                logger.info(f"Reel {i + 1}: got 409 conflict, retrying {attempt}/3...")
                                time.sleep(1)
                            else:
                                logger.error(f"Reel {i + 1}: failed with error: {e}")
                                raise
        message = f"Successfully pulled {i + 1} reels out of requested {num_reels}, first: {reel_ids_list[0]['data']}, last: {reel_ids_list[i]['data']}"

        logger.info("Done processing!")

        logger.info(f"Saved reel IDs to {csv_filename}")
        logger.info(message)

        send_teams_message(message)

        # move old logs to archive as well
        for f in os.listdir(csv_dir):
            full_path = os.path.join(csv_dir, f)
            if f.endswith(".log") and os.path.isfile(full_path):
                try:
                    shutil.move(full_path, os.path.join(log_archive_dir, f))
                except PermissionError: pass


        return reel_ids_list

    except Exception as e:
        raise Exception(f"An exception occurred at get_reel_name_from_cloud_API: {e}")


def send_teams_message(message):
    flow_url = os.environ["teams_url"]

    payload = {
        "text": message  # text is specifically defined in workflow so changing it would break it
    }

    response = requests.post(flow_url, json=payload)
    if response.ok:
        logger.info("Message sent to Teams.")
    else:
        logger.info(f"Failed to send message: {response.status_code} - {response.text}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="test", help="Environment to use")
    parser.add_argument("--owner_id", default="wiliot-ops", help="Owner ID")

    args = parser.parse_args()
    open_reel_id_request_gui(env=args.env, owner_id=args.owner_id)