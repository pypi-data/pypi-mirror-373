from adagenes.tools import open_infile


class Reader():

    infile = None
    infile_src = None

    def __init__(self, genome_version=None):
        self.genome_version=genome_version

    def open_file(self,infile_src):
        self.infile = open_infile(infile_src)

    def close_file(self):
        self.infile.close()

    def read_file(self, infile, remove_quotes=True,start_row=None, end_row=None):
        pass

    def read_file_chunk(self,  infile, bframe):
        pass

    def read_header(self, line):
        pass

    def read_line(self, line, vcf_lines, outfile, header_lines, magic_obj, genome_version, line_count, variant_count,
                  variants, info_lines, is_header_line=False, sep=',', linecount="", columns=[]):
        pass
