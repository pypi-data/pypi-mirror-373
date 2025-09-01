import blosum as bl
from adagenes.tools import parse_variant_exchange


class BLOSUMClient:

    def process_data(self, variant_data):
        """
        Annotates biomarker frame data with BLOSUM62 calculations for amino acid substitutions

        :param variant_data:
        :return:
        """

        matrix = bl.BLOSUM(62)

        for var in variant_data.keys():
            if "variant_data" in variant_data[var]:
                if ("ref_aa" in variant_data[var]["variant_data"]) and ("alt_aa" in variant_data[var]["variant_data"]):
                    ref_aa = variant_data[var]["variant_data"]["ref_aa"]
                    alt_aa = variant_data[var]["variant_data"]["alt_aa"]
                    bl_val = matrix[ref_aa][alt_aa]
                    variant_data[var]["variant_data"]["blosum62"] = str(bl_val)
                elif ("UTA_Adapter" in variant_data[var]):
                    if "variant_exchange" in variant_data[var]["UTA_Adapter"]:
                        aa_exchange = variant_data[var]["UTA_Adapter"]["variant_exchange"]
                        ref_aa, pos, alt_aa = parse_variant_exchange(aa_exchange)
                        bl_val = matrix[ref_aa][alt_aa]
                        variant_data[var]["variant_data"]["blosum62"] = str(bl_val)

        return variant_data
