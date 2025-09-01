import unittest, os
import adagenes


class TestTXTReader(unittest.TestCase):

    def test_txt_reader(self):
        genome_version = 'hg19'
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.txt"
        mapping = {
            "chrom": 1,
            "pos": 2,
            "ref": 4,
            "alt": 5
        }
        bframe = adagenes.TXTReader().read_file(infile, genome_version, mapping=mapping, sep="\t", header=0)
        print(bframe)

