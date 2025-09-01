import unittest, re
import adagenes.tools.preprocessing
import adagenes.tools.hgvs_re


class TestPreprocessing(unittest.TestCase):

    def test_chromosome_identification(self):
        var="chr1"
        var_single = re.compile(adagenes.tools.gencode.chr_pt).match(var)
        self.assertEqual(var_single.groups()[0], "chr", "Should be chr")
        self.assertEqual(var_single.groups()[1], "1", "Should be 1")

    def test__identify_query_parameters_genome_location(self):
        var = "chr7:140753336A>T"
        genome_positions = adagenes.tools.preprocessing.get_genome_location(var)
        self.assertEqual(genome_positions, [var], "Should be "+str([var]))

    def test__identify_query_parameters_genome_location_nc_id(self):
        var = "NC_000007.14:140753336A>T"
        var_val = "chr7:140753336A>T"
        genome_positions = adagenes.tools.preprocessing.get_genome_location(var)
        self.assertEqual(genome_positions, [var_val], "Should be "+str([var_val]))

    def test_convert_aa_exchange_to_single_letter_code(self):
        var = "Arg282Trp"
        var_single = adagenes.tools.gencode.convert_aa_exchange_to_single_letter_code(var, add_refseq=False)
        self.assertEqual(var_single, "R282W", "Should be R282W")

    def test_convert_multiple_letter_code(self):
        var = "Arg"
        var_single = adagenes.tools.gencode.convert_to_single_letter_code(var)
        self.assertEqual(var_single, "R", "Should be R")

    def test_identify_query_parameters_aa_exchange_single_letter_code(self):
        q="TP53:R282W"
        request = adagenes.tools.preprocessing.identify_query_parameters(q, None, None)
        lt = ([],["TP53:R282W"],[],[],[],[])
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_identify_query_parameters_aa_exchange_multiple_letter_code(self):
        q="TP53:Arg282Trp"
        request = adagenes.tools.preprocessing.identify_query_parameters(q, None, None, add_refseq=False)
        lt = ([],["TP53:R282W"],[], [], [],[])
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

