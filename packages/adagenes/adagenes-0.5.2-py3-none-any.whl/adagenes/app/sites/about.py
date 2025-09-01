from dash import Dash, dcc, html, dash_table, Input, Output, State, callback


def get_about_page():
    return html.Div([
            html.H2('About Page'),
            html.P('This is the About page content.')
        ])
