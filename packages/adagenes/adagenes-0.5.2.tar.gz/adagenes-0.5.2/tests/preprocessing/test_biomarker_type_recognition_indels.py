import unittest
import adagenes.tools.preprocessing


class TestBiomarkerRecognitionInDels(unittest.TestCase):

    #def test_insertion_vcf_recognition(self):
    #    q = "chr7:21784210A>AG"
    #    request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
    #    print(request)
    #    lt = ("insfd")
    #    self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_deletion_recognition(self):
        q="chr11:1234del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("deletion")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_deletion_refseq_recognition(self):
        q="chr11:g.1234del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("deletion")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_deletion_nc_recognition(self):
        q="NC_000001.11:1234del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("deletion_nc")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_deletion_nc_refseq_recognition(self):
        q="NC_000001.11:g.1234del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("deletion_nc")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_deletion_nc_refseq_recognition_longdel(self):
        q="NC_000001.11:g.1234_2345del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("deletion_nc_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_insertion_recognition(self):
        q="chr11:g.1234_1235insACGT"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("insertion_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_insertion_refseq_recognition(self):
        q="chr11:g.1234_1235insACGT"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("insertion_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_insertion_nc_recognition(self):
        q="NC_000001.11:1234_1235insACGT"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("insertion_nc_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_insertion_nc_refseq_recognition(self):
        q="NC_000001.11:g.1234_1235insACGT"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("insertion_nc_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_indel_recognition(self):
        q="chr11:123delinsAC"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("indel")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_indel_refseq_recognition(self):
        q="chr1111:g.123delinsAC"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("indel")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_indelnc_recognition(self):
        q="NC_000001.11:123delinsAC"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("indel_nc")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_indel_nc_refseq_recognition(self):
        q="NC_000001.11:g.123delinsAC"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("indel_nc")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_indel_nc_refseq_recognition_longdel(self):
        q="NC_000001.11:g.123_129delinsAC"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("indel_nc_long")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))


