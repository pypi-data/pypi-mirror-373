import unittest, os
import adagenes


class TestGenericWriter(unittest.TestCase):


    def test_get_mapping(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.vcf"
        bframe = adagenes.read_file(infile)
        #print(bframe.data)
        mapping = { "variant_data": ["CHROM",'POS'] }
        labels = []
        features = []
        for var in bframe.data.keys():
            values = adagenes.clients.get_row_values(bframe.data[var], mapping=mapping)
            self.assertListEqual(list(values.keys()),["variant_data_CHROM","variant_data_POS"],"Error testing mapping")

    def test_labels(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.vcf"
        bframe = adagenes.read_file(infile)
        #print(bframe.data)
        mapping = { "variant_data": ["CHROM",'POS'] }
        labels = { "CHROM":"variant_data_CHROM","POS":"variant_data_POS" }
        ranked_labels = ["CHROM","POS"]
        for var in bframe.data.keys():
            values = adagenes.clients.get_row_values(bframe.data[var], mapping=mapping)
            row = adagenes.clients.get_sorted_values(values, labels=labels, ranked_labels=ranked_labels)
            self.assertListEqual(list(values.keys()),["variant_data_CHROM","variant_data_POS"],"Error testing mapping")
            print(row)

    def test_generic_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.vcf"
        bframe = adagenes.read_file(infile)
        outfile = __location__ + "/../test_files/somaticMutations.ln50.custom_mapping.csv"
        mapping = { "variant_data": ["CHROM",'POS'] }
        labels = { "CHROM":"variant_data_CHROM","POS":"variant_data_POS" }
        ranked_labels = ["CHROM","POS"]
        adagenes.write_file(outfile, bframe, mapping=mapping, labels=labels, ranked_labels=ranked_labels)

    def test_get_writer(self):
        outfile = "test.csv"
        writer = adagenes.get_writer(outfile)
        self.assertIsInstance(writer, adagenes.CSVWriter)

