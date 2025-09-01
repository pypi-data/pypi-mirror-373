from adagenes.conf import read_config as config

def separate_unidentified_snvs(annotated_data):
    """
    Separates gene names and protein change that could not be identified by the Coordinates Converter

    :param annotated_data:
    :return:
    """
    snvs = {}
    unidentified_snvs = {}
    for var in annotated_data.keys():
        identified = True
        if "status" in annotated_data[var]["variant_data"]:
            if annotated_data[var]["variant_data"]["status"] == "error":
                identified = False

        if identified:
            annotated_data[var]["mutation_type"] = "snv"
        else:
            annotated_data[var]["mutation_type"] = "unidentified"

    return annotated_data
