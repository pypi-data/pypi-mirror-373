import unittest, os
import adagenes
from adagenes.conf import read_config as conf_reader


class TestTSVWriter(unittest.TestCase):

    def test_tsv_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'
        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        outfile = __location__ + "/../test_files/test_tsv.tsv"

        obj = adagenes.BiomarkerFrame()
        obj.data = data
        print(data)

        # write in file
        adagenes.TSVWriter().write_to_file(outfile, obj)

    def test_tsv_writer_custom_mapping(self):
        genome_version = 'hg19'
        data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        outfile = "../test_files/tsvwriter_custom_mapping.tsv"

        custom_mapping = { conf_reader.revel_srv_prefix: ["Score"],
                 conf_reader.mvp_srv_prefix: ["Score"]
                 }

        obj = adagenes.BiomarkerFrame()
        obj.data = data

        # write in file
        #adagenes.TSVWriter().write_to_file(outfile,obj,mapping=custom_mapping)

