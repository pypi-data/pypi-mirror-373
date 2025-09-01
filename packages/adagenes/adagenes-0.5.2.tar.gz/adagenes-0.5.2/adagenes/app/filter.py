import dash_bootstrap_components
from dash import html, dcc


def load_filter_table():
    """

    :param df:
    :return:
    """
    elements = []

    # Liftover
    liftover = dcc.Dropdown(
        ["hg38/GRCh38", "hg19/GRCh37", "T2T/CHM13"], "hg38/GRCh38", id="select_reference_genome", style={"font-size":"14px"}
    )

    elements.append(liftover)

    # Output format
    output_format = dcc.Dropdown(["AVF","VCF", "MAF", "CSV (Genome)", "CSV (Protein)"], "AVF",
                                 id="select_output_format", style= {"font-size":"14px"})
    elements.append(output_format)

    filter_table = html.Div([
        dash_bootstrap_components.Row([
            dash_bootstrap_components.Col(
                    html.Div(
                        "Reference genome", id="select-reference-genome", style= {"font-size":"14px"}
                    )
                ),
            dash_bootstrap_components.Col(
                    [liftover]
                )
        ],style={"margin-bottom":"10px"}),
        dash_bootstrap_components.Row([
            dash_bootstrap_components.Col([
                html.Div("Output format", style= {"font-size":"14px"})
                ]),
            dash_bootstrap_components.Col(
                [output_format]
            )
        ])
    ])
    return filter_table