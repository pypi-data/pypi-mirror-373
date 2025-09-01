import adagenes.clients.writer as writer
import pandas as pd


class NormalizedDataWriter(writer.Writer):

    def __init__(self, sep='\t', error_logfile=None):
        self.sep=sep

    def write_to_file(self, outfile_src: str, json_obj: pd.DataFrame, save_headers=False, header_lines=None, c=1):
        df = json_obj
        df.to_csv(outfile_src, sep=self.sep)

    def write_to_file_start(self, outfile):
        pass

    def write_to_file_finish(self, outfile, c=0, input_format='json', save_header=False, header_lines=None):
        pass

    def write_chunk_to_file(self, outfile, json_obj,c=1,variants_written=False, save_headers=False, header_lines=None):
        pass


