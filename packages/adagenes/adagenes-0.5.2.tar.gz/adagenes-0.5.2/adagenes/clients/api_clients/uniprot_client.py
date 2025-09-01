import traceback, datetime, json
import adagenes.tools.module_requests as req
from adagenes.conf import read_config as config
import adagenes as ag


class UniprotClient:

    def __init__(self):
        self.info_lines= config.uniprot_info_lines
        self.url_pattern = config.uniprot_src
        self.srv_prefix = config.uniprot_srv_prefix
        self.response_keys = config.uniprot_response_keys
        self.extract_keys = config.uniprot_keys

        self.qid_key = "q_id"
        self.genome_version="hg38"

    def process_data(self, biomarker_data):
        """

        :param biomarker_data:
        :param tumor_type:
        :return:
        """
        try:
            qid_list = []
            uniprot_id_dc = {}
            for var in biomarker_data.keys():
                if "uniprot_id" in biomarker_data[var]:
                    qid_list.append(biomarker_data[var]["uniprot_id"])
                    if biomarker_data[var]["uniprot_id"] not in uniprot_id_dc:
                        uniprot_id_dc[biomarker_data[var]["uniprot_id"]] = []
                    uniprot_id_dc[biomarker_data[var]["uniprot_id"]].append(var)

            qid_lists_query = ag.tools.split_list(qid_list)

            for qlist in qid_lists_query:
                uniprot_ids = ",".join(qlist)
                q = "?uniprot-id=" + uniprot_ids
                res = req.get_connection(q, self.url_pattern, self.genome_version)

                for uid in res.keys():
                    for var in uniprot_id_dc[uid]:
                        biomarker_data[var]["gene_name"] = res[uid]["gene_symbol"]

        except:
            print(traceback.format_exc())

        return biomarker_data
