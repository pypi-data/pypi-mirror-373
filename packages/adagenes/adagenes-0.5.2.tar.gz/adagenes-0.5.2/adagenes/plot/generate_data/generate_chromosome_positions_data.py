
def generate_chromosome_positions_data(variant_data, genome_version):
    """

    :param variant_data:
    :param genome_version:
    :return:
    """
    pos_data = []

    for var in variant_data.keys():
        if ("UTA_Adapter" in variant_data[var]) and ("variant_data" in variant_data[var]):
            if "POS_" + genome_version in variant_data[var]["variant_data"]:
                if ("gene_name" in variant_data[var]["UTA_Adapter"]) and (variant_data[var]["variant_data"]["POS_"+genome_version] != ''):
                    try:
                        dc = {}
                        dc["name"] = variant_data[var]["UTA_Adapter"]["gene_name"]
                        dc["chr"] = variant_data[var]["variant_data"]["CHROM"]
                        dc["start"] = int(variant_data[var]["variant_data"]["POS_"+genome_version])
                        dc["stop"] = int(variant_data[var]["variant_data"]["POS_"+genome_version])
                        pos_data.append(dc)
                    except:
                        print("Error: Could not parse chromosome position for ",var)
                else:
                    print("Error: No UTA adapter gene name annotation available for ", var)
        else:
            print("Error: No UTA adapter annotation available for ",var)

    return pos_data
