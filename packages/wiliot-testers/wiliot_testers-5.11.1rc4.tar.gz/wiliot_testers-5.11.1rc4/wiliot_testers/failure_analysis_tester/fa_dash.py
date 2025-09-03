from dash import Dash, html, dcc, Input, Output, State, clientside_callback, callback_context
import dash_bootstrap_components as dbc
import os
import pandas as pd
import plotly.graph_objects as go
import traceback

from wiliot_core.utils.utils import open_directory
from wiliot_testers.failure_analysis_tester.fa_dash_components import *
from wiliot_testers.failure_analysis_tester.fa_utils import *
from wiliot_testers.failure_analysis_tester.configs_gui import CONFIG_FILE, CONFIGS_DIR, save_config, load_config
from wiliot_testers.failure_analysis_tester.failure_analysis_tester import FailureAnalysisTester

ELEMENT_WIDTH = "300px"
BUTTON_WIDTH = 30
TEST_OPTIONS = [
    {'label': 'IV Curve', 'value': 'IV Curve'},
    {'label': 'Voltage Drop', 'value': 'Voltage Drop'},
    {'label': 'External Power Source', 'value': 'External Power Source'}
]

MAIN_TITLE = html.H3(["Failure Analysis Tester"], className="bg-info p-3 text-center")
DISABLED = False
KILL_APP = False
config = load_config()

try:
    FAT = FailureAnalysisTester()
except ConnectionError as e:
    MAIN_TITLE = html.H3(["Arduino is not connected/has an error.\nPlease close all windows, fix issue and run again"], className="bg-danger p-3 text-center")
    DISABLED = True
    KILL_APP = True
except ValueError as e:
    MAIN_TITLE = html.H3(["SMU is not connected/has an error.\nPlease make sure SMU address is correct"], className="bg-danger p-3 text-center")
    DISABLED = True
except Exception as e:
    MAIN_TITLE = html.H3([f"Unknown error occurred. Please contact Wiliot.\n Error traceback {traceback.format_exc()}\n Error message {str(e)}"], className="bg-danger p-3 text-center")
    DISABLED = True
    KILL_APP = True

app = Dash(__name__, external_stylesheets=[
           dbc.themes.MINTY, dbc.icons.FONT_AWESOME])

color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="color-mode-switch"),
        dbc.Switch(id="color-mode-switch", value=False,
                   className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="color-mode-switch"),
    ]
)

clientside_callback(
    """
    (switchOn) => {
       document.documentElement.setAttribute('data-bs-theme', switchOn ? 'light' : 'dark');
       return window.dash_clientside.no_update
    }
    """,
    Output("color-mode-switch", "id"),
    Input("color-mode-switch", "value"),
)

app.layout = dbc.Container(
    [
        dcc.ConfirmDialog(
            id="confirm", message="Are you sure you want to end the test?"),
        color_mode_switch,
        html.Div(id='title-container', children=[MAIN_TITLE]),
        html.Br(),
        dbc.Modal(
            [
                dbc.ModalBody("Folder Run Name and Tag Alias are required to run the test"),
                dbc.ModalFooter(dbc.Button("Close", id="close_modal", className="ms-auto"))
            ],
            id="modal",
            is_open=False,  # start closed
            backdrop=True,  # click outside to close
            keyboard=True,  # ESC to close
            centered=True,
        ),
        html.Div([
            get_tag_alias(disabled=DISABLED),
            get_folder_name(disabled=DISABLED),
            get_comment(disabled=DISABLED),
            get_test_and_tag_type(disabled=DISABLED),
            get_run_finish_buttons(disabled=DISABLED),
            get_test_checkbox(),
            get_test_result(disabled=DISABLED),
            get_smu_config(default_value=config['visa_addr']),
        ], style={'display': 'grid', 'gridTemplateColumns': 'repeat(4, 1fr)', 'gap': '10px', }),
        html.Br(),
        dcc.Loading(id="loading-output", type="default",
                    children=[html.Div(id="output")]),
        html.Br(),
        get_plot_selection(disabled=DISABLED),
        html.Br(),
        dcc.Graph(id='graph-content', style={"display": "none"}),
        dcc.Store(id="kill_trigger"),  # hidden target

    ],
)


@app.callback(
    Output('graph-content', 'figure'),
    Output('graph-content', 'style'),
    Input('plot-selection', 'value'),
    prevent_initial_call=True
)
def update_graph(value):
    if FAT.is_app_running:
        df = FAT.df
        tag_alias = df['tag_alias'].unique()[0]
    else:
        tag_alias = ''
        df = FAT.all_df

    if value == 'Empty' or (value + '_current_uA' not in df.columns or value + '_voltage_V' not in df.columns):
        return go.Figure(), {"display": "none"}
    
    fig = plot_value(df, FAT.reference_df, value, tag_alias)

    return fig, {"display": "block", "height":"700px"}


@app.callback(
    Output("smu_address_button", "n_clicks"),
    Input("smu_address_button", "n_clicks"),
    State("smu_address", "value"),
    prevent_initial_call=True
)
def set_smu_address(n_clicks, smu_address):
    if n_clicks:
        config['visa_addr'] = smu_address
        save_config(config)
        if DISABLED:
            os._exit(0)
    return 0


@app.callback(
    Output("kill_trigger", "data"),
    Input("finish_test", "disabled"),
    prevent_initial_call=True
)
def kill_app(disabled):
    if disabled and not FAT.is_app_running:
        os._exit(0)
    return disabled
    

@app.callback(
    Output("confirm", "displayed", allow_duplicate=True),
    Output("run_test", "disabled", allow_duplicate=True),
    Output("test_comment", "disabled", allow_duplicate=True),
    Output("test_type", "disabled", allow_duplicate=True),
    Output("tag_alias", "disabled", allow_duplicate=True),
    Output("finish_test", "disabled", allow_duplicate=True),
    Output("tag_type", "disabled", allow_duplicate=True),
    Output("folder_name", "disabled", allow_duplicate=True),
    Output('title-container', 'children'),
    Input("confirm", "submit_n_clicks"),
    State("folder_name", "disabled"),
    State("tag_type", "disabled"),
    prevent_initial_call=True
)
def close_app(n_clicks, folder_name_disabled, tag_type_disabled):
    title = [MAIN_TITLE]
    if n_clicks:
        FAT.is_app_running = False
        FAT.end_test()
        title = [html.H3(["Failure Analysis Tester run is done, to run again please close all windows"], className="bg-danger p-3 text-center")]
        return False, True, True, True, True, True, True, True, title
    return False, False, False, False, False, False, tag_type_disabled, folder_name_disabled, title


@app.callback(
    Output("confirm", "displayed"),
    Input("finish_test", "n_clicks"),
    prevent_initial_call=True
)
def show_confirm(n_clicks):
    return True  # Triggers the pop-up


@app.callback(
    Output("test_result", "style"),
    Input("test_result", "value"),
    prevent_initial_call=True
)
def update_input_style(value):
    color_map = {
        "Fail": "#ffcccc",
        "Pass": "#28a745"
    }
    return {"backgroundColor": color_map.get(value, "")}


@app.callback(
    Output("run_test", "disabled", allow_duplicate=True),
    Output("test_comment", "disabled", allow_duplicate=True),
    Output("test_type", "disabled", allow_duplicate=True),
    Output("tag_type", "disabled", allow_duplicate=True),
    Output("tag_alias", "disabled", allow_duplicate=True),
    Output("finish_test", "disabled", allow_duplicate=True),
    Output("open_output_folder", "disabled"),
    Output("test_result", "value"),
    Output("loading-output", "children"),
    Output("folder_name", "disabled", allow_duplicate=True),
    Output("modal", "is_open", allow_duplicate=True),
    Input("run_test", "disabled"),
    State("test_type", "value"),
    State("tag_type", "value"),
    State("tag_type", "disabled"),
    State("folder_name", "value"),
    State("tag_alias", "value"),
    State("test_comment", "value"),
    State("test_fields", "value"),
    State("open_output_folder", "disabled"),
    prevent_initial_call=True
)
def run_test(disabled, test_type, tag_type, tag_type_disabled, folder_name, tag_alias, comment, test_fields, open_output_folder_disabled):
    test_result = ''
    if not tag_alias or not folder_name:
        return False, False, False, tag_type_disabled, False, False, open_output_folder_disabled, test_result, None, folder_name is not None, True
    if disabled and FAT.is_app_running:
        FAT.run_test(test_type=test_type, folder_name=folder_name.strip(),
                     tag_alias=tag_alias, comment=comment, keys=test_fields)
        test_result = FAT.check_test(tag_type)
        FAT.fill_list_for_report()
        return False, False, False, tag_type_disabled, False, False, False, test_result, None, True, False
    else:
        return True, True, True, True, True, True, False, '', None, True, False


@app.callback(
    Output("folder_name", "disabled", allow_duplicate=True),
    Output("test_comment", "disabled"),
    Output("test_type", "disabled"),
    Output("tag_type", "disabled"),
    Output("tag_alias", "disabled"),
    Output("run_test", "disabled"),
    Output("finish_test", "disabled"),
    Output('plot-selection', 'value'),
    Output('test_result', 'value', allow_duplicate=True),
    Input("run_test", "n_clicks"),
    prevent_initial_call=True
)
def run_test_button(n_clicks):
    return True, True, True, True, True, True, True, 'Empty', ''

@app.callback(
    Output("modal", "is_open", allow_duplicate=True),
    Input("close_modal", "n_clicks"),
    prevent_initial_call=True
)
def toggle_modal(n_clicks):
    return False

@app.callback(
    Output("open_output_folder", "n_clicks"),
    Input("open_output_folder", "n_clicks"),
    prevent_initial_call=True
)
def open_output_folder(n_clicks):
    if n_clicks:
        if FAT.output_dir:
            open_directory(FAT.output_dir)
    return 0


if __name__ == "__main__":
    import webbrowser
    import threading
    import time

    def exit_func():
        time.sleep(5)
        os._exit(0)

    webbrowser.open("http://127.0.0.1:8050/")
    if KILL_APP:
        exit_thread = threading.Thread(target=exit_func, args=())
        exit_thread.start()
    app.run_server()
