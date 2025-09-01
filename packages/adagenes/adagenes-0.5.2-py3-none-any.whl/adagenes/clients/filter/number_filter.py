# if filter_type == "text":
#    data = [
#        row
#        for row in data
#        if str(filter_data["filter"]).lower() in str(row[column]).lower()
#    ]
# elif filter_type == "number":
#    filter_value = filter_data["filter"]
#    if filter_data["type"] == "equals":
#        data = [row for row in data if row[column] == filter_value]
#    elif filter_data["type"] == "greaterThan":
#        data = [row for row in data if row[column] > filter_value]
#    elif filter_data["type"] == "lessThan":
#        data = [row for row in data if row[column] < filter_value]

import copy
import traceback
import pandas as pd
import adagenes
from adagenes.clients import client
import adagenes as ag

def apply_numeric_filter(biomarker_data, biomarker_data_new, filter_def, feature, dc_cols):

    for var in biomarker_data.keys():
        # feature =  self.filter[] #self.filter[0]
        # operator = self.filter[2]
        operator = filter_def["type"]
        # val_comp = float(self.filter[1])
        val_comp = filter_def["filter"]
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
            filtered_df = df.loc[(df[dc_cols[feature]] != '') & (df[dc_cols[feature]] != '.')]

            if operator == ">":
                val = float(df[dc_cols[feature]])
                if val > val_comp:
                    biomarker_data_new[var] = biomarker_data[var]
                else:
                    pass
            elif operator == "<":
                pass
            elif operator == "equals":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) > 0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]])
                            if val_float == val_comp:
                                biomarker_data_new[var] = biomarker_data[var]
                            #elif str(feature) in str(df[dc_cols[feature]]):
                            #    biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "Equals":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) > 0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]].values[0])
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]])
                            if val_float == val_comp:
                                biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "notEqual":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) > 0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]].values[0])
                            #val_float = float(df[dc_cols[feature]])
                            #val_float = float(filtered_df[dc_cols[feature]])
                            if val_float != val_comp:
                                biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "greaterThan":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) >0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]].values[0])
                            #val_float = float(filtered_df[dc_cols[feature]])
                            if val_float > val_comp:
                                biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "greaterThanOrEqual":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) > 0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]].values[0])
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]])
                            if val_float >= val_comp:
                                biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "lessThan":
                    try:
                        #val_float = float(df[dc_cols[feature]])
                        val_float = float(filtered_df[dc_cols[feature]].values[0])
                        #val_float = float(df[dc_cols[feature]])
                        val_float = float(filtered_df[dc_cols[feature]])
                        if val_float < val_comp:
                            biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "lessThanOrEqual":
                    try:
                        #val_float = float(df[dc_cols[feature]])
                        val_float = float(filtered_df[dc_cols[feature]].values[0])
                        #val_float = float(df[dc_cols[feature]])
                        val_float = float(filtered_df[dc_cols[feature]])
                        if val_float <= val_comp:
                            biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())

    return biomarker_data_new, dc_cols


class NumberFilter(client.Client):
    """
    Filters biomarker data according to a defined feature value, filters only exact matches
    """

    def __init__(self, filter=None, error_logfile=None):
        """

        :param filter:
        :param error_logfile:
        """
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

        #print("NUmber filter: ",self.filter)
        dc_cols = {}
        if self.filter is not None:
                if isinstance(self.filter, list):
                    try:
                        #for filter_list in self.filter:
                            #print("flist ",filter_list,"::",self.filter)
                            feature = self.filter[0]
                            filter_entry = self.filter[1]
                            #print("ENTRY ",filter_entry)
                            filter_type = filter_entry["filterType"]


                            if filter_type == "number":
                                filter_def = filter_entry

                                if "operator" not in filter_def.keys():
                                    biomarker_data_new, dc_cols = apply_numeric_filter(biomarker_data, biomarker_data_new,
                                                                              filter_def, feature, dc_cols)

                                else:
                                    filter_def = filter_entry
                                    merge_opt = filter_def["operator"]

                                    if merge_opt == "AND":
                                        for entry in filter_def["conditions"]:
                                            #print(entry)
                                            biomarker_data_new, dc_cols = apply_numeric_filter(biomarker_data,
                                                                                      biomarker_data_new,
                                                                                      entry, feature, dc_cols)
                                            #print("0size bionew ", len(list(biomarker_data_new.keys())))
                                            #biomarker_data = copy.deepcopy(biomarker_data_new)
                                            biomarker_data = biomarker_data_new
                                            biomarker_data_new = {}
                                            #print("size bionew ",len(list(biomarker_data_new.keys())), ", ", len(list(biomarker_data.keys())))

                                    biomarker_data_new = biomarker_data
                    except:
                        print(traceback.format_exc())
                else:
                    print("Error: Filter must be a list")
                    print(self.filter)

        if is_biomarker:
            bframe_new = copy.deepcopy(bframe)
            bframe_new.data = copy.deepcopy(biomarker_data_new)
            return bframe_new

        return biomarker_data_new
