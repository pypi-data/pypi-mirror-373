import unittest
import adagenes as ag


class AATestCase(unittest.TestCase):

    def test_aa_retrieval(self):
        possible_amino_acids = ag.get_amino_acid_list()
        print(possible_amino_acids)
        self.assertEqual(len(possible_amino_acids),25,"")

    def test_convert_aa_code_single(self):
        aa_ex = 'Arg600Glu'
        aa_single = ag.convert_aa_exchange_to_single_letter_code(aa_ex)
        self.assertEqual(aa_single,"R600E","")

    def test_convert_aa_code_multi(self):
        aa_ex = 'R282E'
        aa_multi = ag.convert_aa_exchange_to_multiple_letter_code(aa_ex)
        self.assertEqual(aa_multi,"Arg282Glu","")
