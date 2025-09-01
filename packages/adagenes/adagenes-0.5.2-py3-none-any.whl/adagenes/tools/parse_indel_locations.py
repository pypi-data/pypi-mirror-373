import adagenes


def parse_indel_location(variant,mut_type):
    chrom, ref_seq, pos, ref, alt = adagenes.parse_genome_position(variant)

    if mut_type == "deletion":
        parsed_variant = chrom + ":" + pos + "del"
    elif mut_type == "insertion":
        parsed_variant = chrom + ":" + pos + "ins" + alt

    return parsed_variant