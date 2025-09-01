import re, copy
import traceback

import adagenes
from adagenes.conf import read_config as config
import adagenes.tools.hgvs_re as gencode
from adagenes.tools.preprocessing import get_variant_request_type, get_genome_location, get_chr
import adagenes.tools.parse_genomic_data
import adagenes.tools.frameshift


def get_ins_pos2(pos, ref, alt):
    pos2 = int(pos) + len(alt) -1
    return pos2

def get_del_pos2(pos, ref, alt):
    pos2 = int(pos) + len(ref) -1
    return pos2

def normalize_variant_request(request, target):
    """
    Normalizes a text-based request according to the HGVS notation into a target notation on DNA, transcript or protein
    level.
    Example: A request on protein level, characterized by HUGO gene symbol and amino acid exchange "BRAF:V600E",
    can be converted

    :param request:
    :param target:
    :return:
    """
    normalized_request = ""

    variant_type = get_variant_request_type(request)

    return normalized_request


def identify_biomarkers(bframe, genome_version=None):
    """
    Identify requested variants in a search query and retrieve them either as gene names or as genome positions.
    Identifies whether a text query contains a gene name and variant exchange or a genome position
    Retrieves comma-separated lists of text input, gene names and variant exchange in the format GENE_NAME:VAR_EXCHANGE, and genome positions.
    Returns a list of gene names and variant exchange, a list of genome positions and a list of identified gene fusions

    :param bframe
    :return: Dictionaries for biomarkers separated by gene_names, snvs, indels, genome_positions and gene fusions
    :vartype query: str | list
    """
    bframe_data_new = {}
    for var in bframe.data.keys():

            biomarker_type, groups = get_variant_request_type(var)
            #print("biotype ",biomarker_type)

            # gene fusion
            if biomarker_type == "fusion":
                #print("gene fusion match ",var)
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "g"
                bframe_data_new[var]["mutation_type"] = "fusion"
                bframe_data_new[var]["mdesc"] = biomarker_type
            # protein identifiers
            elif biomarker_type == "gene_name_aa_exchange":
                # gene name, variant exchange
                var_new = adagenes.normalize_protein_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "p"
                bframe_data_new[var_new]["mutation_type"] = "snv"
                bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                try:
                    alt = groups[4]
                    if alt == "*":
                        bframe_data_new[var_new]["mutation_type_detail"] = "Nonsense_Mutation"
                    else:
                        bframe_data_new[var_new]["mutation_type_detail"] = "Missense_Mutation"
                except:
                    print(traceback.format_exc())
                bframe_data_new[var_new]["mdesc"] = biomarker_type
            elif biomarker_type == "gene_name_aa_exchange_long_fs_refseq":
                # gene name, variant exchange
                var_new = adagenes.normalize_protein_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "p"
                bframe_data_new[var_new]["mutation_type"] = "snv"
                bframe_data_new[var_new]["mutation_type_desc"] = "SNP"



                bframe_data_new[var_new]["mdesc"] = biomarker_type
            elif biomarker_type == "gene_name_aa_exchange_long":
                # gene name, variant exchange
                var_new = adagenes.normalize_protein_identifier(var, add_refseq=False, target="one-letter")
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "p"
                bframe_data_new[var_new]["mutation_type"] = "snv"
                bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
            elif biomarker_type == "gene_name_aa_exchange_refseq":
                var_new = adagenes.normalize_protein_identifier(var, add_refseq=False, target="one-letter")
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "p"
                bframe_data_new[var_new]["mutation_type"] = "snv"
                bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
            elif biomarker_type == "gene_name_aa_exchange_long_refseq":
                var_new = adagenes.normalize_protein_identifier(var, add_refseq=False, target="one-letter")
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "p"
                bframe_data_new[var_new]["mutation_type"] = "snv"
                bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
            # genome identifiers
            elif biomarker_type == "genomic_location":
                var_new = var.replace("CHR", "chr")
                var_new = adagenes.normalize_dna_identifier(var_new, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                aa_groups = re.compile(gencode.exp_genome_positions).match(var).groups()
                pos = aa_groups[2]
                ref = aa_groups[3]
                alt = aa_groups[4]
                if len(ref) != len(alt):
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "indel"
                    bframe_data_new[var_new]["orig_id"] = var

                    pos2 = None
                    if len(ref) > len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                        type_suf = "Del"
                        is_frameshift = adagenes.tools.frameshift.is_frameshift_del(var)
                        pos2 = get_del_pos2(pos, ref, alt)
                    elif len(ref) < len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "INS"
                        type_suf = "Ins"
                        is_frameshift = adagenes.tools.frameshift.is_frameshift_ins(var)
                        pos2 = get_ins_pos2(pos, ref, alt)

                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if pos2 is not None:
                        bframe_data_new[var_new]["variant_data"]["POS2"] = pos2

                    bframe_data_new[var_new]["frameshift"] = str(is_frameshift)
                    if is_frameshift == "frameshift":
                        bframe_data_new[var_new]["mutation_type_detail"] = "Frame_Shift_"+type_suf
                    else:
                        bframe_data_new[var_new]["mutation_type_detail"] = "In_Frame_"+type_suf
                else:
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "snv"
                    bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}

                    try:
                        if alt == "*":
                            bframe_data_new[var_new]["mutation_type_detail"] = "Nonsense_Mutation"
                        else:
                            bframe_data_new[var_new]["mutation_type_detail"] = "Missense_Mutation"
                    except:
                        print(traceback.format_exc())

                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if genome_version is not None:
                        bframe_data_new[var_new]["variant_data"]["POS_"+genome_version] = aa_groups[2]
            elif biomarker_type == "genomic_location_refseq":
                var = var.replace("CHR", "chr")
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                aa_groups = re.compile(gencode.exp_genome_positions_refseq).match(var_new).groups()
                pos = aa_groups[2]
                ref = aa_groups[4]
                alt = aa_groups[5]
                pos2 = None
                if len(aa_groups[4]) != len(aa_groups[5]):
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "indel"
                    bframe_data_new[var_new]["orig_id"] = var


                    if len(ref) > len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                        pos2 = get_del_pos2(pos, ref, alt)
                    elif len(ref) < len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "INS"
                        pos2 = get_ins_pos2(pos, ref, alt)

                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if pos2 is not None:
                        bframe_data_new[var_new]["variant_data"]["POS2"] = pos2
                else:
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "snv"
                    bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if pos2 is not None:
                        bframe_data_new[var_new]["variant_data"]["POS2"] = pos2
                    if genome_version is not None:
                        bframe_data_new[var_new]["variant_data"]["POS_"+genome_version] = aa_groups[2]
            elif biomarker_type == "genomic_location_nc":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                aa_groups = re.compile(gencode.exp_genome_positions_nc).match(var).groups()
                ref = aa_groups[4]
                alt = aa_groups[5]
                if len(aa_groups[2]) != len(aa_groups[3]):
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "indel"
                    bframe_data_new[var_new]["orig_id"] = var

                    if len(ref) > len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                    elif len(ref) < len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "INS"

                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if pos2 is not None:
                        bframe_data_new[var_new]["variant_data"]["POS2"] = pos2
                else:
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "snv"
                    bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if pos2 is not None:
                        bframe_data_new[var_new]["variant_data"]["POS2"] = pos2
                    if genome_version is not None:
                        bframe_data_new[var_new]["variant_data"]["POS_"+genome_version] = aa_groups[2]
            elif biomarker_type == "genomic_location_nc_refseq":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                aa_groups = re.compile(gencode.exp_genome_positions_nc_refseq).match(var).groups()
                pos = aa_groups[2]
                ref = aa_groups[4]
                alt = aa_groups[5]
                if len(aa_groups[3]) != len(aa_groups[4]):
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "indel"
                    bframe_data_new[var_new]["orig_id"] = var
                    pos2 = None

                    if len(ref) > len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                        pos2 = get_del_pos2(pos,ref,alt)
                    elif len(ref) < len(alt):
                        bframe_data_new[var_new]["mutation_type_desc"] = "INS"
                        pos2 = get_ins_pos2(pos,ref,alt)

                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if pos2 is not None:
                        bframe_data_new[var_new]["variant_data"]["POS2"] = pos2
                else:
                    bframe_data_new[var_new]["type"] = "g"
                    bframe_data_new[var_new]["mutation_type"] = "snv"
                    bframe_data_new[var_new]["mutation_type_desc"] = "SNP"
                    bframe_data_new[var_new]["mdesc"] = biomarker_type
                    if "variant_data" not in bframe_data_new[var_new]:
                        bframe_data_new[var_new]["variant_data"] = {}
                    bframe_data_new[var_new]["variant_data"]["CHROM"] = aa_groups[1]
                    bframe_data_new[var_new]["variant_data"]["POS"] = aa_groups[2]
                    bframe_data_new[var_new]["variant_data"]["REF"] = ref
                    bframe_data_new[var_new]["variant_data"]["ALT"] = alt
                    if genome_version is not None:
                        bframe_data_new[var_new]["variant_data"]["POS_"+genome_version] = aa_groups[2]
            elif biomarker_type == "refseq_protein":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "p"
                bframe_data_new[var]["mutation_type"] = "gene"

                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "ensembl_transcript":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "gene"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "ensembl_protein":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "p"
                bframe_data_new[var]["mutation_type"] = "gene"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "gene_name":
                # gene name
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "g_name"
                bframe_data_new[var]["mutation_type"] = "gene"
                bframe_data_new[var]["mdesc"] = biomarker_type
            # InDels
            elif biomarker_type == "deletion":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                bframe_data_new[var_new]["orig_id"] = var

                is_frameshift = adagenes.tools.frameshift.is_frameshift_del(var)
                bframe_data_new[var_new]["frameshift"] = str(is_frameshift)
                if is_frameshift == "frameshift":
                    bframe_data_new[var_new]["mutation_type_detail"] = "Frame_Shift_Del"
                else:
                    bframe_data_new[var_new]["mutation_type_detail"] = "In_Frame_Del"

                bframe_data_new[var_new]["mdesc"] = biomarker_type


                var, data = adagenes.tools.parse_genomic_data.parse_variant_elements(var)
                if "variant_data" not in bframe_data_new[var_new].keys():
                    bframe_data_new[var_new]["variant_data"] = {}
                bframe_data_new[var_new]["variant_data"]["CHROM"] = data["CHROM"]
                bframe_data_new[var_new]["variant_data"]["POS"] = data["POS"]
                bframe_data_new[var_new]["variant_data"]["POS_" + str(genome_version)] = data["POS"]
                bframe_data_new[var_new]["variant_data"]["POS2_" + str(genome_version)] = data["POS2"]
                #bframe_data_new[var_new]["variant_data"]["ALT"] = data["ALT"]

            elif biomarker_type == "deletion_nc":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                aa_groups = re.compile(gencode.exp_deletion_ncbichrom).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                bframe_data_new[var_new]["orig_id"] = var
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["frameshift"] = adagenes.tools.frameshift.is_frameshift_del(var)
                if genome_version is not None:
                    bframe_data_new[var_new]["variant_data"]["POS_" + genome_version] = aa_groups[2]
            elif biomarker_type == "deletion_nc_long":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                aa_groups = re.compile(gencode.exp_deletion_ncbichrom_long).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mutation_type_desc"] = "DEL"
                bframe_data_new[var_new]["orig_id"] = var
                bframe_data_new[var_new]["mdesc"] = biomarker_type
            elif biomarker_type == "insertion":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                #var_new = var
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mutation_type_desc"] = "INS"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["orig_id"] = var

                is_frameshift = adagenes.tools.frameshift.is_frameshift_ins(var)
                bframe_data_new[var_new]["frameshift"] = str(is_frameshift)
                if is_frameshift == "frameshift":
                    bframe_data_new[var_new]["mutation_type_detail"] = "Frame_Shift_Ins"
                else:
                    bframe_data_new[var_new]["mutation_type_detail"] = "In_Frame_Ins"

                var, data = adagenes.tools.parse_genomic_data.parse_variant_elements(var)
                if "variant_data" not in bframe_data_new[var_new].keys():
                    bframe_data_new[var_new]["variant_data"] = {}
                bframe_data_new[var_new]["variant_data"]["CHROM"] = data["CHROM"]
                bframe_data_new[var_new]["variant_data"]["POS"] = data["POS"]
                bframe_data_new[var_new]["variant_data"]["POS2"] = data["POS2"]
                bframe_data_new[var_new]["variant_data"]["POS_" + str(genome_version)] = data["POS"]
                bframe_data_new[var_new]["variant_data"]["POS2_" + str(genome_version)] = data["POS2"]
                #bframe_data_new[var_new]["variant_data"]["ALT"] = data["ALT"]

            elif biomarker_type == "insertion_nc":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                aa_groups = re.compile(gencode.exp_insertion_ncbichrom).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mutation_type_desc"] = "INS"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["orig_id"] = var
                bframe_data_new[var_new]["frameshift"] = adagenes.tools.frameshift.is_frameshift_ins(var)
            elif biomarker_type == "insertion_long":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                aa_groups = re.compile(gencode.exp_insertion_long).match(var).groups()
                chrom = aa_groups[0]
                genpos = chrom[0] + ":" + aa_groups[1]
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mutation_type_desc"] = "INS"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["orig_id"] = var
            elif biomarker_type == "indel":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["orig_id"] = var
            elif biomarker_type == "indel_nc":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                aa_groups = re.compile(gencode.exp_indel_ncbichrom).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["orig_id"] = var
            elif biomarker_type == "indel_nc_long":
                var_new = adagenes.normalize_dna_identifier(var, add_refseq=False)
                aa_groups = re.compile(gencode.exp_indel_ncbichrom_long).match(var).groups()
                chrom = get_chr(aa_groups[0])
                genpos = chrom[0] + ":" + aa_groups[1]
                bframe_data_new[var_new] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var_new]["type"] = "g"
                bframe_data_new[var_new]["mutation_type"] = "indel"
                bframe_data_new[var_new]["mdesc"] = biomarker_type
                bframe_data_new[var_new]["orig_id"] = var
            elif biomarker_type == "refseq_transcript":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "gene"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "refseq_transcript_gene":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "gene"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "del_transcript_cdna":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "indel"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "del_transcript_gene_cdna":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "indel"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "del_transcript_cdna_long":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "indel"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "del_transcript_gene_cdna_long":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "r"
                bframe_data_new[var]["mutation_type"] = "indel"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "transcript_cdna":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "c"
                bframe_data_new[var]["mutation_type"] = "snv"
                bframe_data_new[var]["mdesc"] = biomarker_type
            elif biomarker_type == "cnv_del" or biomarker_type == "cnv_dup" or biomarker_type == "cnv_cnv":
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "g"
                bframe_data_new[var]["mutation_type"] = "cnv"
                bframe_data_new[var]["mdesc"] = biomarker_type
                if "variant_data" not in bframe_data_new[var]:
                    bframe_data_new[var]["variant_data"] = {}
                if "info_features" in bframe.data[var]:
                    if "END" in bframe.data[var]["info_features"]:
                        bframe_data_new[var]["variant_data"]["POS2"] = bframe.data[var]["info_features"]["END"]
            else:
                #print("Could not match query: ",var)
                bframe_data_new[var] = copy.deepcopy(bframe.data[var])
                bframe_data_new[var]["type"] = "unidentified"
                bframe_data_new[var]["mutation_type"] = "unidentified"
                bframe_data_new[var]["mdesc"] = biomarker_type
                if "variant_data" not in bframe_data_new[var]:
                    bframe_data_new[var]["variant_data"] = {}
                if "info_features" in bframe.data[var]:
                    if "END" in bframe.data[var]["info_features"]:
                        bframe_data_new[var]["variant_data"]["POS2"] = bframe.data[var]["info_features"]["END"]

    bframe.data = bframe_data_new
    return bframe
