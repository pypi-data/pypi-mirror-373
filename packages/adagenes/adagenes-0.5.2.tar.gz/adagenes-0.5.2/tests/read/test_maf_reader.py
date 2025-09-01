import unittest, os
import adagenes as ag
from adagenes.tools.client_mgt import get_reader, get_writer


class TestMAFReader(unittest.TestCase):

    def test_maf_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg38'

        infile = __location__ + "/../test_files/31e707ed-a30b-42b3-a1ee-a1ee2f8b46ce.wxs.aliquot_ensemble_masked.maf"
        bframe = ag.read_file(infile, genome_version=genome_version)
        #print(list(bframe.data.keys())[0])
        print(bframe.data)
        #self.assertEqual(len(list(bframe.data.keys())), 5, "")

        #self.assertEqual("chr12:25245350C>T",list(bframe.data.keys())[0],"")
        #self.assertEqual("12", bframe.data["chr12:25245350C>T"]["variant_data"]["CHROM"], "")

        #self.assertEqual("chr12:25245350C>T", list(bframe.data.keys())[0], "")
        #self.assertEqual("12", bframe.data["chr12:25245350C>T"]["variant_data"]["CHROM"], "")

        #self.assertEqual("chr12:25245350C>T", list(bframe.data.keys())[0], "")
        #self.assertEqual("25245350", bframe.data["chr12:25245350C>T"]["variant_data"]["POS_hg19"], "")

        #self.assertEqual("snv", bframe.data["chr12:25245350C>T"]["mutation_type"], "")

        #self.assertEqual(bframe.max_variants,5,"")
