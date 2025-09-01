import unittest
import adagenes


class TestProteinNormalization(unittest.TestCase):

    def test_normalize_protein_identifier(self):
        var="BRAF:V600E"
        var = adagenes.normalize_protein_identifier(var, target="one-letter", add_refseq=False)
        self.assertEqual(var,"BRAF:V600E","")

    def test_normalize_protein_identifier_rs(self):
        var="BRAF:p.V600E"
        var = adagenes.normalize_protein_identifier(var, target="one-letter", add_refseq=False)
        self.assertEqual(var,"BRAF:V600E","")

    def test_normalize_protein_identifier_3letter(self):
        var="BRAF:p.Val600Glu"
        var = adagenes.normalize_protein_identifier(var, target="one-letter", add_refseq=False)
        self.assertEqual(var,"BRAF:V600E","")

    def test_convert_multiple_letter_to_single_letter(self):
        var = "BRAF:Val600Glu"
        var = adagenes.convert_protein_to_single_letter_code(var, add_refseq=False)
        self.assertEqual(var,"BRAF:V600E","")

    def test_convert_single_letter_to_multiple_letter(self):
        var = "BRAF:V600E"
        var = adagenes.convert_protein_to_multiple_letter_code(var, add_refseq=False)
        self.assertEqual(var,"BRAF:Val600Glu","")

    def test_convert_multiple_letter_to_single_letter_refseq(self):
        var = "BRAF:p.Val600Glu"
        var = adagenes.convert_protein_to_single_letter_code(var, add_refseq=False)
        self.assertEqual(var,"BRAF:V600E","")

    def test_convert_single_letter_to_multiple_letter_refseq(self):
        var = "BRAF:p.V600E"
        var = adagenes.convert_protein_to_multiple_letter_code(var, add_refseq=False)
        self.assertEqual(var,"BRAF:Val600Glu","")

    def test_convert_single_letter_to_multiple_letter_ter(self):
        var = "BRAF:p.Arg400Ter"
        var = adagenes.convert_protein_to_single_letter_code(var, add_refseq=False)
        self.assertEqual(var,"BRAF:R400X","")

    def test_convert_single_letter_to_multiple_letter_fs(self):
        var = "BRAF:p.Leu400PhefsTer"
        var = adagenes.convert_protein_to_single_letter_code(var, add_refseq=False)
        self.assertEqual(var,"BRAF:L400fs","")
