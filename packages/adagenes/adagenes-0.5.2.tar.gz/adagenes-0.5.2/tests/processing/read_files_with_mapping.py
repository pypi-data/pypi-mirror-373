import unittest, os
import adagenes as ag


class MappingTest(unittest.TestCase):

    def test_read_file_with_mapping(self):
        mapping = {"CHROM": "<DEF>17", "POS": "hg38_Chr17_coordinates", "g_description": "g_description_GRCh38"}

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file = __location__ + "/../test_files/tp53_sample_1.csv"

        bframe = ag.read_file(input_file, mapping=mapping, genome_version="hg38")
        print(bframe)
        self.assertListEqual(list(bframe.data.keys()),
                             ["chr17:7675184A>G",'chr17:7675088C>T','chr17:7675218T>G','chr17:7673767C>T',
                              'chr17:7674216C>G','chr17:7675156_7675157insN',
                              'chr17:7673773del', 'chr17:7675139_7675140del', 'chr17:7675158_7675159insN',
                              'chr17:7675215_7675216delinsAG', 'chr17:7675080_7675110del'
                              ],
                             "")

    def test_read_file_with_mapping_long_file(self):
        mapping = {"CHROM": "<DEF>17", "POS": "hg38_Chr17_coordinates", "g_description": "g_description_GRCh38"}

        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        input_file = __location__ + "/../test_files/tp53_sample.csv"

        bframe = ag.read_file(input_file, mapping=mapping, genome_version="hg38")
        print(bframe)
        #self.assertEqual(list(bframe.data.keys()), ["chr17:7675184A>G",'chr17:7675088C>T','chr17:7675218T>G','chr17:7673767C>T'],"")
