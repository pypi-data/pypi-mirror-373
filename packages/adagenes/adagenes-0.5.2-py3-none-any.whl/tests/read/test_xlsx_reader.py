import unittest, os
import adagenes as ag


class TestXLSXReader(unittest.TestCase):

    def test_excel_reader(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        file = __location__ + "/../test_files/somaticMutations.ln50.revel.xlsx"
        bframe = ag.read_file(file)
        print(bframe)
        #self.assertEqual(bframe.data[])


