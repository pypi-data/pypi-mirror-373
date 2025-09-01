import plotly.graph_objects as go
from plotly.subplots import make_subplots
from adagenes.plot.generate_data.generate_protein_pathogenicity_heatmap_data import getMolWeightValue,getChargeValue,getPolarityValue,getAromaticityValue,getFlexibilityValue,getPhosphorylationValue


def generate_aa_features_heatmap_dataframe_refalt(data):
    z1 = []
    z2 = []
    z3 = []
    z4 = []
    z5 = []
    z6 = []

    for var in data.keys():
        if "UTA_Adapter_gene" in data[var].keys():

            z1.append(list(getMolWeightValue(data, var, refalt=True)))
            z2.append(list(getChargeValue(data, var, refalt=True)))
            z3.append(list(getPolarityValue(data,var, refalt=True)))
            z4.append(list(getAromaticityValue(data, var, refalt=True)))
            z5.append(list(getFlexibilityValue(data, var, refalt=True)))
            z6.append(list(getPhosphorylationValue(data, var, refalt=True)))

    # z1 = [[1, 2, 3]]
    # z2 = [[3, 1, 2]]
    # z3 = [[1, 1, 2]]
    # z4 = [[1, 1, 2]]
    # z5 = [[3, 1, 2]]
    # z6 = [[1, 1, 2]]
    #z6 = [[1,1,1]]
    print("z1 ", z1)
    print("z2 ", z2)
    print("z3 ", z3)
    print("z4 ", z4)
    print("z5 ", z5)
    print("z6 ", z6)

    return z1, z2, z3, z4, z5, z6

def generate_aa_features_heatmap_dataframe(data):
    z1 = [[]]
    z2 = [[]]
    z3 = [[]]
    z4 = [[]]
    z5 = [[]]
    z6 = [[]]

    for var in data.keys():
        if "UTA_Adapter_gene" in data[var].keys():

            z1[0].append(getMolWeightValue(data, var))
            z2[0].append(getChargeValue(data, var))
            z3[0].append(getPolarityValue(data,var))
            z4[0].append(getAromaticityValue(data, var))
            z5[0].append(getFlexibilityValue(data, var))
            z6[0].append(getPhosphorylationValue(data, var))

    # z1 = [[1, 2, 3]]
    # z2 = [[3, 1, 2]]
    # z3 = [[1, 1, 2]]
    # z4 = [[1, 1, 2]]
    # z5 = [[3, 1, 2]]
    # z6 = [[1, 1, 2]]
    #z6 = [[1,1,1]]
    print("z1 ", z1)
    print("z2 ", z2)
    print("z3 ", z3)
    print("z4 ", z4)
    print("z5 ", z5)
    print("z6 ", z6)

    return z1, z2, z3, z4, z5, z6


def generate_aa_features_heatmap(data, patho_img=None, zdata = None,
                                 width=1800, height=500,
                                 variant_labels=None, generate_pathogenicity_heatmap=False,
                                 showlegend=True):

    if zdata is None:
        z1, z2, z3, z4, z5, z6 = generate_aa_features_heatmap_dataframe(data)
    else:
        z1 = zdata[0]
        z2 = zdata[1]
        z3 = zdata[2]
        z4 = zdata[3]
        z5 = zdata[4]
        z6 = zdata[5]

    # Custom discrete colorscales
    #colorscale = [[0, 'red'], [0.5, 'white'], [1, 'blue']]
    #colorscale1 = [[0, 'blue'], [0.5, 'yellow'], [1, 'green']]
    #colorscale2 = [[0, 'red'], [0.5, 'white'], [1, 'black']]
    #colorscale = [[0, '#a9152a'], [0.5, 'white'], [1, '#2e77b5']]
    colorscale = [[0, '#b6212f'], [0.5, 'white'], [1, '#3592e2']]
    num_vars = len(variant_labels)
    #tickvals = [i +(i*5) for i in range(len(variant_labels))]
    tickvals = [i for i in range(len(variant_labels))]

    num_rows = 6
    row_iter = 1
    #if patho_img is not None:
    #    num_rows = 7
    column_widths = [0.01]

    main_plot_width = 0.7  # 70% of total width for heatmaps
    colorbar_area = 0.25  # 25% for colorbars
    label_area = 0.05  # 5% for row labels

    # Create a subplot figure with 2 rows and 1 column
    fig = make_subplots(
        rows=num_rows,
        cols=1,
        vertical_spacing=0.05,
        row_heights=[1] * num_rows,
        column_widths=[main_plot_width],
        specs=[[{"secondary_y": False}] for _ in range(num_rows)]
    )

    # Colorbar grid layout parameters
    colorbar_grid = {
        'x_start': main_plot_width + label_area + 0.42,  # Start position from right edge
        'y_top': 0.85,  # Top row position
        'y_bottom': 0.35,  # Bottom row position
        'x_spacing': 0.90,#0.3,  # Horizontal spacing between colorbars
        'y_spacing': 0.4,  # Vertical spacing between rows
        'colorbar_width': 0.1
    }

    features = [
        ("Mol. weight", "Δ Molecular weight", z1, ["Smaller weight", "", "Unchanged", "", "Higher weight"]),
        ("Charge", "Δ Charge", z2, ["Negative", "", "Unchanged", "", "Positive"]),
        ("Polarity", "Δ Polarity", z3, ["Non-polar", "", "Unchanged", "", "Polar"]),
        ("Aromaticity", "Δ Aromaticity", z4, ["Non-aromatic", "", "Unchanged", "", "Aromatic"]),
        ("Flexibility", "Δ Flexibility", z5, ["Flexibile", "", "Unchanged", "", "Unflexible"]),
        ("Phosphorylation", "Δ Phosphorylation", z6, ["No phosphorylation", "", "Unchanged", "", "Phosphorylation"])
    ]

    for idx, (ylabel, cbar_title, z, ticktext) in enumerate(features):
        # Calculate colorbar position
        if idx < 3:  # Top row
            x_pos = colorbar_grid['x_start'] + (idx * colorbar_grid['x_spacing'])
            y_pos = colorbar_grid['y_top']
        else:  # Bottom row
            x_pos = colorbar_grid['x_start'] + ((idx - 3) * colorbar_grid['x_spacing'])
            y_pos = colorbar_grid['y_bottom']

        print("xpos ",x_pos)
        heatmap = go.Heatmap(
            z=z,
            colorscale=colorscale,
            colorbar=dict(
                title=cbar_title,
                tickvals=[1, 2, 3, 4, 5],
                ticktext=ticktext,
                len=0.25,
                thickness=15,
                xanchor='left',
                yanchor='middle',
                x=x_pos,
                y=y_pos
            ),
            zmin=1,
            zmax=5,
            showscale=showlegend,
            xgap=0.5,
            ygap=0.5
        )

        fig.add_trace(heatmap, row=idx + 1, col=1)

        # Add rotated row labels
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.01,
            y=1 - (idx + 0.5) / len(features),
            text=ylabel,
            showarrow=False,
            textangle=-90,
            font=dict(size=12),
            xanchor="right",
            yanchor="middle"
        )

    # Update layout
    fig.update_layout(
        width=width,
        height=height,
        margin=dict(
            l=width * label_area,  # Dynamic left margin for labels
            r=width * (1 - main_plot_width - label_area),
            t=40, b=20),  # Increased right margin for colorbars
        plot_bgcolor='white',
        xaxis_showgrid=False,
        yaxis_showgrid=False,
        **{f'xaxis{i}_showticklabels': False for i in range(1, num_rows + 1)},
        **{f'yaxis{i}_showticklabels': False for i in range(1, num_rows + 1)}
    )

    return fig


def generate_aa_features_heatmap_refalt(data, zdata = None, width=500, height=400, variant_labels=None,
                                        generate_pathogenicity_heatmap=False, showlegend=True):

    if zdata is None:
        z1, z2, z3, z4, z5, z6 = generate_aa_features_heatmap_dataframe_refalt(data)
    else:
        z1 = zdata[0]
        z2 = zdata[1]
        z3 = zdata[2]
        z4 = zdata[3]
        z5 = zdata[4]
        z6 = zdata[5]

    # Custom discrete colorscales
    colorscale = [[0, 'red'], [0.5, 'white'], [1, 'blue']]
    #colorscale1 = [[0, 'blue'], [0.5, 'yellow'], [1, 'green']]
    #colorscale2 = [[0, 'red'], [0.5, 'white'], [1, 'black']]
    num_vars = len(variant_labels)
    tickvals = [i +(i*5) for i in range(len(variant_labels))]
    tickvals = [0,1,2,3,4,5]
    #tickvals = ["ref", "alt", "change"]
    #tickvals = [0,1,2]

    # Create a subplot figure with 2 rows and 1 column
    fig = make_subplots(rows=6, cols=1, column_widths=[0.03], shared_xaxes=True)

    # Molecular weight
    heatmap1 = go.Heatmap(
        z=z1,xgap=2,ygap=2,
        colorscale=colorscale,
        colorbar=dict(
            title="Δ Mol. weight",
            tickvals=[1, 2, 3, 4, 5],      # Discrete values
            ticktext=["Small", "", "", "", "Large"],  # Custom legend labels
            len=0.5,
            y=1.1,
            yanchor='top',
            x=1.1
        ),
        zmin=1, zmax=5  # Ensure the scale is consistent with the discrete values
    )
    fig.add_trace(heatmap1, row=1, col=1)

    # Charge
    heatmap2 = go.Heatmap(
        z=z2,xgap=2,ygap=2,
        colorscale=colorscale,
        colorbar=dict(
            title="Δ Charge",
            tickvals=[1, 2, 3, 4, 5],      # Discrete values
            ticktext=["Negative", "", "Unchanged", "", "Positive"],  # Custom legend labels
            len=0.5,
            y=1.1,
            yanchor='top',
            x=3.0
        ),
        zmin=1, zmax=5  # Ensure the scale is consistent with the discrete values
    )
    fig.add_trace(heatmap2, row=2, col=1)

    # Polarity
    heatmap3 = go.Heatmap(
        z=z3,xgap=2,ygap=2,
        colorscale=colorscale,
        colorbar=dict(
            title="Δ Polarity",
            tickvals=[1, 2, 3, 4, 5],      # Discrete values
            ticktext=["Non-polar", "", "", "", "Polar"],  # Custom legend labels
            len=0.5,
            y=0.6,
            yanchor='top',
            x=1.1
        ),
        zmin=1, zmax=5  # Ensure the scale is consistent with the discrete values
    )
    fig.add_trace(heatmap3, row=3, col=1)

    # Aromaticity
    heatmap4 = go.Heatmap(
        z=z4,xgap=2,ygap=2,
        colorscale=colorscale,
        colorbar=dict(
            title="Δ Aromaticity",
            tickvals=[1, 2, 3, 4, 5],      # Discrete values
            ticktext=["Non-aromatic","", "", "",  "Aromatic"],  # Custom legend labels
            len=0.5,
            y=0.6,
            yanchor='top',
            x=3.0
        ),
        zmin=1, zmax=5  # Ensure the scale is consistent with the discrete values
    )
    fig.add_trace(heatmap4, row=4, col=1)

    # Flexibility
    heatmap5 = go.Heatmap(
        z=z5,xgap=2,ygap=2,
        colorscale=colorscale,
        colorbar=dict(
            title="Δ Flexibility",
            tickvals=[1, 2, 3, 4, 5],      # Discrete values
            ticktext=["Low", "", "", "", "High"],  # Custom legend labels
            len=0.5,
            y=0.1,
            yanchor='top',
            x=1.1
        ),
        zmin=1, zmax=5  # Ensure the scale is consistent with the discrete values
    )
    fig.add_trace(heatmap5, row=5, col=1)

    # Phosphorylation
    heatmap6 = go.Heatmap(
        z=z6,xgap=2,ygap=2,
        colorscale=colorscale,
        colorbar=dict(
            title="Δ Phosphorylation",
            tickvals=[1, 2, 3, 4, 5],      # Discrete values
            ticktext=["No phosphorylation", "", "", "", "Phosphorylation"],
            len=0.5,
            y=0.1,
            yanchor='top',
            x=3.0
        ),
        zmin=1, zmax=5
    )
    fig.add_trace(heatmap6, row=6, col=1)

    if showlegend is True:
        fig.add_annotation(
            text="Molecular weight",
            xref="paper", yref="paper",
            x=-2, y=1,  # Position to the left of the first heatmap
            showarrow=False,
            font=dict(size=14)
        )

        fig.add_annotation(
            text="Charge",
            xref="paper", yref="paper",
            x=-2, y=0.8,  # Position to the left of the second heatmap
            showarrow=False,
            font=dict(size=14)
        )

        fig.add_annotation(
            text="Polarity",
            xref="paper", yref="paper",
            x=-2, y=0.6,  # Position to the left of the first heatmap
            showarrow=False,
            font=dict(size=14)
        )

        fig.add_annotation(
            text="Aromaticity",
            xref="paper", yref="paper",
            x=-2, y=0.4,  # Position to the left of the second heatmap
            showarrow=False,
            font=dict(size=14)
        )

        fig.add_annotation(
            text="Flexibility",
            xref="paper", yref="paper",
            x=-2, y=0.2,  # Position to the left of the first heatmap
            showarrow=False,
            font=dict(size=14)
        )

        fig.add_annotation(
            text="Phosphorylation",
            xref="paper", yref="paper",
            x=-2, y=0,  # Position to the left of the second heatmap
            showarrow=False,
            font=dict(size=14)
        )

    #print(tickvals)
    print(num_vars)
    fig.update_layout(
        height=height,
        width=width,
        title_text="",
        yaxis={'visible': True, 'showticklabels': False},
        xaxis={'visible': True,'showticklabels': False},
        xaxis2=dict(showticklabels=False),
        yaxis2=dict(showticklabels=False),
        xaxis3=dict(showticklabels=False),
        yaxis3=dict(showticklabels=False),
        xaxis4=dict(showticklabels=False),
        yaxis4=dict(showticklabels=False),
        xaxis5=dict(showticklabels=False),
        yaxis5=dict(showticklabels=False),
        xaxis6={"visible": True, "showticklabels": True, 'ticktext': ["ref","alt","change"], "tickvals":tickvals, "range":[-0.5, 2.5 ]},
        yaxis6=dict(showticklabels=False),
        margin=dict(l=150, r=150)
    )
    #fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)

    return fig
