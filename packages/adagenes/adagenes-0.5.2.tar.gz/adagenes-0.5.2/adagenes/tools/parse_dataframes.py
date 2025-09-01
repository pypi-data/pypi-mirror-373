import traceback, csv, copy
import pandas as pd
import adagenes.conf.read_config as config
import adagenes
from adagenes.tools.parse_genomic_data import parse_variant_identifier_gdesc


def to_single_tsv_line(self, qid, json_obj, mapping=None, labels=None, features=None, sep=','):
    """

    :param qid:
    :param json_obj:
    :param mapping:
    :return:
    """

    # get mappings
    # line = qid + ","#
    line = []
    cols = {}

    for module in mapping:
        if type(mapping[module]) is list:
            keys = mapping[module]
            for key in keys:
                if module in json_obj:
                    if key in json_obj[module]:
                        val = str(json_obj[module][key])
                        val = val.replace(sep, " ")
                        # line.append(val)
                        cols[module + "_" + key] = val
                    else:
                        # print("no key: ",module,",",key)
                        # line.append("")
                        pass
                else:
                    # print("no module: ",module,",",key)
                    # line.append("")
                    pass
        else:
            line.append(str(json_obj[module]))
    # line = line.rstrip(',')
    # line = sort_features(line, cols)
    for feature in features:
        if feature in cols:
            line.append(cols[feature])
        else:
            # print("feature not found ",feature,",",cols.keys())
            line.append("")

    return line


def write_csv_to_file(outfile_src, json_obj, mapping=None,labels=None,sort_features=True,
                      sorted_features=None,sep=','):
    """

    :param outfile_src:
    :param json_obj:
    :param mapping:
    :param labels:
    :param sort_features:
    :param sorted_features:
    :param sep:
    :return:
    """
    if mapping is None:
        mapping = config.tsv_mappings

    if labels is None:
        labels = config.tsv_labels

    if sorted_features is None:
        sorted_features = config.tsv_feature_ranking

    # outfile = open(outfile_src, 'w')
    print("Write data in outfile: ", outfile_src)
    with open(outfile_src, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=sep,
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # print(self.get_tsv_labels(json_obj,mapping=mapping,labels=labels),file=outfile)
        if sort_features is False:
            row = get_tsv_labels(mapping=mapping, labels=labels)
            sorted_features = row
        else:
            row = sorted_features
            newrow = []
            for label in row:
                if label in labels:
                    col = labels[label]
                    newrow.append(col)
            row = newrow
        csvwriter.writerow(row)

        for var in json_obj.data.keys():
            json_obj.row = json_obj.row + 1
            # print(self.to_single_tsv_line(var, json_obj.data[var],mapping=mapping,labels=labels),
            #      file=outfile)
            row = to_single_tsv_line(var, json_obj.data[var], mapping=mapping, labels=labels,
                                          features=sorted_features)
            csvwriter.writerow(row)


def get_tsv_labels(mapping=None, labels=None):
    """
    Returns an array of feature labels

    :param json_obj:
    :param mapping:
    :return:
    """
    # line = "qid,"
    line = []

    if mapping is None:
        mapping = config.tsv_mappings

    # get mappings
    for module in mapping:
        if type(mapping[module]) is list:
            keys = mapping[module]
            for key in keys:
                label = module + "_" + key
                if label in labels:
                    col = labels[label]
                else:
                    col = label
                line.append(col)
        else:
            line.append(module)

    # line = line.rstrip(',')
    # sort_features(line,line)

    return line


def parse_mapping(mapping):
    pass

def parse_line():
    pass


#def parse_csv_line_protein(line, columns, mapping, sep=","):
#    gene_pos = columns.index(mapping["gene"])
#    variant_pos = columns.index(mapping["variant"])
#
#    fields = line.strip().split(sep)

def parse_csv_lines(lines,
                    columns,
                    json_obj,
                    genome_version="hg38",
                    dragen_file:bool = False,
                    mapping=None,
                    level="gene",
                    sep=",",
                    header=True,
                    remove_quotes=True):
    """
    Recognizes the biomarker data format of a dataframe.
    Returns the parsed variant data

    :param lines:
    :param columns:
    :param json_obj:
    :param genome_version:
    :param dragen_file:
    :param mapping:
    :param sep:
    :return:
    """

    genome_mapping = True
    protein_mapping = False
    variant_data_new = {}

    variant_data = {}
    if (columns is None) and (header is True):
        #fields = lines[0]
        columns = lines[0]#[i for i in range(0,len(fields))]
        columns_orig = lines[0]
    else:
        columns_orig = copy.deepcopy(columns)
        columns = [x.lower() for x in columns]

    if isinstance(json_obj,adagenes.BiomarkerFrame):
        json_obj.preexisting_features = columns
    elif isinstance(json_obj, dict):
        variant_data = json_obj
    #print("columns: ", columns)
    data_type = "vcf"

    if genome_version is None:
        genome_version="hg38"


    chrom_pos = 0
    pos_pos = 1
    ref_pos = 2
    alt_pos = 3

    mutation_level = "g"

    chrom_defined = False
    if mapping is not None:
        keys = copy.deepcopy(list(mapping.keys()))
        for key in keys:
            if isinstance(mapping[key], str):
                val = str(mapping[key]).lower()
            else:
                val = copy.deepcopy(mapping[key])

            mapping[key] = val
            mapping[key.lower()] = mapping.pop(key)

        if "chrom" in mapping.keys():
            if "<def>" in str(mapping["chrom"]):
                mapping["chrom"] = mapping["chrom"].replace("<def>","")
                chrom_pos = mapping["chrom"]
                chrom_defined = True
            else:
                if "chrom" in mapping.keys():
                    if isinstance(mapping["chrom"], int):
                        chrom_pos = mapping["chrom"]
                    else:
                        print(mapping)
                        chrom_pos = columns.index(mapping["chrom"])

        if "aa_exchange" in mapping.keys():
            mutation_level = "p"
            if isinstance(mapping["aa_exchange"], int):
                ref_pos = mapping["aa_exchange"]
            else:
                ref_pos = columns.index(mapping["aa_exchange"])
            alt_pos = None
            data_type = "ref_aa"
            if isinstance(mapping["pos"], int):
                pos_pos = mapping["pos"]
            else:
                pos_pos = columns.index(mapping["pos"])
        elif "g_description" in mapping.keys():
            if isinstance(mapping["g_description"], int):
                pos_pos = mapping["g_description"]
            else:
                pos_pos = columns.index(mapping["g_description"])
            alt_pos = None
            ref_pos = None
            data_type = "g_desc"
        elif "gene" in mapping.keys() and "variant" in mapping.keys():
            protein_mapping = True
            genome_mapping = False
            gene_col = mapping["gene"]
            var_col = mapping["variant"]
            gene_pos = columns.index(gene_col)
            var_pos = columns.index(var_col)
        else:
            if "ref" in mapping:
                if isinstance(mapping["ref"], int):
                    ref_pos = mapping["ref"]
                else:
                    ref_pos = columns.index(mapping["ref"])
                if isinstance(mapping["alt"], int):
                    alt_pos = mapping["alt"]
                else:
                    alt_pos = columns.index(mapping["alt"])
            elif "pos2" in mapping:
                if isinstance(mapping["pos2"], int):
                    pos2 = mapping["pos2"]
                else:
                    pos2 = columns.index(mapping["pos2"])

            if isinstance(mapping["pos"], int):
                pos_pos = mapping["pos"]
            else:
                pos_pos = columns.index(mapping["pos"])

    else:
        if ("chrom" in columns) and ("pos" in columns) and ("ref" in columns) and ("alt" in columns):
            chrom_pos = columns.index("chrom")
            pos_pos = columns.index("pos")
            ref_pos = columns.index("ref")
            alt_pos = columns.index("alt")
        elif ("chrom" in columns) and ("pos_hg38" in columns) and ("ref" in columns) and ("alt" in columns) and \
                (genome_version=="hg38"):
            chrom_pos = columns.index("chrom")
            pos_pos = columns.index("pos_hg38")
            ref_pos = columns.index("ref")
            alt_pos = columns.index("alt")
        elif ("chrom" in columns) and ("pos_hg19" in columns) and ("ref" in columns) and ("alt" in columns) and \
                (genome_version=="hg19"):
            chrom_pos = columns.index("chrom")
            pos_pos = columns.index("pos_hg19")
            ref_pos = columns.index("ref")
            alt_pos = columns.index("alt")
        elif ("qid" in columns):
            qid_pos = columns.index("qid")
            data_type="qid"
        elif ('gene' in columns) and ('variant' in columns):
            mutation_level = "p"
            data_type="protein"
        elif ('gene' in columns) and ('aa_exchange' in columns):
            data_type='protein'
            mutation_level = "p"
        elif "chrom" in columns and "pos" in columns and "pos2" in columns:
            data_type="cna"
            mutation_level = "g"
        else:
            #print("Error: Could not find column labels for identifying SNPs (CHROM,POS,REF,ALT) and "
            #      "no column mapping is specified. Please add column labels to your variant file or "
            #      "define a mapping that defined the indices of the associated columns, e.g. "
            #      "        mapping = {"
            #      "  'chrom': 1,"
            #      "  'pos': 2,"
            #      "  'ref': 4,"
            #      "  'alt': 5"
            #      "}"
            #      )
            #return json_obj
            data_type="undefined"

    #print("chrom pos ",chrom_pos," pos ",pos_pos," ref ",ref_pos, " alt pos ",alt_pos)

    for l,line in enumerate(lines):
        fields = line #line.strip().split(sep)
        key = ''
        #print("data type ",data_type)

        if dragen_file is True:
            chr = str(fields[0])
            pos = fields[1]
            ref = fields[3]
            alt = fields[4]
            key = 'chr' + str(chr) + ':' + str(pos) + str(ref) + '>' + str(alt)
            variant_data[key] = {}
            variant_data[key][config.variant_data_key] = {}
            if "chr" in chr:
                chr = chr.replace("chr","")
            variant_data[key][config.variant_data_key]["CHROM"] = chr
            variant_data[key][config.variant_data_key]["POS"] = pos
            variant_data[key][config.variant_data_key]["POS_"+genome_version] = pos
            variant_data[key][config.variant_data_key]["REF"] = ref
            variant_data[key][config.variant_data_key]["ALT"] = alt
            variant_data[key]["additional_columns"] = {}

            variant_data[key]["mutation_type_detail"] = "Missense_Mutation"

            #for j in range(0, (df.shape[1])):
            #    variant_data[key]["additional_columns"][columns[j]] = df.iloc[i, j]
        elif protein_mapping is True:
            #print("protein mapping active, gene pos ", gene_pos," , var pos ",var_pos)
            qid = fields[gene_pos] + ':' + fields[var_pos]
            data = {}
            data["UTA_Adapter"] = {}
            data["UTA_Adapter"]["gene_name"] = fields[gene_pos]
            data["UTA_Adapter"]["variant_exchange"] = fields[var_pos]
            #json_obj.data_type = "p"
            variant_data_new[qid] = data
            #print("var new ",variant_data_new)

        elif data_type=="qid":
            # id_index = columns.index('QID')
            #key = df.iloc[i, :].loc["qid"]
            key = fields[qid_pos] # df.iloc[i, qid_pos]
            chr, ref_seq, pos, ref, alt = adagenes.parse_genome_position(key)
            data = {}
            data[config.variant_data_key] = {}
            if "chr" in chr:
                chr = chr.replace("chr","")
            data[config.variant_data_key]["CHROM"] = chr
            data[config.variant_data_key]["POS"] = pos
            data[config.variant_data_key]["POS_" + genome_version] = pos
            data[config.variant_data_key]["REF"] = ref
            data[config.variant_data_key]["ALT"] = alt
            data["mutation_type_detail"] = "Missense_Mutation"
            variant_data[key] = data
            json_obj.data_type = "g"
        elif data_type=="vcf":
            if chrom_defined is not False:
                chr = chrom_pos
            else:
                chr =  fields[chrom_pos]

            print(fields, ", ",pos_pos)
            pos = fields[pos_pos]
            ref = fields[ref_pos]
            alt = fields[alt_pos]
            chrom_str = str(chr)
            if "chr" not in chrom_str:
                chrom_str = "chr" + chrom_str
            key = chrom_str + ':' + str(pos) + str(ref) + '>' + str(alt)
            data = {}
            data[config.variant_data_key] = {}
            if "chr" in chrom_str:
                chrom_str = chrom_str.replace("chr","")
            data[config.variant_data_key]["CHROM"] = chrom_str
            data[config.variant_data_key]["POS"] = pos
            data[config.variant_data_key]["POS_" + genome_version] = pos
            data[config.variant_data_key]["REF"] = ref
            data[config.variant_data_key]["ALT"] = alt
            data["mutation_type_detail"] = "Missense_Mutation"
            for i,field in enumerate(fields):
                if remove_quotes is True:
                    if field.startswith('"'):
                        field = field.lstrip('"').rstrip('"')
                #data[config.variant_data_key][columns[i]] = field
            variant_data[key] = data
            json_obj.data_type = "g"
        elif ('gene' in columns) and ('variant' in columns):
            #print("read data by gene name and amino acid exchange")
            genome_version = "hg38"
            data = {}
            # data[config.variant_data_key] = {}
            gene_pos = columns.index('gene')
            variant_pos = columns.index('variant')
            gene = fields[gene_pos]  # df.iloc[i, :].loc["gene"]
            variant = fields[variant_pos]
            data[str(gene) + ":" + str(variant)] = {}
            #data[gene + ":" + variant][
            #    config.uta_adapter_genetogenomic_srv_prefix] = {}
            #data[gene + ":" + variant][
            #    config.uta_adapter_genetogenomic_srv_prefix][config.uta_genomic_keys[0]] = gene
            #data[gene + ":" + variant][
            #    config.uta_adapter_genetogenomic_srv_prefix][config.uta_genomic_keys[1]] = variant

            #client = CCSGeneToGenomicClient(genome_version)
            #data = client.process_data(data, input_format='tsv')

            genomic_locations = list(data.keys())
            for genomepos in genomic_locations:
                variant_data[genomepos] = data[genomepos]
                variant_data[genomepos]["level"] = "protein"

                # Add gene and variant data
                variant_data[genomepos]["UTA_Adapter"] = {}
                variant_data[genomepos]["UTA_Adapter"]["gene_name"] = gene
                variant_data[genomepos]["UTA_Adapter"]["variant_exchange"] = variant
            json_obj.data_type = "p"
        elif ('gene' in columns) and ('aa_exchange' in columns):
            #print("read data by gene name and amino acid exchange")
            genome_version = "hg38"
            data = {}
            mutation_level = "p"
            # data[config.variant_data_key] = {}
            gene_pos = columns.index('gene')
            variant_pos = columns.index('aa_exchange')
            gene = fields[gene_pos]  # df.iloc[i, :].loc["gene"]
            variant = fields[variant_pos]
            data[str(gene) + ":" + str(variant)] = {}

            genomic_locations = list(data.keys())
            for genomepos in genomic_locations:
                variant_data[genomepos] = data[genomepos]
                variant_data[genomepos]["level"] = "protein"

                # Add gene and variant data
                variant_data[genomepos]["UTA_Adapter"] = {}
                variant_data[genomepos]["UTA_Adapter"]["gene_name"] = gene
                variant_data[genomepos]["UTA_Adapter"]["variant_exchange"] = variant
            json_obj.data_type = "p"
        elif ("uniprot" in columns) and ('aa_exchange' in columns):
            # print("read data by gene name and amino acid exchange")
            genome_version = "hg38"
            data = {}
            mutation_level = "p"
            # data[config.variant_data_key] = {}
            #print(columns)
            gene_pos = columns.index('uniprot')
            variant_pos = columns.index('aa_exchange')

            if len(fields) == len(columns):
                gene = fields[gene_pos]  # df.iloc[i, :].loc["gene"]
                variant = fields[variant_pos]
                data[str(gene) + ":" + str(variant)] = {}

                genomic_locations = list(data.keys())
                for genomepos in genomic_locations:
                    variant_data[genomepos] = data[genomepos]
                    variant_data[genomepos]["level"] = "protein"

                    # Add gene and variant data
                    variant_data[genomepos]["uniprot_id"] = gene
                    variant_data[genomepos]["aa_exchange"] = variant
                json_obj.data_type = "p"
        elif data_type == "ref_aa":
            try:
                if chrom_defined is not False:
                    chr = chrom_pos
                else:
                    chr = fields[chrom_pos]  # .loc["chrom"]
                pos = fields[pos_pos]  # .loc["pos"]

                # Split reference and alternate allele
                refalt = fields[ref_pos]
                if "del" in refalt:
                    continue
                if "ins" in refalt:
                    continue
                else:
                    elements = refalt.split(">")
                    if len(elements) > 1:
                        ref = elements[0]
                        alt = elements[1]
                    else:
                        print("Could not parse ",refalt)
                        continue
                key = 'chr' + str(chr) + ':' + str(pos) + str(ref) + '>' + str(alt)
                data = {}
                data[config.variant_data_key] = {}
                if "chr" in chr:
                    chr = chr.replace("chr", "")
                data[config.variant_data_key]["CHROM"] = chr
                data[config.variant_data_key]["POS"] = pos
                data[config.variant_data_key]["POS_" + genome_version] = pos
                data[config.variant_data_key]["REF"] = ref
                data[config.variant_data_key]["ALT"] = alt
                variant_data[key] = data
                json_obj.data_type = "g"
            except:
                print(traceback.format_exc())
        elif data_type == "g_desc":
            try:
                if chrom_defined is not False:
                    chr = chrom_pos
                else:
                    chr = fields[chrom_pos]  # .loc["chrom"]
                pos = fields[pos_pos]  # .loc["pos"]

                # Split reference and alternate allele
                gdesc = fields[pos_pos]

                qid, vdata = parse_variant_identifier_gdesc(chr, gdesc, genome_version)
                key = qid
                if qid is not None:
                    #if qid is not None:
                    variant_data[qid] = vdata
                    json_obj.data_type = "g"
            except:
                print(traceback.format_exc())
        elif data_type == "cna":
            try:
                chrom = fields[chrom_pos]
                pos = fields[pos_pos]
                pos2 = fields[pos2]
                mtype = fields[mtype]
                qid = "chr" + chrom + ":" + pos + "_" + pos2 + mtype
            except:
                print(traceback.format_exc())
        #elif data_type == "unidentified":
        #    variant_data[qid] = vdata
        else:
            # Unidentifiable columns
            #print("unidentifiable columns: ", columns, " fields ", fields)
            vdata = {}
            for i,col in enumerate(columns):
                if col != "":
                    try:
                        #print(col," fields ",fields)
                        vdata[col] = fields[i]
                    except:
                        print(traceback.format_exc())
            vdata["type"] = "unidentified"
            qid = str(l) #fields[0]
            variant_data[qid] = vdata

        # Read existing feature data
        for j, feature in enumerate(columns_orig):
            if (key != '') and (key in variant_data.keys()):
                if feature not in variant_data[key]:
                    variant_data[key][feature] = {}
                try:
                    #if feature in config.tsv_mappings.keys():
                    #    # if len(elements) > j:
                    #    #    if elements[j]:
                    #    # print("assign ",elements,", feature ",feature,",",i,": ",elements[i])
                    #    #variant_data[key][feature][config.tsv_mappings[feature]] = df.iloc[i, j]
                    #    pass
                    #else:
                    #print(columns_orig)
                    fields_index = columns_orig.index(feature)
                    if len(fields) > fields_index:
                        variant_data[key][feature] = fields[fields_index]
                    #else:
                    #    print("cannot add ","feature ",feature," at index ",fields_index," line ",fields)
                except:
                    variant_data[key][feature] = ''
                    print("error adding feature (TSV)")
                    print(traceback.format_exc())

    #print("csv vars ",variant_data)
    if isinstance(json_obj, adagenes.BiomarkerFrame):
        pre_features = json_obj.preexisting_features
        json_obj_new = adagenes.BiomarkerFrame(variant_data, genome_version=genome_version,
                                               preexisting_features=pre_features)
        # json_obj.data = variant_data
        json_obj_new.data_type = mutation_level
        json_obj_new.preexisting_features = pre_features
        return json_obj_new
    else:
        pre_features = None
        return variant_data_new


def write_csv_to_dataframe(outfile_src, json_obj, mapping=None,labels=None,sort_features=True,
                      sorted_features=None,sep=','):
    """

    :param outfile_src:
    :param json_obj:
    :param mapping:
    :param labels:
    :param sort_features:
    :param sorted_features:
    :param sep:
    :return:
    """
    if mapping is None:
        mapping = config.tsv_mappings

    if labels is None:
        labels = config.tsv_labels

    if sorted_features is None:
        sorted_features = config.tsv_feature_ranking

    # outfile = open(outfile_src, 'w')
    print("Write data in outfile: ", outfile_src)
    data={}
    # print(self.get_tsv_labels(json_obj,mapping=mapping,labels=labels),file=outfile)
    if sort_features is False:
        row = get_tsv_labels(mapping=mapping, labels=labels)
        sorted_features = row
    else:
        row = sorted_features
        newrow = []
        for label in row:
            if label in labels:
                col = labels[label]
                newrow.append(col)
        row = newrow
    columns = row
    for col in columns:
        data[col] = []

    for var in json_obj.data.keys():
        json_obj.row = json_obj.row + 1
        # print(self.to_single_tsv_line(var, json_obj.data[var],mapping=mapping,labels=labels),
        #      file=outfile)
        row = to_single_tsv_line(var, json_obj.data[var], mapping=mapping, labels=labels,
                                          features=sorted_features)
        #csvwriter.writerow(row)
        for i,col in enumerate(columns):
            data[col].append(row[i])

    df = pd.DataFrame(data=data)
    return df


def is_dragen_file(columns):
    """
    Detects whether an Excel file is in DRAGEN format

    :param columns:
    :return:
    """
    dragen_columns = ['Chromosome', 'Region', 'Type', 'Reference', 'Allele', 'Coverage', 'Frequency', 'Exact match', 'AF',
                          'EUR_AF 1000GENOMES-phase_3_ensembl_v91_o', 'AF_EXAC clinvar_20171029_o', 'CLNSIG clinvar_20171029_o',
                          'RS clinvar_20171029_o', 'Homo_sapiens_refseq_GRCh38_p9_o_Genes', 'Coding region change',
                          'Amino acid change', 'Splice effect', 'mRNA Accession', 'Exon Number', 'dbSNP']
    if len(columns) > 6:
        #print([x for x in columns[0:5] if x in dragen_columns[0:5]])
        if len([x for x in columns[0:5] if x in dragen_columns[0:5]]) == 5:
            print("DRAGEN file detected")
            return True
    #print("Could not detect DRAGEN file ",columns)
    return False

