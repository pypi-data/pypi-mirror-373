import unittest, os
import adagenes as av


class TestFileTypeTestCase(unittest.TestCase):

    def test_file_type_recognition(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.ln50.vcf"
        file_type = av.get_file_type(input_file)
        self.assertEqual("vcf",file_type,"")
