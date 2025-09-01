import traceback
import adagenes.clients.reader as reader
import pandas as pd
import adagenes.conf.read_config as config
from adagenes.tools import parse_genome_position
import adagenes as ag
import adagenes.tools.parse_dataframes


class XLSXReader(reader.Reader):

    def store_additional_columns_in_bframe(self, biomarker, lines,columns):
        """

        :param biomarker:
        :param lines:
        :param columns:
        :return:
        """
        biomarker["additional_columns"] = {}

        for i,feature in enumerate(columns):
            biomarker["additional_columns"][feature] = lines[i]

        return biomarker

    def read_file(self, infile_src, sep='\t', genome_version=None, batch_size=100, columns=None, mapping=None,
                  remove_quotes=True,
                  start_row=None, end_row=None) \
            -> adagenes.BiomarkerFrame:
        """
            Loads a tab or comma-separated file in a variant data object

            :param mapping:
            :param columns:
            :param batch_size:
            :param genome_version:
            :param sep:
            :param infile_src:
            :param infile:
            :return:
        """

        if genome_version is None:
            genome_version = self.genome_version

        df = pd.read_excel(infile_src)

        json_obj = ag.BiomarkerFrame()
        row = 0
        columns = df.columns
        dragen_file = ag.tools.parse_dataframes.is_dragen_file(columns)
        #json_obj = parse_dataframe_biomarkers(df, json_obj, dragen_file=dragen_file)

        lines = []
        for i in range(0,df.shape[0]):
            row = list(df.iloc[i,:])
            if str(row[0]).startswith("#"):
                #columns = ",".join(str(value) for value in row)
                columns = row
            else:
                #line = ",".join(str(value) for value in row)
                line = row
                lines.append(line)
        columns = columns.tolist()
        #print("columns: ",columns)

        if dragen_file:
            import adagenes.clients.transform.dragen_to_vcf_client
            json_obj = ag.tools.parse_dataframes.parse_csv_lines(lines, columns, json_obj, mapping=mapping,
                                                                 genome_version=genome_version, dragen_file=True)
            dragen_client = adagenes.clients.transform.dragen_to_vcf_client.DragenToBFrame(self.genome_version)
            json_obj.data = dragen_client.process_data(json_obj.data)
        else:
            json_obj = ag.tools.parse_dataframes.parse_csv_lines(lines, columns, json_obj, mapping=mapping,
                                                                   genome_version=genome_version)

        # print("loaded tsv: ", variant_data)
        #json_obj.data = variant_data

        return json_obj
