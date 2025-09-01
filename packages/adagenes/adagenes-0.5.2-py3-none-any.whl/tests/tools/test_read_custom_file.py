import unittest
import os
import adagenes as ag


class TestIdentifyBiomarkers(unittest.TestCase):

    def test_identify_wt(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/custom_sample.csv"
        mapping = { "CHROM": 1, "POS": 2, "POS2": 3 }
        bframe = ag.read_file(infile, mapping=mapping)
        print(bframe.data)
