import os, gzip
import adagenes.clients.reader as reader
import adagenes.conf.read_config as conf_reader
from adagenes.tools import parse_genome_position
import adagenes
import pandas as pd


class TXTReader(reader.CSVReader):

    def read_file(self, infile,
                  genome_version='hg38',
                  batch_size=100,
                  columns=None,
                  mapping=None,
                  header=0,
                  sep=',',
                  remove_quotes=True,
                  start_row=None, end_row=None
                  ) -> adagenes.BiomarkerFrame:
        """
        Loads a tab or comma-separated file in a variant data object

        :param batch_size:
        :param sep:
        :param genome_version:
        :param infile:
        :return:
        """
        sep = "\t"
        return super().read_file(infile, columns=columns, genome_version=genome_version, sep=sep, mapping=mapping)

