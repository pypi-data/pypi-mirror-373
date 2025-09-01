from typing import List
import pandas as pd

import adagenes as ag
from adagenes.tools.data_io import get_current_datetime
from adagenes.conf import read_config as config


def generate_vcf_columns(vcf_obj):
    if "INFO" not in vcf_obj[config.variant_data_key]:
        vcf_obj[config.variant_data_key]["INFO"] = "."

    return vcf_obj


def generate_variant_data_section_all_variants(variant_data):
    for var in variant_data:
        variant_data[var] = generate_variant_data_section(variant_data[var])
        chr, ref_seq, pos, ref, alt = ag.parse_genome_position(var)
    return variant_data


def generate_variant_data_section(vcf_obj,qid=None):
    """

    :param vcf_obj:
    :return:
    """
    if config.variant_data_key not in vcf_obj:
        vcf_obj[config.variant_data_key] = {}

        if qid is not None:
            chrom, ref_seq, pos, ref, alt = ag.parse_genome_position(qid)

            vcf_obj[config.variant_data_key]["CHROM"] = chrom
            vcf_obj[config.variant_data_key]["POS"] = pos
            vcf_obj[config.variant_data_key]["REF"] = ref
            vcf_obj[config.variant_data_key]["ALT"] = alt

    if "CHROM" in vcf_obj:
        vcf_obj[config.variant_data_key]["CHROM"] = vcf_obj["CHROM"]
    if "POS" in vcf_obj:
        vcf_obj[config.variant_data_key]["POS"] = vcf_obj["POS"]
    if "REF" in vcf_obj:
        vcf_obj[config.variant_data_key]["REF"] = vcf_obj["REF"]
    if "ALT" in vcf_obj:
        vcf_obj[config.variant_data_key]["ALT"] = vcf_obj["ALT"]

    if "ID" in vcf_obj:
        vcf_obj[config.variant_data_key]["ID"] = vcf_obj["ID"]
    elif "ID" not in vcf_obj[config.variant_data_key]:
        vcf_obj[config.variant_data_key]["ID"] = "."

    if "OPTIONAL" in vcf_obj:
        vcf_obj[config.variant_data_key]["OPTIONAL"] = vcf_obj["OPTIONAL"]
    elif "OPTIONAL" not in vcf_obj[config.variant_data_key]:
        vcf_obj[config.variant_data_key]["OPTIONAL"] = "."

    if "INFO" in vcf_obj:
        vcf_obj[config.variant_data_key]["INFO"] = vcf_obj["INFO"]
    elif "INFO" not in vcf_obj[config.variant_data_key]:
        vcf_obj[config.variant_data_key]["INFO"] = "."

    if "QUAL" in vcf_obj:
        vcf_obj[config.variant_data_key]["QUAL"] = vcf_obj["QUAL"]
    elif "QUAL" not in vcf_obj[config.variant_data_key]:
        vcf_obj[config.variant_data_key]["QUAL"] = "."

    if "FILTER" in vcf_obj:
        vcf_obj[config.variant_data_key]["FILTER"] = vcf_obj["FILTER"]
    elif "FILTER" not in vcf_obj[config.variant_data_key]:
        vcf_obj[config.variant_data_key]["FILTER"] = "."

    return vcf_obj


def extract_uta_adapter_annotations(variant_data, module, qkeys):
    q_annotations = {}
    for key, value in variant_data.items():
        qid = str(key)

        for qkey in qkeys:
            val = variant_data[key][qkey]
            q_annotations[qkey].append(val)

    return q_annotations


def extract_annotations_vcf(vcf_lines, qkeys, extract_from_info_column= True):
    """
    Extracts annotation values from the INFO column of an array of VCF lines. Returns a dictionary containing the requested annotations and a reverse

    :param vcf_lines: Array of lines in VCF format
    :param qkeys: Annotation keys to be extracted
    :return:
    """
    q_annotations = {}
    vcf_columns = ["CHROM", "POS", "REF", "ALT"]

    for qkey in qkeys:
        q_annotations[qkey] = []
    q_annotations['q_id'] = []

    #print("vcf lines extract: ",vcf_lines)

    for key, value in vcf_lines.items():
        qid = str(key)
        annotations = value[config.variant_data_key]["INFO"].split(";")
        #print(annotations)

        for qkey in qkeys:
            found = False
            if extract_from_info_column:
                for val in annotations:
                    key = val.split("=")
                    if len(key) > 0:
                        if key[0] == qkey:
                            q_annotations[qkey].append(key[1])
                            found=True
            else:
                # extract from VCF main columns (genome positions)
                if qkey in vcf_columns:
                    q_annotations[qkey].append( value[qkey] )
                    found=True
            if not found:
                q_annotations[qkey].append("")
        q_annotations['q_id'].append(qid)

    return q_annotations


def extract_annotations_json(vcf_lines, module, qkeys):
    """
    Extracts annotation values from a data section of the intermediate biomarker format.
    Module defines the section identifier, where qkeys describes the feature values within the section. (e.g. "dbsnp", "rsID")
    Returns a dictionary containing the requested annotations and a reverse

    :param vcf_lines: Array of lines in VCF format
    :param module: Module identifier containing the keys
    :param qkeys: Annotation keys to be extracted
    :return:
    """
    q_annotations = {}

    for qkey in qkeys:
        q_annotations[qkey] = []
    q_annotations['q_id'] = []

    for key, value in vcf_lines.items():
        qid = str(key)
        if module in value:
            annotations = value[module]

            for qkey in qkeys:
                if qkey in annotations:
                    q_annotations[qkey].append( str(annotations[qkey]) )
                else:
                    q_annotations[qkey].append("")
            q_annotations['q_id'].append(qid)
        else:
            annotations = value
            for qkey in qkeys:
                if qkey in annotations:
                    q_annotations[qkey].append( annotations[qkey] )
                else:
                    q_annotations[qkey].append("")
            q_annotations['q_id'].append(qid)
    return q_annotations


def extract_annotations_json_part(vcf_lines, module,qkeys, qids_partial):
    """
    Extracts annotation values from the INFO column of an array of VCF lines. Returns a dictionary containing the requested annotations and a reverse

    :param vcf_lines: Array of lines in VCF format
    :param qkeys: Annotation keys to be extracted
    :return:
    """
    q_annotations = {}

    for qkey in qkeys:
        q_annotations[qkey] = []
    q_annotations['q_id'] = []

    for key, value in vcf_lines.items():
        qid = str(key)
        if qid in qids_partial:
            if module in value:
                annotations = value[module]

                for qkey in qkeys:
                    if qkey in annotations:
                        q_annotations[qkey].append( annotations[qkey] )
                    else:
                        q_annotations[qkey].append("")
                q_annotations['q_id'].append(qid)
            else:
                annotations = value
                for qkey in qkeys:
                    if qkey in annotations:
                        q_annotations[qkey].append( annotations[qkey] )
                    else:
                        q_annotations[qkey].append("")
                q_annotations['q_id'].append(qid)
    return q_annotations


def process_vcf_headers(header_lines, genome_version, info_lines=None):
    if info_lines is not None:
        [header_lines.insert(len(header_lines) - 1, x) for x in info_lines]

    if len(header_lines)>0:
        if not header_lines[0].startswith('##AdaGenes v'):
            header_lines.insert(0, "##AdaGenes v" + ag.conf_reader.config['DEFAULT']['VERSION'])
    else:
        header_lines.insert(0, "##AdaGenes v"+ag.conf_reader.config['DEFAULT']['VERSION'])

    # TODO parse genome version
    return header_lines, genome_version

frontend_keys_mapping = {
    "dbSNP_rsID" : "dbsnp_rsid",
    "dbSNP_total": "dbsnp_total",
    "ClinVar_ClinicalSignificance": "clinvar_clinicalsignificance",
    "UTA_Adapter_variant_exchange": "variant_exchange",
    "UTA_Adapter_gene_name": "gene_name",
    "VUS_PREDICT_Score": "vuspredict_score",
    "revel_Score": "revel_score",
    "loftool_Score": "loftool_score"
}

info_col="info"

def get_annotations_as_additional_columns(annotated_vcf):
    """
    Extracts variant annotation data from the INFO columns and adds it as additional dataframe columns

    :param annotated_vcf:
    :return:
    """

    info_col = 7
    for i in range(0, annotated_vcf.shape[0]):
        info_values = annotated_vcf.iloc[i,info_col]
        values = info_values.split(";")
        for val in values:
            pair = val.split('=')
            #print(pair,",",len(pair))
            if len(pair)>1:
                key = pair[0]
                value = pair[1]
                if (key in frontend_keys_mapping.keys()):
                    frontend_key = frontend_keys_mapping[key]
                    if (frontend_keys_mapping[key] not in annotated_vcf.columns):
                        annotated_vcf[str(frontend_key)] = ["0" for x in range(0, annotated_vcf.shape[0])]
                    annotated_vcf.at[i, frontend_key] = value
                    #print("add col ",frontend_key)

    #print("return ",annotated_vcf)
    return annotated_vcf


def generate_file_paths_infile(id_files, id: str, base_path:str=None, infile:str = None, outfile: str = None, module: str=None) -> List:
    """
    Generates the output file paths for variant interpretation results

    :param id:
    :param outfile:
    :return:
    """

    dt = get_current_datetime()
    id_files["current_datetime"] = str(dt)

    if infile is None:
        id_files["base_file"] = id_files["basedir"] + "/variants_" + dt + ".vcf"
    else:
        id_files["base_file"] = infile

    return id_files


def generate_file_paths_outfile(df, id_files, id: str, base_path:str=None, infile:str = None, outfile: str = None) -> List:
    """
    Generates the output file paths for variant interpretation results

    :param id:
    :param outfile:
    :return:
    """

    dt = get_current_datetime()
    id_files["current_datetime"] = str(dt)

    if outfile is None:
        id_files["basedir"] = base_path + "/" + id
        id_files["filtered_file"] = id_files["basedir"] + "/variants_" + dt + ".vcf.filtered"
        id_files["annotated_filename"] = "variants"+ '_' + dt + '_' + str(df.shape[0]+1)  + ".annotated.vcf"
        id_files["annotated_filename_json"] = "variants" + '_' + dt + '_' + str(df.shape[0] + 1) + ".annotated.json"
    else:
        id_files["basedir"] = base_path + "/" + id
        id_files['annotated_filename'] = outfile

    id_files["annotated_file_vcf"] = id_files["basedir"] +"/"+ id_files["annotated_filename"]
    id_files["annotated_file_json"] = id_files["basedir"] + "/" + id_files["annotated_filename_json"]

    return id_files


