import adagenes
from adagenes.conf import read_config as config
import traceback


def generate_variant_data_sections(json_obj):
    for qid in json_obj.keys():
        chrom, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(qid)
        if "variant_data" not in json_obj[qid]:
            json_obj[qid]["variant_data"] = {}

        json_obj[qid]["variant_data"]["CHROM"] = chrom
        json_obj[qid]["variant_data"]["POS"] = pos
        json_obj[qid]["variant_data"]["REF"] = ref
        json_obj[qid]["variant_data"]["ALT"] = alt

    return json_obj


def generate_variant_data(json_obj, variant, chromosome, pos, fields, ref_base, alt_base, genome_version=None):
    """
    Adds an additional biomarker to a biomarker frame

    :param json_obj:
    :param variant:
    :param chromosome:
    :param pos:
    :param fields:
    :param ref_base:
    :param alt_base:
    :return:
    """
    isbframe = False
    if isinstance(json_obj, adagenes.BiomarkerFrame):
        variant_data = json_obj.data
        isbframe = True
    else:
        variant_data = json_obj

    variant_data[variant] = {}
    variant_data[variant][config.variant_data_key] = {
        "CHROM": chromosome,
        "POS": pos,
        "ID": fields[2],
        "REF": ref_base,
        "ALT": alt_base,
        "QUAL": fields[5],
        "FILTER": fields[6],
        "INFO": fields[7],
        "OPTIONAL": fields[8:]
    }

    if genome_version is not None:
        variant_data[variant][config.variant_data_key]["POS_"+genome_version] = pos

    try:
        info_features = fields[7].split(";")
        #print(info_features)
        if "info_features" not in variant_data[variant][config.variant_data_key]:
            variant_data[variant]["info_features"] = {}
        for feature in info_features:
            #print(feature)
            if len(feature.split("=")) > 1:
                split_str = feature.split('=')
                key = split_str[0]
                val = '='.join(split_str[1:])

                #key, val = feature.split("=")
                variant_data[variant]["info_features"][key] = val
            else:
                if feature != "":
                    #print("No valid info feature: ",feature)
                    pass
    except:
        print("error extracting INFO features")
        print(traceback.format_exc())

    if isbframe is True:
        json_obj.data = variant_data
    else:
        json_obj = variant_data

    return json_obj


def generate_keys(json_obj, modules):
    """
    Generates keys with empty dictionaries for all Onkopus modules to avoid missing keys

    Parameters
    ----------
    json_obj

    Returns
    -------

    """
    for variant in json_obj.keys():
        if variant != 'vcf_header':
            for k in modules.keys():
                if k not in json_obj[variant]:
                    json_obj[variant][k] = {}
                if type(modules[k]) is dict:
                    for sk in modules[k].keys():
                        if sk not in json_obj[variant][k].keys():
                            if type(modules[k][sk]) is dict:
                                json_obj[variant][k][sk] = {}
                                for skk in modules[k][sk].keys():
                                    if skk not in json_obj[variant][k][sk].keys():
                                        if type(json_obj[variant][k][sk]) is dict:
                                            json_obj[variant][k][sk][skk] = {}
                                        else:
                                            json_obj[variant][k][sk][skk] = ""
                            else:
                                json_obj[variant][k][sk] = ""

    return json_obj
