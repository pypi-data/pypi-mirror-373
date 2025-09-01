import traceback
import pandas as pd

import adagenes.tools.parse_cancer_type_labels
from adagenes.conf import read_config as config

response_type_cols = {
    "Sensitivity/Response": 10,
    "Sensitive": 10,
    "Resistance": -10,
    "Resistant": -10,
    "": 0
}


def generate_clinical_significance_sunburst_data_biomarker_set(
        json_obj,
        pid,
        section="merged_match_types_data",
        match_types=config.match_types,
        required_fields= ["citation_id","response_type","evidence_level_onkopus"]
    ) -> pd.DataFrame:
    """
    Generates the dataframe for displaying a sunburst plot for a set of biomarkers

    Includes the following columns:
    'PID' (patient_id),
    'Biomarker' (Biomarker in search/variant file),
    'Cancer Type',
    'PMID',
    'EvLevel',
    'Drugs',
    'Response',
    'Drug_Class',
    'num': num

    :param json_obj:
    :param pid:
    :return:
    """
    biomarkers = []
    citation_urls = []
    citation_ids = []
    evlevel = []
    drugs = []
    num = []
    cancer_types = []
    scores = []
    resp_types = []
    drugclasses = []
    match_types = []
    associated_biomarkers = []
    allvars = []

    if pid is None:
        pid = "Biomarkers"

    for qid in json_obj.keys():
        if config.onkopus_aggregator_srv_prefix in json_obj[qid]:
                    #for match_type in config.match_types:
                    #    if match_type in json_obj[qid][config.onkopus_aggregator_srv_prefix][section]:
                    for count, result in enumerate(
                            json_obj[qid][config.onkopus_aggregator_srv_prefix][section]):

                        include_result = True

                        try:
                            if "gene_name" in json_obj[qid][config.uta_adapter_srv_prefix]:
                                gene = json_obj[qid][config.uta_adapter_srv_prefix]["gene_name"]
                            else:
                                gene = ""
                            if "variant_exchange" in json_obj[qid][config.uta_adapter_srv_prefix]:
                                variant_exchange = json_obj[qid][config.uta_adapter_srv_prefix]["variant_exchange"]
                            else:
                                variant_exchange = ""
                            biomarker = gene + ":" + variant_exchange

                            if variant_exchange == "":
                                biomarker = gene

                            if "citation_id" in result:
                                if result["citation_id"] == '':
                                    if "citation_id" in required_fields:
                                        include_result = False
                                    else:
                                        citation_id = "_"
                                else:
                                    citation_id = result["citation_id"]
                            else:
                                if "citation_id" in required_fields:
                                    include_result = False

                            if "evidence_level_onkopus" in result:
                                ev_level = result["evidence_level_onkopus"]
                            else:
                                ev_level = ""
                                if "evidence_level_onkopus" in required_fields:
                                    include_result = False

                            # Parse drugs and drug classes
                            drug = ""
                            drug_classes = []
                            if "drugs" in result:
                                if isinstance(result["drugs"],list):
                                    for d in result["drugs"]:
                                        if (d != "") and (isinstance(d, dict)):
                                            drug += d["drug_name"] + ","
                                            #print(drug)
                                            if "drug_class" in d:
                                                if isinstance(d["drug_class"], list):
                                                    #drug_classes = d["drug_class"]
                                                    for dc in d["drug_class"]:
                                                        if dc != "":
                                                            dc = dc.replace("-","_")
                                                            drug_classes.append(dc)
                                                elif isinstance(d["drug_class"],str):
                                                    #drug_classes = [d["drug_class"]]
                                                    if d["drug_class"] != "":
                                                        dc = d["drug_class"]
                                                        dc = dc.replace("-", "_")
                                                        drug_classes.append(dc)
                                                else:
                                                    #print("No drug class list found: ", d["drug_class"])
                                                    pass
                                        else:
                                            print("no drugs found ", result)
                                            include_result = False
                                elif isinstance(result["drugs"],str):
                                    drug = result["drugs"]
                                drug = drug.rstrip(",")
                                if len(drug_classes) == 0:
                                    drug_classes = ["_"]
                                    if "drug_class" in required_fields:
                                        include_result = False
                            if drug == "":
                                drug = "_"
                                #if "drugs" in required_fields:
                                include_result = False

                            if "disease_normalized" in result:
                                if result["disease_normalized"] != "":
                                    cancer_type = result["disease_normalized"]
                                else:
                                    cancer_type = "_"
                                    if "disease" in required_fields:
                                        include_result = False
                            else:
                                cancer_type = "_"
                                if "disease_normalized" in required_fields:
                                    include_result = False

                            if "match_type" in result:
                                match_type = result["match_type"]
                            else:
                                match_type = ""

                            if "response" in result:
                                res = result["response"]
                            elif "response_type" in result:
                                res = result["response_type"]
                            else:
                                res = ""
                                if ("response" in required_fields) or ("response_type" in required_fields):
                                    include_result = False
                                #continue

                            if res in response_type_cols:
                                resp_type = response_type_cols[res]
                            else:
                                # Append zero for unknown
                                resp_type = 0

                            associated_biomarker = result["biomarker"]
                        except:
                            print(traceback.format_exc())
                            include_result = False
                            continue

                        if include_result is True:
                            #print(result,":",resp_type,":",drug_classes)
                            for drug_class in drug_classes:
                                biomarkers.append(biomarker)
                                citation_urls.append(
                                    "<a href='" + config.config["EXTERNAL_SOURCES"]["PUBMED_URL"] + citation_id + "'>"
                                    + "(" + str(count +1) + ") " + citation_id + "</a>")
                                citation_ids.append(citation_id)
                                evlevel.append(ev_level)
                                drugs.append(drug)
                                cancer_types.append(cancer_type)
                                drugclasses.append(drug_class)
                                resp_types.append(resp_type)
                                match_types.append(match_type)
                                associated_biomarkers.append(associated_biomarker)
                                num.append(1)
                                #patient_id.append(pid)
    count_cancer_types = {}
    for ctype in citation_urls:
        if ctype not in count_cancer_types:
            count_cancer_types[ctype] = 0
        count_cancer_types[ctype] = int(count_cancer_types[ctype]) + 1

    # num = [int(count_cancer_types[citation_url[x]]) for x in range(0, len(citation_url))]
    # num = [float(count_cancer_types[citation_url[x]]) for x in range(0, len(citation_url))]
    #num = [float(resp_types[x]) + 20 for x in range(0, len(resp_types))]
    num = [1 for x in range(0, len(citation_urls))]
    # num = resp_types
    patient_id = [pid for x in range(0, len(num))]
    allvars = ["Molecular profile" for x in range(0, len(num))]

    data = {
        'PID': patient_id,
        'Biomarker': biomarkers,
        'Cancer Type': cancer_types,
        'PMID': citation_urls,
        'Citation ID': citation_ids,
        'EvLevel': evlevel,
        'Drugs': drugs,
        'Response Type': resp_types,
        'Drug_Class': drugclasses,
        'Match_Type': match_types,
        'num': num,
        'Associated_Biomarker': associated_biomarkers,
        'MolProfile': allvars
    }

    print(len(data["PID"]), ", ", len(data["Biomarker"]), ", ", len(data["Cancer Type"]), ", ", len(data["PMID"]), ", ", len(data["EvLevel"]),
          ", ", len(data["Drugs"]), ", ", len(data["Response Type"]), ", ", len(data["Drug_Class"]), ", ", len(data["num"]))
    df = pd.DataFrame(data=data)
    #print(df["Drug_Class"].to_list())
    #print(df.iloc[0:5,:])
    #print(df.shape)
    return df


def generate_treatment_match_type_sunburst_data(
        json_obj,
        pid,
        section="merged_match_types_data",
        required_fields=["citation_id","response_type","evidence_level_onkopus"]) -> pd.DataFrame:
    """

    :param json_obj:
    :param pid:
    :param section: Data section in the biomarker frame where the clinical evidence data is stored
    :param required_fields: List of features that have to be present and not empty in order to include the result in the dataframe
    :return:
    """
    biomarkers = []
    citation_urls = []
    citation_ids = []
    evlevel = []
    drugs = []
    num = []
    patient_id = []
    cancer_types = []
    scores = []
    resp_types = []
    drugclasses = []
    match_types = []
    associated_biomarkers = []
    allvars = []

    if pid is None:
        pid = "Biomarkers"

    qid=pid
    if qid in json_obj:
        if config.onkopus_aggregator_srv_prefix in json_obj[qid]:
                        #for match_type in config.match_types:
                        #    if match_type in json_obj[qid][config.onkopus_aggregator_srv_prefix][section]:
                        for count,result in enumerate(json_obj[qid][config.onkopus_aggregator_srv_prefix][section]):

                            include_result = True

                            try:
                                if "gene_name" in json_obj[qid][config.uta_adapter_srv_prefix]:
                                    gene = json_obj[qid][config.uta_adapter_srv_prefix]["gene_name"]
                                else:
                                    gene = ""
                                if "variant_exchange" in json_obj[qid][config.uta_adapter_srv_prefix]:
                                    variant_exchange = json_obj[qid][config.uta_adapter_srv_prefix]["variant_exchange"]
                                else:
                                    variant_exchange = ""
                                biomarker = gene + ":" + variant_exchange

                                if "citation_id" in result:
                                    if result["citation_id"] == '':
                                        if "citation_id" in required_fields:
                                            include_result = False
                                        else:
                                            citation_id="_"
                                    else:
                                        citation_id = result["citation_id"]
                                else:
                                    if "citation_id" in required_fields:
                                        include_result = False

                                if "evidence_level_onkopus" in result:
                                    ev_level = result["evidence_level_onkopus"]
                                else:
                                    ev_level = ""
                                    if "evidence_level_onkopus" in required_fields:
                                        include_result = False

                                # Parse drugs and drug classes
                                drug = ""
                                drug_classes = []
                                if "drugs" in result:
                                    if isinstance(result["drugs"],list):
                                        for d in result["drugs"]:
                                            if isinstance(d, dict):
                                                if d["drug_name"] != "":
                                                    drug += d["drug_name"] + ","
                                                    if "drug_class" in d:
                                                        if isinstance(d["drug_class"], list):
                                                            drug_classes = d["drug_class"]
                                                        else:
                                                            print("No drug class list found: ", d["drug_class"])
                                            elif (isinstance(d, str)) and (d!=""):
                                                drug = d
                                                print("drug is str: ",result)
                                            else:
                                                print("no drugs found ", result)
                                                include_result = False
                                    elif isinstance(result["drugs"],str):
                                        drug = result["drugs"]
                                    drug = drug.rstrip(",")
                                    if len(drug_classes) == 0:
                                        drug_classes = ["_"]
                                        if "drug_class" in required_fields:
                                            include_result = False
                                if drug == "":
                                    drug = "_"
                                    #if "drugs" in required_fields:
                                    include_result = False

                                if "disease_normalized" in result:
                                    if result["disease_normalized"]!="":
                                        cancer_type = result["disease_normalized"]
                                    else:
                                        cancer_type = "_"
                                        if "disease" in required_fields:
                                            include_result = False
                                else:
                                    cancer_type = "_"
                                    if "disease" in required_fields:
                                        include_result = False

                                if "match_type" in result:
                                    match_type = result["match_type"]
                                else:
                                    match_type = ""

                                if "response" in result:
                                    res = result["response"]
                                elif "response_type" in result:
                                    res = result["response_type"]
                                else:
                                    res = ""
                                    if ("response" in required_fields) or ("response_type" in required_fields):
                                        include_result = False
                                    continue

                                if res in response_type_cols:
                                    resp_type = response_type_cols[res]
                                else:
                                    # Append zero for unknown
                                    resp_type = 0

                                associated_biomarker = result["biomarker"]
                            except:
                                print(traceback.format_exc())
                                include_result = False
                                continue

                            if include_result:
                                for drug_class in drug_classes:
                                    biomarkers.append(biomarker)
                                    citation_urls.append(
                                        "<a href='" + config.config["EXTERNAL_SOURCES"]["PUBMED_URL"] + citation_id + "'>"
                                        + "(" + str(count+1) + ") " + citation_id + "</a>")
                                    citation_ids.append(citation_id)
                                    evlevel.append(ev_level)
                                    drugs.append(drug)
                                    cancer_types.append(cancer_type)
                                    drugclasses.append(drug_class)
                                    resp_types.append(resp_type)
                                    match_types.append(match_type)
                                    associated_biomarkers.append(associated_biomarker)
                                    num.append(1)
                                    patient_id.append(pid)
    else:
        print("query ID not found: ",qid,": ",json_obj)

    count_cancer_types = {}
    for ctype in citation_urls:
        if ctype not in count_cancer_types:
            count_cancer_types[ctype] = 0
        count_cancer_types[ctype] = int(count_cancer_types[ctype]) + 1

    # num = [int(count_cancer_types[citation_url[x]]) for x in range(0, len(citation_url))]
    # num = [float(count_cancer_types[citation_url[x]]) for x in range(0, len(citation_url))]
    #num = [float(resp_types[x]) + 20 for x in range(0, len(citation_urls))]
    #num = [1 for x in range(0, len(cancer_types))]
    # num = resp_types
    #patient_id = [pid for x in range(0, len(num))]

    #cancer_types = adagenes.tools.parse_cancer_type_labels.parse_cancer_entity_labels(cancer_types)
    allvars = ["Molecular profile" for x in range(0, len(num))]

    data = {
        'PID': patient_id,
        'Biomarker': biomarkers,
        'Cancer Type': cancer_types,
        'PMID': citation_urls,
        'Citation ID': citation_ids,
        'EvLevel': evlevel,
        'Drugs': drugs,
        'Response Type': resp_types,
        'Drug_Class': drugclasses,
        'Match_Type': match_types,
        'num': num,
        'Associated_Biomarker': associated_biomarkers,
        'MolProfile': allvars
    }

    # print(data)
    print(len(data["PID"]), ", ", len(data["Biomarker"]), ", ", len(data["Cancer Type"]), ", ", len(data["PMID"]), ", ", len(data["EvLevel"]),
          ", ", len(data["Drugs"]), ", ", len(data["Response Type"]), ", ", len(data["Drug_Class"]), ", ", len(data["num"]))
    df = pd.DataFrame(data=data)
    return df

