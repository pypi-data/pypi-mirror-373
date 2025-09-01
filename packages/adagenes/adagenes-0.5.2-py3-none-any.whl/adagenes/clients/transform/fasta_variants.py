import adagenes


def generate_variant_fasta_in_bframe(bframe, variant, pos=0, ref_aa=None, alt_aa=None):
    """

    :param bframe:
    :param variant:
    :param pos:
    :param ref_aa:
    :param alt_aa:
    :return:
    """
    if isinstance(bframe, adagenes.BiomarkerFrame):
        variant_data = bframe.data
    else:
        variant_data = bframe

    if variant in variant_data.keys():
        fasta = variant_data[variant]["sequence"]
        variant_data[variant]["sequence"] = generate_variant_fasta(fasta, pos, ref_aa, alt_aa)

    if isinstance(bframe, adagenes.BiomarkerFrame):
        bframe.data = variant_data

    return bframe

def generate_variant_fasta(fasta, pos, ref_aa, alt_aa):
    """
    Generates a variant in an amino acid sequence at a specified position

    :param fasta:
    :param pos:
    :param ref_aa:
    :param alt_aa:
    :return:
    """
    if isinstance(fasta, str):
        if len(fasta) >= pos:
            fasta_list = list(fasta)
            fasta_refaa = fasta_list[pos]
            if fasta_refaa == ref_aa:
                fasta_list[pos] = alt_aa
            fasta = "".join(fasta_list)
    return fasta

