import unittest
import adagenes


class TestBLOSUMCalculation(unittest.TestCase):

    def test_blosum_score_calculation(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": { "variant_data": { "ref_aa": "V", "alt_aa": "E" } },
                "chr12:25245350C>T": { "variant_data": { "ref_aa": "G", "alt_aa": "D"} }}
        data = adagenes.tools.generate_variant_data_section_all_variants(data)
        data = adagenes.BLOSUMClient().process_data(data)

        self.assertEqual(data["chr7:140753336A>T"]["variant_data"]["blosum62"], "-2.0", "BLOSUM value not correct")
        self.assertEqual(data["chr12:25245350C>T"]["variant_data"]["blosum62"], "-1.0", "BLOSUM value not correct")

    def test_blosum_score_calculation_SeqCAT(self):
        genome_version = 'hg38'
        data = {"chr7:140753336A>T": { "UTA_Adapter": { "variant_exchange": "V600E" } },
                "chr12:25245350C>T": { "UTA_Adapter": { "variant_exchange": "G12D" } }}
        data = adagenes.tools.generate_variant_data_section_all_variants(data)
        data = adagenes.BLOSUMClient().process_data(data)

        self.assertEqual(data["chr7:140753336A>T"]["variant_data"]["blosum62"], "-2.0", "BLOSUM value not correct")
        self.assertEqual(data["chr12:25245350C>T"]["variant_data"]["blosum62"], "-1.0", "BLOSUM value not correct")

