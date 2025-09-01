import copy
import traceback
import pandas as pd
import adagenes
from adagenes.clients import client


def filter_positions(bframe, threshold: int, op:str="greater_than"):
    """
    Filter positions that are higher or lower than a specified position

    :param bframe:
    :param op:
    :return:
    """
    if isinstance(bframe.data, dict):
        bframe_data_new = {}
        for var in bframe.data.keys():
            pos = int(bframe.data[var]["variant_data"]["POS"])

            if op == "greater_than":
                if pos >= threshold:
                    bframe_data_new[var] = bframe.data[var]
            elif op == "smaller_than":
                if pos < threshold:
                    bframe_data_new[var] = bframe.data[var]

        bframe.data = bframe_data_new

        if bframe.is_sorted is True:
            bframe.sorted_variants = list(bframe.data.keys())


    return bframe

def filter_same_position(bframe):
    """
    Filters variants occurring at the same position of the protein.
    This function is used in case of variant analysis to analyze variants at different positions of the protein

    :param bframe:
    :return:
    """

    if isinstance(bframe.data, dict):
        bframe_data_new = {}
        locations_found = []
        for var in bframe.data.keys():
            if "UTA_Adapter_gene" in bframe.data[var].keys():
                loc = bframe.data[var]["UTA_Adapter_gene"]["prot_location"]
                if loc not in locations_found:
                    bframe_data_new[var] = bframe.data[var]
                    locations_found.append(loc)

        bframe.data = bframe_data_new

        if bframe.is_sorted is True:
            bframe.sorted_variants = list(bframe.data.keys())


    return bframe

