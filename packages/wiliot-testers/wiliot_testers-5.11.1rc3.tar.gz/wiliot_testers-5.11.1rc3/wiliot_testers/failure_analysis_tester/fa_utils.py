from jinja2 import Template
import numpy as np
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
from typing import Union


def plot_value(df: pd.DataFrame, reference_df: Union[pd.DataFrame, None], value: str, tag_alias: str = '') -> go.Figure:
    def denan(arr):
        """Remove NaN values from an array."""
        return arr[~np.isnan(arr)]
    fig = go.Figure()
    for tag in df['tag_alias'].unique():
        p_df = df[df['tag_alias'] == tag]
        fig.add_trace(go.Scatter(
            x=p_df[value + '_current_uA'].values, 
            y=p_df[value + '_voltage_V'].values, 
            mode='markers', 
            name=str(tag),
            marker=dict(size=6)
        ))

    if reference_df is not None and value + '_current_uA' in reference_df.columns:
        x_ref = denan(reference_df[value + '_current_uA'].values)
        lower_limit = denan(reference_df[value + '_min_voltage'].values)
        upper_limit = denan(reference_df[value + '_max_voltage'].values)
        
        # Add red dashed lines for control limits
        fig.add_trace(go.Scatter(
            x=x_ref, 
            y=lower_limit, 
            mode='lines+markers',
            name="Min Control Limit",
            line=dict(color='red', dash='dash', width=2),
            marker=dict(color='red', size=4)
        ))
        fig.add_trace(go.Scatter(
            x=x_ref, 
            y=upper_limit, 
            mode='lines+markers',
            name="Max Control Limit",
            line=dict(color='red', dash='dash', width=2),
            marker=dict(color='red', size=4)
        ))
        
        # Add shaded area between control limits
        fig.add_trace(go.Scatter(
            x=x_ref,
            y=upper_limit,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=x_ref,
            y=lower_limit,
            mode='lines',
            line=dict(width=0),
            fill='tonexty',
            fillcolor='rgba(255, 0, 0, 0.2)',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    chart_title = f"{tag_alias}_{value}" if tag_alias else f"Test_{value}"
    
    fig.update_layout(
        title=chart_title,
        showlegend=True,
        xaxis_title="Current [uA]", 
        yaxis_title="Voltage [V]",
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='black',
            borderwidth=1
        )
    )

    return fig


def generate_html_report(list_for_report, output_path, main_plot):
    """
    Generate an HTML report from a list of test result dictionaries.

    Each dictionary should include:
    - 'Test Name': str
    - 'Tag Id': str
    - 'percent_pass': int or float
    - 'result': str
    - 'graph': plotly.graph_objects.Figure
    """
    # Convert plotly figures to HTML snippets
    for item in list_for_report:
        item['graph_html'] = pio.to_html(item['graph'], include_plotlyjs=True, full_html=False)

    main_plot_html = []
    for p in main_plot:
        main_plot_html.append(pio.to_html(p, include_plotlyjs=True, full_html=False))

    # Jinja2 HTML template
    template = Template("""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Test Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>Test Report</h1>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Test Name</th>
                <th>Tag Id</th>
                <th>Percent Pass</th>
                <th>Result</th>
            </tr>
            {% for row in results %}
            <tr>
                <td>{{ row['Test Name'] }}</td>
                <td>{{ row['Tag Id'] }}</td>
                <td>
                {% if row['percent_pass'] is not none %}
                    {{ row['percent_pass'] | round(1) }}
                {% else %}
                    N/A
                {% endif %}
                </td>
                <td>{{ row['result'] }}</td>
            </tr>
            <tr>
                <td colspan="4">{{ row['graph_html'] | safe }}</td>
            </tr>
            {% endfor %}
        </table>
        <h1>All Results</h1>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            {% for p in main_plot_html %}
            <tr>
                <td colspan="4">{{ p | safe }}</td>
            </tr>
            {% endfor %}
                        
        </table>
    </body>
    </html>
    """)

    # Render and save
    html_output = template.render(results=list_for_report, main_plot_html=main_plot_html)
    with open(output_path, 'w') as f:
        f.write(html_output)

