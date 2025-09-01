import adagenes.clients.writer as writer
import adagenes.conf.vcf_config
from adagenes.conf import read_config as conf_reader
from adagenes.tools.parse_vcf import generate_variant_data_section,generate_vcf_columns
import traceback


def generate_annotations_stream(srv_prefix, vcf_obj, extract_keys, labels):
    """

    :param srv_prefix:
    :param vcf_obj:
    :param extract_keys:
    :return:
    """

    annotations = []
    if isinstance(srv_prefix, str):
        if srv_prefix in vcf_obj:
            service_output = vcf_obj[srv_prefix]
            #print("service output ", service_output)
            #service_output = service_output.replace(";","")
            for k in extract_keys:
                if k in service_output:
                    #anno = service_output[k].replace(";","_")
                    #annotations.append('{}_{}={}'.format(srv_prefix, k, anno))
                    annotations.append('{}_{}={}'.format(srv_prefix, k, service_output[k]))
            #if srv_prefix == "dbnsfp":
            #    print("output DBNSFP")
            #    #print(service_output)
            #    print("annotations ",annotations)
    elif isinstance(srv_prefix, list):
        for i,pref in enumerate(srv_prefix):
            if pref in vcf_obj.keys():
                service_output = vcf_obj[pref]
                #if srv_prefix == "dbnsfp":
                #    print("output DBNSFP")
                #    print(service_output)
                #service_output = service_output.replace(";", "")
                #print("service output ",service_output)
                k_list = extract_keys[i]
                if isinstance(k_list,list):
                    for k in k_list:
                        if k in service_output:
                            annotations.append('{}_{}={}'.format(pref, k, service_output[k]))
                elif isinstance(k_list, str):
                    for j,k in enumerate(extract_keys):
                        if k in service_output:
                            if labels is not None:
                                label = labels[j]
                                annotations.append('{}={}'.format(label, service_output[k]))
                            else:
                                annotations.append('{}_{}={}'.format(pref, k, service_output[k]))
    return annotations


def generate_annotations(vcf_obj,mapping,labels,sorted_features):
    """
    Generates VCF annotations for a single variant

    :param vcf_obj:
    :param mapping:
    :param labels:
    :param sorted_features:
    :return:
    """
    print("mapping ",mapping," labels ",labels, " sorted ",sorted_features)
    base_list=["CHROM","POS","REF","ALT","ID","QUAL","FILTER","INFO","OPTIONAL","GENOME_VERSION"]
    if (mapping is not None) and (labels is not None) and (sorted_features is not None):
        annotations = []
        cols = {}
        for module in mapping:
            if type(mapping[module]) is list:
                keys = mapping[module]
                for key in keys:
                    if module in vcf_obj:
                        if key in vcf_obj[module]:
                            val = str(vcf_obj[module][key])
                            val = val.replace(",", " ")
                            # line.append(val)
                            cols[module + "_" + key] = val
                        else:
                            #print("no key: ",module,",",key)
                            # line.append("")
                            pass
                    else:
                        #print("no module: ",module,",",key)
                        # line.append("")
                        pass
            else:
                # line.append(str(vcf_obj[module]))
                pass
        # line = line.rstrip(',')
        # line = sort_features(line, cols)
        #print("cols ",cols)
        for feature in sorted_features:
            label = labels[feature]
            if label in cols:
                # line.append(cols[feature])
                annotations.append(feature + '=' + cols[label])
                #print("add annotations ",label + '=' + cols[feature])
            else:
                #print("feature not found ",feature,",",cols.keys())
                # line.append("")
                pass
    else:
        annotations = []
        if "variant_data" in vcf_obj:
            for feature in vcf_obj["variant_data"]:
                if feature == "info_features":
                    for info_feature in vcf_obj["variant_data"]["info_features"]:
                        annotations.append(feature+ "=" + vcf_obj["variant_data"]["info_features"][info_feature])
                elif isinstance(vcf_obj["variant_data"][feature],str):
                    if feature not in base_list:
                        annotations.append(feature+"="+vcf_obj["variant_data"][feature])
    return annotations


class BEDWriter(writer.Writer):

    def write_to_file(self, outfile, json_obj, genome_version="hg38",
                      mapping=None, labels=None, ranked_labels=None,
                      sort_features=False, save_headers=True, export_features=None):
        """
        Writes a biomarker JSON representation into a Variant Call Format (VCF) file

        :param outfile: Output file where to save the new file. May either be a file object or a string
        :param json_obj: Biomarker JSON representation
        :param genome_version: Reference genome of the source data which is saved as an additional header line. Possible values are 'hg19', 'GRCh37, 'hg38' and 'GRCh38'
        :param save_headers: Defines whether header lines should be included in the VCF file
        :return:
        """
        close_file = False
        if isinstance(outfile, str):
            outfile = open(outfile, 'w')
            close_file = True

        for var in json_obj.data.keys():
            json_obj.row = json_obj.row + 1
            row = self.to_single_vcf_line(json_obj.data[var], mapping=mapping,labels=labels,
                                              sort_features=sort_features, sorted_features = ranked_labels)
            if row != '':
                print(row,file=outfile)

        if close_file is True:
            outfile.close()


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
        #print("WRITE VCF ",vcf_lines)

        #if save_headers:
        #    for line in json_obj.header_lines:
        #        print(line, file=outfile)

        #for var in json_obj.data.keys():
        #    json_obj.row = json_obj.row + 1
        #    print(self.to_single_vcf_line(json_obj.data[var]), file=outfile)

        # for json_obj in vcf_lines:
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
        print(self.to_single_vcf_line_stream(vcf_lines[var], srv_prefix, extract_keys, labels),
              file=outfile)

    def to_single_vcf_line(self, vcf_obj,mapping=None, labels=None, sort_features=True, sorted_features=None):
        """
        Receives data of a single variant in JSON format and converts it to a line in Variant Call Format (VCF)

        :param vcf_obj:
        :param srv_prefix:
        :param extract_keys:
        :return:
        """

        try:
            vcf_obj = generate_variant_data_section(vcf_obj)
            vcf_obj = generate_vcf_columns(vcf_obj)

            annotations = generate_annotations(vcf_obj,mapping,labels,sorted_features)

            annotations = ';'.join(annotations)
            vcf_obj[conf_reader.variant_data_key]["INFO"] = vcf_obj[conf_reader.variant_data_key]["INFO"] + ";" + annotations
            vcf_obj[conf_reader.variant_data_key]["INFO"] = vcf_obj[conf_reader.variant_data_key]["INFO"].lstrip(";.")

            if (conf_reader.variant_data_key in vcf_obj) and ('OPTIONAL' in vcf_obj[conf_reader.variant_data_key]):
                optional_columns = '\t'.join(vcf_obj[conf_reader.variant_data_key]['OPTIONAL'])
            else:
                optional_columns = ''

            if "variant_data" in vcf_obj:
                if "CHROM" in vcf_obj["variant_data"]:

                    chrom = vcf_obj[conf_reader.variant_data_key]['CHROM']
                    if 'chr' not in chrom:
                        chrom = 'chr' + chrom

                    pos = int(vcf_obj[conf_reader.variant_data_key]['POS']) -1

                    if "POS2" in vcf_obj["variant_data"]:
                        pos2 = int(vcf_obj["variant_data"]["POS"]) -1
                    else:
                        pos2 = int(vcf_obj[conf_reader.variant_data_key]['POS'])

                    gene = ""
                    if "UTA_Adapter" in vcf_obj:
                        if "gene_name" in vcf_obj["UTA_Adapter"]:
                            gene = vcf_obj["UTA_Adapter"]["gene_name"]
                    if gene == "":
                        gene = str(chrom) + ":" + str(pos) + "-" + str(pos2)

                    qual = vcf_obj[conf_reader.variant_data_key]['QUAL']
                    if qual == "":
                        qual = "."
                    filter_vcf = vcf_obj[conf_reader.variant_data_key]['FILTER']
                    if filter_vcf == "":
                        filter_vcf = "."
                    id_vcf = vcf_obj[conf_reader.variant_data_key]['ID']
                    if id_vcf == "":
                        id_vcf = "."
                    info_vcf = vcf_obj[conf_reader.variant_data_key]['INFO']
                    if info_vcf == "":
                        info_vcf = "."

                    vcfline = f"{chrom}\t{pos}\t{pos2}\t{gene}"
                    vcfline = vcfline.rstrip("\t")
                    return vcfline
                else:
                    print("Could not identify: ",vcf_obj)
                    return ""
        except:
            print(traceback.format_exc())
            return ''

    def pre_process(self, outfile, ranked_labels=None):
        row = ranked_labels
        if row is None:
            pass
            #row=self.ranked_labels
        #print(','.join(row),file=outfile)

    def to_single_vcf_line_stream(self, vcf_obj, srv_prefix, extract_keys, labels):
        """

        :param vcf_obj:
        :param srv_prefix:
        :param extract_keys:
        :return:
        """
        if srv_prefix is not None:
            annotations = generate_annotations_stream(srv_prefix, vcf_obj, extract_keys, labels)
        else:
            annotations = []


        chrom = vcf_obj[conf_reader.variant_data_key]['CHROM']
        if 'chr' not in chrom:
            chrom = 'chr' + chrom

        # splits = vcf_lines[qid].split("\t")
        #print("to vcf: ",vcf_obj)
        if "INFO" not in vcf_obj.keys():
            if "INFO" in vcf_obj["variant_data"].keys():
                vcf_obj["INFO"] = vcf_obj["variant_data"]["INFO"]
                vcf_obj["OPTIONAL"] = vcf_obj["variant_data"]["OPTIONAL"]
                vcf_obj["ID"] = vcf_obj["variant_data"]["ID"]
                vcf_obj["QUAL"] = vcf_obj["variant_data"]["QUAL"]
                vcf_obj["FILTER"] = vcf_obj["variant_data"]["FILTER"]

        if "INFO" not in vcf_obj.keys():
            vcf_obj["INFO"] = ""

        #print("vcf annos ",annotations)
        vcf_obj["INFO"] = vcf_obj["INFO"] + ";" + ';'.join(annotations)

        # vcf_lines[qid] = "\t".join(splits)
        vcf_obj["INFO"] = vcf_obj["INFO"].lstrip(";.")

        if vcf_obj["INFO"] == "":
            vcf_obj["INFO"] = "."
        #print("INFO col ", vcf_obj["INFO"])

        if "OPTIONAL" not in vcf_obj.keys():
            vcf_obj["OPTIONAL"] = []
        if "ID" not in vcf_obj.keys():
            vcf_obj["ID"] = ""
        if "QUAL" not in vcf_obj.keys():
            vcf_obj["QUAL"] = ""
        if "FILTER" not in vcf_obj.keys():
            vcf_obj["FILTER"] = ""
        optional_columns = '\t'.join(vcf_obj['OPTIONAL'])
        # vcfline = f"{vcf_obj['CHROM']}\t{vcf_obj['POS']}\t{vcf_obj['ID']}\t{vcf_obj['REF']}" \
        #    f"\t{vcf_obj['ALT']}\t{vcf_obj['QUAL']}\t{vcf_obj['FILTER']}\t{vcf_obj['INFO']}" \
        #    f"\t{optional_columns}"
        # print("obj ",vcf_obj)
        vcfline = f"{chrom}\t{vcf_obj['variant_data']['POS']}\t{vcf_obj['ID']}\t{vcf_obj['variant_data']['REF']}" \
                  f"\t{vcf_obj['variant_data']['ALT']}\t{vcf_obj['QUAL']}\t{vcf_obj['FILTER']}\t{vcf_obj['INFO']}" \
                  f"\t{optional_columns}"

        return vcfline.rstrip("\t")

    def generate_columns(self, outfile, mapping,sep="\t"):
        pass
