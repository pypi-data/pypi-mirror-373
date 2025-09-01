import pandas as pd
import adagenes.conf.read_config as conf_reader
import adagenes.plot.generate_data.plot_config as plot_config
from statistics import mean


def transform_missense3d_prediction_to_val(m3d_val):
    """
    Maps Missense3D variant pathogenicity predictions to float values in the range [0,1](0=benign, 1=pathogenic)

    :param m3d_val:
    :return:
    """

    if m3d_val == "Damaging":
        val = 1.0
    elif m3d_val == "Neutral":
        val = 0.5
    else:
        val = 0.0

    return val


def get_list_of_pathogenicity_scores(json_obj, modules, features):
    """
    Aggregates a list of pathogenicity score values in a list

    :param json_obj:
    :param modules:
    :param features:
    :return:
    """
    scores = []
    for i, module in enumerate(modules):
        if module in json_obj:
            if features[i] in json_obj[module]:
                val = json_obj[module][features[i]]
                if val == ".":
                    val = 0
                else:
                    try:
                        if features[i] == "Missense3D":
                            val = transform_missense3d_prediction_to_val(val)

                        val = float(val)
                    except:
                        print("Error converting score value to float: ",json_obj[module][features[i]],"; ",module,",",features[i])
                        val = 0
                scores.append(val)
            else:
                scores.append(0)
        else:
            scores.append(0)

    return scores


def generate_biomarker_identifiers(variant_data):
    """
    Returns a list of biomarker identifiers found in a biomarker set. Required for plot legends

    :param variant_data:
    :return:
    """
    identifiers = []
    for var in variant_data.keys():
        if conf_reader.uta_adapter_srv_prefix in variant_data[var]:
            if ("gene_name" in variant_data[var][conf_reader.uta_adapter_srv_prefix]) and \
            ("variant_exchange" in variant_data[var][conf_reader.uta_adapter_srv_prefix]):
                identifiers.append(
                    variant_data[var][conf_reader.uta_adapter_srv_prefix]["gene_name"] + ":" +
                    variant_data[var][conf_reader.uta_adapter_srv_prefix]["variant_exchange"]
                )
    return identifiers


def generate_single_biomarker_radar_plot_data(variant_data, qid, labels=None, modules=None, features=None) -> pd.DataFrame:
    """
    Generates dataframe for a radar plot displaying the pathogenicity scores for a single variant

    :param variant_data:
    :param qid:
    :return:
    """
    if labels is None:
        labels = plot_config.default_pathogenicity_labels
    if modules is None:
        modules = plot_config.default_pathogenicity_modules
    if features is None:
        features = plot_config.default_pathogenicity_features

    #r = [1, 5, 2, 2, 2]
    #theta = ['a', 'b', 'c', 'd', 'e']
    scores = get_list_of_pathogenicity_scores(variant_data[qid], modules, features)
    data = {
        "r": scores,
        "theta": labels
    }
    df = pd.DataFrame(data=data)
    #print(df)
    return df


def generate_multiple_biomarker_radar_plot_data(variant_data, labels=None, modules=None, features=None) -> pd.DataFrame:
    """
    Generates dataframe for a radar plot displaying the pathogenicity scores for a single variant

    :param variant_data:
    :param qid:
    :return:
    """
    if labels is None:
        labels = plot_config.default_pathogenicity_labels
    if modules is None:
        modules = plot_config.default_pathogenicity_modules
    if features is None:
        features = plot_config.default_pathogenicity_features

    dfs = []
    for qid in variant_data:
        scores = get_list_of_pathogenicity_scores(variant_data[qid], modules, features)
        data = {
            "r": scores,
            "theta": labels
        }
        df = pd.DataFrame(data=data)
        dfs.append(df)
    return dfs


def generate_categorical_scores(dfs):
    """
    Generates a dataframe of categorically grouped scores

    :param dfs:
    :return:
    """
    cat_score_dfs = []

    for df in dfs:
        scores= []
        labels = []
        for cat in plot_config.cat_dc:
            #print("scores: ",cat_dc[cat])
            labels.append(cat)
            found_scores = []
            for score in plot_config.cat_dc[cat]:
                if score in list(df["theta"]):
                    r = list(df.loc[df["theta"] == score]["r"])[0]
                    if r != 0:
                        found_scores.append(r)
                else:
                    print("score not found: ",score)
            #print("Found scores (" + cat +")",found_scores)
            if len(found_scores) > 0:
                weighted_score = mean(found_scores)
            else:
                weighted_score = 0.0
            #print("Computed mean score: ",weighted_score)
            scores.append(weighted_score)
        df = pd.DataFrame(data={ "r":scores, "theta":labels })
        #dfs.append(df)
        cat_score_dfs.append(df)

    return cat_score_dfs
