import unittest, os
import adagenes as ag


class AVFProcessorTestCase(unittest.TestCase):

    #def test_processor_avf_writer(self):
    #    __location__ = os.path.realpath(
    #        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    #    infile = __location__ + "/../test_files/somaticMutations.l100.vcf"
    #    outfile = infile + ".anno.avf"

    #    ag.process_file(infile, outfile, ag.LiftoverClient(genome_version="hg19", target_genome="hg38"), writer=ag.AVFWriter(genome_version="hg19"))
    #    bframe = ag.read_file(outfile)

    #    self.assertEqual(str(bframe.data["chr7:21744592insG"]["variant_data"]["POS_hg19"]), "21784210", "")
    #    self.assertEqual(str(bframe.data["chr7:21744592insG"]["variant_data"]["POS_hg38"]), "21744592", "")

    def test_processor_vcf_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.l100.vcf"
        outfile = infile + ".anno.vcf"

        bframe = ag.read_file(infile, genome_version="hg19")
        print(bframe.data.keys())
        print(bframe.data)
        print(bframe.data["chr7:21784211insG"])
        self.assertEqual(str(bframe.data["chr7:21784211insG"]["variant_data"]["POS_hg19"]), '21784211', "")
        self.assertEqual(len(bframe.data), 97, "")

        ag.process_file(infile, outfile, ag.LiftoverClient(genome_version="hg19", target_genome="hg38"))
        bframe = ag.read_file(outfile)
        print(bframe.data.keys())

        print(bframe.data["chr7:21744594insG"])
        self.assertEqual(str(bframe.data["chr7:21744594insG"]["info_features"]["POS_hg38"]), '21744593', "")
        self.assertEqual(len(bframe.data),97,"")

