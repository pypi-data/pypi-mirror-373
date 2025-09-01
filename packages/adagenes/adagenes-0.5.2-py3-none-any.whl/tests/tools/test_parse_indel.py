import unittest
import adagenes as ag


class TestIndel(unittest.TestCase):

    def test_parse_deletion(self):
        var = "chr17:g.7675152del"
        chr, mtype, pos, pos2, alt = ag.parse_indel(var)
        self.assertEqual(pos,"7675152","")
        self.assertEqual(chr, "17", "")
        self.assertEqual(mtype, "del", "")
        self.assertEqual(pos2, None, "")
        self.assertEqual(alt, "", "")


    def test_parse_insertion(self):
        var = "chr17:g.7675158_7675159insN"
        chr, mtype, pos, pos2, alt = ag.parse_indel(var)
        self.assertEqual(pos,"7675158","")
        self.assertEqual(chr, "17", "")
        self.assertEqual(mtype, "ins", "")
        self.assertEqual(pos2, "7675159", "")
        self.assertEqual(alt, "N", "")

    def test_parse_indel(self):
        var = "chr17:g.7675215_7675216delinsAG"
        chr, mtype, pos, pos2, alt = ag.parse_indel(var)
        self.assertEqual(pos,"7675215","")
        self.assertEqual(chr, "17", "")
        self.assertEqual(mtype, "delins", "")
        self.assertEqual(pos2, "7675216", "")
        self.assertEqual(alt, "AG", "")
