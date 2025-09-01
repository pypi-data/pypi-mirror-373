import unittest
import adagenes as ag


class TestIdentifyBiomarkers(unittest.TestCase):

    def test_identify_wt(self):
        data = {"chr10:8115914C>.": {}}
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        self.assertEqual(bframe.data["chr10:8115914C>."]["mdesc"], "genomic_location", "")

    def test_identify_biomarkers(self):
        biomarker_type, groups = ag.get_variant_request_type("BRAF:V600E")
        #print("BRAF: ",biomarker_type,": ",groups)
        self.assertEqual(biomarker_type, "gene_name_aa_exchange", "")
        self.assertEqual(groups[3], "600", "")

        data = {"TP53":{}, "chr7:140753336A>T":{}, "BRAF:p.V600E":{}, "CRTAP:c.320_321del": {}}
        bframe= ag.BiomarkerFrame(data,genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        #print(bframe.data)
        self.assertEqual(list(bframe.data.keys()),["TP53","chr7:140753336A>T","BRAF:V600E", "CRTAP:c.320_321del"],"")
        self.assertEqual(bframe.data["CRTAP:c.320_321del"]["mutation_type"],"indel","")

    def test_transcript_cdna_recognition(self):
        data = {"NM_000546.6:c.844C>T":{}}
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        #print(bframe.data)

    def test_protein_recognition(self):
        data = {"TP53:p.Arg282Trp":{}}
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        #print(bframe.data)
        self.assertEqual(bframe.data["TP53:R282W"]["mutation_type_desc"], "SNP","")
        self.assertEqual(bframe.data["TP53:R282W"]["mutation_type_detail"], "Missense_Mutation", "")

    def test_identify_insertion(self):
        data = {"chr1:g.1234_1235insACGT": {}}
        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        #print(bframe.data)
        self.assertEqual(bframe.data["chr1:g.1234_1235insACGT"]["mdesc"],"insertion_long","")
        self.assertEqual(bframe.data["chr1:g.1234_1235insACGT"]["mutation_type"], "indel", "")
        self.assertEqual(bframe.data["chr1:g.1234_1235insACGT"]["type"], "g", "")

    def test_identify_protein_fs(self):
        qid = "BRAF:p.L400fs"
        mtype = ag.get_variant_request_type(qid)
        #print(mtype)
        self.assertEqual(mtype[0],"gene_name_aa_exchange_fs","")

    def test_identify_protein_fs_long(self):
        mtype = ag.get_variant_request_type("BRAF:p.Leu400PhefsTer")
        #print(mtype)
        self.assertEqual(mtype[0],"gene_name_aa_exchange_long_fs","")

    def test_identify_protein_del_short(self):
        mtype = ag.get_variant_request_type("BRAF:p.Leu400del")
        #print(mtype)
        self.assertEqual(mtype[0],"gene_name_aa_exchange_long_fs_short","")

    def test_identify_transcript_identifier(self):
        data = {"NM_004985.5:c.35G>A":{}}
        mtype = ag.get_variant_request_type("NM_004985.5:c.35G>A")
        #print(mtype)
        self.assertEqual(mtype[0], "transcript_cdna", "")

        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        #print(bframe.data)
        self.assertEqual(bframe.data["NM_004985.5:c.35G>A"]["mutation_type"],"snv","")
        self.assertEqual(bframe.data["NM_004985.5:c.35G>A"]["type"], "c", "")

        data = {"NM_004985.5:C.35G>A": {}}
        mtype = ag.get_variant_request_type("NM_004985.5:c.35G>A")
        #print(mtype)
        self.assertEqual(mtype[0], "transcript_cdna", "")

        bframe = ag.BiomarkerFrame(data, genome_version="hg38")
        bframe = ag.tools.identify_biomarkers(bframe)
        #print(bframe.data)
        self.assertEqual(bframe.data["NM_004985.5:C.35G>A"]["mutation_type"], "snv", "")
        self.assertEqual(bframe.data["NM_004985.5:C.35G>A"]["type"], "c", "")

    def test_identify_cna(self):
        qid = "chr1:1234_1235del"
        data = {qid}
        mtype = ag.get_variant_request_type(qid)
        # print(mtype)
        self.assertEqual(mtype[0], "deletion_long", "")

    def test_identify_del(self):
        qid = "chr7:140753336del"
        data = {qid}
        mtype, groups = ag.get_variant_request_type(qid)
        print(list(groups))
        self.assertEqual(mtype, "deletion", "")

    def test_identify_chrompos(self):
        qid = "chr7:140753336"
        data = {qid}
        mtype, groups = ag.get_variant_request_type(qid)
        print(list(groups))
        self.assertEqual(mtype, "chrom_position", "")

    def test_identify_cna2(self):
        qid = "chr1:1234-1235_DEL"
        data = {qid}
        mtype = ag.get_variant_request_type(qid)
        # print(mtype)
        self.assertEqual(mtype[0], "cnv_del", "")


