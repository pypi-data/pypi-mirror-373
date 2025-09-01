import unittest
import adagenes as ag
import adagenes.tools.frameshift


class FrameshiftTestCase(unittest.TestCase):

    def test_frameshift_recognition(self):
        data = {
            "chrX:44922951TG>T": {},
            "chr17:7579345CAAG>C": {},
            "chr6:75901432TTCCAG>T": {},
            "chr10:8111553C>CT": {},
            "chr10:89717702TTCCCTCAGCCGTTACCTGTGTG>T": {},
            "chr17:12011182GATGAT>G": {}
        }

        bframe = ag.BiomarkerFrame(data=data)
        print("bframe data ",bframe.data)
        #for var in data.keys():
        #    isinframe = adagenes.tools.frameshift.is_frameshift_del(var)

        self.assertEqual(bframe.data["chrX:44922952del"]["frameshift"], "frameshift", "")
        self.assertEqual(bframe.data["chrX:44922952del"]["orig_id"], "chrX:44922951TG>T", "")

        self.assertEqual(bframe.data["chr17:7579346_7579348del"]["frameshift"], "in-frame", "")
        self.assertEqual(bframe.data["chr17:7579346_7579348del"]["orig_id"], "chr17:7579345CAAG>C", "")

        self.assertEqual(bframe.data["chr6:75901433_75901437del"]["frameshift"], "frameshift", "")
        self.assertEqual(bframe.data["chr6:75901433_75901437del"]["orig_id"], "chr6:75901432TTCCAG>T", "")

        self.assertEqual(bframe.data["chr10:8111554insT"]["frameshift"], "frameshift", "")
        self.assertEqual(bframe.data["chr10:8111554insT"]["orig_id"], "chr10:8111553C>CT", "")

        self.assertEqual(bframe.data["chr10:89717703_89717724del"]["frameshift"], "frameshift", "")
        self.assertEqual(bframe.data["chr10:89717703_89717724del"]["orig_id"], "chr10:89717702TTCCCTCAGCCGTTACCTGTGTG>T", "")

        self.assertEqual(bframe.data["chr17:12011183_12011187del"]["frameshift"], "frameshift", "")
        self.assertEqual(bframe.data["chr17:12011183_12011187del"]["orig_id"], "chr17:12011182GATGAT>G", "")


