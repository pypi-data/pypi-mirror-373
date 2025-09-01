import adagenes as ag


class SectionFilter():

    def process_data(self, biomarker_data, section):
        """
        Returns variants that are annotated with a specific feature

        :param biomarker_data:
        :param section:
        :return:
        """
        if isinstance(biomarker_data, ag.BiomarkerFrame):
            biomarker_data = biomarker_data.data

        biomarker_data_new = {}
        for var in biomarker_data:
            if section in biomarker_data[var].keys():
                biomarker_data_new[var] = biomarker_data[var]
            else:
                #print("no section ",biomarker_data[var])
                pass

        return biomarker_data_new

