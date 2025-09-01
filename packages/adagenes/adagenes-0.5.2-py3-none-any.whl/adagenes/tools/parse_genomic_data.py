import re, logging, traceback
import pandas as pd
from adagenes.conf import read_config as config
import adagenes as ag
import adagenes.tools.hgvs_re as gencode

def generate_qid_list_from_other_reference_genome(vcf_lines):
    """
    Generates request if the source file is not hg38: Looks for hg38 annotations and uses them if available to
    query the annotation modules

    :param vcf_lines:
    :return:
    """
    qid_list_hg38 = []
    qid_list_dc = {}

    for var in vcf_lines.keys():
        #print("parse variants ",vcf_lines[var])
        mtype, data = parse_variant_elements(var)
        #print("data ",data," orig ",vcf_lines[var])
        #print(mtype,", ",data)
        #print(vcf_lines[var])
        pos_found=False

        pos_found=False
        if "variant_data" in vcf_lines[var].keys():
            if "POS_hg38" in vcf_lines[var]["variant_data"]:
                try:
                    if (mtype == "genomic_location") or (mtype == "genomic_location_refseq"):
                        chr = data["CHROM"]
                        pos = data["POS"]
                        ref = data["REF"]
                        alt = data["ALT"]
                        qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"])  + ref + ">" + alt
                        pos_found = True
                    elif (mtype == "insertion") or (mtype=="deletion"):
                        chr = data["CHROM"]
                        pos = data["POS"]
                        pos2 = data["POS2"]
                        alt = data["ALT"]
                        #if pos2 != "":
                        #    qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                        #else:
                        qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                        pos_found = True
                    elif (mtype == "insertion_long") or (mtype=="deletion_long"):
                        chr = data["CHROM"]
                        pos = data["POS"]
                        pos2 = data["POS2"]
                        alt = data["ALT"]
                        #if pos2 != "":
                        #    qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                        #else:
                        qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                        pos_found = True
                    else:
                        #qid_hg38 = data["POS"]
                        #qid_hg38 = var
                        #pos_found = False
                        continue
                    #print(" add ",var)
                    if pos_found is True:
                        qid_list_dc[qid_hg38] = var
                        qid_list_hg38.append(qid_hg38)
                        pos_found = True
                except:
                    print(traceback.format_exc())
        if (pos_found is False) and ("info_features" in vcf_lines[var].keys()):
            if "POS_hg38" in vcf_lines[var]["info_features"]:
                try:
                    if (mtype == "genomic_location") or (mtype == "genomic_location_refseq"):
                        chr = data["CHROM"]
                        pos = data["POS"]
                        ref = data["REF"]
                        alt = data["ALT"]
                        qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["info_features"]["POS_hg38"])  + ref + ">" + alt
                        pos_found = True
                    elif (mtype == "insertion") or (mtype=="deletion"):
                        chr = data["CHROM"]
                        pos = data["POS"]
                        pos2 = data["POS2"]
                        alt = data["ALT"]
                        #if pos2 != "":
                        #    qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                        #else:
                        qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                        pos_found = True
                    if pos_found is True:
                        qid_list_dc[qid_hg38] = var
                        qid_list_hg38.append(qid_hg38)
                        pos_found = True
                except:
                    print(traceback.format_exc())
        if pos_found is False and "POS_hg38" in vcf_lines[var].keys():
            #print("PARSE POS")
            if (mtype == "genomic_location") or (mtype == "genomic_location_refseq"):
                chr = data["CHROM"]
                pos = data["POS"]
                ref = data["REF"]
                alt = data["ALT"]
                qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["POS_hg38"]) + ref + ">" + alt
                pos_found = True
            elif (mtype == "insertion") or (mtype == "deletion"):
                chr = data["CHROM"]
                pos = data["POS"]
                pos2 = data["POS2"]
                alt = data["ALT"]
                # if pos2 != "":
                #    qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                # else:
                qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["POS_hg38"]) + "ins" + alt
                pos_found = True
            elif (mtype == "insertion_long") or (mtype == "deletion_long"):
                chr = data["CHROM"]
                pos = data["POS"]
                pos2 = data["POS2"]
                alt = data["ALT"]
                # if pos2 != "":
                #    qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["variant_data"]["POS_hg38"]) + "ins" + alt
                # else:
                qid_hg38 = "chr" + chr + ":" + str(vcf_lines[var]["POS_hg38"]) + "ins" + alt
                pos_found = True
            else:
                continue
                #qid_hg38 = var
            #print(" add ",var,": ",qid_hg38)
            if pos_found is True:
                qid_list_dc[qid_hg38] = var
                qid_list_hg38.append(qid_hg38)
                pos_found = True
        if pos_found is False:
            #qid_list_dc[var] = var
            #qid_list_hg38.append(var)
            pass
    #print("generated list ",qid_list_hg38,": ",qid_list_dc)
    return qid_list_dc, qid_list_hg38


def parse_variant_elements(var):
    biomarker_type, elements = ag.get_variant_request_type(var)
    #print("recognized ",biomarker_type, elements)
    if (biomarker_type == "genomic_location") or (biomarker_type == "genomic_location_refseq"):
        chrom, refseq, pos, ref, alt = ag.parse_genome_position(var)
        data = {}
        data["CHROM"] = chrom
        data["POS"] = pos
        data["REF"] = ref
        data["ALT"] = alt
        data["type_desc"] = biomarker_type
        return biomarker_type, data
    elif (biomarker_type == "insertion") or (biomarker_type=="deletion"):
        chr, mtype, pos, pos2, alt = ag.parse_indel(var)
        data = {}
        data["CHROM"] = chr
        data["POS"] = pos
        data["POS2" ] = pos2
        data["ALT"] = alt
        data["type_desc"] = biomarker_type
        return biomarker_type, data
    elif (biomarker_type == "insertion_long") or (biomarker_type=="deletion_long"):
        chr, mtype, pos, pos2, alt = ag.parse_indel(var)
        data = {}
        data["CHROM"] = chr
        data["POS"] = pos
        data["POS2" ] = pos2
        data["ALT"] = alt
        data["type_desc"] = biomarker_type
        return biomarker_type, data
    else:
        return None, None


def parse_variant_identifier_gdesc(chr, gdesc, genome_version):
    """

    :param chr:
    :param gdesc:
    :param genome_version:
    :return:
    """
    biomarker_type, elements = ag.get_variant_request_type("chr"+chr + ":" + gdesc)
    print("biomarker type ",chr,",",gdesc,": ",biomarker_type,": ",elements)
    if "chr" in chr:
        chr = chr.replace("chr", "")
    # SNV
    if (biomarker_type == "genomic_location") or (biomarker_type == "genomic_location_refseq"):
        key = 'chr' + str(chr) + ':' + str(gdesc)
        chrom, refseq, pos, ref, alt = ag.parse_genome_position(key)
        data = {}
        data["CHROM"] = chr
        data["POS"] = pos
        data["POS_" + genome_version] = pos
        data["REF"] = ref
        data["ALT"] = alt
        data["type_desc"] = biomarker_type
        return key, data
    # InDel
    elif (biomarker_type == "insertion_long"):
        key = "chr" + str(chr) + ":" + str(gdesc)
        chrom, refseq, pos1, pos2, alt = ag.parse_indel(key)
        data = {}
        data["CHROM"] = chr
        data["type_desc"] = biomarker_type
        return key, data
    return None, {}



def generate_dictionary(list1, list2):
    """
    Generates a dictionary from two lists, where the first list respresents the keys and the second list represents the
    values of the dictionary

    :param list1:
    :param list2:
    :return:
    """
    dc = {}
    for i, el in enumerate(list1):
        dc[el] = list2[i]
    return dc


def generate_liftover_genompos(variant,liftover_pos):
    chrom, ref_seq, pos, ref, alt = parse_genome_position(variant)
    liftover_genompos = "chr" + str(chrom) + ":" + str(liftover_pos) + ref+ ">" + alt
    return liftover_genompos


def generate_liftover_qid_list(variant_list, liftover_position_list):
    liftover_dc = {}
    variant_dc = {}

    for i, variant in enumerate(variant_list):
        liftover_genompos = generate_liftover_genompos(variant, liftover_position_list[i])
        variant_dc[variant] = liftover_genompos
        liftover_dc[liftover_genompos] = variant

    return variant_dc, liftover_dc


def parse_variant_exchange(variant_exchange):
    """
    Returns the reference amino acid, the position, and the alternate amino acid of an amino acid exchange at protein level

    E.g. 'V600E' -> 'V','600','E'

    :param variant_exchange:
    :return:
    """
    if re.compile(gencode.variant_exchange_long_pt_ext).match(variant_exchange):
        p = re.compile(gencode.variant_exchange_long_pt_ext).match(variant_exchange).groups()
        aaref = p[1]
        pos = p[2]
        aaalt = p[3]
        return aaref, pos, aaalt
    else:
        return None, None, None


def parse_fusion(genompos):
    """

    :param genompos:
    :return:
    """
    rsregex = r'(chr\d+|chr[XY]):(\d+)-(chr\d+|chr[XY]):(\d+)'
    if re.compile(rsregex).match(genompos):
        p = re.compile(rsregex).match(genompos).groups()
        chr0 = p[0]
        pos0 = p[1]
        chr1 = p[3]
        pos1 = p[4]
        return chr0, pos0, chr1, pos1

def parse_indel(genompos):
    """

    :param genompos:
    :return:
    """
    rsregex = r'([A-Za-z0-9]+):(?:g\.)?(\d+)(?:_(\d+))?(delins|del|ins)?([A-Z]*)?'
    if re.compile(rsregex).match(genompos):
        p = re.compile(rsregex).match(genompos).groups()
        chr = p[0]
        pos = p[1]
        #ref_seq = p[2]
        pos2 = p[2]
        mtype = p[3]
        alt = p[4]
        if "chr" in chr:
            chr = chr.replace("chr","")
        return chr, mtype, pos, pos2, alt
    else:
        return None, None, None, None, None


def parse_transcript_cdna(genompos):
    """
    Parses and returns the components of a transcript and cDNA identifier.
    Returns the chromosome, reference sequence, position,
    reference allele and alternate allele

    :param genompos:
    :return:
    """
    rsregex = gencode.exp_refseq_transcript_pt
    if re.compile(rsregex).match(genompos):
        p = re.compile(rsregex).match(genompos).groups()
        #print("groups ",p)
        nm = p[0]
        pos = p[2]
        ref_seq = p[1]
        ref = p[3]
        alt = p[4]

        return nm, ref_seq, pos, ref, alt
    else:
        print("no match for genomic location: ",genompos)
    print("Error: Could not parse ",genompos)
    return None, None, None, None, None


def parse_genome_position(genompos):
    """
    Parses and returns the components of a genomic location. Returns the chromosome, reference sequence, position,
    reference allele and alternate allele

    :param genompos:
    :return:
    """
    rsregex = "(NC_[0]+)([1-9|X|Y][0-9|X|Y]?).([0-9]+):(g.|c.)?([0-9]+)([A|C|G|T|-]+)>([A|C|G|T|-]+)"
    if re.compile(rsregex).match(genompos):
        p = re.compile(rsregex).match(genompos).groups()
        chr = p[1]
        pos = p[4]
        ref_seq = p[3]
        ref = p[5]
        alt = p[6]
        return chr, ref_seq, pos, ref, alt
    rsregex = "(CHR|chr)([0-9|X|Y|MT]+):(g.|c.)?([0-9]+)([A|C|G|T|-]+)>([A|C|G|T|-]+)"
    if re.compile(rsregex).match(genompos):
        p = re.compile(rsregex).match(genompos).groups()
        chr = p[1]
        pos = p[3]
        ref_seq = p[2]
        ref = p[4]
        alt = p[5]
        return chr, ref_seq, pos, ref, alt

    print("Error: Could not parse ",genompos)
    return None, None, None, None, None


def generate_variant_data_section(variant_data):
    """
    Generates the variant data section that contains the genomic location data  for a biomarker data frame

    :param variant_data:
    :return:
    """

    for var in variant_data:
        if "variant_data" not in variant_data[var]:
            variant_data[var]["variant_data"] = {}
            try:
                chrom, ref_seq, pos, ref, alt = parse_genome_position(var)
                variant_data[var]["variant_data"]["CHROM"] = chrom
                variant_data[var]["variant_data"]["POS"] = pos
                variant_data[var]["variant_data"]["REF"] = ref
                variant_data[var]["variant_data"]["ALT"] = alt
                variant_data[var]["variant_data"]["info_features"] = ""
            except:
                print("Could not parse genomic location: ",var)
                variant_data[var]["variant_data"]["CHROM"] = ""
                variant_data[var]["variant_data"]["POS"] = ""
                variant_data[var]["variant_data"]["REF"] = ""
                variant_data[var]["variant_data"]["ALT"] = ""
                variant_data[var]["variant_data"]["info_features"] = ""

    return variant_data


def get_clinical_evidence_data(variant_data, data_section="merged_evidence_data") -> pd.DataFrame:
    """

    :param variant_data:
    :return:
    """

    chrom = []
    pos_hg19 = []
    pos_hg38 = []
    ref = []
    alt = []
    drugs = []
    drug_classes = []
    evidence_levels = []
    response_types = []
    associated_biomarkers = []
    match_types = []
    cancer_types = []
    citation_ids = []
    sources = []

    for qid in variant_data.keys():
        if config.onkopus_aggregator_srv_prefix in variant_data[qid]:
            for match_type in config.match_types:
                if match_type in variant_data[qid][config.onkopus_aggregator_srv_prefix][data_section]:
                    for result in variant_data[qid][config.onkopus_aggregator_srv_prefix][data_section][match_type]:

                        include_result = True

                        if "evidence_level_onkopus"in result:
                            evidence_level = result["evidence_level_onkopus"]
                        else:
                            evidence_level = ""

                        if include_result:
                            chrom.append(variant_data[qid]["variant_data"]["CHROM"])
                            pos_hg19.append(variant_data[qid]["variant_data"]["POS_hg19"])
                            pos_hg38.append(variant_data[qid]["variant_data"]["POS_hg38"])
                            ref.append(variant_data[qid]["variant_data"]["REF"])
                            alt.append(variant_data[qid]["variant_data"]["ALT"])

                            drugs.append(result["drugs"])
                            drug_classes.append(result["drugs"])
                            evidence_levels.append(evidence_level)
                            response_types.append(result["response"])
                            associated_biomarkers.append(result["biomarker"])
                            match_types.append(match_type)
                            cancer_types.append(result["disease"])
                            citation_ids.append(result["citation_id"])
                            sources.append(result["source"])

    treatment_data = {
        'CHROM': chrom,
        'POS_HG19': pos_hg19,
        'POS_HG38': pos_hg38,
        'REF': ref,
        'ALT': alt,
        'Drugs': drugs,
        'Drug Class': drug_classes,
        'Evidence Level': evidence_levels,
        'Response Type': response_types,
        'Associated Biomarker': associated_biomarkers,
        'Match Type': match_types,
        'Tumor Type': cancer_types,
        'Citation ID': citation_ids,
        'Source': sources
        }

    df = pd.DataFrame(data=treatment_data)
    return df