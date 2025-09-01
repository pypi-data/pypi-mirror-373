import unittest
import adagenes.tools.preprocessing


class TestBiomarkerRecognitionTranscripts(unittest.TestCase):

    def test_transcript_gene_recognition(self):
        q = "CRTAP:c.320_321del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("del_transcript_gene_cdna_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_transcript_cdna_recognition(self):
        q = "NM_000546.6:c.844C>T"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("transcript_cdna")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

