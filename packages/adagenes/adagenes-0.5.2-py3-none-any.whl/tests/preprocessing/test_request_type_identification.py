import unittest
import adagenes


class TestRequestTypeIdentification(unittest.TestCase):

    def test_request_type_identification_genomic_location_nc_refseq(self):
        q = "NC_000007.14:g.140753336A>T"
        res = adagenes.tools.identify_query_parameters(q)
        print(res)
        lt = ([],[],[],['chr7:140753336A>T'],[],[])
        self.assertEqual(res, lt, "Did not match query identification, should be " + str(lt))

    def test_request_type_identification_genomic_location_nc(self):
        q = "NC_000007.14:140753336A>T"
        res = adagenes.tools.identify_query_parameters(q)
        print(res)
        lt = ([],[],[],['chr7:140753336A>T'],[],[])
        self.assertEqual(res, lt, "Did not match query identification, should be " + str(lt))

    def test_request_type_identification_genomic_location_refseq(self):
        q = "chr7:g.140753336A>T"
        res = adagenes.tools.identify_query_parameters(q)
        print(res)
        lt = ([],[],[],['chr7:140753336A>T'],[],[])
        self.assertEqual(res, lt, "Did not match query identification, should be " + str(lt))

    def test_request_type_identification(self):
        #q = "FLT3:p.Gly533Asp"
        q = "FLT3:P.G533D"
        #q = "NRAS:p.Q61L"
        res = adagenes.tools.identify_query_parameters(q)
        print(res)

