import unittest
import adagenes as ag
import adagenes.tools.seqcat_genetogenomic_client


class TestGeneToGenomicTestCase(unittest.TestCase):

    def test_seqcat_gene_to_genomic(self):
        data= { "BRAF:p.V600E": {} }
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        print("loaded ",bframe)
        client = adagenes.tools.seqcat_genetogenomic_client.SeqCATProteinClient(genome_version="hg38")
        bframe.data = client.process_data(bframe.data)
        print(bframe)
        self.assertEqual(1, len(bframe.data.keys()), "")
        self.assertEqual("chr7:140753336A>T", list(bframe.data.keys())[0],"")


