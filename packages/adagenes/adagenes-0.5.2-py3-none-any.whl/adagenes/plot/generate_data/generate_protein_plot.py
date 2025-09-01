from json import JSONDecodeError

import requests
import adagenes.conf.read_config as conf_reader


def generate_protein_plot(variant_data):
    """
    Generates data for a variant needleplot

    :param variant_data:
    :return:
    """
    q = variant_data["UTA_Adapter"]["gene_name"] + ':' + variant_data["UTA_Adapter"]["variant_exchange"]
    url = conf_reader.protein_module_src + q
    #print(url)
    graphJSON = requests.get(url, timeout=60)
    try:
        return graphJSON.json()
    except JSONDecodeError:
        print("Could not decode JSON: ",graphJSON)
        return {}

