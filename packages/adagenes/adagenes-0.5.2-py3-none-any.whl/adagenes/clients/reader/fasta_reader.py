import re, gzip
import adagenes.clients.reader as reader
import adagenes.conf.read_config as config
from adagenes.tools import parse_vcf
import adagenes
import adagenes.conf.vcf_config
import adagenes.tools.data_io


class FASTAReader(reader.Reader):
    """
    Reader for reading data in FASTA format
    """

    def read_file(self, infile, file_reader=None, genome_version=None, columns=None,sep=None,
                  mapping=None, remove_quotes=True,start_row=None, end_row=None):
        """

        :param infile:
        :param file_reader:
        :param genome_version:
        :param columns:
        :return:
        """

        if type(infile) is str:
            #file_extension = adagenes.tools.get_file_type(infile)
            if file_reader is not None:
                if file_reader == 'gtf':
                    infile = open(infile, 'r')
                else:
                    infile = open(infile, 'r')
            else:
                if adagenes.tools.data_io.is_gzip(infile):
                    infile = gzip.open(infile, 'rt')
                else:
                    infile = open(infile, 'r')

        json_obj = adagenes.BiomarkerFrame()
        json_obj.header_lines = []
        json_obj.data = {}
        json_obj.info_lines = {}
        json_obj.genome_version = genome_version
        variant_count = 0
        line_count = 0
        json_obj.variants = {}
        json_obj.format="fasta"

        active_seq_id=""

        for line in infile:
            if line.startswith('>'):
                seq_id = line.lstrip(">").rstrip("\n")
                json_obj.data[seq_id] = {}
                active_seq_id = seq_id
                continue
            else:
                variant_count += 1
                line_count += 1

            if "sequence" not in json_obj.data[active_seq_id]:
                json_obj.data[active_seq_id]["sequence"] = line.rstrip("\n")
            else:
                # Append amino acid sequence to existing sequence
                json_obj.data[active_seq_id]["sequence"] += line.rstrip("\n")

        infile.close()

        return json_obj


