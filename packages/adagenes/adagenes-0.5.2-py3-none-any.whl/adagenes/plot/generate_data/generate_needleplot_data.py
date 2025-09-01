import pandas as pd


def generate_needleplot_data_all_biomarkers(variant_data):

    x_list = []
    y_list = []
    mutation_groups = []
    domains = []

    for qid in variant_data.keys():
        pos = variant_data[qid]["variant_data"]["POS"]
        x_list.append(pos)

        y_list.append(1)

        mutation_groups.append("Helix")

    data = {
        'x': x_list,
        'y': y_list,
        'mutationGroups': mutation_groups,
        'domains': domains,
    }

    return data
