import re
import adagenes


def convert_aa_exchange_to_multiple_letter_code(aa_exchange, add_refseq=False):
    """
    Converts a single letter variant exchange into multiple letter codes

    :param aa_exchange: e.g. 'R282W'
    :return:
    """
    if re.compile(variant_exchange_long_pt_ext).match(aa_exchange):
        groups = re.compile(variant_exchange_long_pt_ext).match(aa_exchange).groups()
        #print(groups)
        try:
            aa_1 = groups[1].upper()
            aa_2 = groups[3].upper()
            aa1_multiple = protein_dc_single_lower[aa_1]
            aa2_multiple = protein_dc_single_lower[aa_2]
            p = ""
            if add_refseq is True:
                p = 'p.'
        except:
            print("error converting multiple letter code into single letter code: ", aa_1, ",", aa_2)
            return aa_exchange
        return p + aa1_multiple + groups[2] + aa2_multiple
    else:
        return None


def convert_aa_exchange_to_single_letter_code(aa_exchange, add_refseq=False, mtype=None):
    """
    Converts a multiple letter variant exchange into single letter codes

    :param aa_exchange: e.g. 'Arg600Glu', 'p.Arg600Glu'
    :param add_refseq: Defines if protein reference sequence (p.) should be added
    :return: Single letter notation amino acid exchange, e.g. 'R600E'
    """
    #print("mtype ",mtype)
    if (mtype is not None) and (mtype == "gene_name_aa_exchange_long_fs"):
            groups = re.compile(variant_exchange_long_pt_fs).match(aa_exchange).groups()
            aa_1 = groups[1].lower()
            aa_2 = "fs"
            aa1_single = protein_dc_lower[aa_1]
            return aa1_single + groups[2] + aa_2
    else:
        if re.compile(variant_exchange_long_pt_ext).match(aa_exchange):
            groups = re.compile(variant_exchange_long_pt_ext).match(aa_exchange).groups()
            try:
                aa_1 = groups[1].lower()
                aa_2 = groups[3].lower()
                aa1_single = protein_dc_lower[aa_1]

                if mtype == "gene_name_aa_exchange_long_fs":
                    aa2_single = "fs"
                else:
                    aa2_single = protein_dc_lower[aa_2]
            except:
                print("error converting multiple letter code into single letter code: ", aa_1, ",", aa_2)
                return aa_exchange
            if add_refseq is True:
                return 'p.' + aa1_single + groups[2] + aa2_single
            else:
                return aa1_single + groups[2] + aa2_single
        else:
            return None


def convert_to_single_letter_code(aa):
    """

    :param aa:
    :return:
    """
    if aa in adagenes.tools.gencode.protein_dc:
        return adagenes.tools.gencode.protein_dc[aa]
    else:
        return None


# Protein
# genomic location patterns
gene_symbol_pt = '([A-Z|a-z|0-9]+)'
variant_exchange_pt = '(p.)?([a-z|A-Z])([0-9]+)([a-z|A-Z|=|\\*])$'
variant_exchange_pt_fs = '(p.)?([a-z|A-Z])([0-9]+)(fs|del|dup|DEL|DUP$)'
variant_exchange_long_pt = '(p.)?([a-z|A-Z]+)([0-9]+)([a-z|A-Z|=|\\*]{1,3})'
variant_exchange_long_pt_fs = '(p.)?([A-Z|a-z]+)([0-9]+)([A-Z|a-z]+)(del|DEL|dup|DUP|fs)([A-Z|a-z]+)' #'p\.[A-Za-z]+[0-9]+(del|DEL|dup|DUP|fs[A-Za-z=*]{3})' #'([a-z|A-Z]+[0-9]+[a-z|A-Z|=|\\*]{3}fs|del|DEL|dup|DUP[a-z|A-Z|=|\\*]{3}$)'
variant_exchange_long_pt_ext = '(p.)?([a-z|A-Z]+)([0-9]+)([a-z|A-Z|=|\\*]+)'
variant_exchange_long_pt_fs_short = '(p.)?([A-Z|a-z]+)([0-9]+)(del|DEL|dup|DUP|fs)'

variant_exchange_pt_refseq = '([p|P]?\\.?)' + variant_exchange_pt
variant_exchange_long_pt_refseq = '([p|P]?\\.?)' + variant_exchange_long_pt
variant_exchange_pt_fs_refseq = '([p|P]?\\.?)' + variant_exchange_pt_fs
variant_exchange_long_pt_fs_refseq = '(p\.)' + variant_exchange_long_pt_fs

exp_gene_name = '(^[A-Za-z0-9]+)$'
exp_gene_name_comb = '(^[A-Za-z0-9]+)'

exp_gene_name_variant_exchange = gene_symbol_pt + ":" + variant_exchange_pt
exp_gene_name_variant_exchange_fs = gene_symbol_pt + ":" + variant_exchange_pt_fs
exp_gene_name_variant_exchange_fs_refseq = gene_symbol_pt + ":" + variant_exchange_pt_fs_refseq
exp_gene_name_variant_exchange_long_fs_short = gene_symbol_pt + ":" + variant_exchange_long_pt_fs_short

exp_gene_name_variant_exchange_long = gene_symbol_pt + ":" + variant_exchange_long_pt
exp_gene_name_variant_exchange_long_fs = gene_symbol_pt + ":" + variant_exchange_long_pt_fs
exp_gene_name_variant_exchange_long_fs_refseq = gene_symbol_pt + ":" + variant_exchange_long_pt_fs_refseq

exp_gene_name_variant_exchange_refseq = gene_symbol_pt + ":" + variant_exchange_pt_refseq
exp_gene_name_variant_exchange_long_refseq = gene_symbol_pt + ":" + variant_exchange_long_pt_refseq

chr_pt = '([c|C][h|H][r|R])([X|Y|N|M|x|y|n|m|0-9]+)'
refseq_chromosome_pt = '(NC_[0-9]+\.[0-9]+)'
refseq_transcript = '(NM_[0-9]+\\.[0-9]+)'
refseq_protein = '(NP_[0-9]+\.?[0-9]?)'

ref_seq_pt = '([p|P|c|C|o|O|r|R][\\.])'
ref_seq_gt = '([g|G]\\.)?'
pos_pt = '([0-9]+)'
ref_pt = '([A|C|G|T]+)'
alt_pt = '([A|C|G|T|\\.]+)'

refseq_transcript_aaexchange_snv = '([c|C]?[\\.]?)([0-9]+)([A|C|G|T|N]+)>([A|C|G|T|N]+)'
# e.g. c.4375_4376insACCT
refseq_genomic_aaexchange_ins = '([g|G]?[\\.]?)([0-9]+)([i|I][n|N][s|S])([C|G|A|T|N]?)'
refseq_genomic_aaexchange_ins_long = '([g|G]?[\\.]?)([0-9]+)_([0-9]+)([i|I][n|N][s|S])([C|G|A|T|N]?)'
# e.g. c.4375_4379del or c.4375_4379delCGATT
refseq_genomic_aaexchange_del = '([g|G]?[\\.]?)([0-9]+)([d|D][e|E][l|L]+)'
refseq_genomic_aaexchange_del_long = '([g|G]?[\\.]?)([0-9]+)_([0-9]+)([d|D][e|E][l|L]+)'
# e.g. c.4375_4385dup
# or c.4375_4385dupCGATTATTCCA
refseq_transcript_aaexchange_ins = '([c|C]?[\\.]?)([0-9]+)([i|I][n|N][s|S])([C|G|A|T|N]?)'
refseq_transcript_aaexchange_ins_long = '([c|C]?[\\.]?)([0-9]+)_([0-9]+)([i|I][n|N][s|S])([C|G|A|T|N]?)'
# e.g. c.4375_4379del or c.4375_4379delCGATT
refseq_transcript_aaexchange_del = '([c|C]?[\\.]?)([0-9]+)([d|D][e|E][l|L]+)'
refseq_transcript_aaexchange_del_long = '([c|C]?[\\.]?)([0-9]+)_([0-9]+)([d|D][e|E][l|L]+)'
refseq_transcript_aaexchange_dup = '(c\\.)([0-9]+)_([0-9]+)dup([C|G|A|T]?)'
# e.g. c.4375_4376delinsACTT
# or c.4375_4376delCGinsAGTT
# delins e.g. NC_000001.11:g.123delinsAC
refseq_transcript_aaexchange_delins = '([g|G]?[\\.]?)([0-9]+)([d|D][e|E][l|L][i|I][n|N][s|S]+)([A|C|G|T|N]?)'
refseq_transcript_aaexchange_delins_long = '([g|G]?[\\.]?)([0-9]+)_([0-9]+)([d|D][e|E][l|L][i|I][n|N][s|S]+)([A|C|G|T|N]?)'
#refseq_transcript_aaexchange_insdel = '(c\\.[0-9]+_[0-9]delins[C|G|A|T]?)'

# TODO
# Transcripts NM
exp_refseq_transcript = "NM_\d{6,}\.\d+"
# Protein IDs NP_
exp_refseq_protein = "NP_\d{6,}\.\d+"
# Ensembl proteins ENST
exp_ensembl_transcript = "ENST\d{11,}\.\d+"
# Ensembl transcripts
exp_ensembl_protein = "ENSP\d{11,}\.\d+"
# Uniprot variants
exp_uniprot_accession_numbers = "\b([A-NR-Z][0-9]{4}[0-9A-Z]|[O-Q][0-9]{4}[A-Z0-9])\b"
exp_uniprot_entry_names = "\b[A-Z0-9]{2,}_([A-Z]{2,})\b"

# Position
exp_positions = chr_pt + ":" + ref_seq_gt + pos_pt

# SNV: Genomic location
exp_genome_positions = chr_pt + ":" + pos_pt + ref_pt + ">" + alt_pt
exp_genome_positions_nc = refseq_chromosome_pt + ":" + pos_pt + ref_pt + ">" + alt_pt
exp_genome_positions_refseq = chr_pt + ":" + ref_seq_gt + pos_pt + ref_pt + ">" + alt_pt
exp_genome_positions_nc_refseq = refseq_chromosome_pt + ":" + ref_seq_gt + pos_pt + ref_pt + ">" + alt_pt

# InDel
exp_insertion = chr_pt + ":" + refseq_genomic_aaexchange_ins
exp_insertion_ncbichrom = refseq_chromosome_pt + ":" + refseq_genomic_aaexchange_ins
exp_insertion_long = chr_pt + ":" + refseq_genomic_aaexchange_ins_long
exp_insertion_ncbichrom_long = refseq_chromosome_pt + ":" + refseq_genomic_aaexchange_ins_long
exp_deletion = chr_pt + ":" + refseq_genomic_aaexchange_del
exp_deletion_ncbichrom = refseq_chromosome_pt + ":" + refseq_genomic_aaexchange_del
exp_deletion_long = chr_pt + ":" + refseq_genomic_aaexchange_del_long
exp_deletion_ncbichrom_long = refseq_chromosome_pt + ":" + refseq_genomic_aaexchange_del_long
exp_indel = chr_pt + ":" + refseq_transcript_aaexchange_delins
exp_indel_ncbichrom = refseq_chromosome_pt + ":" + refseq_transcript_aaexchange_delins
exp_indel_long = chr_pt + ":" + refseq_transcript_aaexchange_delins_long
exp_indel_ncbichrom_long = refseq_chromosome_pt + ":" + refseq_transcript_aaexchange_delins_long

# Transcript
exp_refseq_transcript_pt = refseq_transcript + ":" + refseq_transcript_aaexchange_snv
exp_refseq_transcript_gene = exp_gene_name_comb + ":" + refseq_transcript_aaexchange_snv
exp_refseq_transcript_del = refseq_transcript + ":" + refseq_transcript_aaexchange_del
exp_refseq_transcript_del_gene = exp_gene_name_comb + ":" + refseq_transcript_aaexchange_del
exp_refseq_transcript_del_long = refseq_transcript + ":" + refseq_transcript_aaexchange_del_long
exp_refseq_transcript_del_gene_long = exp_gene_name_comb + ":" + refseq_transcript_aaexchange_del_long
exp_refseq_transcript_ins = refseq_transcript + ":" + refseq_transcript_aaexchange_ins
exp_refseq_transcript_ins_gene = exp_gene_name_comb + ":" + refseq_transcript_aaexchange_ins
exp_refseq_transcript_ins_long = refseq_transcript + ":" + refseq_transcript_aaexchange_ins_long
exp_refseq_transcript_ins_gene_long = exp_gene_name_comb + ":" + refseq_transcript_aaexchange_ins_long

# Protein
exp_protein_np = refseq_protein + ":" + variant_exchange_pt
exp_protein_np_refseq = refseq_protein + ":" + variant_exchange_pt_refseq
exp_protein_np_long = refseq_protein + ":" + variant_exchange_long_pt
exp_protein_np_long_refseq = refseq_protein + ":" + variant_exchange_long_pt_refseq

exp_fusions = '(CHR[0-9|X|Y]+:[0-9]+)-(CHR[0-9|X|Y]+:[0-9]+)'

aalist = ["A","R","N","D","C","Q","E","G","H","I","L","K","M","F","P","S","T","W","Y","V","U","O","B","Z","X"]

# CNV
exp_cnv_del = "([cC][hH][rR])([XYNMxy0-9]+):([0-9]+)-([0-9]+)_(DEL)"
exp_cnv_dup = "([cC][hH][rR])([XYNMxy0-9]+):([0-9]+)-([0-9]+)_(DUP)"
exp_cnv_cnv = "([cC][hH][rR])([XYNMxy0-9]+):([0-9]+)-([0-9]+)_(CNV)"

# Chromosomal position only
chrom_position = "^([cC][hH][rR])([XYNMxy0-9]+):(g.)?([0-9]+)$"

def get_amino_acid_list():
    return aalist

protein_dc_lower = {
    "ala": "A",
    "arg": "R",
    "asn": "N",
    "asp": "D",
    "cys": "C",
    "gln": "Q",
    "glu": "E",
    "gly": "G",
    "his": "H",
    "ile": "I",
    "leu": "L",
    "lys": "K",
    "met": "M",
    "phe": "F",
    "pro": "P",
    "ser": "S",
    "thr": "T",
    "trp": "W",
    "tyr": "Y",
    "val": "V",
    "sec": "U",
    "pyl": "O",
    "asx": "B",
    "glx": "Z",
    "xaa": "X",
    "ter": "X",
    "*": "*",
    "=": "="
}

protein_dc_upper = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
    "SEC": "U",
    "PYL": "O",
    "ASX": "B",
    "GLX": "Z",
    "XAA": "X",
    "TER": "X",
    "*": "*",
    "=": "="
}

protein_dc = {
    "Ala": "A",
    "Arg": "R",
    "Asn": "N",
    "Asp": "D",
    "Cys": "C",
    "Gln": "Q",
    "Glu": "E",
    "Gly": "G",
    "His": "H",
    "Ile": "I",
    "Leu": "L",
    "Lys": "K",
    "Met": "M",
    "Phe": "F",
    "Pro": "P",
    "Ser": "S",
    "Thr": "T",
    "Trp": "W",
    "Tyr": "Y",
    "Val": "V",
    "Sec": "U",
    "Pyl": "O",
    "Asx": "B",
    "Glx": "Z",
    "Xaa": "X",
    "*": "*",
    "=": "="
}

protein_dc_single_lower = {
    "A": "Ala",
    "R": "Arg",
    "N": "Asn",
    "D": "Asp",
    "C": "Cys",
    "Q": "Gln",
    "E": "Glu",
    "G": "Gly",
    "H": "His",
    "I": "Ile",
    "L": "Leu",
    "K": "Lys",
    "M": "Met",
    "F": "Phe",
    "P": "Pro",
    "S": "Ser",
    "T": "Thr",
    "W": "Trp",
    "Y": "Tyr",
    "V": "Val",
    "U": "Sec",
    "O": "Pyl",
    "B": "Asx",
    "Z": "Glx",
    "X": "Xaa",
    "*": "*",
    "=": "="
}