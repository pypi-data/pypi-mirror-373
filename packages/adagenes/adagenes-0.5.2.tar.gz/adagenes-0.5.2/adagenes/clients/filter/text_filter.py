import copy
import traceback
import pandas as pd
import adagenes
from adagenes.clients import client
import adagenes as ag

def apply_text_filter(biomarker_data, biomarker_data_new, filter_def, feature, dc_cols):

    print("filter ",filter_def)
    for var in biomarker_data.keys():
        # feature =  self.filter[] #self.filter[0]
        # operator = self.filter[2]
        operator = filter_def["type"]
        # val_comp = float(self.filter[1])
        val_comp = str(filter_def["filter"])
        df = pd.json_normalize(biomarker_data[var])
        columns_lower = []
        for key in df.columns:
            dc_cols[key.lower()] = key
            columns_lower.append(key.lower())

        if feature not in columns_lower:
            if "variant_data." + feature in columns_lower:
                feature = "variant_data." + feature
            elif "info_features." + feature in columns_lower:
                feature = "info_features." + feature

        if feature in columns_lower:
            if operator == ">":
                val = float(df[dc_cols[feature]])
                if val > val_comp:
                    biomarker_data_new[var] = biomarker_data[var]
                else:
                    pass
            elif operator == "<":
                pass
            elif operator == "contains":
                #print("df ",df.columns, "feater ",feature, "cols ",dc_cols)
                #print("fil ",df[dc_cols[feature]])
                #print(df.shape)
                filtered_df = df[dc_cols[feature]].astype(str)
                filtered_df = filtered_df.str
                #print(filtered_df)
                filtered_df = filtered_df.contains(str(val_comp), case=False, na=False)
                filtered_df = df[filtered_df]
                if not filtered_df.empty:
                    biomarker_data_new[var] = biomarker_data[var]
            elif operator == "notContains":
                filtered_df = df[~df[dc_cols[feature]].str.contains(val_comp)]
                if not filtered_df.empty:
                    biomarker_data_new[var] = biomarker_data[var]

    return biomarker_data_new, dc_cols

class TextFilter(client.Client):
    """
    Filters biomarker data according to a defined feature value, filters only exact matches
    """

    def __init__(self, filter=None, error_logfile=None):
        self.filter = filter

        self.qid_key = "q_id"
        self.error_logfile = error_logfile

    def process_data(self, bframe):
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
        if isinstance(bframe, dict):
            biomarker_data = bframe
        elif isinstance(bframe, adagenes.BiomarkerFrame):
            biomarker_data = bframe.data
            is_biomarker = True
        else:
            biomarker_data = bframe
        biomarker_data_new = {}

        if (self.filter is None) and (isinstance(bframe, ag.BiomarkerFrame)):
            self.filter = bframe.filter
        #print("Run text filter: ",str(self.filter), ":", biomarker_data)

        if self.filter is not None:
                if isinstance(self.filter, list):
                    try:
                        dc_cols = {}
                        feature = self.filter[0]
                        #operator = self.filter[2]
                        #val_comp = str(self.filter[1])
                        filter_entry = self.filter[1]
                        # print("ENTRY ",filter_entry)
                        filter_type = filter_entry["filterType"]

                        if filter_type == "text":
                            filter_def = filter_entry

                            if "operator" not in filter_def.keys():
                                biomarker_data_new, dc_cols = apply_text_filter(biomarker_data, biomarker_data_new,
                                                                                   filter_def, feature, dc_cols)

                            else:
                                filter_def = filter_entry
                                merge_opt = filter_def["operator"]

                                if merge_opt == "AND":
                                    for entry in filter_def["conditions"]:
                                        # print(entry)
                                        biomarker_data_new, dc_cols = apply_text_filter(biomarker_data,
                                                                                           biomarker_data_new,
                                                                                           entry, feature, dc_cols)
                                        # print("0size bionew ", len(list(biomarker_data_new.keys())))
                                        # biomarker_data = copy.deepcopy(biomarker_data_new)
                                        biomarker_data = biomarker_data_new
                                        biomarker_data_new = {}
                                        # print("size bionew ",len(list(biomarker_data_new.keys())), ", ", len(list(biomarker_data.keys())))

                                biomarker_data_new = biomarker_data
                    except:
                        print(traceback.format_exc())
                else:
                    print("Error: Filter must be a list")

        if is_biomarker:
            bframe_new = copy.deepcopy(bframe)
            bframe_new.data = copy.deepcopy(biomarker_data_new)
            return bframe_new

        print("return  ",biomarker_data_new)
        return biomarker_data_new
