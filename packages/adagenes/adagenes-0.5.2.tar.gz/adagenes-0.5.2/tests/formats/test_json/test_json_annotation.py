import unittest, os
import adagenes


class TestJSONAnnotation(unittest.TestCase):

    def test_json_annotation(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.l8.vcf.json"
        outfile = __location__ + '/../../test_files/somaticMutations.l8.vcf.dbsnp.json'

        writer = adagenes.JSONWriter()
        reader = adagenes.JSONReader()
        #json_obj = reader.read_file(input_file)
        #writer.write_to_file(outfile, json_obj.data)

    def test_json_annotation_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.ln_12.vcf.json"
        outfile = __location__ + '/../../test_files/somaticMutations.ln_12.vcf.dbsnp.json'
        genome_version="hg19"
