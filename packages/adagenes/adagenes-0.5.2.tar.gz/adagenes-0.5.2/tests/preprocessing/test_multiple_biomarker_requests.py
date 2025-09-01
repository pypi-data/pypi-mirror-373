import unittest
import adagenes.tools.preprocessing
import adagenes.tools.hgvs_re

class TestGeneRequest(unittest.TestCase):

    def test_gene_request(self):
        q="chr14:67885931T>G,TP53"
        #q="braf:val600glu,chr14:67885931T>G"
        request = adagenes.tools.preprocessing.identify_query_parameters(q)
        print(request)
        lt = (["TP53"],[],[], ["chr14:67885931T>G"],[],[])
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

