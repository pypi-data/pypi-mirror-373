import unittest, os
import adagenes as av

class TestJSONReaderWriter(unittest.TestCase):

    def test_json_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.ln50.vcf"
        #reader = JSONReader()
        #data = reader.read_file(input_file)
        #print(data)

    def test_json_reader_recognition(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.ln50.vcf"
        #reader = get_reader(input_file)
        #data = reader.read_file(input_file)
        #print(data)

    def test_json_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.ln50.vcf"
        outfile = __location__ + '/../../test_files/somaticMutations.ln50.vcf.json'

        writer = av.JSONWriter()
        reader = av.VCFReader()
        data = reader.read_file(input_file)
        writer.write_to_file(outfile, data)

