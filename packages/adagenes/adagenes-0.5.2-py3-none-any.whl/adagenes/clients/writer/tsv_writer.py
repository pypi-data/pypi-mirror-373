import adagenes.clients.writer as writer
import traceback
import adagenes


class TSVWriter(writer.CSVWriter):

    def write_to_file(self, outfile,
                      json_obj,
                      genome_version="hg38",
                      mapping=None,
                      labels=None,
                      ranked_labels=None,
                      sep=',', export_features=None):
        """
        Writes a biomarker frame in a tab-separated file

        :param outfile_src:
        :param json_obj:
        :param mapping:
        :return:
        """
        super(TSVWriter, self).write_to_file(outfile, json_obj,
                                             mapping=None, labels=None,
                                             ranked_labels=ranked_labels,sep="\t")

