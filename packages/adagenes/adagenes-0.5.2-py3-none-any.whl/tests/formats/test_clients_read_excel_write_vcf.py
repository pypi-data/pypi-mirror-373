import json
import unittest
import adagenes


class TestTSVClients(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTSVClients, self).__init__(*args, **kwargs)
        self.output_format='tsv'
        self.input_file = '../test_files/somaticMutations.l8.xlsx'
        self.output_file = '../test_files/somaticMutations.l8.xlsx.json'

    def test_load_excel_file(self):
        #biomarker_data = adagenes.clients.XLSXReader().read_file(self.input_file, sep='\t', genome_version='hg38')
        #print(biomarker_data.data)
        #adagenes.clients.JSONWriter().write_to_file(self.output_file, biomarker_data)
        pass
