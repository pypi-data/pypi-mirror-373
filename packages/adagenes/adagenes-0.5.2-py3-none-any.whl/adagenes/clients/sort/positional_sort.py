from functools import cmp_to_key
import adagenes as ag


def compare_genomic_positions(item1, item2):
    """
    Custom comparator for sorting lists of genomic positions

    :param item1:
    :param item2:
    :return:
    """
    chr, ref_seq, pos, ref, alt = ag.parse_genome_position(item1)
    chr2, ref_seq2, pos2, ref2, alt2 = ag.parse_genome_position(item2)

    chr = chr.replace("chr","")
    chr = chr.replace("CHR", "")
    chr2 = chr2.replace("chr", "")
    chr2 = chr2.replace("CHR", "")

    # Compare chromosomes
    if int(chr) < int(chr2):
        return -1
    elif int(chr) > int(chr2):
        return 1

    # Compare positions
    if int(pos) < int(pos2):
        return 1
    elif int(pos) > int(pos2):
        return -1
    else:
        return 0


def positional_sort(bframe, ascending=True):
    """
    Sorts the variants in a biomarker frame according to the genomic positions

    :param bframe:
    :param ascending:
    :return:
    """

    sorted_vars = list(bframe.data.keys())
    sorted_vars = sorted(sorted_vars, key=cmp_to_key(compare_genomic_positions))

    bframe.sorted_variants = sorted_vars
    bframe.is_sorted = True

    return bframe

