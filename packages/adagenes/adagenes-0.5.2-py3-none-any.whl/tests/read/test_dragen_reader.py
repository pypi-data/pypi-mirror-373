import unittest, os
import adagenes as ag
from adagenes.tools.client_mgt import get_reader, get_writer


class TestDragenReader(unittest.TestCase):

    def test_dragen_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        infile = os.getenv("INFILE")
        #infile = __location__ + "/../test_files/somaticMutations.ln_4.vcf"
        bframe = ag.read_file(infile, genome_version=genome_version)
        print(list(bframe.data.keys())[0])
        print(bframe)

        self.assertEqual("chr12:25245350C>T",list(bframe.data.keys())[0],"")
        self.assertEqual("12", bframe.data["chr12:25245350C>T"]["variant_data"]["CHROM"], "")

        self.assertEqual("chr12:25245350C>T", list(bframe.data.keys())[0], "")
        self.assertEqual("12", bframe.data["chr12:25245350C>T"]["variant_data"]["CHROM"], "")

        self.assertEqual("chr12:25245350C>T", list(bframe.data.keys())[0], "")
        self.assertEqual("25245350", bframe.data["chr12:25245350C>T"]["variant_data"]["POS_hg19"], "")

        self.assertEqual("snv", bframe.data["chr12:25245350C>T"]["mutation_type"], "")
