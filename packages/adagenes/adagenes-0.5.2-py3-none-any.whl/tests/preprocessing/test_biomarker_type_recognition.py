import unittest
import adagenes.tools.preprocessing


class TestBiomarkerRecognition(unittest.TestCase):

    def test_genome_position_nc_refseq_recognition(self):
        q="NC_000014.8:g.67885931T>G"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("genomic_location_nc_refseq")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_genome_position_nc_recognition(self):
        q="NC_000014.8:67885931T>G"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("genomic_location_nc")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_genome_position_refseq_recognition(self):
        q="chr14:g.67885931T>G"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("genomic_location_refseq")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_genome_position_recognition(self):
        q="chr14:67885931T>G"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("genomic_location")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_gene_name_recognition(self):
        q="TP53"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("gene_name")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_refseq_transcript_recognition(self):
        q="NM_001130009.2:c.905G>A"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("transcript_cdna")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_protein_recognition(self):
        q="BRAF:R735M"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("gene_name_aa_exchange")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_refseq_protein_recognition(self):
        q="NP_004976.2:p.Gly12Cys"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("refseq_protein")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_refseq_transcript_recognition2(self):
        q="NM_004985.5:c.34G>T"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("transcript_cdna")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_ensembl_protein_recognition(self):
        q="ENSP00000308495.3"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("ensembl_protein")
        self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_uniprot_accession_recognition(self):
        q="P01116"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
        lt = ("ensembl_protein")
        #self.assertEqual(request, lt, "Did not match query identification, should be " + str(lt))

    def test_short_indel_recognition(self):
        q="chr2:179220958del"
        request, groups = adagenes.tools.preprocessing.get_variant_request_type(q)
        print(request)
