import unittest, os
import adagenes as ag


class TestStreamBasedFiltering(unittest.TestCase):

    def test_stream_based_filtering(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.vcf"
        outfile = infile + ".anno.csv"

        client = ag.FeatureFilter()

        ag.process_file(infile, outfile, client, filter=["revel","0.6", ">"], genome_version="hg19")
