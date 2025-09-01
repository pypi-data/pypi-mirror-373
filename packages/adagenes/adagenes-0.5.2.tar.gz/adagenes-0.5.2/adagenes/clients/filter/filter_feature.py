import copy
import traceback
import pandas as pd
import adagenes
from adagenes.clients import client
import adagenes as ag


class FeatureFilter(client.Client):
    """
    Filters biomarker data according to a defined feature value, filters only exact matches
    """

    def process_data(self, bframe, filter=None, module=None, inv=False):
        """
        Filters biomarkers according to specified feature values

        Filter arguments are defined as a list in the filter argument, consisting of a property, a defined value, and an operator.

        Example: Filter all variants according to allele frequency
        filter = ['AC', '0.1', '>']
        
        :param bframe: AdaGenes biomarker frame object
        :param filter: List of arguments to define the filter
        :param inv:
        :return:
        """
        is_biomarker = False
        if isinstance(bframe,dict):
            biomarker_data = bframe
        elif isinstance(bframe, adagenes.BiomarkerFrame):
            biomarker_data = bframe.data
            is_biomarker = True
        else:
            biomarker_data = bframe
        biomarker_data_new = {}

        if (filter is None) and (isinstance(bframe, ag.BiomarkerFrame)):
            filter = bframe.filter

        for var in biomarker_data:
            if filter is not None:
                if isinstance(filter,list):
                    try:
                        feature = filter[0]
                        operator = filter[2]
                        val_comp = float(filter[1])
                        df = pd.json_normalize(biomarker_data[var])
                        if feature in df.columns:
                            if operator == ">":
                                val = float(df[feature])
                                if val > val_comp:
                                    biomarker_data_new[var] = biomarker_data[var]
                                else:
                                    pass
                    except:
                        print(traceback.format_exc())
                else:
                    print("Error: Filter must be a list")

        if is_biomarker:
            bframe_new = copy.deepcopy(bframe)
            bframe_new.data = copy.deepcopy(biomarker_data_new)
            return bframe_new

        return biomarker_data_new
