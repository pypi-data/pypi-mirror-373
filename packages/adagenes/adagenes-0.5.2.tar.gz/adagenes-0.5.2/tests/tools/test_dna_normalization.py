import unittest
import adagenes
import adagenes as ag


class TestDNANormalization(unittest.TestCase):

    def test_pos_normalization(self):
        var = "chr7:140753336"
        var = adagenes.normalize_dna_identifier_position(var, add_refseq=False)
        self.assertEqual(var,"chr7:140753336","")

    def test_pos_normalization_rs(self):
        var = "chr7:g.140753336"
        var = adagenes.normalize_dna_identifier_position(var, add_refseq=False)
        self.assertEqual(var,"chr7:140753336","")

    def test_nc_normalization(self):
        var = "NC_000007.14:140753336A>T"
        var = adagenes.normalize_dna_identifier(var, add_refseq=False)
        self.assertEqual(var,"chr7:140753336A>T","")

    def test_nc_normalization_refseq(self):
        var = "NC_000007.14:g.140753336A>T"
        var = adagenes.normalize_dna_identifier(var, add_refseq=False)
        self.assertEqual(var,"chr7:140753336A>T","")

    def test_normalization(self):
        var = "chr7:140753336A>T"
        var = adagenes.normalize_dna_identifier(var, add_refseq=False)
        self.assertEqual(var,"chr7:140753336A>T","")

    def test_normalization_refseq(self):
        var = "chr7:g.140753336A>T"
        var = adagenes.normalize_dna_identifier(var, add_refseq=False)
        self.assertEqual(var,"chr7:140753336A>T","")

    def test_general_normalization(self):
        var = "chr7:g.140753336A>T"
        bframe = ag.BiomarkerFrame(var, genome_version="hg38")
        #bframe.data[var] = {"variant_data":{"mutation_type": "g"}}
        print(bframe.data)
        #var = adagenes.normalize_identifier(var, bframe.data[var], add_refseq=False)
        self.assertListEqual(list(bframe.data.keys()), ["chr7:140753336A>T"], "")
        #self.assertEqual(bframe.data[var]["mutation_type"],"snv","")

    def test_normalize_all_identifiers(self):
        json_obj = {"chr7:g.140753336A>T":{}}
        bframe = ag.BiomarkerFrame(data=json_obj, genome_version="hg38")
        print(bframe)
        self.assertEqual(list(bframe.data.keys()),["chr7:140753336A>T"],"Error in ID normalization")
        self.assertEqual(bframe.data["chr7:140753336A>T"]["mutation_type"], "snv", "Error in ID normalization")
