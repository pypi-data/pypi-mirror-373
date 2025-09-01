import unittest, os
import adagenes as ag


class TestStreamBasedCSV(unittest.TestCase):

    def test_stream_based_csv(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations_cclab_brca.vcf"
        outfile = __location__ + "/../test_files/somaticMutations_cclab_brca.csv"

        client = None

        ag.process_file(infile, outfile, client, genome_version="hg19", writer=ag.CSVWriter(), output_format="csv")

        bframe = ag.read_file(infile, input_format="vcf")
        self.assertEqual(len(list(bframe.data.keys())), 10046, "")

        bframe = ag.read_file(outfile,input_format="csv")
        #self.assertEqual(len(list(bframe.data.keys())), 10017,"")


    def test_stream_based_csv_annotation(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations_cclab_brca.vcf"
        outfile = __location__ + "/../test_files/somaticMutations_cclab_brca.liftoveranno.csv"

        client = ag.LiftoverAnnotationClient(genome_version="hg19",target_genome="t2t")

        ag.process_file(infile, outfile, client, genome_version="hg19", writer=ag.CSVWriter(), output_format="csv")

        bframe = ag.read_file(infile, input_format="vcf")
        self.assertEqual(len(list(bframe.data.keys())), 10046, "")

        bframe = ag.read_file(outfile, input_format="csv")
        #self.assertEqual(len(list(bframe.data.keys())), 10017,"")


