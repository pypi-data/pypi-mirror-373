import copy

import adagenes


class DragenToBFrame:
    """
    Converts variant data in Dragen format into VCF format
    """

    def __init__(self, genome_version, error_logfile=None):
        pass

    def transform_mnv_into_multiple_snvs(self, variant):

        new_snvs = {}
        if "additional_columns" in variant:
            if "Type" in variant["additional_columns"]:
                biomarker_type = variant["additional_columns"]["Type"]
                if biomarker_type == "MNV":

                    pos_start,pos_end = variant["variant_data"]["POS"].split("..")
                    #print("pos start ",pos_start,", ",pos_end)

                    for i,(pos_ref,pos_alt) in enumerate(zip(variant["variant_data"]["REF"], variant["variant_data"]["ALT"])):
                        #print("compare ",pos_ref,",",pos_alt)
                        if pos_ref != pos_alt:
                            #print("pos ",int(pos_start) + i, ", ",pos_ref," to ",pos_alt)
                            new_snv_pos = int(pos_start) + i
                            new_snv_qid = "chr" + str(variant["variant_data"]["CHROM"]) + ":" + str(new_snv_pos) + str(pos_ref) + ">" + str(pos_alt)

                            new_snv_data = { "variant_data": {
                                    "CHROM": variant["variant_data"]["CHROM"],
                                    "POS": str(new_snv_pos),
                                    "REF": pos_ref,
                                    "ALT": pos_alt
                                }, "additional_columns": {"TYPE": "SNV"}
                            }

                            new_snvs[new_snv_qid] = new_snv_data

        return variant, new_snvs

    def transform_indel_into_vcf_indel(self,variant):

        if "additional_columns" in variant:
            if "Type" in variant["additional_columns"]:
                biomarker_type = variant["additional_columns"]["Type"]
                if (biomarker_type == "Deletion") or (biomarker_type == "Insertion"):
                    pos_start, pos_end = variant["variant_data"]["POS"].split("..")
                    variant["variant_data"]["POS"] = pos_start

        return variant

    def process_data(self, json_obj):
        """

        :param json_obj: Biomarker data frame
        :return:
        """
        qids = copy.copy(list(json_obj.keys()))
        #for qid in qids:
            #json_obj[qid], new_snvs = self.transform_mnv_into_multiple_snvs(json_obj[qid])
            #if json_obj[qid]["additional_columns"]["type"] == "MNV":
            #    json_obj.pop(qid)

            #json_obj.update(new_snvs)

        qids = copy.copy(list(json_obj.keys()))
        for qid in qids:
            json_obj[qid] = self.transform_indel_into_vcf_indel(json_obj[qid])
        #print(json_obj.keys())

        return json_obj
