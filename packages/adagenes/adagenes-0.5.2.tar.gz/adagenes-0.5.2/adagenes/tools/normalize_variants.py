import re
import adagenes as ag
import adagenes.tools.hgvs_re as hgvs_re
import adagenes.tools


def normalize_identifiers(json_obj, add_refseq = False):
    """

    :param json_obj:
    :param add_refseq:
    :return:
    """
    new_json_obj = {}
    for var in json_obj.keys():
        new_var = normalize_identifier(var, json_obj[var], add_refseq=add_refseq)
        new_json_obj[new_var] = json_obj[var]
        new_json_obj[new_var]["orig_identifier"] = var
    return new_json_obj


def normalize_identifier(qid, json_obj, add_refseq=False):
    """

    :param qid:
    :param json_obj
    :param add_refseq:
    :return:
    """
    #print("normalize ",qid,":", json_obj)
    if "type" in json_obj:
        if json_obj["type"] == "g":
            new_qid = normalize_dna_identifier(qid,add_refseq=add_refseq)
            #print("return normalized ",new_qid)
            return new_qid
    #print("could not normalize ",qid)
    return qid


def normalize_protein_identifier(protein, target="one-letter", add_refseq=True):
    """

    :param protein:
    :return:
    """
    protein_normalized = ""

    protein = protein.replace("(", "")
    protein = protein.replace(")", "")

    request_type, groups = adagenes.get_variant_request_type(protein)

    refseq = ""
    if add_refseq is True:
        refseq = "p."

    if request_type == "gene_name_aa_exchange":
        if target == "one-letter":
            gene = groups[0]
            aaex = groups[2] + groups[3] + groups[4]
            protein_normalized = gene + ":" + refseq + aaex
        elif target == "3-letter":
            protein_normalized = convert_protein_to_multiple_letter_code(protein,add_refseq=add_refseq)
    elif request_type == "gene_name_aa_exchange_long":
        if target == "one-letter":
            print("convert protein ",protein)
            protein_normalized = convert_protein_to_single_letter_code(protein, add_refseq=add_refseq)
        elif target == "3-letter":
            gene = groups[0]
            #aaex = groups[2]
            aaex = groups[2] + groups[3] + groups[4]
            protein_normalized = gene + ":" + refseq + aaex
    elif request_type == "gene_name_aa_exchange_refseq":
        if target == "one-letter":
            if add_refseq is True:
                protein_normalized = protein
            else:
                #print("GROUPS ",groups)
                gene = groups[0]
                #aaex = groups[2]
                aaex = groups[3] + groups[4] + groups[5]
                protein_normalized = gene + ":" + aaex
        else:
            protein_normalized = convert_protein_to_multiple_letter_code(protein,add_refseq=add_refseq)
    elif request_type == "gene_name_aa_exchange_long_refseq":
        if target == "one-letter":
            protein_normalized = convert_protein_to_single_letter_code(protein, add_refseq=add_refseq)
        else:
            protein_normalized = protein
    elif request_type == "gene_name_aa_exchange_long_fs":
        if target == "one-letter":
            protein_normalized = convert_protein_to_single_letter_code(protein, add_refseq=add_refseq)
        else:
            protein_normalized = protein
    else:
        protein_normalized = protein

    return protein_normalized


def normalize_transcript_identifier(transcript):
    """

    :param transcript:
    :return:
    """
    transcript_normalized = ""

    return transcript_normalized


def normalize_dna_identifier_position(var, add_refseq=True):
    """

    :param var:
    :param add_refseq:
    :return:
    """
    if re.compile(hgvs_re.exp_positions).match(var):
        aa_groups = re.compile(hgvs_re.exp_positions).match(var).groups()
        chrom = aa_groups[0]
        refseq = ""
        if add_refseq is True:
            refseq = "g."
        if len(aa_groups) == 4:
            pos = aa_groups[3]
        elif len(aa_groups) == 3:
            pos = aa_groups[2]
        return chrom + aa_groups[1] + ":" + refseq + pos


def normalize_dna_identifier(var, target="vcf", add_refseq=True, mtype=None):
    """
    Normalizes a DNA identifier in VCF notation, e.g. 'chr7:g.140753336A>T'

    :param dna_id:
    :param target:
    :return:
    """
    snv_identified = False
    refseq = "g."
    if add_refseq is False:
        refseq = ""

    # SNVs
    if re.compile(hgvs_re.exp_genome_positions_nc).match(var):
        aa_groups = re.compile(hgvs_re.exp_genome_positions_nc).match(var).groups()
        chrom = adagenes.tools.get_chr(aa_groups[0])[0]
        pos = aa_groups[1]
        ref = aa_groups[2]
        alt = aa_groups[3]
        if len(ref) > len(alt):
            mtype = "del"
        elif len(ref) < len(alt):
            mtype = "ins"
        else:
            mtype="snv"
        snv_identified = True
    elif re.compile(hgvs_re.exp_genome_positions_nc_refseq).match(var):
        aa_groups = re.compile(hgvs_re.exp_genome_positions_nc_refseq).match(var).groups()
        chrom = adagenes.tools.get_chr(aa_groups[0])[0]
        pos = aa_groups[2]
        ref = aa_groups[3]
        alt = aa_groups[4]
        if len(ref) > len(alt):
            mtype = "del"
        elif len(ref) < len(alt):
            mtype = "ins"
        else:
            mtype="snv"
        snv_identified = True
    elif re.compile(hgvs_re.exp_genome_positions).match(var):
        aa_groups = re.compile(hgvs_re.exp_genome_positions).match(var).groups()
        chrom = "chr" + aa_groups[1]
        pos = aa_groups[2]
        ref = aa_groups[3]
        alt = aa_groups[4]
        if len(ref) > len(alt):
            mtype = "del"
        elif len(ref) < len(alt):
            mtype = "ins"
        else:
            mtype="snv"
        snv_identified = True
    elif re.compile(hgvs_re.exp_genome_positions_refseq).match(var):
        aa_groups = re.compile(hgvs_re.exp_genome_positions_refseq).match(var).groups()
        chrom = "chr" + aa_groups[1]
        pos = aa_groups[3]
        ref = aa_groups[4]
        alt = aa_groups[5]
        if len(ref) > len(alt):
            mtype = "del"
        elif len(ref) < len(alt):
            mtype = "ins"
        else:
            mtype="snv"
        snv_identified = True

    if (snv_identified is True) and (mtype == "snv"):
        var = chrom + ":" + refseq + pos + ref + ">" + alt
        return var

    if mtype is not None:
        # indel
        if mtype == "del":
            pos = int(pos) + 1
            lenpos = len(ref) - len(alt)
            pos2 = ""
            bases = ""
            #print("DELDEL ",pos,ref,": ",alt)
            if lenpos > 1:
                pos2 = "_" + str(int(pos) + lenpos -1)
                bases = alt

            if pos2 != "":
                var = chrom + ":" + refseq + str(pos) + pos2 + "del" # + bases
            else:
                var = chrom + ":" + refseq + str(pos) + "del" #+ bases

        elif mtype == "ins":
            lenpos = len(alt) - len(ref)
            pos2 = ""
            bases = ""
            #if lenpos > 1:
            #    pos2 = "_" + str(int(pos) + lenpos)
            pos = int(pos) + 1
            lenpos = len(alt) - len(ref)
            pos2 = ""
            if lenpos > 1:
                pos2 = "_" + str(int(pos) + lenpos - 1)
            bases = alt[1:]
            #var = chrom + ":" + refseq + pos + pos2 + "ins" + bases
            if pos2 != "":
                var = chrom + ":" + refseq + str(pos) + pos2 + "ins" + bases
            else:
                var = chrom + ":" + refseq + str(pos) + "ins" + bases

    indel_identified = False
    # InDels
    if re.compile(hgvs_re.exp_deletion).match(var):
        aa_groups = re.compile(hgvs_re.exp_deletion).match(var).groups()
        indel_identified = True
    elif re.compile(hgvs_re.exp_deletion_long).match(var):
        aa_groups = re.compile(hgvs_re.exp_deletion_long).match(var).groups()
        chrom = "chr" + aa_groups[1]
        indel_identified = True
    elif re.compile(hgvs_re.exp_deletion_ncbichrom).match(var):
        aa_groups = re.compile(hgvs_re.exp_deletion_ncbichrom).match(var).groups()
        chrom = adagenes.tools.get_chr(aa_groups[0])[0]
        #var
        indel_identified = True

    #print("norm ",var)
    #if indel_identified is True:
    #    var = chrom + ":" + refseq + pos + "del"
    #    return var


    # duplication

    # inversion

    return var


def recognize_mutation_types_from_vcf_format(data: dict) -> dict:
    """

    :param data:
    :return:
    """
    for var in data.keys():
        if isinstance(var, str):
            if "ins" in var:
                data[var]["mutation_type"] = "insertion"
            elif "del" in var:
                data[var]["mutation_type"] = "deletion"
            elif "delins" in var:
                data[var]["mutation_type"] = "indel"

    return data


def convert_protein_to_single_letter_code(var, add_refseq=True):
    """
    Convert a protein identifier from 3-letter to single letter codes

    :param aa_groups: 3-letter protein identifier, e.g. 'BRAF:p.Arg600Glu'
    :return:
    """
    mtype, groups = ag.get_variant_request_type(var)
    #print(mtype, groups)
    if mtype == "gene_name_aa_exchange_long_fs":
        aa_exchange = groups[2] + groups[3] + groups[4] + groups[5] + groups[6]
    #elif mtype == "gene_name_aa_exchange_long":
    #    print(groups)
    else:
        aa_exchange = groups[2] + groups[3] + groups[4]
    aa_exchange_single_letter = hgvs_re.convert_aa_exchange_to_single_letter_code(aa_exchange, add_refseq=add_refseq, mtype=mtype)

    refseq = "p."
    if add_refseq is False:
        refseq = ""

    var = groups[0] + ":" + refseq + aa_exchange_single_letter
    return var


def convert_protein_to_multiple_letter_code(var, add_refseq=True):
    """
    Convert a protein identifier from single letter to 3-letter codes

    :param var:
    :return:
    """
    mtype, groups = ag.get_variant_request_type(var)
    print("mtype ",mtype, ", G ",groups)

    aa_exchange = groups[2] + groups[3] + groups[4]

    aa_exchange_single_letter = hgvs_re.convert_aa_exchange_to_multiple_letter_code(aa_exchange, add_refseq=add_refseq)
    refseq = "p."
    if add_refseq is False:
        refseq = ""
    var = groups[0] + ":" + refseq + aa_exchange_single_letter
    return var
