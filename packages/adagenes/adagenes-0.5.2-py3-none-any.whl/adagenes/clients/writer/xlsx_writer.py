import adagenes.conf.read_config as conf_reader
import adagenes.clients.writer as writer
import traceback
import adagenes.tools.parse_dataframes


class XLSXWriter(writer.Writer):

    def write_to_file(self, outfile_src, json_obj, genome_version="hg38",
                      mapping=None, labels=None, sorted_features=None,
                      sort_features=False, save_headers=True, export_features=None):
        """

        :param outfile:
        :param json_obj:
        :param genome_version:
        :param mapping:
        :param labels:
        :param sorted_features:
        :param sort_features:
        :param save_headers:
        :return:
        """
        if mapping is None:
            mapping = conf_reader.tsv_mappings

        data = adagenes.tools.parse_dataframes.write_csv_to_dataframe(outfile_src,
                                                                      json_obj,
                                                                      mapping=mapping,
                                                                      labels=labels,
                                                                      sort_features=sort_features,
                                                                      sorted_features=sorted_features,
                                                                      sep='\t')
        data.to_excel(outfile_src)

