import copy
from adagenes.clients import client
import adagenes.conf.read_config as conf_reader


class AltAlleleFilter(client.Client):

    def filter_alleles(self,variant_data):
        variant_data_filtered = {}
        for var in variant_data.keys():
            if conf_reader.variant_data_key in variant_data[var]:
                alt = var[conf_reader.variant_data_key]["ALT"]
                if "," not in alt:
                    variant_data_filtered[var] = copy.deepcopy(variant_data[var])

        return variant_data_filtered

    def process_data(self, biomarker_data, module=None, feature=None, inv=False):
        return self.filter_alleles(biomarker_data)
