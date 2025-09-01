import traceback, json


def aggregate_evidence_data_by_pmid_drugs(variant_data, databases=None):
    """
        Aggregates evidence data from a set of databases by a set of features

        :param variant_data:
        :param keys:
        :param databases:
        :return:
        """
    agg_key = "agg"

    for var in variant_data.keys():
        variant_data[var]["onkopus_aggregator"][agg_key] = {}
        results = variant_data[var]["onkopus_aggregator"]["merged_match_types_data"]
        for i, res in enumerate(results):
                #pmids = str(variant_data[var]["onkopus_aggregator"]["aggregated_evidence_data"]["exact_match"][i]['citation_id']).upper().split(',')
                drugs = res['drugs']
                source = str(res['source'])

                for el in drugs:
                            try:
                                        #print("DRUGEL ", el)
                                        if isinstance(el, dict):
                                            drug_name = el["drug_name"].lower()
                                            print("DRUGNAME ",drug_name)

                                            if drug_name not in variant_data[var]["onkopus_aggregator"][agg_key].keys():
                                                aggregated_data = {}
                                                aggregated_data['sources'] = []
                                                aggregated_data['sources'].append(source)
                                                print("add ",drug_name,": ",aggregated_data)
                                                variant_data[var]["onkopus_aggregator"][agg_key][drug_name] = aggregated_data
                                            else:
                                                # variant_data[var][agg_key][pmid]['sources'].append(source)
                                                variant_data[var]["onkopus_aggregator"][agg_key][drug_name]['sources'].append(source)
                            except:
                                print(traceback.format_exc())

                    #for pmid in pmids:
                    #    value = pmid + "-" + drugs
                    #    if value not in variant_data[var][agg_key].keys():
                    #        aggregated_data = {}
                    #        aggregated_data['sources'] = []
                    #        aggregated_data['sources'].append(source)
                    #        variant_data[var][agg_key][value] = aggregated_data
                    #    else:
                    #        variant_data[var][agg_key][value]['sources'].append(source)
        print(var," agg ",variant_data[var]["onkopus_aggregator"][agg_key])
    return variant_data

def aggregate_evidence_data_by_pmid_drug_classes(variant_data, databases=None):
    """
        Aggregates evidence data from a set of databases by a set of features

        :param variant_data:
        :param keys:
        :param databases:
        :return:
        """
    agg_key = "agg"

    for var in variant_data.keys():
        variant_data[var]["onkopus_aggregator"][agg_key] = {}
        results = variant_data[var]["onkopus_aggregator"]["merged_match_types_data"]
        for i, res in enumerate(results):
                drugs = res['drugs']
                source = str(res['source'])

                for el in drugs:
                    try:
                                    if isinstance(el, dict):
                                        print("el ",el)
                                        drug_classes = el["drug_class"]

                                        for drug_class in drug_classes:
                                            print("DRUGclass ",drug_class)

                                            if drug_class not in variant_data[var]["onkopus_aggregator"][agg_key].keys():
                                                aggregated_data = {}
                                                aggregated_data['sources'] = []
                                                aggregated_data['sources'].append(source)
                                                print("add ",drug_class,": ",aggregated_data)
                                                variant_data[var]["onkopus_aggregator"][agg_key][drug_class.lower()] = aggregated_data
                                            else:
                                                # variant_data[var][agg_key][pmid]['sources'].append(source)
                                                variant_data[var]["onkopus_aggregator"][agg_key][drug_class.lower()]['sources'].append(source)
                    except:
                        print(traceback.format_exc())

        #print(var," agg ",variant_data[var]["onkopus_aggregator"][agg_key])
    return variant_data


def aggregate_evidence_data_by_pmid(variant_data, databases=None):
    """
        Aggregates evidence data from a set of databases by a set of features

        :param variant_data:
        :param keys:
        :param databases:
        :return:
        """
    #agg_key = config.get_config()['DEFAULT']['AGGREGATED_EVIDENCE_DATA_KEY']
    agg_key = "agg"
    if databases is None:
        databases = ["","",""]

    for var in variant_data.keys():
        if "onkopus_aggregator" in variant_data[var].keys():
            variant_data[var]["onkopus_aggregator"][agg_key] = {}
            #for db in databases:
            #results = variant_data[var][db + '_extract_norm']
            results = variant_data[var]["onkopus_aggregator"]["merged_match_types_data"]
            #results = variant_data[var]["onkopus_aggregator"]["aggregated_evidence_data"]["exact_match"]
            for i, res in enumerate(results):
                        #pmids = str(variant_data[var][db + '_extract_norm'][i]['citation_id']).upper().split(',')

                        #for pmid in pmids:
                            #value = pmid
                            source = res["source"]
                            pmid =  res["citation_url"]
                            print(pmid)
                            if pmid not in variant_data[var]["onkopus_aggregator"][agg_key].keys():
                                aggregated_data = {}
                                aggregated_data['sources'] = []
                                aggregated_data['sources'].append(source)
                                variant_data[var]["onkopus_aggregator"][agg_key][pmid] = aggregated_data
                            else:
                                #variant_data[var][agg_key][pmid]['sources'].append(source)
                                variant_data[var]["onkopus_aggregator"][agg_key][pmid]['sources'].append(source)
    #print(variant_data)
    return variant_data


def aggregate_evidence_data_by_features(variant_data, keys, databases=None):
    """
    Aggregates evidence data from a set of databases by a set of features

    :param variant_data:
    :param keys:
    :param databases:
    :return:
    """
    agg_key = "merged_match_types_data"

    for var in variant_data.keys():
        variant_data[var][agg_key] = {}
        for db in databases:
            results = variant_data[var][db + '_extract_norm']
            for i, res in enumerate(results):
                for key in keys:
                    value = variant_data[var][db + '_extract_norm'][i][key]
                    if value not in variant_data[var][agg_key].keys():
                        aggregated_data = {}
                        aggregated_data['sources'] = []
                        aggregated_data['sources'].append(db)
                        variant_data[var][agg_key][value] = aggregated_data
                    else:
                        variant_data[var][agg_key][value]['sources'].append(db)
    return variant_data
