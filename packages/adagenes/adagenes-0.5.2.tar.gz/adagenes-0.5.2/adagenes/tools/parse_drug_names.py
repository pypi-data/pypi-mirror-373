
def parse_drug_name(drug_name):
    """

    :param drug_name:
    :return:
    """
    drug_name_norm = ""
    drug_name = drug_name.lower()
    if (drug_name == "n/a") or (drug_name == 'N/A'):
        pass
    elif "/" in drug_name:
        print("add normalized drug ",drug_name_norm)
        drug_name_norm = drug_name.replace("/", "_")
    else:
        drug_name_norm = drug_name

    return drug_name_norm


def parse_drug_names(variant_data,match_types,section="merged_match_types_data"):
    """
    Parse drug names of clinical evidence data to generate valid drug identifiers

    :param variant_data:
    :return:
    """

    for var in variant_data.keys():
        for match_type in match_types:
            if "onkopus_aggregator" in variant_data[var]:
                if match_type in variant_data[var]["onkopus_aggregator"][section]:
                    for i,treatment in enumerate(variant_data[var]["onkopus_aggregator"][section][match_type]):

                            if "drugs" in treatment:
                                for d,drug in enumerate(treatment["drugs"]):
                                    if isinstance(drug, dict):
                                        if "drug_name" in drug:
                                            drug_name = drug["drug_name"]
                                            drug_name_norm = parse_drug_name(drug_name)
                                            #print("parse drug names ", drug, ": ", variant_data[var]["onkopus_aggregator"]["merged_match_types_data"][i]["drugs"][d])
                                            variant_data[var]["onkopus_aggregator"][section][match_type][i]["drugs"][d]["drug_name_norm"] = drug_name_norm
                                    elif isinstance(drug, str):
                                        drug_name = drug
                                        drug_dc = {}
                                        drug_dc["drug_name"] = drug_name
                                        drug_dc["drug_name_norm"] = parse_drug_name(drug_name)
                                        print("Set new drug dictionary: (", treatment["source"] ,")",drug_dc)
                                        #variant_data[var]["onkopus_aggregator"]["merged_match_types_data"][i]["drugs"] = drug_dc
                                        print("Assign ",drug_dc ," to ",variant_data[var]["onkopus_aggregator"][section][match_type][i]["drugs"][d])
                            else:
                                print("Error (drug class client): No drugs section found for ",var)

    return variant_data

