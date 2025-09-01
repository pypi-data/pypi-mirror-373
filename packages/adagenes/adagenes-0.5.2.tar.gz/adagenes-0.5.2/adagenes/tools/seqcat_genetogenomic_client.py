import traceback, copy
import adagenes.tools.module_requests as req
import adagenes.tools.parse_genomic_data

batch_size = 100
#uta_adapter_src = "https" + "://" + "mtb.bioinf.med.uni-goettingen.de" + "/CCS/v1/GenomicToGene/{}/"
uta_genomic_keys = ['gene_name', 'variant_exchange', 'input_data']
uta_gene_keys = ['results_string']
uta_gene_response_keys = ['chr', 'start', 'ref', 'var', 'input_data']
uta_adapter_genetogenomic_src = "https" + "://" + "mtb.bioinf.med.uni-goettingen.de" + "/CCS/v1/GeneToGenomic/{}/"
uta_adapter_info_lines = [
    '##INFO=<ID=UTA-Adapter-GeneName,Number=1,Type=String,Description="Gene name of genomic location">',
    '##INFO=<ID=UTA-Adapter-VariantExchange,Number=1,Type=Float,Description="Variant exchange of a genomic location">'
]
uta_adapter_srv_prefix = 'UTA_Adapter'
uta_adapter_genetogenomic_srv_prefix = 'UTA_Adapter_gene'
uta_adapter_genetogenomic_gene_prefix = 'Gene'
uta_adapter_genetogenomic_variant_prefix = 'Variant'


def strip_long_indels(variants):
    variants_new = []
    for variant in variants:
        if not len(variant) > 30:
            variants_new.append(variant)

    return variants_new


class SeqCATProteinClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines = uta_adapter_info_lines
        self.url_pattern = uta_adapter_genetogenomic_src
        self.srv_prefix = uta_adapter_srv_prefix
        self.genomic_keys = uta_genomic_keys
        self.gene_keys = uta_gene_keys
        self.gene_response_keys = uta_gene_response_keys
        self.extract_keys = uta_genomic_keys

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def generate_variant_list(self, variants, variant_list_without_alternate_alleles):
        """
        Generates a list of variants for module requests and the associated reference genome. Prioritizes hg38/GRCh38 positions if data is available.

        :param variants:
        :param variant_list_without_alternate_alleles:
        :return:
        """
        request_genome = self.genome_version
        check_for_hg38 = False
        variant_list = []
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            check_for_hg38 = True
            request_genome = "hg38"
        for var in variant_list_without_alternate_alleles:
            if check_for_hg38:
                if "POS_hg38" in variants[var]["variant_data"]:
                    hg38_id = variants[var]["variant_data"]["CHROM"] + ":" + variants[var]["variant_data"]["POS_hg38"] \
                              + variants[var]["variant_data"]["REF"] + ">" + variants[var]["variant_data"]["ALT"]
                    variant_list.append(hg38_id)
                else:
                    variant_list.append("")
            else:
                variant_list.append(var)

        return variant_list, request_genome

    def process_data(self, vcf_lines):
        """
        Retrieves genomic, transcriptomic and proteomic data from the Coordinates Converter service

        :param vcf_lines:
        :return:
        """
        qid_list = copy.deepcopy(list(vcf_lines.keys()))
        while True:
            max_length = int(batch_size)
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]

            vars = []
            for var in vcf_lines.keys():
                if "type" in vcf_lines[var]:
                    if vcf_lines[var]["type"] == "p":
                        vars.append(var)

            #variants_without_alternate_alleles = adagenes.tools.filter_alternate_alleles(qids_partial)
            request_genome_version = self.genome_version

            #print(variants_without_alternate_alleles)
            variants_without_alternate_alleles = strip_long_indels(vars)

            variants = ','.join(variants_without_alternate_alleles)
            #print("vars ",variants)
            annotated_data = {}

            if variants != "":

                try:
                    json_body = req.get_connection(variants, uta_adapter_genetogenomic_src, self.genome_version)
                    for item in json_body:

                        if (item["data"] is not None) and not (isinstance(item["data"], str)):
                            for res in item["data"]:
                                if res != "Error":
                                    try:
                                        results_string = res['results_string']
                                        annotated_data = protein_to_genomic(annotated_data, results_string,
                                                                                          res,
                                                                                          self.srv_prefix,
                                                                                          genome_version=self.genome_version)

                                    except:
                                        print("Error retrieving genomic UTA response ", res)
                                        print(traceback.format_exc())
                        else:
                            qid = item["header"]["qid"]
                            gene, protein = qid.split(":")

                            if qid not in annotated_data:
                                annotated_data[qid] = {}

                            if "variant_data" not in annotated_data[qid]:
                                annotated_data[qid]["variant_data"] = {}
                            annotated_data[qid]["variant_data"]["gene"] = gene
                            annotated_data[qid]["variant_data"]["variant_exchange"] = protein
                            annotated_data[qid]["variant_data"]["type"] = "unidentified"
                            annotated_data[qid]["variant_data"]["status"] = "error"
                            annotated_data[qid]["variant_data"]["status_msg"] = item["data"]
                except:
                    print("error: genomic to gene")
                    print(traceback.format_exc())

                for i in range(0, max_length):
                    del qid_list[0]  # qid_list.remove(qid)
                if len(qid_list) == 0:
                    break
            else:
                return vcf_lines

        return annotated_data

def protein_to_genomic(annotated_data, results_string, res, module, genome_version="hg38"):
    """
    Converts data of a single biomarker including IDs on protein level into IDs on genomic level

    :param annotated_data:
    :param results_string:
    :return:
    """
    chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(
        results_string)
    qid = 'chr' + chr + ':' + pos + ref + '>' + alt

    if qid not in annotated_data:
        annotated_data[qid] = {}

    if "variant_data" not in annotated_data[qid]:
        annotated_data[qid]["variant_data"] = {}

    annotated_data[qid]["variant_data"]['CHROM'] = chr
    annotated_data[qid]["variant_data"]['reference_sequence'] = ref_seq
    annotated_data[qid]["variant_data"]['POS'] = pos
    annotated_data[qid]["variant_data"]['REF'] = ref
    annotated_data[qid]["variant_data"]['ALT'] = alt
    annotated_data[qid]["variant_data"]['POS_' + genome_version] = pos
    annotated_data[qid]["q_id"] = "chr" + chr + ":" + str(pos) + ref + ">" + alt
    annotated_data[qid]["variant_data"]['ID'] = ''
    annotated_data[qid]["variant_data"]['QUAL'] = ''
    annotated_data[qid]["variant_data"]['FILTER'] = ''

    if "refAmino" in res:
        annotated_data[qid]["variant_data"]['ref_aa'] = res["refAmino"]
        annotated_data[qid]["variant_data"]['alt_aa'] = res["varAmino"]

    if module is not None:
        annotated_data[qid][module] = res
    else:
        annotated_data[qid] = res

    # add previously known information on gene names and aa exchange
    if "hgnc_symbol" in res:
        annotated_data[qid]["variant_data"]["gene_name"] = res['hgnc_symbol']
        annotated_data[qid]["variant_data"]["amino_acid_exchange"] = res['aminoacid_exchange']

    annotated_data[qid][uta_adapter_genetogenomic_srv_prefix] = res
    annotated_data[qid]["level"] = "g"

    return annotated_data
