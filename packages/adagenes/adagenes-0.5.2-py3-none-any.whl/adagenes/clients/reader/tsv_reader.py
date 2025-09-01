import adagenes.clients.reader as reader
import adagenes


class TSVReader(reader.CSVReader):

    def __init__(self, genome_version=None):
        super(TSVReader, self).__init__(genome_version=genome_version)

    def read_file(self,
                  infile,
                  sep='\t',
                  genome_version='hg38',
                  batch_size=100,
                  columns=None,
                  mapping=None,
                  header=True,
                  remove_quotes=True,
                  start_row=None, end_row=None) -> adagenes.BiomarkerFrame:
        sep="\t"
        return super().read_file(infile, columns=columns, genome_version=genome_version,sep=sep, mapping=mapping)

