import adagenes.conf.read_config as conf_reader
import adagenes.clients.writer as writer
import adagenes
import traceback, csv, copy
import pandas as pd


def avf_to_csv(infile, outfile,mapping=None,labels=None,ranked_labels=None):
    bframe = adagenes.read_file(infile, input_format="avf")
    adagenes.write_file(outfile, bframe, file_type="csv", mapping=mapping, labels=labels, ranked_labels=ranked_labels)

def get_tsv_labels(mapping=None, labels=None, ranked_labels=None):
    """

    :param json_obj:
    :param mapping:
    :return:
    """
    # line = "qid,"
    line = []

    for feature in ranked_labels:
        line.append(feature)
    # get mappings
    #if (mapping is not None) and (labels is not None) and (ranked_labels is not None):
    #    for module in mapping:
    #        if type(mapping[module]) is list:
    #            keys = mapping[module]
    #            for key in keys:
    #                label = module + "_" + key
    #                if label in labels:
    #                    col = labels[label]
    #                else:
    #                    col = label
    #                line.append(col)
    #        else:
    #            line.append(module)
    return line


def get_sorted_values(cols: dict, labels: dict = None, ranked_labels: list = None, qid=None) -> str:
    """

    :param cols:
    :param labels:
    :param ranked_labels:
    :return:
    """
    #print("get sorted values: ",labels)
    #print("ranked labels ",ranked_labels)
    #print("cols ",cols)
    line = []
    #if qid is not None:
    #    line.append(qid)
    if (labels is not None) and (ranked_labels is not None):
        for feature in ranked_labels:
            if feature in cols:
                line.append(cols[feature])
            elif feature in labels.keys():
                mapped_feature = labels[feature]
                if mapped_feature in cols:
                    line.append(cols[mapped_feature])
                else:
                    line.append("")
            else:
                line.append("")
    else:
        for feature in cols.keys():
            line.append(cols[feature])
    return line


def get_row_values(json_obj,mapping=None,sep=","):
    """

    :param json_obj:
    :param mapping:
    :param labels:
    :param features:
    :param sep:
    :return:
    """
    cols = {}

    #print(json_obj)
    for module in mapping:
        if module in json_obj:
            if type(mapping[module]) is list:
                keys = mapping[module]
                for key in keys:
                    if module in json_obj:
                        if isinstance(json_obj[module], dict):
                            try:
                                if key in json_obj[module].keys():
                                    val = str(json_obj[module][key])
                                    val = val.replace(sep, " ")
                                    cols[module + "_" + key] = val
                                else:
                                    pass
                            except:
                                print(key)
                                print(module)
                                print(json_obj)
                                print(traceback.format_exc())
                        else:
                            pass
                    else:
                        pass
            elif isinstance(mapping[module], str):
                if mapping[module] != "":
                    print(module,", ", json_obj[module][mapping[module]])
                    cols[module] = json_obj[module][mapping[module]]
                else:
                    cols[module] = json_obj[module]
            elif isinstance(mapping[module], dict):
                for sub_feature in mapping[module]:
                    if type(mapping[module][sub_feature]) is list:
                        keys = mapping[module][sub_feature]
                        for key in keys:
                            if module in json_obj:
                                if sub_feature in json_obj[module]:
                                    if key in json_obj[module][sub_feature]:
                                        val = str(json_obj[module][sub_feature][key])
                                        val = val.replace(sep, " ")
                                        cols[module + "_" + sub_feature + "_" + key] = val
                                    else:
                                        pass
                            else:
                                pass
                    elif isinstance(mapping[module], str):
                        cols[module] = json_obj[module]

    return cols


def sort_features(line, keys):
    new_line = []
    for key in conf_reader.tsv_feature_ranking:
        if key in keys:
            index = keys.index(key)
            new_line.append(line[index])
    return new_line


class CSVWriter(writer.Writer):

    def __init__(self):
        self.mapping = {
                "variant_data": ["CHROM","POS","REF","ALT"]
            }
        self.labels = {
            "CHROM": "variant_data_CHROM",
            "POS": "variant_data_POS",
            "REF": "variant_data_REF",
            "ALT": "variant_data_ALT"
        }
        self.ranked_labels = ["CHROM", "POS", "REF", "ALT"]

    def pre_process(self, outfile, ranked_labels=None):
        # Write columns
        row = ranked_labels
        if row is None:
            row=self.ranked_labels
        #print(','.join(row),file=outfile)

    def post_process(self, outfile):
        pass

    def write_chunk_to_file(self,
                            outfile,
                            vcf_lines,
                            c,
                            srv_prefix,
                            extract_keys,
                            first_chunk=False,
                            last_chunk=False,
                            mapping=None,
                            ranked_labels=None,
                            labels=None,
                            variants_written=False, save_headers=False):
        """

        :param outfile:
        :param json_obj:
        :param variants_written:
        :param save_headers:
        :return:
        """
        if first_chunk is True:
            print(','.join())

        #self.write_to_file(outfile,json_obj)
        #fields = [vcf_lines[x] for x in list(vcf_lines.keys())]
        #print(type(vcf_lines))
        #print("fields ",fields)
        #print(','.join(fields), file=outfile)

        if mapping is None:
            mapping=self.mapping
            labels=self.labels
            ranked_labels=self.ranked_labels

        for var in vcf_lines.keys():
            row = self.to_single_tsv_line(var, vcf_lines[var], mapping=mapping, labels=labels,
                                          ranked_labels=ranked_labels)
            row = ','.join(row)
            print(row,file=outfile)


    def write_line_to_file(self, outfile, var, vcf_lines, magic_obj, save_headers=False, variants_written=False,
                           mapping=None,
                           ranked_labels=None,
                           labels=None,first_chunk=False, columns=None
                           ):
        """
        Writes a defined number of lines in an output file

        :param outfile:
        :param json_obj:
        :param save_headers:
        :param variants_written:
        :return:
        """
        if hasattr(magic_obj, 'key_labels'):
            labels = magic_obj.key_labels
        else:
            labels = None
        if (not hasattr(magic_obj, 'srv_prefix')) and (magic_obj is not None):
            magic_obj.srv_prefix = None
        if (not hasattr(magic_obj, 'extract_keys')) and (magic_obj is not None):
            magic_obj.extract_keys = None

        if magic_obj is None:
            srv_prefix = ""
            extract_keys = []
        else:
            srv_prefix = magic_obj.srv_prefix
            extract_keys = magic_obj.extract_keys

        print(self.to_single_tsv_line_stream(var, vcf_lines[var], mapping, ranked_labels, first_chunk=first_chunk,columns=columns),
              file=outfile)

    def write_to_file(self, outfile,
                      json_obj,
                      genome_version="hg38",
                      mapping=None,
                      labels=None,
                      ranked_labels=None,
                      sep=',',qid=False,
                      export_features=None):
        """
        Write a biomarker frame to an output file in CSV format

        :param outfile:
        :param json_obj:
        :param mapping:
        :param labels: Dictionary mapping feature identifiers to column labels to be exported
        :param sorted_features: Sorted list of features to export
        :return:
        """
        #print("CSVWriter: Write data in outfile: ", outfile)

        close_file = False
        if isinstance(outfile, str):
            outfile = open(outfile, 'w', newline='')
            close_file = True

        if (mapping is not None) and (ranked_labels is not None):
            csvwriter = csv.writer(outfile, delimiter=sep,
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

            #row = ranked_labels
            #newrow=[]
            #for label in row:
            #    if label in labels:
            #        col = labels[label]
            #        newrow.append(col)
            #    else:
            #        newrow.append(label)
            #row = copy.deepcopy(newrow)
            row = ranked_labels
            csvwriter.writerow(row)
            #print("len ",len(json_obj.data.keys()))

            for var in json_obj.data.keys():
                json_obj.row = json_obj.row + 1
                if qid is True:
                    q = var
                else:
                    q = None
                row = self.to_single_tsv_line(q, json_obj.data[var],mapping=mapping,labels=labels, ranked_labels=ranked_labels)
                #print(len(ranked_labels))
                #print(len(row))
                csvwriter.writerow(row)

            if close_file:
                outfile.close()
        elif export_features is not None:

            if isinstance(export_features, dict):
                ef_keys = list(export_features.keys())
                ef_values = list(export_features.values())
            elif isinstance(export_features, list):
                ef_values = export_features
                ef_keys = export_features

            # Header
            #columns = ",".join(json_obj.preexisting_features + ef_keys)
            columns = ",".join(ef_keys)
            #print("columns ",columns)
            outfile.write(columns + "\n")

            #if json_obj.preexisting_features is not None:
            #    export_features = json_obj.preexisting_features + export_features

            for var in json_obj.data.keys():
                line = ""
                #for feature in json_obj.preexisting_features:
                #    #print("pre feature ",feature," ",json_obj.data[var]["variant_data"][feature] + ",")
                #    if feature in json_obj.data[var]["variant_data"].keys():
                #        line += json_obj.data[var]["variant_data"][feature] + ","
                #    elif feature in json_obj.data[var].keys():
                #        line += json_obj.data[var][feature] + ","
                #    else:
                #        line += ","

                for feature in ef_values:
                    #print("add feature ",feature)
                    if ">" not in feature:
                        if feature in json_obj.data[var].keys():
                            #print("add feature ",feature,": ", json_obj.data[var][feature])
                            line += str(json_obj.data[var][feature]) + ","
                        else:
                            print("not found ",feature, " ",json_obj.data[var])
                            line += ","
                    else:
                        levels = feature.split(">")
                        if len(levels) == 2:
                            #print(levels)
                            if levels[0] in json_obj.data[var]:
                                if levels[1] in json_obj.data[var][levels[0]]:
                                    #print("add feature ", feature, ": ", json_obj.data[var][levels[0]][levels[1]])
                                    line += str(json_obj.data[var][levels[0]][levels[1]]) + ","
                                else:
                                    line += ","
                            else:
                                line += ","
                        else:
                            print("error levels ",str(levels))
                line = line.rstrip(",") + "\n"
                outfile.write(line)
            outfile.close()
        else:
            df = None
            if isinstance(json_obj.data, dict):
                for var in json_obj.data.keys():
                    df_new = pd.json_normalize(json_obj.data[var])
                    if df is not None:
                        df = pd.concat([df,df_new],axis=0)
                    else:
                        df = copy.deepcopy(df_new)
                df["QID"] = list(json_obj.data.keys())
                df.set_index("QID")
                cols = df.columns.tolist()
                cols = cols[-1:] + cols[:-1]
                df = df[cols]
                df.to_csv(outfile,index=False)

    def to_single_tsv_line(self, qid,json_obj,mapping=None, labels=None, ranked_labels=None,sep=',') -> list:
        """

        :param qid:
        :param json_obj:
        :param mapping:
        :return:
        """

        # get mappings
        cols = get_row_values(json_obj,mapping=mapping,sep=sep)
        #print("row values ",str(len(cols)))
        #print("cols ", cols)
        #print("labels ",labels)
        #print("ranked labels ",ranked_labels)
        line = get_sorted_values(cols,labels=labels,ranked_labels=ranked_labels,qid=qid)
        #print("line ",str(len(line)))
        #print(line)
        return line

    def to_single_tsv_line_stream(self, qid, vcf_obj, mapping, ranked_labels,sep=",", first_chunk=False,columns=None) -> list:
        """

        :param qid:
        :param json_obj:
        :param mapping:
        :return:
        """
        #print("to line: ",vcf_obj)

        #mapping = {srv_prefix: extract_keys}
        #ranked_labels = labels
        #print("mapping ",mapping)
        ln = 0
        #columns = []
        if isinstance(mapping, dict):
            for key in mapping.keys():
                if key != '':
                    ln += 1
        #print("mapping ",mapping)

        if ln>0:
            # get mappings
            cols = get_row_values(vcf_obj, mapping=mapping, sep=sep)
            # print("row values ",str(len(cols)))
            # print("cols ", cols)
            # print("labels ",labels)
            # print("ranked labels ",ranked_labels)
            #line = get_sorted_values(cols, labels=None, ranked_labels=ranked_labels, qid=qid)
            # print("line ",str(len(line)))
            #print(vcf_obj)
            #print(line)
            #line_str = ",".join('"' + line + '"') + '\n'
            #line_str = ",".join('"' + element + '"' for element in line)
            #cols = [col.replace("info_features","") for col in cols]
            #print(cols)
            #print("columns: ",columns)

            line_str = ''
            for col in columns:
                if col in cols:
                    line_str += cols[col] + sep
                elif "info_features_" + col in cols:
                    line_str += cols["info_features_"+col] + sep
                else:
                    line_str += sep
            line_str = line_str.rstrip(sep)

            #print("return ",line_str)
        else:
            normalized_variant_data = {}
            for key in vcf_obj.keys():
                if (key != "variant_data") and isinstance(vcf_obj[key], str):
                    normalized_variant_data[key] = vcf_obj[key]

            if "variant_data" in vcf_obj.keys():
                normalized_variant_data["CHROM"] = vcf_obj["variant_data"]["CHROM"]
                normalized_variant_data["POS"] = vcf_obj["variant_data"]["POS"]
                normalized_variant_data["REF"] = vcf_obj["variant_data"]["REF"]
                normalized_variant_data["ALT"] = vcf_obj["variant_data"]["ALT"]

            if "info_features" in vcf_obj.keys():
                for key in vcf_obj["info_features"].keys():
                    normalized_variant_data[key] = vcf_obj["info_features"][key]
            #    for key in vcf_obj["variant_data"].keys():
            #        if isinstance(vcf_obj["variant_data"][key], str):
            #            normalized_variant_data[key] = vcf_obj["variant_data"][key]

            #df = pd.DataFrame([normalized_variant_data])
            #print(df)
            #print(df.columns)
            line = []
            cols = []

            first_chunk=False
            if first_chunk is False:
                #print("norm ",normalized_variant_data)

                df = pd.DataFrame([normalized_variant_data])
                cols = df.columns
                for i, row in df.iterrows():
                    line_str = ",".join('"' + element + '"' for element in row)

                #for key in vcf_obj.keys():
                #    if (key != "variant_data") and isinstance(vcf_obj[key], str):
                #        if key not in cols:
                #            cols.append(key)
                #        line.append()
                #print(line_str)
            else:
                print("FIRST CHUNK")
                df = pd.DataFrame([normalized_variant_data])
                line_str = ",".join('"' + element + '"' for element in df.columns)
                #print("df cols ",df.columns)
                #print("cols ",line_str)
                first_chunk = False

        return line_str

    def get_feature_keys(self, variant_data, extract_keys):
        """

        :param variant_data:
        :param extract_keys:
        :return:
        """
        feature_labels = []
        #feature_labels.append("QID")

        tsv_features = conf_reader.tsv_columns
        if self.features is not None:
            tsv_features = self.features

        for col in tsv_features:
            # if col in variant_data.keys():
            #    for key in variant_data[var].keys():
            #        if (key not in feature_labels) and (key in config.tsv_columns):
            #                feature_labels.append(key)
            feature_labels.append(col)

        return ','.join(feature_labels)

    def generate_columns(self, outfile, mapping,sep=","):
        cols = []
        for key in mapping.keys():
            if key != "info_features":
                if key not in cols:
                    cols.append(key)
            elif key == "info_features":
                for feature in mapping["info_features"]:
                    if feature not in cols:
                        cols.append(feature)
        print(sep.join(cols),file=outfile)
        return cols
