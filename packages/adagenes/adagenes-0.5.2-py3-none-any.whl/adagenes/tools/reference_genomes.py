
def add_hg38_positions(bframe):
    """
    Generates the hg38/GRCh38 position as the default variant position

    :param bframe:
    :return:
    """
    for var in bframe.keys():
        if "POS_hg38" in bframe[var]["variant_data"]:
            bframe[var]["variant_data"]["POS_hg38"] = bframe[var]["variant_data"]["POS"]
    return bframe
