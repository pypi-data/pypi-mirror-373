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

import sys
import time
import logging
import pandas as pd
from dash import Dash, html, dcc, dash_table, ctx
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import threading
from werkzeug.serving import make_server

HOST = '127.0.0.1'
PORT = 8070
COLUMNS = ['location', 'wiliot_code', 'asset_code', 'timestamp', 'scan_status',
           'is_associated', 'associate_status_code', 'adv_address', 'n_packets', 'external_id', 'is_success']


class AssociationAndVerificationGUI(object):
    def __init__(self, logger_name='root', get_data_func=None, get_stat_func=None, common_run_name='', stop_event=None):
        self.logger = logging.getLogger(logger_name)
        self.stop_button_status = False
        self.is_running = True
        self.common_run_name = common_run_name
        self.stop_event = stop_event
        self.demo_index = 0
        self.get_data = get_data_func if get_data_func is not None else self.get_data_demo
        self.get_stat = get_stat_func if get_stat_func is not None else self.calc_stat_demo
        self.results = pd.DataFrame()
        self.dash_app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.dash_app.title = 'Wiliot Association & Verification Tester'

        self.all_cards = {'location_number': 'secondary',
                          'scan_success': 'primary',
                          'association_success': 'success',
                          'responding_rate': 'info'}

        self.generate_inlay()

        self.server = self.dash_app.server
        self.init_callbacks()

    def generate_inlay(self):
        def header(name):
            title = html.H2(name, style={"margin-top": 5})
            logo = html.Img(
                src='https://www.wiliot.com/src/uploads/Wiliotlogo.png', style={"float": "right", "height": 50}
            )
            return dbc.Row([dbc.Col(title, md=9), dbc.Col(logo, md=3)])

        def card_content(card_id):
            return [html.Div(id=card_id),
                    html.P(card_id.capitalize().replace('_', ' '), className="card-text")]

        # Card components
        cards = [dbc.Card(card_content(card_name), body=True, color=card_color, inverse=True)
                 for card_name, card_color in self.all_cards.items()]

        # table
        data_table = dash_table.DataTable(
            id='results_table',
            columns=[{'name': col, 'id': col} for col in COLUMNS],
            data=[],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'fontWeight': 'bold'},
        )

        # buttons
        stop_button = dbc.Button("Stop", id="stop-btn", className="mb-3", color="danger", n_clicks=0)
        pause_button = dbc.Button("Pause", id="pause-btn", className="mb-3", color="warning", n_clicks=0)

        self.dash_app.layout = dbc.Container(
            [
                html.Br(),
                header("Wiliot Association & Verification Tester"),
                html.Hr(),
                dbc.Row([dbc.Col(card) for card in cards]),
                html.Br(),
                html.Div([html.Div(id='app-title', children=f'{self.common_run_name}: 0 success out of 0',
                                   style={'fontSize': 20, 'fontWeight': 'bold'})]),
                html.Br(),
                html.Div([stop_button, pause_button, html.Div(id='app-state', children='Application is running')]),
                html.Br(),
                html.Div([html.H3("Results"), data_table, html.Div(id='results_table_container')]),
                dcc.Interval(
                    id='interval-component',
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=0),
                html.Footer('Copyright (c) 2024 Wiliot')
            ],
            fluid=False,
        )

    def init_callbacks(self):

        @self.server.route('/shutdown', methods=['POST'])
        def shutdown():
            self.logger.info('Wiliot A&V has been stopped')
            sys.exit(-1)

        @self.dash_app.callback(
            [Output(card_name, 'children') for card_name in self.all_cards.keys()] + [Output('results_table', 'data'),
                                                                                      Output('app-title', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_data(n_intervals):
            self.results = self.get_data()
            new_stat = self.get_stat()

            n_locations = html.H2(new_stat['n_locations'], className="card-title")
            scan_success = html.H2(new_stat['scan_success'], className="card-title")
            association_success = html.H2(new_stat['association_success'], className="card-title")
            responding_rate = html.H2(new_stat['responding_rate'], className="card-title")

            msg = f'{self.common_run_name}: {new_stat["n_success"]} success out of {new_stat["n_locations"]}'
            style = {}
            if self.stop_event is not None and self.stop_event.is_set():
                msg += ' \n Application Was Stopped'
                style = {"fontSize": "40px", "backgroundColor": "red", 'whiteSpace': 'pre-line'}

            return [n_locations, scan_success, association_success, responding_rate, self.results.to_dict("records"),
                    html.Div(msg,style=style)]

        @self.dash_app.callback(
            [Output('app-state', 'children'), Output('pause-btn', 'children'), Output('pause-btn', 'color')],
            [Input('stop-btn', 'n_clicks'), Input('pause-btn', 'n_clicks')]
        )
        def buttons(n_clicks1, n_click2):
            msg = 'Application is running'
            pause_str = 'Pause'
            pause_style = 'warning'
            style = {}

            if "stop-btn" == ctx.triggered_id:
                self.stop_button_status = True
                self.is_running = False
                msg = 'Application was stopped'
                style = {"fontSize": "40px", "backgroundColor": "red"}
            elif "pause-btn" == ctx.triggered_id:
                self.is_running = (not self.is_running)
                if not self.is_running:
                    msg = 'Application was paused'
                    pause_str = 'Run'
                    pause_style = 'success'

            return [html.Div(msg, style=style), pause_str, pause_style]

    def run_app(self):
        self.server = make_server(HOST, PORT, self.dash_app.server)
        logging.getLogger('werkzeug').setLevel(logging.ERROR)
        self.server.serve_forever()

    def is_stopped_by_user(self):
        return self.stop_button_status

    def is_app_running(self):
        return self.is_running

    @staticmethod
    def get_url():
        return f"http://{HOST}:{PORT}/"

    def calc_stat_demo(self):
        df_in = self.results
        stat_out = {}
        rel_data = df_in.loc[~df_in['location'].isna()]
        n_location = len(rel_data)
        stat_out['n_locations'] = str(n_location)
        stat_out['n_tags_outside_test'] = str(len(df_in) - n_location)
        if n_location:
            stat_out['scan_success'] = f'{round(rel_data["scan_status"].sum() / n_location * 100, 2)}%'
            stat_out['association_success'] = f'{round(rel_data["is_associated"].sum() / n_location * 100, 2)}%'
            stat_out['responding_rate'] = f'{round(rel_data["n_packets"].notna().sum() / n_location * 100, 2)}%'

        return stat_out

    def get_data_demo(self):
        self.demo_index += 1
        path = "C:/Users/shunit/Downloads/association_and_verification_log_20240414_165814_results_df.csv"
        df = pd.read_csv(path)
        return df.iloc[0:self.demo_index]


if __name__ == '__main__':
    import webbrowser

    t = AssociationAndVerificationGUI()
    plot_thread = threading.Thread(target=t.run_app, daemon=True, args=())
    plot_thread.start()
    webbrowser.open(t.get_url())
    while True:
        if not plot_thread.is_alive():
            break
        time.sleep(10)
