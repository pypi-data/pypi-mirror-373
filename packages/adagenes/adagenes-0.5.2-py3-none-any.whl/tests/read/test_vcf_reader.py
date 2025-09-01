import unittest, os
import adagenes as ag
from adagenes.tools.client_mgt import get_reader, get_writer


class TestVCFReader(unittest.TestCase):

    def test_vcf_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        infile = __location__ + "/../test_files/somaticMutations.ln_4.vcf"
        bframe = ag.read_file(infile, genome_version=genome_version)
        #print(list(bframe.data.keys())[0])
        #print(bframe)
        self.assertEqual(len(list(bframe.data.keys())), 5, "")

        self.assertEqual("chr12:25245350C>T",list(bframe.data.keys())[0],"")
        self.assertEqual("12", bframe.data["chr12:25245350C>T"]["variant_data"]["CHROM"], "")

        self.assertEqual("chr12:25245350C>T", list(bframe.data.keys())[0], "")
        self.assertEqual("12", bframe.data["chr12:25245350C>T"]["variant_data"]["CHROM"], "")

        self.assertEqual("chr12:25245350C>T", list(bframe.data.keys())[0], "")
        self.assertEqual("25245350", bframe.data["chr12:25245350C>T"]["variant_data"]["POS_hg19"], "")

        self.assertEqual("snv", bframe.data["chr12:25245350C>T"]["mutation_type"], "")

        self.assertEqual(bframe.max_variants,5,"")

    def test_vcf_reader2(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.ln50.vcf"
        reader = ag.VCFReader()
        json_obj = reader.read_file(input_file)
        print(json_obj.data)
        #print(len(json_obj.data.keys()))
        self.assertEqual(len(json_obj.data.keys()),48,"Variant size does not match")
        self.assertEqual(json_obj.data['chr10:8115913C>T']["mutation_type_detail"],"Missense_Mutation","")
        self.assertEqual(json_obj.data["chr7:21784211insG"]["mutation_type"], "indel", "")
        self.assertEqual(json_obj.data["chr7:21784211insG"]["mutation_type_detail"],"Frame_Shift_Ins","")

        self.assertEqual(json_obj.max_variants, 48, "")

    def test_vcf_reader_recognition(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.ln50.vcf"
        reader = get_reader(input_file)
        json_obj = reader.read_file(input_file)
        #print(json_obj.data)

    def test_vcf_reader_annotated_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.l520.protein.vcf"
        reader = get_reader(input_file)
        bframe = reader.read_file(input_file)
        #print(json_obj.data.keys()[0].keys())
        #print(bframe.data)

        self.assertEqual(len(list(bframe.data.keys())),481,"")

    def test_vcf_reader_special_chars(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/cl_sample.vcf"
        reader = get_reader(input_file)
        bframe = reader.read_file(input_file)
        # print(json_obj.data.keys()[0].keys())
        print(bframe.data)

        self.assertEqual(len(list(bframe.data.keys())), 22, "")
        self.assertEqual(bframe.data["chr20:62709342C>T"]["info_features"]["UTA_Adapter_variant_exchange"],"R45=","")
        self.assertEqual(bframe.data["chrX:32364705G>C"]["info_features"]["UTA_Adapter_variant_exchange"], "Y1677*", "" )

    def test_read_cnvs(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/cnv_sample.vcf"
        bframe = ag.read_file(input_file)

        print(bframe.data.keys())
        print(bframe.data)

        cna_id = "chr1:258946-714338_DEL"

        self.assertEqual(len(list(bframe.data.keys())),1,"")
        self.assertEqual(bframe.data[cna_id]["type"], "g", "")
        self.assertEqual(bframe.data[cna_id]["mutation_type"], "cnv", "")
        self.assertEqual(bframe.data[cna_id]["mdesc"],"cnv_del","")
