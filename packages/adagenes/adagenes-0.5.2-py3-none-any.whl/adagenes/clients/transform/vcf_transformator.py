

class VCFTransformator:

    def __init__(self, transform_model):
        self.transform_model = transform_model

    def process_data(self, bframe):

        print("Start VCF transform: ",self.transform_model)

        map_chrom = self.transform_model["chrom"]
        map_pos = self.transform_model["pos"]
        map_ref = self.transform_model["ref"]
        map_alt = self.transform_model["alt"]

        #print(bframe)
        bframe_new = {}

        for var in bframe.keys():
            if "variant_data" not in bframe[var].keys():
                bframe[var]["variant_data"] = {}

            keys_dc = {}
            for key in bframe[var].keys():
                keys_dc[key.lower()] = key

            if map_chrom in keys_dc.keys():
                chrom = bframe[var][ keys_dc[map_chrom] ]
                if 'chr' not in chrom:
                    chrom = 'chr' + str(chrom)
                pos = bframe[var][ keys_dc[map_pos] ]
                ref = bframe[var][ keys_dc[map_ref] ]
                alt = bframe[var][ keys_dc[map_alt] ]
                qid = chrom + ':' + str(pos) + str(ref) + '>' + str(alt)

                bframe_new[qid] = {}
                bframe_new[qid]["variant_data"] = {}
                bframe_new[qid]["variant_data"]["CHROM"] = chrom
                bframe_new[qid]["variant_data"]["POS"] = pos
                bframe_new[qid]["variant_data"]["REF"] = ref
                bframe_new[qid]["variant_data"]["ALT"] = alt
                bframe_new[qid]["variant_data"]["ID"] = '.'
                bframe_new[qid]["variant_data"]["QUAL"] = '.'
                bframe_new[qid]["variant_data"]["FILTER"] = '.'
                bframe_new[qid]["variant_data"]["INFO"] = '.'
                bframe_new[qid]["variant_data"]["OPTIONAL"] = '.'

                infovals = []
                for key in bframe[var].keys():
                    if (key != map_chrom) and (key != map_pos) and (key != map_ref) and (key != map_alt) \
                            and (key != "variant_data"):
                        bframe_new[qid][key] = bframe[var][key]
                        infovals.append(key + '=' + bframe[var][key])
                #if "variant_data" in bframe[var].keys():
                #    for key in bframe[var]["variant_data"].keys():
                if len(infovals) > 0:
                    bframe_new[qid]["variant_data"]["INFO"] = ";".join(infovals)
            else:
                print("Error: Feature ",map_chrom,", model ",self.transform_model, " not found: ",bframe[var])

        #print(bframe_new)
        return bframe_new


