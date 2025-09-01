from typing import List
import pandas as pd
import re
import adagenes.tools
from adagenes.conf import read_config as config
import adagenes.tools.hgvs_re as gencode


def get_chr(accessor:str) -> str:
    """
    Maps NC chromosome identifiers

    :param accessor:
    :return:
    """
    chr = {
        "NC_000001.9":["chr1"],
        "NC_000001.10":["chr1"],
        "NC_000001.11":["chr1"],
        "NC_000002.11":["chr2"],
        "NC_000002.12":["chr2"],
        "NC_000003.11":["chr3"],
        "NC_000003.12":["chr3"],
        "NC_000004.11":["chr4"],
        "NC_000004.12":["chr4"],
        "NC_000005.9":["chr5"],
        "NC_000005.10":["chr5"],
        "NC_000006.11":["chr6"],
        "NC_000006.12":["chr6"],
        "NC_000007.13":["chr7"],
        "NC_000007.14":["chr7"],
        "NC_000008.10":["chr8"],
        "NC_000008.11":["chr8"],
        "NC_000009.11":["chr9"],
        "NC_000009.12":["chr9"],
        "NC_000010.10":["chr10"],
        "NC_000010.11":["chr10"],
        "NC_000011.9":["chr11"],
        "NC_000011.10":["chr11"],
        "NC_000012.11":["chr12"],
        "NC_000012.12":["chr12"],
        "NC_000013.10":["chr13"],
        "NC_000013.11":["chr13"],
        "NC_000014.8":["chr14"],
        "NC_000014.9":["chr14"],
        "NC_000015.9":["chr15"],
        "NC_000015.10":["chr15"],
        "NC_000016.8":["chr16"],
        "NC_000016.9":["chr16"],
        "NC_000016.10":["chr16"],
        "NC_000017.10":["chr17"],
        "NC_000017.11":["chr17"],
        "NC_000018.9":["chr18"],
        "NC_000018.10":["chr18"],
        "NC_000019.9":["chr19"],
        "NC_000019.10":["chr19"],
        "NC_000020.10":["chr20"],
        "NC_000020.11":["chr20"],
        "NC_000021.8":["chr21"],
        "NC_000021.9":["chr21"],
        "NC_000022.10":["chr22"],
        "NC_000022.11":["chr22"],
        "NC_000023.9":["chr23"],
        "NC_000023.10":["chr23"],
        "NC_000023.11":["chr23"],
        "NC_000024.10":["chr24"],
        "NC_012920.1":["mitoc"]
                 }
    return chr[accessor]


def get_chromosome_accessors(id) -> List:
    """
    Maps chromosome identifiers to NC chromosome identifiers

    :param id:
    :return:
    """
    accessors = { "chr1": ["NC_000001.9", "NC_000001.10", "NC_000001.11"],
    "chr2": ["NC_000002.11", "NC_000002.12"],
    "chr3": [ "NC_000003.11", "NC_000003.12"],
    "chr4": [ "NC_000004.11", "NC_000004.12"],
    "chr5": [ "NC_000005.9", "NC_000005.10"],
    "chr6": [ "NC_000006.11", "NC_000006.12"],
    "chr7": [ "NC_000007.13", "NC_000007.14"],
    "chr8": [ "NC_000008.10", "NC_000008.11"],
    "chr9": ["NC_000009.11", "NC_000009.12"],
    "chr10": ["NC_000010.10", "NC_000010.11"],
    "chr11": ["NC_000011.9", "NC_000011.10"],
    "chr12": ["NC_000012.11", "NC_000012.12"],
    "chr13": ["NC_000013.10", "NC_000013.11"],
    "chr14": ["NC_000014.8", "NC_000014.9"],
    "chr15": ["NC_000015.9", "NC_000015.10"],
    "chr16": ["NC_000016.8", "NC_000016.9", "NC_000016.10"],
    "chr17": ["NC_000017.10", "NC_000017.11"],
    "chr18": ["NC_000018.9", "NC_000018.10"],
    "chr19": ["NC_000019.9", "NC_000019.10"],
    "chr20": ["NC_000020.10", "NC_000020.11"],
    "chr21": ["NC_000021.8", "NC_000021.9"],
    "chr22": ["NC_000022.10", "NC_000022.11"],
    "chr23": ["NC_000023.9", "NC_000023.10", "NC_000023.11"],
    "chr24": ["NC_000024.10"],
    "mitoc": ["NC_012920.1"]
                  }
    return accessors[id]


def generate_biomarker_frame_from_gene_name_str(gene_names_prot_change):
    """
    Generates a biomarker frame from a comma-separated list of gene names and protein change

    :param gene_names_prot_change:
    :return:
    """
    variant_str = gene_names_prot_change.split(",")
    gene_data = {}
    for var in variant_str:
        resp = split_gene_name(var)
        if resp:
            gene, variant_exchange = resp[0], resp[1]
            gene_data[var] = {}
            gene_data[var]["variant_daata"] = {
                "variant_exchange": variant_exchange,
                "gene": gene
            }
            gene_data[var][config.uta_adapter_srv_prefix] = {
                config.__FEATURE_VARIANT__: variant_exchange,
                config.__FEATURE_GENE__: gene
            }
        else:
            gene_data[var] = {}
    return gene_data


def split_gene_name(variant_str:str) -> (str, str):
    """
    Splits a tuple containing the gene name and the protein information of the form 'gene:protein'. Returns the gene nema and the variant exchange

    Parameters
    ----------
    variant_str

    Returns
    -------

    """
    if isinstance(variant_str,str):
        labels = variant_str.split(":")
        if len(labels)>1:
            return labels[0], labels[1]
        else:
            return None
    else:
        print("Error: Could not parse ",variant_str)


def generate_chromosome_labels(vcf_data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds chromosome labels to the chromosome column

    Parameters
    ----------
    vcf_data

    Returns
    -------

    """
    variant_pattern_str = "[0-9|X|Y|N]+"
    valid = re.compile(variant_pattern_str)
    for i in range(0, vcf_data.shape[0]):
        if valid.match(vcf_data.iloc[i,0]):
            #print("add chr label ",vcf_data.iloc[i,0])
            vcf_data.at[i,"chr"] = "chr" + str(vcf_data.iloc[i,:].loc["chr"])
        else:
            print("no match: ",vcf_data.iloc[i,0])
    return vcf_data


def get_chromosome_parts(id:str) -> re.Match:
    #id = id.replace(".","")
    #chr_pattern_str="(chr[0-9|X|Y|N]+):(g.|p.)?([0-9]+)([C|A|T|G|N]+)>([C|A|G|T|N]+)"
    chr_pattern_str = "(NC_[0-9]+.[0-9]+):(g.|p.)?([0-9]+)([C|A|T|G|N]+)>([C|A|G|T|N]+)"
    val = re.compile(chr_pattern_str)
    res= val.match(id)
    return res


def get_chromosome(id) -> str:
    parts = id.split(':')
    return parts[len(parts)-2]+ ":" + parts[len(parts)-1]


def split_gene_location(variant:str) -> List:
    variant_pattern_str = "(chr[0-9|X|Y|N]+):(g.|p.)?([0-9]+)([C|A|T|G|N]+)>([C|A|G|T|N]+)"
    valid = re.compile(variant_pattern_str)
    res = valid.match(variant)

    #print("split genes match ",variant)
    variant_elements = [None]*4
    variant_elements[0] = res.group(1)
    variant_elements[1] = res.group(3)
    variant_elements[2] = res.group(4)
    variant_elements[3] = res.group(5)

    return variant_elements


def generate_request_str_of_gene_names(
        annotated_data,
        gene=None,
        ve=None,
        input=None):

    #variant_list = [x for x in vcf[gene] + ":" + vcf[ve]]
    variant_list=[]

    # generate variant requests from gene names
    for key, val in annotated_data.items():
        if config.__FEATURE_GENE__ in val:
            variant_list.append(val[config.__FEATURE_GENE__] + ":" + val[config.__FEATURE_VARIANT__])

    variant_str = ','.join(variant_list)
    print(variant_str,":", variant_list)
    return variant_str, variant_list


def generate_variant_list_from_df(vcf, chr=None,pos=None,ref=None,var=None):
    vcf = vcf.astype('str')
    print("as str ",vcf)
    # VCF format: CHROM: vcf[0], POS: vcf[1], REF: vcf[2], VAR: vcf[3]
    #variant_list = [x for x in "chr" + vcf["chr"] + ":" + vcf["pos"] + vcf["ref"] + ">" + vcf["alt"]]
    #variant_list = [x for x in vcf["chr"] + ":" + vcf["pos"] + vcf["ref"] + ">" + vcf["alt"]]

    variant_list = [x for x in vcf[chr] + ":" + vcf[pos] + vcf[ref] + ">" + vcf[var]]

    #variant_list = []
    #for i in range(0,vcf.shape[0]):
    #    variant_list.append(vcf.iloc[i,0] +":"+ vcf.iloc[i,1] + vcf.iloc[i,3]+">"+ vcf.iloc[i,4])
    print("variant list: ", str(variant_list))
    variant_str = ','.join(variant_list)
    print(variant_str)
    return variant_str, variant_list


def remove_empty_variants(variant_list):
    new_list=[]
    for var in variant_list:
        if var != "0":
            new_list.append(var)
    return new_list


def generate_query_str_loftool(vcf: pd.DataFrame):
    vcf = vcf.astype('str')
    variant_list = [x for x in vcf["gene_name"]]
    #variant_list = remove_empty_variants(variant_list)
    if len(variant_list) > 0:
        variant_str = ','.join(variant_list)
        return variant_str, variant_list
    else:
        return None,None


def generate_query_list_vuspredict(vcf: pd.DataFrame):
    vcf = vcf.astype('str')
    variant_list = [x for x in "genesymbol="+vcf["gene_name"]+"&variant="+vcf["variant_exchange"]+"&genompos="+vcf["input_data"] ]
    variant_str = ','.join(variant_list)
    return variant_str, variant_list


def generate_query_str_metakb(vcf: pd.DataFrame):
    vcf = vcf.astype('str')
    variant_list = [x for x in vcf["gene_name"] + ":" + vcf["variant_exchange"] + ":cancer" + ":" + vcf["input_data"] ]
    variant_str = ','.join(variant_list)
    return variant_str, variant_list


def generate_queryids(vcf: pd.DataFrame, chr=None,pos=None,ref=None,var=None) -> pd.DataFrame:
    if config.query_id not in vcf.columns:
        vcf["q_id"] = [x for x in vcf[chr] + ":" + vcf[pos] + vcf[ref] + ">" + vcf[var]]
    return vcf


def get_variant_request_type(var):
    """
    Identifies the biomarker type of a text request. Possible request types are gene name, gene name and amino acid exchange,
    gene name and multiple letter amino acid exchange, genomic location and gene fusion

    :param var:
    :return:
    """
    # fusion, gene_name_aa_exchange, gene_name_aa_exchange_long, genomic_location, gene_name
    if not isinstance(var, str):
        return "undefined", None

    # Gene fusion
    if re.compile(gencode.exp_fusions).match(var):
        groups = re.compile(gencode.exp_fusions).match(var).groups()
        return "fusion", groups

    # SNV: Genomic location
    if re.compile(gencode.exp_genome_positions).match(var):
        groups = re.compile(gencode.exp_genome_positions).match(var).groups()
        return "genomic_location", groups
    if re.compile(gencode.exp_genome_positions_refseq).match(var):
        groups = re.compile(gencode.exp_genome_positions_refseq).match(var).groups()
        return "genomic_location_refseq", groups
    if re.compile(gencode.exp_genome_positions_nc).match(var):
        groups = re.compile(gencode.exp_genome_positions_nc).match(var).groups()
        return "genomic_location_nc", groups
    if re.compile(gencode.exp_genome_positions_nc_refseq).match(var):
        groups = re.compile(gencode.exp_genome_positions_nc_refseq).match(var).groups()
        return "genomic_location_nc_refseq", groups

    # SNV: Transcript
    if re.compile(gencode.exp_refseq_transcript_pt).match(var):
        groups = re.compile(gencode.exp_refseq_transcript_pt).match(var).groups()
        return "transcript_cdna", groups
    if re.compile(gencode.exp_refseq_transcript_gene).match(var):
        groups = re.compile(gencode.exp_refseq_transcript_gene).match(var).groups()
        return "refseq_transcript_gene", groups
    if re.compile(gencode.exp_refseq_protein).match(var):
        groups = re.compile(gencode.exp_refseq_protein).match(var).groups()
        return "refseq_protein", groups
    if re.compile(gencode.exp_ensembl_transcript).match(var):
        groups = re.compile(gencode.exp_ensembl_transcript).match(var).groups()
        return "ensembl_transcript", groups
    if re.compile(gencode.exp_ensembl_protein).match(var):
        groups = re.compile(gencode.exp_ensembl_protein).match(var).groups()
        return "ensembl_protein", groups
    if re.compile(gencode.exp_uniprot_accession_numbers).match(var):
        groups = re.compile(gencode.exp_uniprot_accession_numbers).match(var).groups()
        return "uniprot_accession", groups
    if re.compile(gencode.exp_uniprot_entry_names).match(var):
        groups = re.compile(gencode.exp_uniprot_entry_names).match(var).groups()
        return "uniprot_entry", groups

    # InDel: Genomic location
    if re.compile(gencode.exp_insertion).match(var):
        groups = re.compile(gencode.exp_insertion).match(var).groups()
        return "insertion", groups
    if re.compile(gencode.exp_insertion_ncbichrom).match(var):
        groups = re.compile(gencode.exp_insertion_ncbichrom).match(var).groups()
        return "insertion_nc", groups
    if re.compile(gencode.exp_insertion_long).match(var):
        groups = re.compile(gencode.exp_insertion_long).match(var).groups()
        return "insertion_long", groups
    if re.compile(gencode.exp_insertion_ncbichrom_long).match(var):
        groups = re.compile(gencode.exp_insertion_ncbichrom_long).match(var).groups()
        return "insertion_nc_long", groups

    if re.compile(gencode.exp_indel).match(var):
        groups = re.compile(gencode.exp_indel).match(var).groups()
        return "indel", groups
    if re.compile(gencode.exp_indel_ncbichrom).match(var):
        groups = re.compile(gencode.exp_indel_ncbichrom).match(var).groups()
        return "indel_nc", groups
    if re.compile(gencode.exp_indel_long).match(var):
        groups = re.compile(gencode.exp_indel_long).match(var).groups()
        return "indel_long", groups
    if re.compile(gencode.exp_indel_ncbichrom_long).match(var):
        groups = re.compile(gencode.exp_indel_ncbichrom_long).match(var).groups()
        return "indel_nc_long", groups

    if re.compile(gencode.exp_deletion).match(var):
        groups = re.compile(gencode.exp_deletion).match(var).groups()
        return "deletion", groups
    if re.compile(gencode.exp_deletion_ncbichrom).match(var):
        groups = re.compile(gencode.exp_deletion_ncbichrom).match(var).groups()
        return "deletion_nc", groups
    if re.compile(gencode.exp_deletion_long).match(var):
        groups = re.compile(gencode.exp_deletion_long).match(var).groups()
        return "deletion_long", groups
    if re.compile(gencode.exp_deletion_ncbichrom_long).match(var):
        groups = re.compile(gencode.exp_deletion_ncbichrom_long).match(var).groups()
        return "deletion_nc_long", groups

    # InDels: Transcript
    if re.compile(gencode.exp_refseq_transcript_del).match(var):
        groups = re.compile(gencode.exp_refseq_transcript_del).match(var).groups()
        return "del_transcript_cdna", groups
    if re.compile(gencode.exp_refseq_transcript_del_gene).match(var):
        groups = re.compile(gencode.exp_refseq_transcript_del_gene).match(var).groups()
        return "del_transcript_gene_cdna", groups
    if re.compile(gencode.exp_refseq_transcript_del_long).match(var):
        groups = re.compile(gencode.exp_refseq_transcript_del_long).match(var).groups()
        return "del_transcript_cdna_long", groups
    if re.compile(gencode.exp_refseq_transcript_del_gene_long).match(var):
        groups = re.compile(gencode.exp_refseq_transcript_del_gene_long).match(var).groups()
        return "del_transcript_gene_cdna_long", groups

    # SNV: Protein
    if re.compile(gencode.exp_gene_name_variant_exchange).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange).match(var).groups()
        return "gene_name_aa_exchange", groups
    else:
        pass

    if re.compile(gencode.exp_gene_name_variant_exchange_fs).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_fs).match(var).groups()
        return "gene_name_aa_exchange_fs", groups


    if re.compile(gencode.exp_gene_name_variant_exchange_fs_refseq).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_fs_refseq).match(var).groups()
        return "gene_name_aa_exchange_fs_refseq", groups

    #print("match: ",var)
    if re.compile(gencode.exp_gene_name_variant_exchange_long_fs_short).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_long_fs_short).match(var).groups()
        return "gene_name_aa_exchange_long_fs_short", groups

    if re.compile(gencode.exp_gene_name_variant_exchange_long_fs).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_long_fs).match(var).groups()
        return "gene_name_aa_exchange_long_fs", groups

    if re.compile(gencode.exp_gene_name_variant_exchange_long).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_long).match(var).groups()
        return "gene_name_aa_exchange_long", groups

    if re.compile(gencode.exp_gene_name_variant_exchange_refseq).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_refseq).match(var).groups()
        return "gene_name_aa_exchange_refseq", groups


    if re.compile(gencode.exp_gene_name_variant_exchange_long_fs_refseq).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_long_fs_refseq).match(var).groups()
        return "gene_name_aa_exchange_long_fs_refseq", groups

    if re.compile(gencode.exp_gene_name_variant_exchange_long_refseq).match(var):
        groups = re.compile(gencode.exp_gene_name_variant_exchange_long_refseq).match(var).groups()
        return "gene_name_aa_exchange_long_refseq", groups
    if re.compile(gencode.exp_gene_name).match(var):
        groups = re.compile(gencode.exp_gene_name).match(var).groups()
        return "gene_name", groups

    # CNV
    if re.compile(gencode.exp_cnv_del).match(var):
        groups = re.compile(gencode.exp_cnv_del).match(var).groups()
        return "cnv_del", groups
    elif re.compile(gencode.exp_cnv_dup).match(var):
        groups = re.compile(gencode.exp_cnv_dup).match(var).groups()
        return "cnv_dup", groups
    elif re.compile(gencode.exp_cnv_cnv).match(var):
        groups = re.compile(gencode.exp_cnv_cnv).match(var).groups()
        return "cnv_cnv", groups


    # Position only
    if re.compile(gencode.chrom_position).match(var):
        groups = re.compile(gencode.chrom_position).match(var).groups()
        return "chrom_position", groups
    else:
        return "unidentified", None

    return "unidentified", None

def identify_query_parameters(query, gene_name_q=None, genompos_q=None, add_refseq=False):
    """
    Identify requested variants in a search query and retrieve them either as gene names or as genome positions.
    Identifies whether a text query contains a gene name and variant exchange or a genome position
    Retrieves comma-separated lists of text input, gene names and variant exchange in the format GENE_NAME:VAR_EXCHANGE, and genome positions.
    Returns a list of gene names and variant exchange, a list of genome positions and a list of identified gene fusions

    :param query: Comma-separated string of biomarker identifiers
    :param gene_name_q:
    :param genompos_q:
    :return: Dictionaries for biomarkers separated by gene_names, snvs, indels, genome_positions and gene fusions
    :vartype query: str | list
    """
    if query is None:
        return {}, {}, {}, {}, {}

    if isinstance(query,str):
        query = query.replace(" ", "")
        variants = query.split(',')
    elif isinstance(query,list):
        variants = query
    elif isinstance(query,dict):
        variants = list(query.keys())
    else:
        return {}, {}, {}, {}, {}

    gene_names, genome_positions, fusions = [],[],[]
    snvs, indels, unidentified = [], [], []

    if variants is not None:
        for var in variants:

            if isinstance(query, dict):
                if "variant_data" in query[var]:
                    if "type" in query[var]["variant_data"]:
                        #print(query[var]["variant_data"]["type"])
                        if query[var]["variant_data"]["type"]=="insertion":
                            var = adagenes.tools.parse_indel_location(var, "insertion")
                            indels = indels + [var]
                        elif query[var]["variant_data"]["type"]=="deletion":
                            var = adagenes.tools.parse_indel_location(var, "deletion")
                            indels = indels + [var]
                        elif query[var]["variant_data"]["type"]=="unidentified":
                            unidentified = unidentified + [var]
                        else:
                            genome_positions = genome_positions + [var]
                        continue
            reg_genompos = "():()()>()"

            #genome_positions = genome_positions + get_genome_location(var)
            biomarker_type, groups = get_variant_request_type(var)
            #print("biomarker type(" + var + "): ",biomarker_type)

            # gene fusion
            if biomarker_type == "fusion":
                print("gene fusion match ",var)
                fusions = fusions + [ var ]
            elif biomarker_type == "gene_name_aa_exchange":
                # gene name, variant exchange
                print("Request match: Gene name, variant exchange ", var)
                snvs = snvs + [var]
            elif biomarker_type == "gene_name_aa_exchange_long":
                # gene name, variant exchange
                print("Request match: Gene name, variant exchange (long)", var)

                # Convert to single letter codes
                aa_groups = re.compile(gencode.exp_gene_name_variant_exchange_long).match(var).groups()
                #print(aa_groups)
                aa_exchange = aa_groups[2] + aa_groups[3] + aa_groups[4]
                aa_exchange_single_letter = gencode.convert_aa_exchange_to_single_letter_code(aa_exchange, add_refseq = add_refseq)
                var = aa_groups[0] + ":" + aa_exchange_single_letter

                snvs = snvs + [var]
            elif biomarker_type == "gene_name_aa_exchange_refseq":
                print("Request type: Gene name:(Reference sequence) protein change")
                aa_groups = re.compile(gencode.exp_gene_name_variant_exchange_refseq).match(var).groups()
                #aa_exchange = aa_groups(2)
                var = aa_groups[0] + ":" + aa_groups[3]
                print("new identifier: ",var)
                snvs = snvs + [var]
            elif biomarker_type == "gene_name_aa_exchange_long_refseq":
                print("Request type: Gene name:(Reference sequence) protein change (long)")
                aa_groups = re.compile(gencode.exp_gene_name_variant_exchange_long_refseq).match(var).groups()
                print(aa_groups)
                aa_exchange = aa_groups[2]
                #var = aa_groups[0] + ":" + aa_groups[2]
                aa_exchange_single_letter = gencode.convert_aa_exchange_to_single_letter_code(aa_exchange)
                var = aa_groups[0] + ":" + aa_exchange_single_letter
                print("new identifier: ",var)
                snvs = snvs + [var]
            elif biomarker_type == "genomic_location":
                # genomic location
                aa_groups = re.compile(gencode.exp_genome_positions).match(var).groups()
                ref = aa_groups[3]
                alt = aa_groups[4]
                if len(ref) != len(alt):
                    var = var.replace("CHR", "chr")
                    indels = indels + [var]
                else:
                    genome_positions = genome_positions + get_genome_location(var)
            elif biomarker_type == "genomic_location_refseq":
                aa_groups = re.compile(gencode.exp_genome_positions_refseq).match(var).groups()
                genpos = 'chr' + aa_groups[1] + ":" + aa_groups[3] + aa_groups[4] + ">" + aa_groups[5]
                if len(aa_groups[4]) != len(aa_groups[5]):
                    var = var.replace("CHR", "chr")
                    indels = indels + [var]
                else:
                    genome_positions = genome_positions + [genpos]
            elif biomarker_type == "genomic_location_nc":
                aa_groups = re.compile(gencode.exp_genome_positions_nc).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1] + aa_groups[2] + ">" + aa_groups[3]
                if len(aa_groups[2]) != len(aa_groups[3]):
                    var = var.replace("CHR", "chr")
                    indels = indels + [var]
                else:
                    genome_positions = genome_positions + [genpos]
            elif biomarker_type == "genomic_location_nc_refseq":
                aa_groups = re.compile(gencode.exp_genome_positions_nc_refseq).match(var).groups()
                chrom = get_chr(aa_groups[0])
                #print(chrom)
                genpos = chrom[0] + ":" + aa_groups[2] + aa_groups[3] + ">" + aa_groups[4]
                if len(aa_groups[3]) != len(aa_groups[4]):
                    var = var.replace("CHR","chr")
                    indels = indels + [var]
                else:
                    genome_positions = genome_positions + [genpos]
            elif biomarker_type == "gene_name":
                # gene name
                gene_names = gene_names + [var]
            elif biomarker_type == "deletion":
                indels = indels + [var]
            elif biomarker_type == "deletion_nc":
                aa_groups = re.compile(gencode.exp_deletion_ncbichrom).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                indels = indels + [genpos]
            elif biomarker_type == "deletion_nc_long":
                aa_groups = re.compile(gencode.exp_deletion_ncbichrom_long).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                indels = indels + [genpos]
            elif biomarker_type == "insertion":
                indels = indels + [var]
            elif biomarker_type == "insertion_nc":
                aa_groups = re.compile(gencode.exp_insertion_ncbichrom).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                indels = indels + [genpos]
            elif biomarker_type == "indel":
                indels = indels + [var]
            elif biomarker_type == "indel_nc":
                aa_groups = re.compile(gencode.exp_indel_ncbichrom).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                indels = indels + [genpos]
            elif biomarker_type == "indel_nc_long":
                aa_groups = re.compile(gencode.exp_indel_ncbichrom_long).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                indels = indels + [genpos]
            else:
                print("Could not match query: ",var)
                unidentified = unidentified + [var]

    #print("indels ",indels)
    return gene_names, snvs, indels, genome_positions, fusions, unidentified


def get_genome_location(var):
    """
    Test string for genome position

    :param var:
    :return:
    """
    genome_positions = []
    if re.compile(gencode.exp_genome_positions).match(var):
        genome_positions = genome_positions + [var]
        return genome_positions
    elif re.compile(gencode.exp_genome_positions_nc).match(var):
        groups = re.compile(gencode.exp_genome_positions_nc).match(var).groups()
        nc = groups[0]
        chrom = get_chr(nc)[0]
        print(groups)
        loc = chrom + ":" + groups[1] + groups[2] + ">" + groups[3]

        genome_positions = genome_positions + [loc]
        return genome_positions

    return []
