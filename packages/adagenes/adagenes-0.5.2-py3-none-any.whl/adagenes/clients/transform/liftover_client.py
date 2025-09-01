import traceback, os
from liftover import ChainFile
import adagenes.conf.read_config as conf_reader
import time
import adagenes


def liftover(bframe: adagenes.BiomarkerFrame,
             lo_hg19=None, lo_hg38=None, target_genome=None) -> adagenes.BiomarkerFrame:
    """
    Recognizes biomarker type according to the biomarker identifier

    :param bframe:
    :return:
    """
    client = LiftoverClient()
    return client.process_data(bframe,lo_hg19=lo_hg19, lo_hg38=lo_hg38, target_genome=target_genome)


class LiftoverClient:

    def __init__(self, genome_version=None,target_genome=None, error_logfile=None):
        self.genome_version = genome_version
        self.data_dir = conf_reader.__LIFTOVER_DATA_DIR__
        self.srv_prefix=["variant_data"]
        self.target_genome = target_genome
        self.extract_keys = []
        self.key_labels = []
        if genome_version is not None:
            self.extract_keys.append("POS_" + self.genome_version)
            self.key_labels.append( "POS_" + self.genome_version)
        if target_genome is not None:
            self.extract_keys.append("POS_" + self.target_genome)
            self.key_labels.append("POS_" + self.target_genome)

    def process_data(self, bframe, genome_version=None, lo_hg19=None, lo_hg38=None, lo_t2t=None, target_genome=None) \
            -> adagenes.BiomarkerFrame:
        """

        :param bframe:
        :param lo_hg19: hg19toHg38
        :param lo_hg38: hg38toHg19
        :param target_genome: Reference genome of genome positions (hg19/hg38/t2t)
        :return:
        """
        #print("liftover ",genome_version,": ",self.genome_version,": ",self.target_genome)

        if genome_version is None:
            genome_version = self.genome_version

        if target_genome is None:
            target_genome = self.target_genome

        #print("liftover ", genome_version, " to", target_genome)

        isbframe = False
        if isinstance(bframe, adagenes.BiomarkerFrame):
            variant_data = bframe.data
            self.genome_version = bframe.genome_version
            isbframe = True
        elif isinstance(bframe, dict):
            variant_data = bframe
            bframe_proc = adagenes.BiomarkerFrame(data=variant_data, genome_version=genome_version)
            variant_data = bframe_proc.data
        else:
            return bframe

        # Download liftover files if they cannot be found
        #adagenes.tools.check_liftover_files(conf_reader.__LIFTOVER_DATA_DIR__)

        if genome_version is not None:
            self.genome_version = genome_version
            if "POS_" + genome_version not in self.extract_keys:
                self.extract_keys.append("POS_" + self.genome_version)
                self.key_labels.append("POS_" + self.genome_version)

        if target_genome is not None:
            self.target_genome = target_genome
            if "POS_" + target_genome not in self.extract_keys:
                self.extract_keys.append("POS_" + self.target_genome)
                self.key_labels.append("POS_" + self.target_genome)

        vcf_lines_new = {}
        variant_count=0
        variants = {}

        pre_hg = self.genome_version
        #print("PRE HG ",pre_hg)

        if pre_hg is None:
            return bframe

        if target_genome is None:
            return bframe
        else:
            if target_genome=="hg19":
                convert_go = "hg19"
                #pre_hg = "hg38"
                #liftover_file = os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hg38ToHg19.over.chain.gz')
                if lo_hg38 is not None:
                    lo = lo_hg38
                else:
                    if pre_hg == "hg38":
                        lo = ChainFile(os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hg38ToHg19.over.chain.gz'), one_based=True)
                    elif pre_hg == "t2t":
                        lo = ChainFile(os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hs1ToHg19.over.chain.gz'), one_based=True)
            elif target_genome=="hg38":
                convert_go = "hg38"

                if lo_hg19 is not None:
                    lo = lo_hg19
                else:
                    if pre_hg == "hg19":
                        lo = ChainFile(os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hg19ToHg38.over.chain.gz'), one_based=True)
                    elif pre_hg == "t2t":
                        lo = ChainFile(os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hs1ToHg38.over.chain.gz'), one_based=True)
            elif target_genome == "t2t":
                convert_go = "t2t"
                if lo_t2t is not None:
                    lo = lo_t2t
                else:
                    if pre_hg == "hg38":
                        lo = ChainFile(os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hg38ToGCA_009914755.4.over.chain.gz'), one_based=True)
                    elif pre_hg == "hg19":
                        lo = ChainFile(os.path.join(conf_reader.__LIFTOVER_DATA_DIR__, 'hg19ToHs1.over.chain.gz'), one_based=True)

        pos_key = "POS_" + pre_hg

        variant_data_new = {}
        for var in variant_data.keys():

            if "type" in variant_data[var]:
                #print(variant_data[var])
                if variant_data[var]["type"] != "g":
                    variant_data_new[var] = variant_data[var]
                    continue

            if "variant_data" not in variant_data[var]:
                variant_data[var]["variant_data"] = {}

            if "CHROM" not in variant_data[var]["variant_data"]:
                chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(var)
                variant_data[var]["variant_data"]["CHROM"] = chr
                variant_data[var]["variant_data"]["POS"] = pos
                variant_data[var]["variant_data"]["POS_"+self.genome_version] = pos
                variant_data[var]["variant_data"]["REF"] = ref
                variant_data[var]["variant_data"]["ALT"] = alt

            chrom = 'chr' + str(variant_data[var]["variant_data"]["CHROM"])
            if pos_key in variant_data[var]["variant_data"]:
                pos = variant_data[var]["variant_data"][pos_key]
            else:
                variant_data[var]["variant_data"][pos_key] = variant_data[var]["variant_data"]["POS"]
                pos = variant_data[var]["variant_data"]["POS"]
            try:
                #print("liftover ", var,",",convert_go,",",self.genome_version,": ",variant_data[var])

                if "mutation_type" in variant_data[var]:
                    if variant_data[var]["mutation_type"] == "snv":
                        chrom, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(var)
                        #print("get liftover: ", chrom, ":", pos)
                        # loc = lo.convert_coordinate("chr"+str(chrom), int(pos))
                        chr_str = "chr"
                        if "chr" in chrom:
                            chr_str = ""
                        loc = lo[chr_str + str(chrom)][int(pos)]
                        #print("liftover position (", pre_hg, "to", target_genome, ")", chrom, ":", pos, " hg38: ", loc,": ",len(loc))
                        if len(loc) > 0:
                            pos_new = loc[0][1]
                            qid_new = "chr" + str(chrom) + ":" + str(pos_new) + ref + ">" + alt
                            variant_data_new[qid_new] = variant_data[var]

                            variant_data_new[qid_new]["variant_data"]["CHROM"] = "chr" + str(chrom)
                            variant_data_new[qid_new]["variant_data"]["POS"] = int(pos_new)
                            variant_data_new[qid_new]["variant_data"]["POS_" + convert_go] = int(loc[0][1])
                            variant_data_new[qid_new]["variant_data"]["POS_" + pre_hg] = int(pos)
                            variant_data_new[qid_new]["variant_data"]["strand"] = loc[0][2]
                        else:
                            print("Could not find liftover position ",var)
                    elif (variant_data[var]["mutation_type"] == "indel") \
                            or (variant_data[var]["mutation_type"] == "insertion") \
                            or (variant_data[var]["mutation_type"] == "deletion"):
                        chrom, mtype, pos, pos2, alt = adagenes.parse_indel(var)
                        #print("get liftover: ", chrom, ":", pos, ": ",pos2)
                        # loc = lo.convert_coordinate("chr"+str(chrom), int(pos))
                        chr_str = "chr"
                        if "chr" in chrom:
                            chr_str = ""
                        loc = lo[chr_str + str(chrom)][int(pos)]
                        #print("liftover position (", pre_hg, "to", target_genome, ")", chrom, ":", pos, " hg38: ", loc)
                        if len(loc) > 0:
                            pos_new = loc[0][1]
                            qid_new = "chr" + str(chrom) + ":" + str(pos_new) + mtype + alt
                            variant_data_new[qid_new] = variant_data[var]

                            variant_data_new[qid_new]["variant_data"]["CHROM"] = "chr" + str(chrom)
                            variant_data_new[qid_new]["variant_data"]["POS"] = int(pos_new)
                            variant_data_new[qid_new]["variant_data"]["POS_" + convert_go] = int(loc[0][1])
                            variant_data_new[qid_new]["variant_data"]["POS_" + pre_hg] = int(pos)
                            variant_data_new[qid_new]["variant_data"]["strand"] = loc[0][2]
                        else:
                            print("Could not find liftover position for InDel ",var)
                    elif variant_data[var]["mutation_type"] == "fusion":
                        chr0, pos0, chr1, pos1 = adagenes.parse_fusion(var)
                        continue

            except:
                print("Liftover error: Could not retrieve liftover position of ",var,": ",traceback.format_exc())

        if isbframe:
            bframe.data = variant_data_new
            bframe.genome_version = convert_go
            return bframe
        else:
            return variant_data_new

