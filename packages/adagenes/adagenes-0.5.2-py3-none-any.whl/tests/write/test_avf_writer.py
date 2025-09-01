import unittest, os
import adagenes


class TestAVFWriter(unittest.TestCase):

    def test_avf_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file = __location__ + "/../test_files/somaticMutations.ln50.txt"
        outfile = __location__ + '/../test_files/somaticMutations.ln50.test.avf'
        genome_version="hg38"
        mapping = {
            "chrom": 1,
            "pos": 2,
            "ref": 4,
            "alt": 5
        }

        bframe = adagenes.TXTReader().read_file(input_file, genome_version=genome_version, mapping=mapping, sep="\t")
        adagenes.AVFWriter().write_to_file(outfile, bframe)
