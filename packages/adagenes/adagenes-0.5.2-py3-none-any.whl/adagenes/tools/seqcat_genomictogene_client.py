import traceback, copy
import adagenes.tools.module_requests as req
import adagenes.tools.parse_genomic_data

batch_size=100
uta_adapter_src = "https"+ "://" + "mtb.bioinf.med.uni-goettingen.de" + "/CCS/v1/GenomicToGene/{}/"
uta_genomic_keys = ['gene_name', 'variant_exchange', 'input_data']
uta_gene_keys = ['results_string']
uta_gene_response_keys = ['chr', 'start', 'ref', 'var', 'input_data']
#uta_adapter_genetogenomic_src = __MODULE_PROTOCOL__ + "://" + __MODULE_SERVER__ + __PORT_UTAADAPTER__ + "/CCS/v1/GeneToGenomic/{}/"
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

class SeqCATGenomicClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.info_lines= uta_adapter_info_lines
        self.url_pattern = uta_adapter_src
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
        if (self.genome_version == "hg19") or (self.genome_version=="GRCh37"):
            check_for_hg38 = True
            request_genome="hg38"
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

            variants_without_alternate_alleles = adagenes.tools.filter_alternate_alleles(qids_partial)
            request_genome_version = self.genome_version

            variants_without_alternate_alleles = strip_long_indels(variants_without_alternate_alleles)

            variants = ','.join(variants_without_alternate_alleles)

            try:
                json_body = req.get_connection(variants, self.url_pattern, request_genome_version)
    
                for item in json_body:
                            qid = str(item["header"]["qid"])
                            if qid not in vcf_lines.keys():
                                qid = qid.replace("g.","")
                                qid = qid.replace("p.","")
                                qid = qid.replace("c.","")
    
                            if item["data"] is not None:
                                # add variant data
                                if "variant_data" not in vcf_lines[qid]:
                                    vcf_lines[qid]["variant_data"] = {}
    
                                if type(item["data"]) is dict:
    
                                    if "gene name" in item["data"]:
                                        vcf_lines[qid]["variant_data"]['Gene name'] = item["data"]["gene_name"]
                                        vcf_lines[qid]["variant_data"]['Variant exchange'] = item["data"]["variant_exchange"]
                                        vcf_lines[qid]["variant_data"]['Biomarker'] = item["data"]["gene_name"] + " " + item["data"][
                                            "variant_exchange"]
    
                                    chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(
                                        qid)
                                    vcf_lines[qid]["variant_data"]['CHROM'] = chr
                                    vcf_lines[qid]["variant_data"]['reference_sequence'] = ref_seq
                                    vcf_lines[qid]["variant_data"]['POS'] = pos
                                    vcf_lines[qid]["variant_data"]['REF'] = ref
                                    vcf_lines[qid]["variant_data"]['ALT'] = alt
                                    vcf_lines[qid]["variant_data"]['POS_' + self.genome_version] = pos
                                    vcf_lines[qid]["variant_data"]['ID'] = ''
                                    vcf_lines[qid]["variant_data"]['QUAL'] = ''
                                    vcf_lines[qid]["variant_data"]['FILTER'] = ''
    
                                    vcf_lines[qid][self.srv_prefix] = item["data"]
                                else:
                                    vcf_lines[qid][self.srv_prefix] = {}
                                    vcf_lines[qid][self.srv_prefix]["status"] = 400
                                    vcf_lines[qid][self.srv_prefix]["msg"] = item["data"]

                                # Generate existing variant data
            except:
                print("error: genomic to gene")
                print(traceback.format_exc())

            for i in range(0, max_length):
                del qid_list[0] #qid_list.remove(qid)
            if len(qid_list) == 0:
                break

        return vcf_lines
