import pandas as pd
import adagenes.conf.read_config
import adagenes.clients.writer as writer


class PandasWriter(writer.Writer):

    def write_to_dataframe(self, variant_data,mapping=None):
        """

        :param variant_data:
        :return:
        """

        columns = adagenes.conf.read_config.tsv_columns
        data={}
        #for column in columns:
        #    data[column] = []

        for var in variant_data.keys():
            data = self.to_single_df_line(variant_data[var], data,mapping=mapping)

        print("df", data)
        df = pd.DataFrame(data=data)
        return df

    def to_single_df_line(self, json_obj,data,mapping=None):
        """


        :param json_obj:
        :param data:
        :param mapping:
        :return:
        """

        if mapping is None:
            mapping = adagenes.conf.read_config.tsv_mappings
            print(mapping)

        # get mappings
        for module in mapping:
            if isinstance(mapping[module], list):
                keys = mapping[module]
                for key in keys:
                    column = module + "_" + key
                    if column not in data.keys():
                        data[column] = []
                    if module in json_obj:
                        if key in json_obj[module]:
                            data[column].append(str(json_obj[module][key]))
                        else:
                            data[column].append('')
                    else:
                        data[column].append('')
            else:
                if module not in data:
                    data[module] = []
                data[module].append(str(json_obj[module]))

        return data


