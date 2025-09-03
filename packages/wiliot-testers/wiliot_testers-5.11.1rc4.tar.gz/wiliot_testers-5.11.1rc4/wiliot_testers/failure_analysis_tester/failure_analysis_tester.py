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

import datetime
import logging
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

from wiliot_core.utils.utils import open_directory
from wiliot_testers.failure_analysis_tester.configs_gui import load_config, FA_TEST_DIR, TESTER_NAME, TIME_NOW, RELAY_CONFIG, CONFIGS_DIR
from wiliot_testers.failure_analysis_tester.fa_utils import plot_value, generate_html_report
from wiliot_testers.wiliot_tester_log import WiliotTesterLog
from wiliot_test_equipment.visa_test_equipment.gpio_router import GPIORouter
from wiliot_test_equipment.visa_test_equipment.smu import SMU


class FailureAnalysisTester:
    def __init__(self, debug=False):
        self.set_logger()
        self.df = pd.DataFrame()
        self.all_df = pd.DataFrame()
        self.reference_df = None
        self.load_config()
        self.tag_aliases = []
        self.list_for_report = []
        self.is_app_running = True
        if debug:
            from wiliot_core.internal.utils import get_sharepoint_path
            self.df = pd.read_csv(get_sharepoint_path('Tags Team files') / 'misc' / 'fa_tester.csv')
            self.all_df = pd.read_csv(get_sharepoint_path('Tags Team files') / 'misc' / 'fa_tester_merged.csv')
            self.output_dir = FA_TEST_DIR / 'results' / 'test' / f"test_{TIME_NOW}"
            self.output_dir.mkdir(exist_ok=True, parents=True)
        else:
            self.gpio_router = GPIORouter(logger=self.logger)
            self.smu = SMU(visa_addr=self.config['visa_addr'], logger=self.logger)

    def set_logger(self):
        run_name = 'failure_analysis_' + TIME_NOW
        self.log_obj = WiliotTesterLog(run_name=run_name)
        self.log_obj.set_logger(tester_name=TESTER_NAME,
                                log_path=FA_TEST_DIR / 'logs')
        self.logger = self.log_obj.logger

    def load_config(self):
        self.config = load_config()

    def generate_csv_report(self):
        reshaped_rows = []
        for ch in RELAY_CONFIG.keys():
            if f'{ch}_voltage_V' in self.all_df.columns:
                temp_df = pd.DataFrame({
                    'CH1 Voltage (V)': self.all_df[f'{ch}_voltage_V'],
                    'CH1 Source (uA)': self.all_df[f'{ch}_current_uA'],
                    'ID': self.all_df['tag_alias'],
                    'Target': ch,
                    'result': self.all_df.get(f'{ch}_result', pd.Series([''] * len(self.all_df))),
                })
                reshaped_rows.append(temp_df)
        output_df = pd.concat(reshaped_rows, ignore_index=True)
        output_csv_path = self.output_dir / \
            f'SMU_report_{datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.csv'
        output_df.to_csv(output_csv_path, index=False)
        
    def end_test(self):
        self.generate_csv_report()
        self.html_output_path = self.output_dir / f'SMU_report_{datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.html'
        main_plot = []
        for ch in RELAY_CONFIG.keys():
            if f'{ch}_voltage_V' in self.all_df.columns:
                main_plot.append(plot_value(self.all_df, self.reference_df, ch))
        generate_html_report(self.list_for_report,
                             self.html_output_path,
                             main_plot=main_plot)
        open_directory(self.output_dir)
        open_directory(self.html_output_path)

    def load_reference_csv(self, tag_type:str = 'E4'):
        git_config_path = Path(__file__).parent / 'configs'
        csv_files = list(git_config_path.glob(f"*{tag_type}*.csv"))
        if len(csv_files) == 1:
            self.reference_df = pd.read_csv(csv_files[0])

    def fill_list_for_report(self) -> None:
        cols = [s.replace('_current_uA','') for s in list(self.df.columns) if 'current_uA' in s]
        for col in cols:
            percent_pass = self.df.get(col + '_percent_pass', None)
            result_dict = {'Test Name': col,
                           'Tag Id': self.df['tag_alias'][0],
                           'percent_pass': None,
                           'result': 'N/A',
                           'graph': plot_value(self.df, self.reference_df, col, self.df['tag_alias'][0])}
            if percent_pass is not None:
                percent_pass = percent_pass.iloc[0] if isinstance(percent_pass, pd.Series) else percent_pass
                result_dict['percent_pass'] = percent_pass
                if percent_pass >= 95:
                    result_dict['result'] = 'pass'
                else:
                    result_dict['result'] = 'fail'
            self.list_for_report.append(result_dict)

    def check_test(self, tag_type:str = 'E4') -> str:
        out_str = ''
        if self.reference_df is None:
            self.load_reference_csv(tag_type)

        if self.reference_df is not None:
            thresh = self.config['compare_threshold_percent'] / 100
            cols = [s.replace('_current_uA','') for s in list(self.df.columns) if 'current_uA' in s]
            for col in cols:
                res = 0
                err = False
                for i, (cur, vol) in enumerate(zip(self.df[col + '_current_uA'], self.df[col + '_voltage_V'])):
                    try:
                        nearest_index = self.reference_df[col + '_current_uA'].sub(cur).abs().idxmin()
                        single_res = vol < self.reference_df[col + '_min_voltage'].iloc[nearest_index] or vol > self.reference_df[col + '_max_voltage'].iloc[nearest_index]
                        res += single_res
                        self.df.loc[i, col + '_result'] = 'pass' if single_res else 'fail'
                    except KeyError:
                        out_str += f'{col} is missing\n'
                        err = True
                        break
                if not err:
                    res = 100 * (1 - res / len(self.df[col + '_current_uA']))
                    self.df[col + '_percent_pass'] = res

                    if res >= 95:
                        out_str += f'{col} pass rate: {res:.2f}%  ✅\n'
                    else:
                        out_str += f'{col} pass rate: {res:.2f}%  ❌\n'
                        
                    
            return out_str
        else:
            return 'Reference file issue'

    def run_test(self, test_type: str, folder_name: str, tag_alias: str, comment: str, keys=None):
        # add suffix to tag_alias for retests
        if tag_alias in self.tag_aliases:
            idx = 1
            while tag_alias + '_' + str(idx) in self.tag_aliases:
                idx += 1
            tag_alias = tag_alias + '_' + str(idx)

        self.tag_aliases.append(tag_alias)
        self.logger.info(
            f'running {test_type}, {folder_name}, {tag_alias}')
        self.df = pd.DataFrame()
        self.output_dir = FA_TEST_DIR / 'results' / \
            folder_name / f"{folder_name}_{TIME_NOW}"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        csv_path = self.output_dir / \
            f'{test_type}_{tag_alias}_{datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")}.csv'
        if test_type == 'IV Curve':
            self.run_iv_curve_test(keys=keys)
        else:
            raise NotImplementedError
        self.df['tag_alias'] = tag_alias
        self.df['comment'] = comment
        self.df.to_csv(csv_path)
        self.all_df = pd.concat([self.all_df, self.df], ignore_index=True)
        self.all_df.to_csv(self.output_dir / 'merged.csv')

    def run_iv_curve_test(self, keys=None):
        if not keys:
            keys = RELAY_CONFIG.keys()
        for key in keys:
            self.test_field(key)

    def test_field(self, field):
        self.gpio_router.set_gpio_state(RELAY_CONFIG[field])
        kwargs = self.config[field]
        time_list_float, current_A_list_float, voltage_V_list_float = self.smu.run_and_read_current_sweep(
            **kwargs)
        current_uA_list_float = [x * 1e6 for x in current_A_list_float]
        # self.df[field + '_time'] = time_list_float
        df = pd.DataFrame()
        df[field + '_current_uA'] = current_uA_list_float
        df[field + '_voltage_V'] = voltage_V_list_float
        self.df = pd.concat([self.df, df], axis=1)


if __name__ == '__main__':
    FAT = FailureAnalysisTester()
    FAT.output_dir = FA_TEST_DIR / 'results' / 'test' / f"test_{TIME_NOW}"
    FAT.output_dir.mkdir(exist_ok=True, parents=True)
    FAT.check_test('E2')
    FAT.fill_list_for_report()
    FAT.end_test()
    # FAT.run_test('IV Curve', 'smu_fix', 'aaa', '')
