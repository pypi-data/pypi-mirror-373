import unittest, os
import adagenes as ag


class TestCSVReader(unittest.TestCase):

    def test_csv_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        infile = __location__ + "/../test_files/somaticMutations.ln50.revel.csv"
        mapping = {""}
        bframe = ag.read_file(infile, genome_version=genome_version)
        print(list(bframe.data.keys())[0])
        print("bframe ",bframe.data)

        self.assertEqual("chr7:21744593insG",list(bframe.data.keys())[0],"")
        self.assertEqual("7", bframe.data["chr7:21744593insG"]["variant_data"]["CHROM"], "")

        self.assertEqual("chr7:21744593insG", list(bframe.data.keys())[0], "")
        self.assertEqual("7", bframe.data["chr7:92029936A>G"]["variant_data"]["CHROM"], "")

    def test_csv_protein_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/tp53_mutations.csv"
        reader = ag.get_reader(input_file)
        json_obj = reader.read_file(input_file)
        print("Protein data: ",json_obj.data)
        print(len(json_obj.data.keys()))
        self.assertEqual(len(json_obj.data.keys()),12,"Error reading protein data")

    def test_read_custom_csv(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/tp53_tumor_variants.csv"
        reader = ag.get_reader(input_file)
        mapping = {"CHROM": "<DEF>17", "POS": "hg38_Chr17_coordinates", "g_description": "g_description_GRCh38"}
        json_obj = reader.read_file(input_file,mapping=mapping,genome_version="hg38")
        print("Protein data: ", json_obj.data)
        print(len(json_obj.data.keys()))
        self.assertEqual(json_obj.data["chr17:7675184A>G"]["ExonIntron"],"5-exon", "")

    def test_read_custom_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/CDX30_F3.csv"
        #reader = ag.get_reader(input_file)
        #mapping = {"CHROM": "<DEF>17", "POS": "hg38_Chr17_coordinates", "g_description": "g_description_GRCh38"}
        #json_obj = reader.read_file(input_file, mapping=mapping, genome_version="hg38")
        
        bframe = ag.read_file(input_file)
        
        #print("Protein data: ", json_obj.data)
        #print(len(json_obj.data.keys()))
        #self.assertEqual(json_obj.data["chr17:7675184A>G"]["ExonIntron"], "5-exon", "")
        print(bframe.data)
        self.assertEqual(list(bframe.data.keys()),['KRAS:G12D', 'ROBO2:P1194S', 'TP53:G59*'],"")

    def test_read_protein_csv(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/tp53_mutations2.csv"
        mapping = {"gene": "genename", "variant": "variantname"}
        bframe = ag.read_file(input_file, mapping=mapping)

        print(bframe.data)
        self.assertEqual(bframe.data,{},"")
