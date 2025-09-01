import adagenes.tools
from adagenes.conf import read_config as config
import adagenes.tools.hgvs_re


def get_biomarker_type_aaexchange(json_obj):
    """
    Identify biomarker types by their amino acid exchange characteristics.
    Receives the data body of a biomarker frame and parses the amino acid exchanges to identify
    single nucleotide variants (SNVs), insertions and deletion, copy number variations and gene fusions.
    Adds the identified biomarker types as a new feature 'type' in the 'variant data' section of the biomarker body

    :param json_obj:
    :return:
    """

    for qid in json_obj.keys():

        if config.variant_data_key in json_obj[qid]:
            # SNV
            if ("REF" in json_obj[qid][config.variant_data_key]) and ("ALT" in json_obj[qid][config.variant_data_key]):
                try:
                    # SNV
                    if (len(json_obj[qid][config.variant_data_key]["REF"])==1) and (len(json_obj[qid][config.variant_data_key]["ALT"])==1):
                        alt = json_obj[qid][config.variant_data_key]["ALT"]
                        if config.uta_adapter_srv_prefix in json_obj[qid]:
                            if "variant_exchange" in json_obj[qid][config.uta_adapter_srv_prefix]:
                                variant_exchange= json_obj[qid][config.uta_adapter_srv_prefix]["variant_exchange"]
                                aaref, pos, aaalt = adagenes.tools.parse_variant_exchange(variant_exchange)
                                if aaalt is not None:
                                    if aaalt in adagenes.tools.gencode.aalist:
                                        json_obj[qid][config.variant_data_key]["type"] = "Missense SNV"
                                    elif aaalt == '*':
                                        json_obj[qid][config.variant_data_key]["type"] = "Nonsense SNV"
                                    elif aaalt == '=':
                                        json_obj[qid][config.variant_data_key]["type"] = "Silent SNV"
                                    elif aaalt == '?':
                                        json_obj[qid][config.variant_data_key]["type"] = "Unknown substitution"
                        else:
                            json_obj[qid][config.variant_data_key]["type"] = "SNV"
                        continue
                    # multiple alternate alleles
                    # TODO
                    elif "," in json_obj[qid][config.variant_data_key]["ALT"]:
                        json_obj[qid][config.variant_data_key]["type"] = "unidentified"
                        continue
                    # deletion
                    elif len(json_obj[qid][config.variant_data_key]["REF"]) > len(json_obj[qid][config.variant_data_key]["ALT"]):
                        json_obj[qid][config.variant_data_key]["type"] = "deletion"
                        # TODO: Parse biomarker ID
                    # insertion
                    elif len(json_obj[qid][config.variant_data_key]["REF"]) < len(
                            json_obj[qid][config.variant_data_key]["ALT"]):
                        json_obj[qid][config.variant_data_key]["type"] = "insertion"
                        # TODO: Parse biomarker ID
                except:
                    print("Error: Could not detect biomarker type for ",qid)
        else:
            json_obj[qid][config.variant_data_key] = {}

        if "type" not in json_obj[qid][config.variant_data_key]:
            json_obj[qid][config.variant_data_key]["type"] = ""

    return json_obj
