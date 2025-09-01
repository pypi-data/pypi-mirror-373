import unittest, os
import adagenes


class TestAVFReader(unittest.TestCase):

    def test_read_avf(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file= __location__ + "/../test_files/somaticMutations.ln50.avf"
        bframe = adagenes.AVFReader().read_file(input_file)
        print(len(bframe.data.keys()))
        self.assertEqual(len(bframe.data.keys()),48,"Wrong number of biomarkers loaded")
        self.assertEqual(bframe.genome_version,"hg38","Could not read genome version")

    def test_read_avf_ln250(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file= __location__ + "/../test_files/somaticMutations_brca_ln250.avf"
        bframe = adagenes.AVFReader().read_file(input_file)
        print(len(bframe.data.keys()))
        self.assertEqual(len(bframe.data.keys()),235,"Wrong number of biomarkers loaded")
        self.assertEqual(bframe.genome_version,"hg19","Could not read genome version")

