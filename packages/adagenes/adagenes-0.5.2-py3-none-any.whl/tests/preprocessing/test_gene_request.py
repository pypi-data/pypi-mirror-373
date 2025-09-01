import unittest
import adagenes.tools.preprocessing
import adagenes.tools.hgvs_re

class TestGeneRequest(unittest.TestCase):

    def test_gene_request(self):
        q="TP53"
        request = adagenes.tools.preprocessing.identify_query_parameters(q, None, None)
        lt = (["TP53"],[],[], [], [],[])
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

