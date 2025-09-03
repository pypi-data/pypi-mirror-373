from dash import html, dcc
import dash_bootstrap_components as dbc

from wiliot_testers.failure_analysis_tester.configs_gui import RELAY_CONFIG

ELEMENT_WIDTH = "300px"
HALF_ELEMENT_WIDTH = "150px"
BUTTON_WIDTH = 30
CELL_STYLE = {"width": ELEMENT_WIDTH, "display": "flex", "justifyContent": "center",
              "alignItems": "center", "flexDirection": "column", "gap": "10px"}
BUTTON_STYLE = {"width": "200px", "height": "20px", "fontSize": "14px",
                "display": "flex", "alignItems": "center", "justifyContent": "center"}
TEST_OPTIONS = [
    {'label': 'IV Curve', 'value': 'IV Curve'},
    # {'label': 'Voltage Drop', 'value': 'Voltage Drop'},
    # {'label': 'External Power Source', 'value': 'External Power Source'}
]
TAG_OPTIONS = [
    {'label': 'E4', 'value': 'E4'},
    {'label': 'E2', 'value': 'E2'}] 


def get_tag_alias(disabled=False):
    return html.Div(
        [html.Label("Tag Alias"),
         dbc.Input(id="tag_alias", type="text", disabled=disabled)],
        style={"width": ELEMENT_WIDTH})


def get_folder_name(disabled=False):
    return html.Div(
        [html.Label("Folder Run Name"),
         dbc.Input(id="folder_name", type="text", disabled=disabled)],
        style={"width": ELEMENT_WIDTH})


def get_comment(disabled=False):
    return html.Div(
        [html.Label("Comment (optional)"),
         dbc.Input(id="test_comment", type="text", disabled=disabled)],
        style={"width": ELEMENT_WIDTH})


def get_test_and_tag_type(disabled=False):
    return html.Div([
        html.Div([
        html.Label("Test Type"),
        dcc.Dropdown(
            disabled=disabled,
            id='test_type',
            options=TEST_OPTIONS,
            value='IV Curve'),],
        style={"width": HALF_ELEMENT_WIDTH}), 
        html.Div([
        html.Label("Tag Type"),
        dcc.Dropdown(
            disabled=disabled,
            id='tag_type',
            options=TAG_OPTIONS,
            value='E4'),],
        style={"width": HALF_ELEMENT_WIDTH})
        ], style={'display': 'flex', 'flexDirection': 'row', 'gap': '10px'})


def get_run_finish_buttons(disabled=False):
    return html.Div([
        dbc.Button("Run Test", id="run_test", color="success",
                   n_clicks=0, style={"width": "200px"}, disabled=disabled),
        dbc.Button("Finish Test", id="finish_test",
                   color="danger", n_clicks=0, style={"width": "200px"}, disabled=disabled),
    ], style=CELL_STYLE)


def get_test_checkbox():
    return html.Div([
        dcc.Checklist(list(RELAY_CONFIG.keys()), list(
                    RELAY_CONFIG.keys()), id="test_fields",),
    ], style={"width": ELEMENT_WIDTH, "gap": "10px", "display": "flex", "alignItems": "center"})


def get_test_result(disabled=False):
    return html.Div([
        html.Label("Results"),
        dbc.Textarea(id="test_result", rows=4, disabled=True)
    ], style={"width": ELEMENT_WIDTH})


def get_smu_config(default_value=''):
    return html.Div([
        dbc.Input(id="smu_address", type="text", value=default_value),
        dbc.Button("Set SMU address", id="smu_address_button",
                   color="info", n_clicks=0, style=BUTTON_STYLE),
        dbc.Button("Open Output Folder", id="open_output_folder",
            color="info", className="mb-2", style=BUTTON_STYLE, disabled=True),

    ], style={"width": ELEMENT_WIDTH, "display": "flex", "justifyContent": "center",
              "alignItems": "center", "flexDirection": "column", "gap": "10px"})



def get_plot_selection(disabled=False):
    return html.Div([
        html.Label("Plot Selection"),
        dcc.Dropdown(
            id='plot-selection',
            options=['Empty'] + list(RELAY_CONFIG.keys()),
            value='Empty',
            disabled=disabled),
    ], style={"width": ELEMENT_WIDTH})

