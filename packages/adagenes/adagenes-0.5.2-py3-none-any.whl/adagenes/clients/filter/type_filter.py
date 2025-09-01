from adagenes.clients import client
import adagenes
import adagenes.conf.read_config as conf_reader


class TypeFilterClient(client.Client):
    """
    Mutation type filter that selects mutations of a specific mutation type

    """

    def process_data(self, biomarker_data, get_types=None):

        biomarker_data_new = {}

        for var in biomarker_data:
            if get_types is not None:
                if conf_reader.variant_data_key in biomarker_data[var].keys():
                    if "mutation_type" in biomarker_data[var][conf_reader.variant_data_key].keys():
                        if biomarker_data[var][conf_reader.variant_data_key]["mutation_type"].lower() in get_types:
                            biomarker_data_new[var] = biomarker_data[var]
                    elif "mutation_type" in biomarker_data[var].keys():
                        if biomarker_data[var]["mutation_type"].lower() in get_types:
                            biomarker_data_new[var] = biomarker_data[var]

        return biomarker_data_new
