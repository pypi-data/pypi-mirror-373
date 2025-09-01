import json
import adagenes.conf.read_config as config
import adagenes.clients.writer as writer
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


class JSONWriter(writer.Writer):

    def write_to_file(self, outfile, json_obj, save_headers=False, header_lines=None, c=1):
        if type(outfile) is str:
            outfile = open(outfile, 'w')

        print('{', file=outfile)

        num_vars = len( list(json_obj.data.keys()) )
        for var in json_obj.data.keys():
            json_str = json.dumps(json_obj.data[var], cls=NpEncoder)
            json_str = "\"" + var + "\"" + ":" + json_str
            if c < num_vars:
                json_str = json_str + ','
            print(json_str, file=outfile)
            c += 1
        #json_str = json_str.rstrip(",")

        # add VCF header
        if save_headers:
            data = {}
            data[config.vcf_header_key] = header_lines

            print('{', file=outfile)
            json_str = json.dumps(data[config.vcf_header_key])
            json_str = ", \"" + config.vcf_header_key + "\"" + ":" + json_str
            if c < len(data):
                json_str = json_str + ','
            json_str = json_str.rstrip(",")
            print(json_str, file=outfile)

        print('}', file=outfile)
        outfile.close()

    def write_to_file_start(self, outfile):
        print('{', file=outfile)

    def write_to_file_finish(self, outfile, c=0, input_format='json', save_header=False, header_lines=None):
        if (input_format == 'vcf') and save_header:
            data = {}
            data[config.vcf_header_key] = header_lines

            print('{', file=outfile)
            json_str = json.dumps(data[config.vcf_header_key])
            json_str = ", \"" + config.vcf_header_key + "\"" + ":" + json_str
            if c < len(data):
                json_str = json_str + ','
            json_str = json_str.rstrip(",")
            print(json_str, file=outfile)

        print('}', file=outfile)

    def write_chunk_to_file(self, outfile, json_obj,c=1,variants_written=False, save_headers=False, header_lines=None):
        if variants_written:
            print(',', file=outfile, end='')

        num_vars = len(list(json_obj.data.keys()))
        for var in json_obj.data.keys():
            json_str = json.dumps(json_obj.data[var])
            json_str = "\"" + var + "\"" + ":" + json_str
            if c < num_vars:
                json_str = json_str + ','
            print(json_str, file=outfile)
            c += 1

    def to_json(self, json_obj, outfile_str: str):
        """
        Writes variant data in JSON format into a JSON output file

        :param json_obj:
        :param outfile_str:
        :return:
        """
        outfile = open(outfile_str, 'rw')
        json.dumps(json_obj, file=outfile)
        outfile.close()

