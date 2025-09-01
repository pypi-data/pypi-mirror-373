import unittest, os
import adagenes as ag


class FastaReaderTestCase(unittest.TestCase):

    def test_fasta_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/AVP.fasta"
        bframe = ag.read_file(infile)

        print(bframe.data)
        self.assertEqual(bframe.data[' AVP; NM_000490.5']["sequence"][0:3],"MPD","")
