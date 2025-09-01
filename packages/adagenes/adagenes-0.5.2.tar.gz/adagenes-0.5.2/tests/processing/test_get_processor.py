import unittest
import adagenes as ag


class GetProcessorTestCase(unittest.TestCase):

    def test_get_processor(self):
        infile="mutations.vcf"
        processor = ag.get_processor(infile)
        print(processor)
        self.assertIsInstance(processor, ag.clients.processor.vcf_processor.VCFProcessor, "")

    #def test_get_avf_processor(self):
    #    infile="mutations.vcf.GRCh38.avf"
    #    processor = ag.get_processor(infile)
    #    print(processor)
    #    self.assertIsInstance(processor, ag.clients.processor.avf_processor.AVFProcessor, "")

