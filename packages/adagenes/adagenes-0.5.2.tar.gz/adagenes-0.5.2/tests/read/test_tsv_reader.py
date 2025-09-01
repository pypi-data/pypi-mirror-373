import unittest, os
import adagenes


class TestTSVReader(unittest.TestCase):

    def test_tsv_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        infile = __location__ + "/../test_files/clinvar_variants_01.tsv"
        mapping = {""}
        bframe = adagenes.read_file(infile, genome_version=genome_version)
        print(list(bframe.data.keys())[0])
        print(bframe)

        self.assertEqual("chr1:930165G>A",list(bframe.data.keys())[0],"")
        self.assertEqual("1", bframe.data["chr1:930165G>A"]["variant_data"]["CHROM"], "")
        self.assertEqual("SAMD11", bframe.data["chr1:930165G>A"]["Gene"], "")

        self.assertEqual("H257Y", bframe.data["chr1:930314C>T"]["variant_exchange"], "")


