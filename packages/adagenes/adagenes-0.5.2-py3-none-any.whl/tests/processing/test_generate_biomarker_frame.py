import unittest
import adagenes as ag


class BiomarkerFrameGenerationTestCase(unittest.TestCase):

    def test_generate_bframe(self):
        query = "TP53:R282W,GATA3:T421M,BRAF:V600E,BRCA2:P2204A,CHR7:47368770-CHRX:67643257"
        query = query.split(",")
        bframe = ag.BiomarkerFrame(query, genome_version="hg38")
        print(bframe)
        self.assertEqual(len(list(bframe.data.keys())), 5, "")
        self.assertEqual(bframe.data['CHR7:47368770-CHRX:67643257']['mutation_type'],'fusion','')
        self.assertEqual(bframe.data['GATA3:T421M']['mutation_type'], 'snv', '')
