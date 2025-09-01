import unittest, os
from adagenes.tools.client_mgt import get_reader, get_writer
from adagenes.clients import VCFReader, VCFWriter


class TestVCF2CSVReaderWriter(unittest.TestCase):

    def test_vcf2csv_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.ln100.vcf"
        #reader = VCFReader()
        #json_obj = reader.read_file(input_file)
        #print(json_obj.data)