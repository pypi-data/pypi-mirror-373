import unittest, os
import adagenes


class TestTXT2CSV(unittest.TestCase):

    def test_txt2csv_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../../test_files/somaticMutations.ln50.txt"
        outfile = __location__ + "/../../test_files/somaticMutations.ln50.test.csv"
        reader = adagenes.TXTReader()
        mapping = {
            "chrom": 1,
            "pos": 2,
            "ref": 4,
            "alt": 5
        }
        bframe = reader.read_file(input_file,mapping=mapping,sep="\t")
        adagenes.CSVWriter().write_to_file(outfile, bframe)
