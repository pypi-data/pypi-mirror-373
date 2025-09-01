import unittest, os
import adagenes as ag


class TestVCFWriter(unittest.TestCase):

    def test_bed_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/sample_brca.vcf"
        bframe = ag.read_file(infile)
        outfile = __location__ + "/../test_files/sample_brca.bed"
        ag.write_file(outfile, bframe)

        file = open(outfile)
        contents = file.read()
        contents_expected = ('chr7\t21784210\t21784210\tchr7:21784210-21784210\n'
 'chr10\t8115912\t8115913\tchr10:8115912-8115913\n'
 'chr17\t7681743\t7681744\tchr17:7681743-7681744\n'
 'chr1\t144886114\t1')
        self.assertEqual(contents[0:150], contents_expected, "")
        file.close()


