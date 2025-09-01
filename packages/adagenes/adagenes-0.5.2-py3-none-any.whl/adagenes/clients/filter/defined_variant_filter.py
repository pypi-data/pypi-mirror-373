import adagenes as ag


class DefinedVariantFilter():

    def process_data(self, biomarker_data, vars):
        """
        Returns variants that are annotated with a specific feature

        :param biomarker_data:
        :param section:
        :return:
        """
        if isinstance(biomarker_data, ag.BiomarkerFrame):
            biomarker_data = biomarker_data.data

        i = 0
        biomarker_data_new = {}
        for var in vars:
                biomarker_data_new[var] = biomarker_data[var]

        return biomarker_data_new

