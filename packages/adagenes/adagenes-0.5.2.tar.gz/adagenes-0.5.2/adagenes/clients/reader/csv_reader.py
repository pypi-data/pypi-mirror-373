import os, gzip, csv, copy
import traceback

import adagenes.clients.reader as reader
import adagenes as ag
#from adagenes.tools.parse_dataframes import parse_dataframe_biomarkers, is_dragen_file


def parse_csv_line(line, sep=",", quote_char='"', remove_quotes=True):
    fields = []        # List to store the parsed fields
    field = []         # List to collect characters for the current field
    inside_quotes = False  # Flag to track if we are inside a quoted field

    i = 0
    while i < len(line):
        char = line[i]

        if char == quote_char:  # Handle quote characters
            if inside_quotes:
                # Look ahead to see if the next character is also a quote
                if i + 1 < len(line) and line[i + 1] == quote_char:
                    # Double quote inside quoted field; add a single quote to field
                    field.append(quote_char)
                    i += 1  # Skip the next quote character
                else:
                    # Closing quote, toggle inside_quotes off
                    inside_quotes = False
            else:
                # Opening quote, toggle inside_quotes on
                inside_quotes = True

        elif char == sep and not inside_quotes:
            # If we encounter a comma outside of quotes, end of field
            fields.append(''.join(field))
            field = []  # Reset the field for the next entry

        else:
            # Add character to the current field
            field.append(char)

        i += 1

    # Add the last field to the list (if there's anything left)
    fields.append(''.join(field))
    return fields


class CSVReader(reader.Reader):

    def __init__(self, mapping=None, genome_version=None):
        super(CSVReader, self).__init__()
        self.mapping = mapping

    def read_file(self,
                  infile,
                  sep=',',
                  genome_version='hg38',
                  batch_size=100,
                  columns=None,
                  mapping=None,
                  header=True,
                  remove_quotes=True,
                  start_row=None, end_row=None
                  ) -> ag.BiomarkerFrame:
        """
        Loads a tab or comma-separated file in a variant data object

        :param batch_size:
        :param sep:
        :param genome_version:
        :param infile:
        :return:
        """
        if genome_version is None:
            genome_version = self.genome_version

        fileopen = False
        if isinstance(infile, str):
            fileopen = True
            file_name, file_extension = os.path.splitext(infile)
            input_format_recognized = file_extension.lstrip(".")
            if input_format_recognized == "gz":
                infile = gzip.open(infile, 'rt')
            else:
                infile = open(infile, 'r')

        #reader = csv.reader(infile, quotechar='"', delimiter=',', skipinitialspace=True)
        lines = []
        columns = None

        variant_count = 0
        line_count = 0
        #json_obj.variants = {}
        line_num_abs = 0
        line_num_all = 0

        for line_num,line in enumerate(infile):
            line_num_abs += 1
            line_num_all += 1

            if (start_row is not None) and (end_row is not None):
                if line_num_abs < start_row:
                    continue
                elif line_num_abs > end_row:
                    continue

            if line.startswith("#"):
                columns = line.replace("#","").strip().split(sep)
            elif (line_num==0) and (header is True):
                columns = parse_csv_line(line.strip(), remove_quotes=remove_quotes, sep=sep)# .split(sep)
            else:
                lines.append(parse_csv_line(line.strip(), sep=sep))

        json_obj = ag.BiomarkerFrame(preexisting_features=columns)
        row = 0
        #dragen_file = ag.is_dragen_file(df.columns)
        #if dragen_file:
        #    json_obj.data_type = "g"

        #print("columns ",columns, ":: ",json_obj.preexisting_features)
        #print("lines ",lines)
        json_obj = ag.tools.parse_dataframes.parse_csv_lines(lines,columns,json_obj, mapping=mapping,
                                                                   genome_version=genome_version,sep=sep, header=header,
                                                                   remove_quotes=remove_quotes)

        if fileopen is True:
            infile.close()

        json_obj.max_variants = line_num_all
        return json_obj

    def read_file_chunk(self, infile, json_obj: ag.BiomarkerFrame, genome_version="hg38") -> ag.BiomarkerFrame:
        """
        Reads a defined number of lines from a file object, adds them to the given biomarker set and returns the extended biomarker list

        :param genome_version:
        :param infile:
        :type infile:
        :param json_obj:
        :type json_obj: BiomarkerSet
        :return: json_obj
        """

        json_obj_new = self.read_file(infile,genome_version=genome_version)
        json_obj.data = json_obj_new.data

        return json_obj

    def read_line(self, line, vcf_lines, outfile, header_lines, magic_obj, genome_version, line_count, variant_count,
                  variants, info_lines,is_header_line=False, linecount = "",sep="','", columns = [], mapping=None):

        # check if line is first row
        if is_header_line is False:
            #fields = line.strip().split(sep)

            gene_var = False
            gene = ""
            variant = ""

            if mapping is None:
                qid = str(linecount)
            else:
                if ("gene" in mapping.keys()) and ("variant" in mapping.keys()):
                    qid = str(linecount)
                    gene_var = True
                    gene_map = mapping["gene"]
                    var_map = mapping["variant"]
                else:
                    qid = str(linecount)

            vcf_lines[qid] = {}
            #print(columns, ": fields ",fields)
            #reader = csv.reader(line)
            lines = []
            reader = csv.reader([line], delimiter=',', quotechar='"')

            for row in reader:
                #print(columns, ": fields ",row)
                try:
                    for i,field in enumerate(row):
                        vcf_lines[qid][columns[i]] = field
                    lines.append(row)
                except:
                    print(traceback.format_exc())
            #if gene_var is True:
            #    qid_new = gene + ":" + variant
            #    vcf_lines[qid_new] = vcf_lines[qid]
            #    vcf_lines.pop(qid)

            vcf_lines = ag.merge_dictionaries(vcf_lines, ag.tools.parse_dataframes.parse_csv_lines(lines, columns, vcf_lines, mapping=mapping,
                                                                 genome_version=genome_version, sep=sep))
            vcf_lines.pop(qid)
            #print("vcf lines ",vcf_lines)
        else:
            # parse header column
            #columns = line.strip().split(sep)
            reader = csv.reader([line], delimiter=',', quotechar='"')
            for row in reader:
                #print(columns)
                columns=row

        # normalize identifiers
        vcf_lines = ag.TypeRecognitionClient().process_data(vcf_lines)

        #print(vcf_lines)
        return vcf_lines, header_lines, variant_count, line_count,is_header_line, info_lines, variants, columns

