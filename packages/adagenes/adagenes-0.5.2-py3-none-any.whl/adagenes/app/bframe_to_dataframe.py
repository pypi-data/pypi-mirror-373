import pandas as pd
import adagenes as ag


def bframe_to_app_dataframe(bframe, output_format="AVF"):
    """
    Converts a biomarker frame into a dataframe for the adagenes application

    :param bframe:
    :return:
    """
    data = {}

    #bframe = ag.protein_to_genomic(bframe)
    #print("norm ",bframe)

    if output_format == "AVF":
        data = generate_avf_data(bframe)
    elif output_format == "VCF":
        data = { "CHROM":[], "POS":[], "ID":[], "REF":[], "ALT":[], "QUAL":[], "FILTER":[], "INFO":[] }
        for key in bframe.data.keys():
            var = bframe.data[key]
            data["CHROM"].append(var["variant_data"]["CHROM"])
            data["POS"].append(var["variant_data"]["POS"])
            data["ID"].append(var["variant_data"]["ID"])
            data["REF"].append(var["variant_data"]["REF"])
            data["ALT"].append(var["variant_data"]["ALT"])
            data["QUAL"].append(var["variant_data"]["QUAL"])
            data["FILTER"].append(var["variant_data"]["FILTER"])
            if "INFO" in var["variant_data"]:
                data["INFO"].append(var["variant_data"]["INFO"])
            else:
                data["INFO"].append("")

    df = pd.DataFrame(data=data)
    return df


def generate_avf_data(bframe):
    """
    Generates the data displayed from an AVF file

    :param bframe:
    :return:
    """
    data = {"CHROM": [], "POS": [], "REF": [], "ALT": [], "Gene":[], "Variant":[], "ClinVar": [], "Frequency(dbSNP)": []}
    for key in bframe.data.keys():
        var = bframe.data[key]
        data["CHROM"].append(var["variant_data"]["CHROM"])
        data["POS"].append(var["variant_data"]["POS"])
        data["REF"].append(var["variant_data"]["REF"])
        data["ALT"].append(var["variant_data"]["ALT"])
        #print(var)

        if "UTA_Adapter" in var.keys():
            data["Gene"].append(var["UTA_Adapter"]["hgnc_symbol"])
        else:
            data["Gene"].append("")

        if "UTA_Adapter" in var.keys():
            data["Variant"].append(var["UTA_Adapter"]["aminoacid_exchange"])
        else:
            data["Variant"].append("")

        if "clinvar" in var.keys():
            data["ClinVar"].append(var["clinvar"]["gene_name"])
        else:
            data["ClinVar"].append("")

        if "dbsnp" in var.keys():
            data["Frequency(dbSNP)"].append(var["dbsnp"]["freq_total"])
        else:
            data["Frequency(dbSNP)"].append("")

    return data