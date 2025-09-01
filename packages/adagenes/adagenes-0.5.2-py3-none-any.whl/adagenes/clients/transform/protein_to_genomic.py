import traceback
import adagenes as ag
import adagenes.tools.module_requests as req

__MODULE_PROTOCOL__ = "https"
__MODULE_SERVER__ = "mtb.bioinf.med.uni-goettingen.de"

def refseq_protein_to_gene(bframe, batch_size=100):
    """
    Converts a biomarker frame with variants at protein level to genomic level.

    :param bframe:
    :return:
    """
    url_pattern = __MODULE_PROTOCOL__ + "://" + __MODULE_SERVER__ + "/mane-adapter/v1/proteinRequest"
    var_data_new = {}

    qid_list = []
    for var in bframe.data.keys():
        mdesc = bframe.data[var]["mdesc"]
        if mdesc == "refseq_protein":
            qid_list.append(var)
        else:
            var_data_new[var] = bframe.data[var]

    while True:
        max_length = int(batch_size)
        if max_length > len(qid_list):
            max_length = len(qid_list)
        qids_partial = qid_list[0:max_length]

        proteins = ",".join(qids_partial)
        query = '?q=' + proteins

        try:
            json_body = req.get_connection(query, url_pattern, "hg38")

            for protein_id in json_body.keys():

                gene_name = list(json_body[protein_id].keys())[0]

                try:
                    #bframe.data[qid][self.srv_prefix] = json_body[gene_name]
                    var_data_new[gene_name] = bframe.data[protein_id]
                    var_data_new[gene_name]["mane"] = json_body[protein_id][gene_name][0]
                except:
                        print("Error processing variant response: ", traceback.format_exc())
        except:
            print(": error processing variant response: ;", traceback.format_exc())

        for i in range(0, max_length):
            # del gene_names[0] #gene_names.remove(qid)
            # del variant_exchange[0]  #variant_exchange.remove(qid)
            del qid_list[0]  # qid_list.remove(qid)
        if len(qid_list) == 0:
            break

    bframe.data = var_data_new

    return bframe
