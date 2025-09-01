import json
import adagenes.clients.reader as reader
import adagenes


class JSONReader(reader.Reader):

    def read_file(self, infile, genome_version=None, columns=None,
                  start_row=None, end_row=None):
        if type(infile) is str:
            infile = open(infile, 'r')

        json_obj = adagenes.BiomarkerFrame()
        json_obj.data = json.load(infile)
        if 'vcf_header' in json_obj.data.keys():
            json_obj.data.pop('vcf_header')
        infile.close()

        return json_obj

    def read_file_chunk(self, infile, json_obj):
        biomarker_data = json.load(infile)
        if 'vcf_header' in biomarker_data.keys():
            biomarker_data.pop('vcf_header')
        #for i, key in enumerate(biomarker_data.keys()):
        #    biomarker_data[i] = key
        json_obj.data = biomarker_data

        return json_obj
