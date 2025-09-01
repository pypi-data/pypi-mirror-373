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

def apply_filter(biomarker_data, biomarker_data_new, filter_model, dc_cols):
    """

    :param biomarker_data:
    :param biomarker_data_new:
    :param filter_model:
    :param dc_cols:
    :return:
    """

    elements = filter_model.split(" ")
    if len(elements) == 3:
        feature = elements[0]
        operator = elements[1]
        val_comp = elements[2]
    else:
        #print("length no match ",elements, filter_model)
        return biomarker_data, dc_cols

    try:
        val_comp = float(val_comp)
    except:
        pass

    for var in biomarker_data.keys():
        df = pd.json_normalize(biomarker_data[var])
        columns_lower = []
        for key in df.columns:
            dc_cols[key.lower()] = key
            columns_lower.append(key.lower())
        #print("columns: ",columns_lower)

        if feature not in columns_lower:
            feature = feature.lower()
            if "variant_data." + feature in columns_lower:
                feature = "variant_data." + feature
            elif "info_features." + feature in columns_lower:
                feature = "info_features." + feature

        #print("feature ",feature, " columns ",columns_lower)
        if feature in columns_lower:
            filtered_df = df.loc[(df[dc_cols[feature]] != '') & (df[dc_cols[feature]] != '.')]

            if operator == ">":
                try:
                    if len(filtered_df[dc_cols[feature]].values) > 0:
                        # val_float = float(df[dc_cols[feature]])
                        val_float = float(filtered_df[dc_cols[feature]].values[0])
                        # val_float = float(filtered_df[dc_cols[feature]])
                        if val_float > val_comp:
                            biomarker_data_new[var] = biomarker_data[var]
                except:
                    print(traceback.format_exc())
            elif operator == "<":
                try:
                    # val_float = float(df[dc_cols[feature]])
                    val_float = float(filtered_df[dc_cols[feature]].values[0])
                    # val_float = float(df[dc_cols[feature]])
                    val_float = float(filtered_df[dc_cols[feature]])
                    if val_float < val_comp:
                        #print(f"{val_float} less than {val_comp}")
                        biomarker_data_new[var] = biomarker_data[var]
                except:
                    print(traceback.format_exc())
            elif operator == "=":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) > 0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]].values[0])
                            if val_float == val_comp:
                                biomarker_data_new[var] = biomarker_data[var]
                            #elif str(feature) in str(df[dc_cols[feature]]):
                            #    biomarker_data_new[var] = biomarker_data[var]
                    except:
                        try:
                            val = str(filtered_df[dc_cols[feature]].values[0])
                            if val == val_comp:
                                #print("VALCOMP ",val,": ",val_comp)
                                biomarker_data_new[var] = biomarker_data[var]
                        except:
                            print(traceback.format_exc())
            elif operator == "equals":
                    try:
                        if len(filtered_df[dc_cols[feature]].values) > 0:
                            #val_float = float(df[dc_cols[feature]])
                            val_float = float(filtered_df[dc_cols[feature]].values[0])
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
            elif operator == "notEquals":
                    try:
                        filtered_rows = filtered_df[filtered_df[dc_cols[feature]] != val_comp]
                        for num in filtered_rows.index:
                            biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())

                    #try:
                    #    if len(filtered_df[dc_cols[feature]].values) > 0:
                    #        #val_float = float(df[dc_cols[feature]])
                    #        val_float = float(filtered_df[dc_cols[feature]].values[0])
                    #        #val_float = float(df[dc_cols[feature]])
                    #        #val_float = float(filtered_df[dc_cols[feature]])
                    #        if val_float != val_comp:
                    #            biomarker_data_new[var] = biomarker_data[var]
                    #except:
                    #    print(traceback.format_exc())
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
            elif operator == "contains":
                try:
                    print(filtered_df)
                    filtered_rows = filtered_df[filtered_df[dc_cols[feature]].str.contains(val_comp)]
                    #print(val_comp)
                    #print("filtered rows ",filtered_rows)
                    for num in filtered_rows.index:
                        biomarker_data_new[var] = biomarker_data[var]

                    #val = str(filtered_df[dc_cols[feature]])
                    #print("compare ",val," and ",val_comp)
                    #if val_comp in val:
                    #    biomarker_data_new[var] = biomarker_data[var]
                except:
                    print(traceback.format_exc())
            elif operator == "notContains":
                    try:
                        filtered_rows = filtered_df[~filtered_df[dc_cols[feature]].str.contains(val_comp, na=False)]
                        for num in filtered_rows.index:
                            biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "beginsWith":
                    try:
                        filtered_rows = filtered_df[filtered_df[dc_cols[feature]].str.beginsWith(val_comp)] #contains(val_comp)]
                        for num in filtered_rows.index:
                            biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())
            elif operator == "endsWith":
                    try:
                        filtered_rows = filtered_df[filtered_df[dc_cols[feature]].str.endsWith(val_comp)] #contains(val_comp)]
                        for num in filtered_rows.index:
                            biomarker_data_new[var] = biomarker_data[var]
                    except:
                        print(traceback.format_exc())

    #print("apply ",type(biomarker_data_new))
    return biomarker_data_new, dc_cols


class NumberAndTextFilter(client.Client):
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

        #print("Number filter: ",self.filter)
        dc_cols = {}
        if self.filter is not None:
                filter_model = self.filter

                if "AND" in filter_model:
                    elements = filter_model.split(" AND ")
                    if len(elements) > 1:
                        data = copy.deepcopy(biomarker_data)
                        #print("elements ",elements)
                        for model in elements:
                            #print("model ",model)
                            #print("data elements",len(list(data.keys())))
                            biomarker_data_new, dc_cols = apply_filter(data, biomarker_data_new, model, dc_cols)
                            data = copy.deepcopy(biomarker_data_new)
                            biomarker_data_new = {}
                        #print("data elements ",len(list(data.keys())))
                        biomarker_data_new = copy.deepcopy(data)

                elif "OR" in filter_model:
                    datasets = []
                    elements = filter_model.split(" OR ")
                    if len(elements) > 1:
                        for model in elements:
                            print("model ",model)
                            data, dc_cols= apply_filter(biomarker_data, biomarker_data_new, model, dc_cols)
                            datasets.append(data)
                        biomarker_data_new = {}
                        print("datasets ",datasets)
                        for sublist in datasets:
                            biomarker_data_new.update(sublist)
                        #biomarker_data = copy.deepcopy(biomarker_data_new)
                else:
                    biomarker_data_new = {}
                    #print("return ", type(biomarker_data_new))

                    biomarker_data_new, dc_cols = apply_filter(biomarker_data, biomarker_data_new, filter_model, dc_cols)
                    #biomarker_data = copy.deepcopy(biomarker_data_new)

                    #biomarker_data_new, dc_cols = apply_filter(biomarker_data,
                    #                                            biomarker_data_new,
                    #                                            filter_model, dc_cols)
                    #print("return ", type(biomarker_data_new))


        if is_biomarker:
            bframe_new = copy.deepcopy(bframe)
            bframe_new.data = copy.deepcopy(biomarker_data_new)
            return bframe_new


        return biomarker_data_new
