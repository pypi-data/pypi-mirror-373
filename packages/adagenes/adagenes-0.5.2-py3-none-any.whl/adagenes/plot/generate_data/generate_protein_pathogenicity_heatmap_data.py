import adagenes as ag



def getMolWeightValue(data, var, refalt=False):
    if "molecular_weight_alt" in data[var]["UTA_Adapter_gene"]:
        mw_ref = data[var]["UTA_Adapter_gene"]["molecular_weight_ref"]["biopython_mol_weight"]
        mw_alt = data[var]["UTA_Adapter_gene"]["molecular_weight_alt"]["biopython_mol_weight"]
        vol_ref = data[var]["UTA_Adapter_gene"]["volume_ref"][0]
        vol_alt = data[var]["UTA_Adapter_gene"]["volume_alt"][0]

        delta = 0
        if vol_ref == "very large":
            ref = 5
        elif vol_ref == "large":
            ref = 4
        elif vol_ref == "middle":
            ref = 3
        elif vol_ref == "small":
            ref = 2
        elif vol_ref == "very small":
            ref = 1
        else:
            ref = 0

        if vol_alt == "very large":
            alt = 5
        elif vol_alt == "large":
            alt = 4
        elif vol_alt == "middle":
            alt = 3
        elif vol_alt == "small":
            alt = 2
        elif vol_alt == "very small":
            alt = 1
        else:
            alt=0

        if vol_ref == vol_alt:
            delta = 3
        elif (vol_ref == "very large") and ((vol_alt == "middle") or (vol_alt=="small") or (vol_alt=="very small")):
            delta = 1
        elif (vol_ref == "very large") and ((vol_alt == "large")):
            delta = 2
        elif (vol_ref == "large") and ((vol_alt == "middle") or (vol_alt=="small") or (vol_alt=="very small")):
            delta = 1
        elif (vol_ref == "large") and ((vol_alt == "very large")):
            delta = 4
        elif (vol_ref == "middle") and ((vol_alt=="large") or (vol_alt=="very large")):
            delta = 4
        elif (vol_ref == "middle") and ((vol_alt == "small") or (vol_alt=="very small")):
            delta = 2
        elif (vol_ref == "small") and ((vol_alt == "middle") or (vol_alt=="large") or (vol_alt=="very large")):
            delta = 4
        elif (vol_ref == "small") and ((vol_alt == "very small")):
            delta = 2
        elif (vol_ref == "very small") and ((vol_alt == "middle") or (vol_alt=="large") or (vol_alt=="very large")):
            delta = 5
        elif (vol_ref == "very small") and ((vol_alt == "small")):
            delta = 4

        #print("MOLWEIGHT ",delta, " , ",vol_ref,", ",vol_alt)

        #if float(mw_ref) > float(mw_alt):
        #    delta = 1
        #elif float(mw_ref) < float(mw_alt):
        #    delta = 5
        #else:
        #    delta = 3
    else:
        print("Could not find feature: Molecular weight")
        mw_ref = 0
        mw_alt = 0
        delta = 0

    if refalt is False:
        return delta
    else:
        return ref, alt, delta


def getChargeValue(data, var, refalt = False):
    delta = 0
    mw_ref = 0
    mw_alt = 0
    if "charge_alt" in data[var]["UTA_Adapter_gene"]:
        mw_ref = data[var]["UTA_Adapter_gene"]["charge_ref"][0]
        mw_alt = data[var]["UTA_Adapter_gene"]["charge_alt"][0]

        if (mw_ref == "uncharged") and (mw_alt == "uncharged"):
            delta = 3
        elif (mw_ref == "uncharged") and (mw_alt == "negative"):
            delta = 2
        elif (mw_ref == "uncharged") and (mw_alt == "positive"):
            delta = 4
        elif (mw_ref == "positive") and (mw_alt == "negative"):
            delta = 1
        elif (mw_ref == "positive") and (mw_alt == "uncharged"):
            delta = 2
        elif (mw_ref == "negative") and (mw_alt == "positive"):
            delta = 5
        elif (mw_ref == "negative") and (mw_alt == "uncharged"):
            delta = 4
        else:
            delta = 3

        if mw_ref == "positive":
            ref = 5
        elif mw_ref == "uncharged":
            ref = 3
        elif mw_ref == "negative":
            ref = 1
        else:
            ref = 3

        if mw_alt == "positive":
            alt = 5
        elif mw_alt == "uncharged":
            alt = 3
        elif mw_alt == "negative":
            alt = 1
        else:
            alt = 3

    if refalt is False:
        return delta
    else:
        return ref, alt, delta


def getPolarityValue(data,var, refalt=False):
    mw_ref = 0
    mw_alt = 0
    delta = 0
    if "polarity_alt" in data[var]["UTA_Adapter_gene"]:
        mw_ref = data[var]["UTA_Adapter_gene"]["polarity_ref"]
        mw_alt = data[var]["UTA_Adapter_gene"]["polarity_alt"]

        if (mw_ref == "nonpolar") and (mw_alt == "nonpolar"):
            delta = 3
        elif (mw_ref == "nonpolar") and (mw_alt == "polar"):
            delta = 5
        elif (mw_ref == "polar") and (mw_alt == "polar"):
            delta = 3
        elif (mw_ref == "polar") and (mw_alt == "nonpolar"):
            delta = 1
        else:
            delta = 3

        if mw_ref == "polar":
            ref = 5
        elif mw_ref == "nonpolar":
            ref = 1
        else:
            ref = 3

        if mw_alt == "polar":
            alt = 5
        elif mw_alt == "nonpolar":
            alt = 1
        else:
            alt = 3

    if refalt is False:
        return delta
    else:
        return ref, alt, delta


def getAromaticityValue(data,var, refalt=False):
    mw_ref = 0
    mw_alt = 0
    delta = 0
    if "aromaticity_alt" in data[var]["UTA_Adapter_gene"]:
        mw_ref = str(data[var]["UTA_Adapter_gene"]["aromaticity_ref"])
        mw_alt = str(data[var]["UTA_Adapter_gene"]["aromaticity_alt"])

        if (mw_ref == "0") and (mw_alt == "0"):
            delta = 3
        elif (mw_ref == "0") and (mw_alt == "1"):
            delta = 5
        elif (mw_ref == "1") and (mw_alt == "1"):
            delta = 3
        elif (mw_ref == "1") and (mw_alt == "0"):
            delta = 1
        else:
            delta = 3

        if mw_ref == "1":
            ref = 5
        elif mw_ref == "0":
            ref = 1
        else:
            ref = 3

        if mw_alt == "1":
            alt = 5
        elif mw_alt == "0":
            alt = 1
        else:
            alt = 3

    if refalt is False:
        return delta
    else:
        return ref, alt, delta

def getFlexibilityValue(data, var, refalt=False):
    ref = 0
    alt = 0
    delta = 0
    if "flexibility_alt" in data[var]["UTA_Adapter_gene"]:
        mw_ref = data[var]["UTA_Adapter_gene"]["flexibility_ref"]
        mw_alt = data[var]["UTA_Adapter_gene"]["flexibility_alt"]

        if (mw_ref == "middle") and (mw_alt == "middle"):
            delta = 3
        elif (mw_ref == "middle") and (mw_alt == "low"):
            delta = 2
        elif (mw_ref == "middle") and (mw_alt == "high"):
            delta = 4
        elif (mw_ref == "high") and (mw_alt == "low"):
            delta = 1
        elif (mw_ref == "high") and (mw_alt == "middle"):
            delta = 2
        elif (mw_ref == "low") and (mw_alt == "high"):
            delta = 3
        elif (mw_ref == "low") and (mw_alt == "middle"):
            delta = 4
        else:
            delta = 3


        if mw_ref == "high":
            ref = 5
        elif mw_ref == "middle":
            ref = 3
        elif mw_ref == "low":
            ref = 1
        else:
            ref = 3

        if mw_alt == "high":
            alt = 5
        elif mw_alt == "middle":
            alt = 3
        elif mw_alt == "low":
            alt = 1
        else:
            alt = 3

    if refalt is False:
        return delta
    else:
        return ref, alt, delta


def getPhosphorylationValue(data, var, refalt=False):
    mw_ref = 0
    mw_alt = 0
    delta = 0
    if "phosphorylation_alt" in data[var]["UTA_Adapter_gene"]:
        mw_ref = str(data[var]["UTA_Adapter_gene"]["phosphorylation_ref"])
        mw_alt = str(data[var]["UTA_Adapter_gene"]["phosphorylation_alt"])

        if (mw_ref == "0") and (mw_alt == "0"):
            delta = 3
        elif (mw_ref == "0") and (mw_alt == "1"):
            delta = 5
        elif (mw_ref == "1") and (mw_alt == "1"):
            delta = 3
        elif (mw_ref == "1") and (mw_alt == "0"):
            delta = 1
        else:
            delta = 3

        if mw_ref == "1":
            ref = 5
        elif mw_ref == "0":
            ref = 1
        else:
            ref = 3

        if mw_alt == "1":
            alt = 5
        elif mw_alt == "0":
            alt = 1
        else:
            alt = 3

    if refalt is False:
        return delta
    else:
        return ref, alt, delta

def generate_pathogenicity_aa_features_joint_data(bframe, score_labels_raw):

    if isinstance(bframe, dict):
        variants = bframe
        is_sorted=False
    elif isinstance(bframe, ag.BiomarkerFrame):
        variants = bframe.data
        is_sorted = bframe.is_sorted
    scores = []
    zdata = []
    z1 = [[]]
    z2 = [[]]
    z3 = [[]]
    z4 = [[]]
    z5 = [[]]
    z6 = [[]]

    print("data ",variants.keys())

    variant_labels = []

    score_values = {}
    #score_values = []
    if is_sorted is False:
            for var in variants.keys():
                if "dbnsfp" in variants[var].keys():
                    if "UTA_Adapter_gene" in variants[var].keys():
                        if "molecular_weight_ref" in variants[var]["UTA_Adapter_gene"]:
                            for score_label in score_labels_raw:
                                if score_label not in score_values.keys():
                                    score_values[score_label] = []
                                if score_label in variants[var]["dbnsfp"]:
                                    score_values[score_label].append(ag.get_max_value(variants[var]["dbnsfp"][score_label]))
                                    z1[0].append(getMolWeightValue(bframe.data,var))
                                    z2[0].append(getChargeValue(bframe.data,var))
                                    z3[0].append(getPolarityValue(bframe.data,var))
                                    z4[0].append(getAromaticityValue(bframe.data,var))
                                    z5[0].append(getFlexibilityValue(bframe.data,var))
                                    z6[0].append(getPhosphorylationValue(bframe.data,var))

                            var_label = variants[var]["UTA_Adapter_gene"]["aminoacid_exchange"]
                            #var_label = var

                            variant_labels.append(var_label)
                            print("all variant labels present: ",var)
    else:
            for var in bframe.sorted_variants:
                if "dbnsfp" in variants[var].keys():
                    if "UTA_Adapter_gene" in variants[var].keys():
                        if "molecular_weight_ref" in variants[var]["UTA_Adapter_gene"]:
                            for score_label in score_labels_raw:
                                if score_label not in score_values.keys():
                                    score_values[score_label] = []
                                if score_label in variants[var]["dbnsfp"]:
                                    score_values[score_label].append(ag.get_max_value(variants[var]["dbnsfp"][score_label]))
                                    z1[0].append(getMolWeightValue(bframe.data,var))
                                    z2[0].append(getChargeValue(bframe.data,var))
                                    z3[0].append(getPolarityValue(bframe.data,var))
                                    z4[0].append(getAromaticityValue(bframe.data,var))
                                    z5[0].append(getFlexibilityValue(bframe.data,var))
                                    z6[0].append(getPhosphorylationValue(bframe.data,var))

                            var_label = variants[var]["UTA_Adapter_gene"]["aminoacid_exchange"]
                            #var_label = var

                            variant_labels.append(var_label)
                            print("all variant labels present: ",var)

    for score_label in score_labels_raw:
        scores.append(score_values[score_label])

    zdata.append(z1)
    zdata.append(z2)
    zdata.append(z3)
    zdata.append(z4)
    zdata.append(z5)
    zdata.append(z6)

    return variant_labels, scores, zdata

def generate_pathogenicity_plot_data(bframe, score_labels_raw):
    """
    
    :param variants:
    :param score_labels_raw:
    :return:
    """
    if isinstance(bframe, dict):
        variants = bframe
        is_sorted=False
    elif isinstance(bframe, ag.BiomarkerFrame):
        variants = bframe.data
        is_sorted = bframe.is_sorted
    scores = []

    for score_label in score_labels_raw:
        score_values = []
        if is_sorted is False:
            for var in variants.keys():
                if "dbnsfp" in variants[var].keys():
                    if score_label in variants[var]["dbnsfp"]:
                        score_values.append(ag.get_max_value(variants[var]["dbnsfp"][score_label]))
        else:
            for var in bframe.sorted_variants:
                if "dbnsfp" in variants[var].keys():
                    if score_label in variants[var]["dbnsfp"]:
                        score_values.append(ag.get_max_value(variants[var]["dbnsfp"][score_label]))
        scores.append(score_values)
    return scores
