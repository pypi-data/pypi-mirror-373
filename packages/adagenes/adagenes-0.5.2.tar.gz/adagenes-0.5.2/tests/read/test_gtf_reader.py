import unittest, os
import adagenes


class TestGTFReader(unittest.TestCase):

    def test_read_gtf(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file= __location__ + "/../test_files/sample.gtf"
        bframe = adagenes.GTFReader().read_file(input_file)
        print(len(bframe.data.keys()))
        print(bframe.data)
        #self.assertEqual(len(bframe.data.keys()),48,"Wrong number of biomarkers loaded")
        #self.assertEqual(bframe.genome_version,"hg38","Could not read genome version")



