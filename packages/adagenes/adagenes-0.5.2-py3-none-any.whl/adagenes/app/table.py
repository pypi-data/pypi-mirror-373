from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import datetime


def generate_column_defs(df):
    """
    Generates the column definition for the AG Grid table

    :param df:
    :return:
    """
    #columnDefs = [
    #    {'field': '#CHROM'},
    #    {'field': 'POS'},
    #    {'field': 'REF'},
    #]
    column_defs = []
    for col in df.columns:
        if col == "POS":
            column_defs.append({'field': col,'filter': 'agNumberColumnFilter'})
        else:
            column_defs.append({'field': col})

    return column_defs


def display_table(df, label, genome_version, output_format):
    return html.Div([
        html.H5(label + ", Reference genome: " + genome_version + ", Output format: "+ output_format),

        dash_table.DataTable(
            df.to_dict('records'),
            [{'name': i, 'id': i} for i in df.columns],
            export_format="csv"
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        #html.Div('Raw Content'),
        #html.Pre(contents[0:200] + '...', style={
        #    'whiteSpace': 'pre-wrap',
        #    'wordBreak': 'break-all'
        #})
    ], style={'marginLeft': '40px', 'marginRight': '50px', 'marginBottom': 50, 'marginTop': 25})
