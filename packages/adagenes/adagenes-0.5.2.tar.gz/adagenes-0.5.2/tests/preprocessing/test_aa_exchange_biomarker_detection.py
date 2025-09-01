import adagenes
import unittest


class TestAAExchangeBiomarkerTypeDetection(unittest.TestCase):

    def test_biomarker_recognition_aaexchange(self):
        data = {
            "chr1:2561824GGT>G": {},
            "chr7:140753336A>T": {},
            "chr10:63851203G>T": {},
            "chr10:8115724AGAAG>A": {},
            "chr10:8115928C>CA": {}
        }
        for var in data.keys():
            data[var] = adagenes.generate_variant_data_section(data[var], qid=var)
        data = adagenes.tools.get_biomarker_type_aaexchange(data)
        for qid in data:
            print("type: ",data[qid]["variant_data"]["type"])


