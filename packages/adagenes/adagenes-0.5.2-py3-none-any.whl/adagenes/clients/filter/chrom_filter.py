from adagenes.clients import client
import adagenes.conf.read_config as conf_reader


class ChromosomeFilter(client.Client):

    def process_data(self, biomarker_data, filter_chroms:list=None):
        if filter_chroms is None:
            return biomarker_data

        if isinstance(filter_chroms, str):
            filter_chroms = [filter_chroms]

        if isinstance(filter_chroms,list):
            chroms = []
            for chrom in filter_chroms:
                chroms.append(chrom.replace("chr",""))
            biomarker_data_new = {}
            for var in biomarker_data:
                if conf_reader.variant_data_key in biomarker_data[var]:
                    if biomarker_data[var][conf_reader.variant_data_key]["CHROM"].lower() in chroms:
                        biomarker_data_new[var] = biomarker_data[var]

            return biomarker_data_new
        return biomarker_data
