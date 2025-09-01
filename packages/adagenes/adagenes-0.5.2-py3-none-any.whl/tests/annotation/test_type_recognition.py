import unittest
import adagenes as ag

class TestVariantTypeRecognition(unittest.TestCase):

    def test_type_recognition(self):
        genome_version = 'hg19'
        data = {"chr7:140753336A>T": {}, "chr12:25245350C>T": {}}
        infile = "../test_files/somaticMutations.l12.txt"

        #bframe = adagenes.BiomarkerFrame(data=data, genome_version=genome_version)
        #bframe = adagenes.recognize_biomarker_types(bframe)
        #data = adagenes.TXTReader(genome_version).read_file(infile)
        #data = adagenes.TypeRecognitionClient(genome_version).process_data(data.data)
        print(data)
        #self.assertEqual()

    def test_position_recognition(self):
        genome_version = 'hg19'
        pos = "chr12:25245350"

        #bframe = ag.BiomarkerFrame(data=data, genome_version=genome_version)

        biomarker_type, groups = ag.get_variant_request_type(pos)
        #bframe = adagenes.recognize_biomarker_types(bframe)
        #data = adagenes.TXTReader(genome_version).read_file(infile)
        #data = adagenes.TypeRecognitionClient(genome_version).process_data(data.data)
        print(groups)
        self.assertEqual(biomarker_type, "chrom_position", "")
        self.assertEqual(groups[3], '25245350', "")


