import traceback
import plotly.express as px
import adagenes as ag
import plotly.graph_objects as go
from flask import Flask, jsonify
import json
from plotly.utils import PlotlyJSONEncoder

def sort_genomic_locations(locations):
    # Define a custom sorting key
    def sort_key(location):
        # Extract the chromosome part
        chromosome = location.split(':')[0]
        # Remove 'chr' prefix
        chromosome = chromosome[3:]
        # Define the order for chromosomes
        if chromosome.isdigit():
            return (0, int(chromosome))
        elif chromosome == 'X':
            return (1, 0)
        elif chromosome == 'Y':
            return (2, 0)
        elif chromosome == 'N':
            return (3, 0)
        else:
            return (4, 0)

    # Sort the list using the custom sorting key
    sorted_locations = sorted(locations, key=sort_key)
    return sorted_locations

def get_max_score(score):
    if isinstance(score, str):
        elements = score.split(";")
    else:
        elements = [score]
    score_max = 0
    for el in elements:
        if el !=".":
            try:
                if float(el) > score_max:
                    score_max = float(el)
            except:
                print(traceback.format_exc())
    return score_max

def generate_pathogenicity_heatmap(bframe):
    scores = {
        "AlphaMissense_score": [], "REVEL_rankscore": [], "PrimateAI_rankscore": [], "EVE_rankscore": [],
        "ESM1b_rankscore": [], "VARITY_ER_LOO_rankscore": [],
        "PROVEAN_converted_rankscore": [], "MutationTaster_converted_rankscore": [],
        "MutationAssessor_rankscore": [],
        "MVP_rankscore": [], "GERP++_RS_rankscore": []
    }

    var_list = list(bframe.data.keys())
    sorted_locations = sort_genomic_locations(var_list)

    # Calculate aggregate pathogenicity score for each variant
    pathogenicity_scores = {}
    for var in sorted_locations:
        aggregate_score = 0
        count = 0
        for score in scores.keys():
            if "dbnsfp" in bframe.data[var]:
                if score in bframe.data[var]["dbnsfp"]:
                    val = bframe.data[var]["dbnsfp"][score]
                    if val != "" and val != ".":
                        val = get_max_score(val)
                        val = float(val)
                        aggregate_score += val
                        count += 1
        if count > 0:
            pathogenicity_scores[var] = aggregate_score / count
        else:
            pathogenicity_scores[var] = 0

    # Sort variants by aggregate pathogenicity score
    sorted_variants = sorted(pathogenicity_scores, key=pathogenicity_scores.get, reverse=True)

    # Select top 50 variants
    top_50_variants = sorted_variants[:50]

    # Prepare data for the heatmap
    scores_list = []
    x_labels = []
    y_labels = [
        "AlphaMissense", "REVEL", "PrimateAI", "EVE",
        "ESM1b", "VARITY ER LOO", "PROVEAN", "MutationTaster", "MutationAssessor",
        "MVP", "GERP++ RS"
    ]

    for var in top_50_variants:
        if "UTA_Adapter" in bframe.data[var]:
            if "gene_name" in bframe.data[var]["UTA_Adapter"] and "variant_exchange" in bframe.data[var]["UTA_Adapter"]:
                label = bframe.data[var]["UTA_Adapter"]["gene_name"] + ":" + bframe.data[var]["UTA_Adapter"][
                    "variant_exchange"]
            else:
                label = var
        else:
            label = var
        # x_labels.append(var)
        x_labels.append(label)
        for score in scores.keys():
            if "dbnsfp" in bframe.data[var]:
                if score in bframe.data[var]["dbnsfp"]:
                    val = bframe.data[var]["dbnsfp"][score]
                    if val != "" and val != ".":
                        val = get_max_score(val)
                        val = float(val)
                        scores[score].append(val)
                    else:
                        scores[score].append(0)
                else:
                    scores[score].append(0)
            else:
                scores[score].append(0)

    for score in scores.keys():
        scores_list.append(scores[score])
    # print("scores ", len(scores_list))
    # print("scores ", scores_list)

    num_x_labels = len(x_labels)
    num_y_labels = len(y_labels)

    width = max(800, num_x_labels * 20)  # Adjust the multiplier as needed
    height = max(400, num_y_labels * 20)  # Adjust the multiplier as needed
    tick_label_size = max(10, min(16, int(num_x_labels / 10)))

    fig = ag.generate_protein_pathogenicity_plot(scores_list, x_title="Variant", y_title="",
                                                 x_labels=x_labels, y_labels=y_labels,
                                                 width=width, height=height, tick_label_size=tick_label_size)
    return fig

def generate_protein_pathogenicity_plot_variantlist(variants,
                                        x_title="",
                                        y_title="",
                                        x_labels="",
                                        y_labels="",
                                        font_size=12,
                                        label_color='#000000',
                                        width=400,
                                        height=200,
                                        tick_label_size=12
                                        ):
    """

    :param scores:
    :param x_title:
    :param y_title:
    :param x_labels:
    :param y_labels:
    :return:
    """
    scores = {
        "dbnsfp_alphamissense_rankscore": [], "dbnsfp_revel_rankscore": [], "dbnsfp_primateai_rankscore": [],
        "dbnsfp_eve_rankscore": [],
        "dbnsfp_esm1b_rankscore": [], "dbnsfp_varity_er_loo_rankscore": [],
        "dbnsfp_provean_converted_rankscore": [], "dbnsfp_mutationtaster_converted_rankscore": [],
        "dbnsfp_mutationassessor_rankscore": [],
        "dbnsfp_mvp_rankscore": [], "dbnsfp_gerp++_rs_rankscore": []
    }

    #var_list = list(bframe.data.keys())
    #sorted_locations = sort_genomic_locations(var_list)
    sorted_locations = variants
    vars = {}

    # Calculate aggregate pathogenicity score for each variant
    pathogenicity_scores = {}
    for var in sorted_locations:
        #print(var)
        if 'qid' in var:
            qid = var["qid"]
            vars[qid] = var
            aggregate_score = 0
            count = 0
            scores_found = 0
            for score in scores.keys():
                #if "dbnsfp" in bframe.data[var]:
                    if score in var.keys():
                        val = var[score]
                        if val != "" and val != ".":
                            val = get_max_score(val)
                            val = float(val)
                            aggregate_score += val
                            scores_found += 1
                    else:
                        #print("score not found ",score,": ",var)
                        pass
                    count += 1
            if scores_found > 0:
                pathogenicity_scores[qid] = aggregate_score / count
            else:
                pathogenicity_scores[qid] = 0

    # Sort variants by aggregate pathogenicity score
    sorted_variants = sorted(pathogenicity_scores, key=pathogenicity_scores.get, reverse=True)

    # Select top 50 variants
    #top_50_variants = sorted_variants[:50]
    top_50_variants = sorted_variants[:30]

    # Prepare data for the heatmap
    scores_list = []
    x_labels = []
    y_labels = [
        "AlphaMissense", "REVEL", "PrimateAI", "EVE",
        "ESM1b", "VARITY ER LOO", "PROVEAN", "MutationTaster", "MutationAssessor",
        "MVP", "GERP++ RS"
    ]

    for var in top_50_variants:
        variant = vars[var]
        if "uta_adapter_gene_name" in variant and "uta_adapter_variant_exchange" in variant:
            label = variant["uta_adapter_gene_name"] + ":" + variant["uta_adapter_variant_exchange"]
        else:
            label = var
        # x_labels.append(var)
        x_labels.append(label)
        for score in scores.keys():
            #if "dbnsfp" in var:
                if score in variant:
                    val = variant[score]
                    if val != "" and val != ".":
                        val = get_max_score(val)
                        val = float(val)
                        #print("found score ",score, " val ", val)
                        scores[score].append(val)
                    else:
                        scores[score].append(0)

                else:
                    scores[score].append(0)
                    #print("score not found ", score, " ", variant)
            #else:
            #    scores[score].append(0)

    for score in scores.keys():
        scores_list.append(scores[score])
    # print("scores ", len(scores_list))
    # print("scores ", scores_list)

    num_x_labels = len(x_labels)
    num_y_labels = len(y_labels)

    width = max(800, num_x_labels * 20)  # Adjust the multiplier as needed
    height = max(400, num_y_labels * 20)  # Adjust the multiplier as needed
    tick_label_size = max(10, min(16, int(num_x_labels / 10)))

    fig = ag.generate_protein_pathogenicity_plot(scores_list, x_title="Variant", y_title="",
                                                 x_labels=x_labels, y_labels=y_labels,
                                                 width=width, height=height, tick_label_size=tick_label_size)

    #return jsonify(fig.to_dict())

    #fig_json = json.dumps(fig.to_dict(), cls=PlotlyJSONEncoder)
    fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    return fig_json

def generate_protein_pathogenicity_plot(scores,
                                        x_title="",
                                        y_title="",
                                        x_labels="",
                                        y_labels="",
                                        font_size=12,
                                        label_color='#000000',
                                        width=350,
                                        height=200,
                                        tick_label_size=12
                                        ):
    """

    :param scores:
    :param x_title:
    :param y_title:
    :param x_labels:
    :param y_labels:
    :return:
    """
    fig = px.imshow(scores,labels={"x":x_title,"y":y_title}, y=y_labels, x=x_labels,
                    color_continuous_scale='Bluyl',color_continuous_midpoint=0.5, zmin=0.0, zmax=1.0)

    fig.update_layout(
        margin=dict(l=10, r=0, t=0, b=0, pad=0),
        font=dict(
            family="Arial",
            size=tick_label_size,
            color=label_color
        ),
        paper_bgcolor="#ffffff",
        width=int(width),
        height=int(height)
    )
    return fig


    #return fig

    heatmap_data = go.Heatmap(
        z=scores,
        x=x_labels,
        y=y_labels,
        colorscale='Viridis'
    )

    # Create the layout
    layout = go.Layout(
        title='Pathogenicity Heatmap',
        xaxis=dict(title='Variants'),
        yaxis=dict(title='Scores'),
        colorbar=dict(title='Pathogenicity Score')
    )

    # Create the figure
    fig = go.Figure(data=[heatmap_data], layout=layout)

    # Convert the figure to JSON
    plot_data = fig.to_json()

    return jsonify(plot_data)

