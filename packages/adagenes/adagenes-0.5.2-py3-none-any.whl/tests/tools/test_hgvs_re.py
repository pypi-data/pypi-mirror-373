import unittest
import adagenes as ag


class HGVSTestCase(unittest.TestCase):

    def test_aaexchange_multi2single_letter_conversion_refseq(self):
        aa_exchange = 'p.Lys2Glu'
        aa_ex_single = ag.convert_aa_exchange_to_single_letter_code(aa_exchange, add_refseq=False)
        print(aa_ex_single)
        self.assertEqual(aa_ex_single,"K2E","")

    def test_aaexchange_multi2single_letter_conversion(self):
        aa_exchange = 'Lys2Glu'
        aa_ex_single = ag.convert_aa_exchange_to_single_letter_code(aa_exchange, add_refseq=False)
        print(aa_ex_single)
        self.assertEqual(aa_ex_single,"K2E","")

    def test_aaexchange_multi2single_letter_conversion1(self):
        aa_exchange = 'Arg600Glu'
        aa_ex_single = ag.convert_aa_exchange_to_single_letter_code(aa_exchange, add_refseq=False)
        print(aa_ex_single)
        self.assertEqual(aa_ex_single,"R600E","")
