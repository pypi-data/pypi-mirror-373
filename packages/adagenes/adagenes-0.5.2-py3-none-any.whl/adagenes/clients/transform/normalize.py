import traceback
import pandas as pd
from adagenes.clients import client


class Normalizer(client.Client):
    def __init__(self, error_logfile=None):
        pass

    def export_feature_results_lv2(self,biomarker_data, record_path=None, meta=None) -> pd.DataFrame:
        """
        Exports biomarker data in full mode with level 2 meta data

        :param biomarker_data:
        :param outfile_src:
        :param feature:
        :param record_path:
        :param meta:
        :param sep:
        :return:
        """
        df_sum = pd.DataFrame()
        for var in biomarker_data:
            df = pd.json_normalize(data=biomarker_data[var], record_path=record_path, meta=meta)
            df_sum = pd.concat([df_sum, df], axis=0)
        return df_sum

    def process_data(self, biomarker_data, record_path=None, meta=None) -> pd.DataFrame:

        try:
            biomarker_data = self.export_feature_results_lv2(biomarker_data.data, record_path=record_path, meta=meta)

        except:
            print(traceback.format_exc())

        return biomarker_data
