from numpy import bool_

import adagenes.conf.read_config as conf_reader
import adagenes.clients.writer as writer
import adagenes
import traceback, csv, copy, json
import numpy as np


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, bool):
            return str(obj)
        if isinstance(obj, bool_):
            return str(obj)
        return super(NpEncoder, self).default(obj)

class AVFWriter(writer.Writer):

    def __init__(self, genome_version=None):
        self.genome_version= genome_version

    def write_to_file(self, outfile,
                      json_obj: adagenes.BiomarkerFrame,
                      genome_version="hg38",
                      mapping=None,
                      labels=None,
                      ranked_labels=None,
                      sep=',',
                      export_features=None):
        close_file = False
        if isinstance(outfile, str):
            outfile = open(outfile, 'w')
            close_file = True

        # Write header lines
        print("# GENOME_VERSION=" + str(json_obj.genome_version), file=outfile)

        # Write main data
        print(json.dumps(json_obj.data, cls=NpEncoder), file=outfile)

        print("\n", file=outfile)

        if close_file is True:
            outfile.close()

    def write_chunk_to_file(self, outfile, vcf_lines, c, srv_prefix, extract_keys, variants_written=False,
                            save_headers=False, first_chunk=False, last_chunk=False,
                            mapping=None,
                            ranked_labels=None,
                            labels=None,
                            ):
        """

        :param outfile:
        :param vcf_lines:
        :param c:
        :param srv_prefix:
        :param extract_keys:
        :param variants_written:
        :param save_headers:
        :return:
        """
        #if first_chunk is True:
        #    print("{", file=outfile)

        #print("write avf to file ",vcf_lines)
        for var in vcf_lines.keys():
            json_str = json.dumps(vcf_lines[var])
            # json_str = json_str.lstrip('{').rstrip('}')
            json_str = "\"" + var + "\"" + ":" + json_str
            if c < len(vcf_lines):
                json_str = json_str + ','
            # else:
            #    json_str = json_str + '}'

            c += 1

            print(json_str, file=outfile)

        #if last_chunk is True:
        #    print("}", file=outfile)

    def post_process(self, outfile):
        print("}", file=outfile)

    def pre_process(self, outfile,ranked_labels=None):
        print("# GENOME_VERSION=" + str(self.genome_version), file=outfile)
        print('{', file=outfile)

