import os, gzip
import adagenes.clients.reader as reader
import adagenes.conf.read_config as config
from adagenes.tools import parse_vcf
import adagenes
import adagenes.tools.maf_mgt


class MAFReader(reader.Reader):

    def __init__(self, *args, **kwargs):
        super(MAFReader, self).__init__(*args, **kwargs)

        self.maf_columns = adagenes.tools.maf_mgt.maf_columns
        self.maf_indices = adagenes.tools.maf_mgt.maf_column_indices

    def generate_column_indices(self, columns, json_obj):
        for i, col in enumerate(columns):
            json_obj.column_indices[i] = col
        return json_obj

    def read_file(self, infile, genome_version=None, columns=None, max_length=None, sep="\t", mapping=None,
                  remove_quotes=True, start_row=None, end_row=None):
        """
        Reads a MAF file in a biomarker frame

        :param infile:
        :param genome_version:
        :param columns:
        :param max_length:
        :param sep:
        :param mapping:
        :return:
        """
        sep = "\t"
        if isinstance(infile, str):
            file_name, file_extension = os.path.splitext(infile)
            input_format_recognized = file_extension.lstrip(".")
            if input_format_recognized == "gz":
                infile = gzip.open(infile, 'rt')
            else:
                infile = open(infile, 'r')

        json_obj = adagenes.BiomarkerFrame(src_format='maf')
        json_obj.columns = []
        json_obj.column_indices = {}
        json_obj.header_lines = []
        json_obj.data = {}
        json_obj.info_lines = {}
        json_obj.genome_version = genome_version
        variant_count = 0
        line_count = 0
        json_obj.variants = {}

        line_count = 0
        for line in infile:

            line = line.strip()
            #print(line)
            if line.startswith("#"):
                json_obj = self.read_header(line, json_obj)
                continue
            fields = line.split(sep)
            if fields[0] == 'Hugo_Symbol':
                json_obj = self.read_header(line, json_obj)
                continue

            #print(line)
            if len(fields) > 1:
                #print(json_obj.columns)
                qid = fields[self.maf_indices["Chromosome"]] + ":" + fields[self.maf_indices["Start_Position"]] \
                    + \
                    fields[self.maf_indices["Tumor_Seq_Allele1"]] + ">" + fields[self.maf_indices["Tumor_Seq_Allele2"]]
                json_obj.data[qid] = {}

                maf_dc = {}
                for i,field in enumerate(fields):
                    if len(json_obj.columns) > i:
                        maf_dc[json_obj.columns[i]] = field
                    else:
                        print("Columns out of range: ",str(i),":",field)
                json_obj.data[qid]["info_features"] = maf_dc
                json_obj.data[qid]["variant_data"] = {}

                #print(json_obj.data[qid]["info_features"])

                # Add REF, ALT features
                json_obj.data[qid][adagenes.conf.read_config.variant_data_key]["CHROM"] = \
                    json_obj.data[qid]["info_features"]["Chromosome"].replace("chr","")
                json_obj.data[qid][adagenes.conf.read_config.variant_data_key]["POS"] = \
                    json_obj.data[qid]["info_features"]["Start_Position"]
                json_obj.data[qid][adagenes.conf.read_config.variant_data_key]["POS_"+genome_version] = \
                    json_obj.data[qid]["info_features"]["Start_Position"]
                json_obj.data[qid]["info_features"]["REF"] = json_obj.data[qid]["info_features"]["Reference_Allele"]
                json_obj.data[qid][adagenes.conf.read_config.variant_data_key]["ALT"] = \
                    json_obj.data[qid]["info_features"]["Tumor_Seq_Allele1"]
                # json_obj.data[qid]["info_features"]["Tumor_Seq_Allele2"]

                if max_length is not None:
                    if line_count > max_length:
                        break

        infile.close()
        json_obj.data_type = "g"
        return json_obj

    def read_header(self, line, json_obj):
        """

        :param line:
        :param json_obj:
        :return:
        """
        if line.startswith("#"):
            json_obj.header_lines.append(line)
        else:
            json_obj.columns = line.split("\t")

        return json_obj
