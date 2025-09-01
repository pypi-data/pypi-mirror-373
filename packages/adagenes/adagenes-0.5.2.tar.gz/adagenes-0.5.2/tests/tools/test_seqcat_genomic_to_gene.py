import unittest
import adagenes as ag
import adagenes.tools.seqcat_genomictogene_client


class TestGenomicToGeneTestCase(unittest.TestCase):

    def test_seqcat_genomic_to_gene(self):
        data= { "chr7:g.140753336A>T": {} }
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        print("loaded ",bframe)
        client = adagenes.tools.seqcat_genomictogene_client.SeqCATGenomicClient(genome_version="hg38")
        bframe.data = client.process_data(bframe.data)
        print(bframe)
        self.assertEqual(1, len(bframe.data.keys()), "")
        self.assertEqual("chr7:140753336A>T", list(bframe.data.keys())[0],"")
        self.assertListEqual(['type', 'mutation_type', 'mutation_type_desc',
                              'mdesc', 'variant_data', 'UTA_Adapter'],
                             list(bframe.data["chr7:140753336A>T"].keys()), "")


