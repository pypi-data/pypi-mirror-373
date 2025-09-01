import os, unittest
import adagenes as ag

class VCFTest(unittest.TestCase):

    def test_vcf_reader_annotated_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/Merged_Data.vcf"
        #reader = ag.get_reader(input_file)
        #bframe = reader.read_file(input_file)
        # print(json_obj.data.keys()[0].keys())
        # print(bframe.data)

        #self.assertEqual(len(list(bframe.data.keys())), 489, "")
