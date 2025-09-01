

class Writer():

    outfile = None
    outfile_src = None

    def __init__(self):
        pass

    def open_file(self, infile_src):
        #self.outfile = open_outfile(infile_src)
        pass

    def close_file(self):
        self.outfile.close()

    def write_to_file_start(self, outfile):
        pass

    def write_to_file_finish(self, outfile):
        pass

    def write_to_file(self, outfile, json_obj, genome_version=None,
                      sort_features=None,mapping=None, labels=None, sorted_features=None,
                      export_features=None
                      ):
        pass

    def write_chunk_to_file(self, outfile, json_obj, c, srv_prefix, extract_keys,
                            variants_written=False, save_headers=False,
                            first_chunk=None, last_chunk=None):
        pass

    def post_process(self, outfile):
        pass

    def pre_process(self, outfile, ranked_labels=None):
        pass

    def write_line_to_file(self,outfile, var, vcf_lines, magic_obj, save_headers=False, variants_written=False,
                           mapping=None,
                           ranked_labels=None,
                           labels=None, first_chunk=False,
                           columns=None):
        pass

    def generate_columns(self, outfile, mapping,sep="\t"):
        pass
