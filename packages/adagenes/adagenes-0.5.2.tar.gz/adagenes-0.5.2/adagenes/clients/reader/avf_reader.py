import json, os, gzip
import traceback

import adagenes.clients.reader as reader
import adagenes


class AVFReader(reader.Reader):

    def read_file(self, infile, genome_version=None,mapping=None,sep="\t",
                  remove_quotes=True,start_row=None, end_row=None) \
            -> adagenes.BiomarkerFrame:
        """

        :param infile:
        :param genome_version:
        :param mapping:
        :param sep:
        :param remove_quotes:
        :param start_row:
        :param end_row:
        :return:
        """
        if isinstance(infile, str):
            file_name, file_extension = os.path.splitext(infile)
            input_format_recognized = file_extension.lstrip(".")
            if input_format_recognized == "gz":
                infile = gzip.open(infile, 'rt')
            else:
                infile = open(infile, 'r')

        bframe = adagenes.BiomarkerFrame()
        data_str = ""
        for line in infile:
            if line.startswith("#"):
                data_line = line.strip()
                data_line = data_line.lstrip("#")
                try:
                    key,val = data_line.split("=")
                    key = key.lower()
                    key = key.replace(" ","")
                    if key == "genome_version":
                        if genome_version is None:
                            bframe.genome_version = val
                        else:
                            bframe.genome_version = genome_version
                    elif key == "source_file":
                        bframe.src = val
                except:
                    print("Error: Could not parse header line: ",line)
                    print(traceback.format_exc())
            else:
                data_str += line.strip()
        try:
            data = json.loads(data_str)
        except:
            print("Error: Could not parse variant data")
            print(traceback.format_exc())
            data = {}
        bframe.data = data

        return bframe

