import unittest
import adagenes

class TestVariantTypeRecognitionProtein(unittest.TestCase):

    def test_transcript_recognition(self):
        input_var="NM_000551.4:c.293A>G"
        request, groups = adagenes.get_variant_request_type(input_var)

        print(request)
        print("groups ",groups)
        self.assertEqual(request,"transcript_cdna","")
