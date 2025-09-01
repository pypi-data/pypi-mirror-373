import unittest
import adagenes as ag
import adagenes.processing.protein_to_genomic


class TestProteinToGenomicTestCase(unittest.TestCase):

    def test_protein_to_genomic(self):
        data= { "BRAF:p.V600E": {}, "":{} }
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        print("loaded ",bframe)
        bframe = adagenes.processing.protein_to_genomic(bframe)
        print(bframe)
        self.assertEqual("g",bframe.data_type,"")
        self.assertEqual("chr7:140753336A>T", list(bframe.data.keys())[0], "")

