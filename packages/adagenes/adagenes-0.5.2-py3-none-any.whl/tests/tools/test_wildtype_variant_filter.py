import unittest
import adagenes as ag

class VariantFilterTestCase(unittest.TestCase):

    def test_variant_filter(self):
        variant_data = { "chr7:140753336A>T": {}, "chrY:21660782A>.":{}, "chr1:147837282G>.":{}, "chr1:147837282G>AA":{} }
        bframe = ag.BiomarkerFrame(variant_data)
        print(bframe.data)
        variant_data_filtered = ag.tools.filter_wildtype_variants(bframe.data)
        print("filtered: ",variant_data_filtered)
        dc = { "chr7:140753336A>T": {'type': 'g', 'mutation_type': 'snv', 'mdesc': 'genomic_location',
                                     'variant_data': {'CHROM': '7', 'POS': '140753336', 'REF': 'A', 'ALT': 'T'}},
               'chr1:147837282G>AA': {'mutation_type': 'unidentified', 'mdesc': 'unidentified'}}
        #self.assertDictEqual(dc, variant_data_filtered)
        self.assertListEqual(list(variant_data_filtered.keys()), ["chr7:140753336A>T","chr1:147837283insA"],"")
