import adagenes
import adagenes as ag
import adagenes.clients.writer as writer
import traceback
import adagenes.tools.maf_mgt


class MAFWriter(writer.Writer):

    def __init__(self, mapping=None):
        self.mapping = mapping
        if self.mapping is None:
            #self.mapping = ag.tools.maf_mgt.onkopus_maf_mapping
            self.mapping = ag.tools.maf_mgt.onkopus_maf_mapping_knime
            self.columns = ag.tools.maf_mgt.maf_columns_knime

    def pre_process(self, outfile, ranked_labels=None):
        """
        Prints the MAF column labels to an output file

        :param outfile:
        :return:
        """
        # line = adagenes.tools.maf_mgt.maf_columns
        self.print_header(outfile, None)
        columns = list(self.columns)
        print("\t".join(columns), file=outfile)

    def write_chunk_to_file(self, outfile, json_obj, variants_written=False, save_headers=False):
        """

        :param outfile:
        :param json_obj:
        :param variants_written:
        :param save_headers:
        :return:
        """
        self.write_to_file(outfile,json_obj)

    def write_to_file(self, outfile, json_obj,
                      mapping=None, gz=False, export_feature=None,
                      labels=None, sorted_features=None,
                      export_features=None, ranked_labels=None
                      ):
        """
        Write a biomarker frame to a MAF file

        :param outfile_src:
        :param json_obj:
        :param mapping:
        :return:
        """
        close_file = False
        if isinstance(outfile, str):
            if gz is False:
                outfile = open(outfile, 'w')
            else:
                outfile = open(outfile, 'wb')
            close_file = True

        self.pre_process(outfile)
        #self.print_header(outfile, json_obj)
        #print_maf_columns(outfile)

        for var in json_obj.data.keys():
            json_obj.row = json_obj.row + 1
            if "variant_data" in json_obj.data[var]:
                if "type" in json_obj.data[var]["variant_data"]:
                    if json_obj.data[var]["variant_data"]["type"] == "unidentified":
                        continue
            print(self.to_single_line(var, json_obj.data[var]), file=outfile)

        if close_file is True:
            outfile.close()

    def print_header(self, outfile, bframe: adagenes.BiomarkerFrame):
        """
        Prints the header lines of a MAF if the source format had been MAF as well

        :param outfile: Output file
        :param bframe: Annotated biomarker frame
        :return:
        """
        if bframe is not None:
            #headers="#version 2.3\n"
            if (bframe.src_format == "maf"):
                for line in bframe.header_lines:
                    print(line, file=outfile)

    def to_single_line(self, qid, json_obj):
        """

        :param qid:
        :param json_obj:
        :param mapping:
        :return:
        """
        line = ""
        #print(json_obj)
        for feature in adagenes.tools.maf_mgt.maf_columns_knime:
            feature_added = False
            if self.mapping is not None:
                if feature in self.mapping.keys():
                    module = self.mapping[feature]
                    if isinstance(module, dict):
                        for key, val in module.items():
                            #print("search key ",key,": ",val)

                            if key in json_obj.keys():
                                if val == "POS2":
                                    if val not in json_obj[key].keys():
                                        val = "POS"
                                if val in json_obj[key].keys():
                                    if val == "POS2":
                                        if val not in json_obj[key].keys():
                                            val = "POS"
                                            #print("assign pos")
                                        else:
                                            #print("PIS2 ",json_obj[key][val])
                                            if (json_obj[key][val] is None) or (json_obj[key][val] == "None"):
                                                val = "POS"
                                                #print("assign pos")

                                    if json_obj[key][val] != '':
                                        #print("added: ",val, ": ",json_obj[key][val])
                                        line += str(json_obj[key][val]) + "\t"
                                        feature_added = True
                                    #else:
                                    #    print(val, "val null")
                    elif isinstance(module, str):
                        if module in json_obj.keys():
                            if json_obj[module] != '':
                                line += json_obj[module] + "\t"
                                feature_added = True
            if feature_added is False:
                if "info_features" in json_obj.keys():
                    if feature in json_obj["info_features"]:
                        if json_obj["info_features"][feature] != '':
                            line += json_obj["info_features"][feature] + "\t"
                            feature_added = True

            if feature_added is False:
                line += ".\t"
        #line = line.rstrip('.\t')

        last_occurrence = line.rfind('\t')
        if last_occurrence != -1:
            line = line[:last_occurrence] + line[last_occurrence + len('\t'):]

        #print("line ",line)

        return line
