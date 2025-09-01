import copy
import traceback
import adagenes.conf.read_config as conf_reader
import time
from liftover import ChainFile
import adagenes


class LiftoverAnnotationClient:

    def __init__(self, genome_version=None, target_genome= None, error_logfile=None):
        self.srv_prefix = ["variant_data"]
        self.genome_version = genome_version
        self.data_dir = conf_reader.__LIFTOVER_DATA_DIR__
        self.target_genome = target_genome
        self.extract_keys = []
        self.key_labels = []
        self.info_lines = ['##INFO=<ID=POS_hg19,Number=1,Type=Integer,Description="Variant position in hg19(GRCh37)">',
                           '##INFO=<ID=POS_hg38,Number=1,Type=Integer,Description="Variant position in hg38(GRCh38)">',
                           '##INFO=<ID=POS_t2t,Number=1,Type=Integer,Description="Variant position in T2T-CHM13">'
                           ]
        if genome_version is not None:
            self.extract_keys.append("POS_" + self.genome_version)
            self.key_labels.append("POS_" + self.genome_version)
        if target_genome is not None:
            self.extract_keys.append("POS_" + self.target_genome)
            self.key_labels.append("POS_" + self.target_genome)

    def process_data(self, bframe, lo_hg19=None, lo_hg38=None, lo_t2t=None, genome_version = None, target_genome=None) \
            -> adagenes.BiomarkerFrame:
        """

        :param bframe:
        :param lo_hg19:
        :param lo_hg38:
        :param lo_t2t:
        :param target_genome:
        :return:
        """


        start_time = time.time()
        #adagenes.conf.check_liftover_files(conf_reader.__LIFTOVER_DATA_DIR__)
        if genome_version is None:
            genome_version = self.genome_version

        if target_genome is None:
            target_genome = self.target_genome

        #print("LO annotation ", genome_version, " target ", target_genome)

        isbframe = False
        if isinstance(bframe, adagenes.BiomarkerFrame):
            variant_data = bframe.data
            self.genome_version = bframe.genome_version
            isbframe = True
        elif isinstance(bframe, dict):
            variant_data = bframe
            bframe = adagenes.BiomarkerFrame(data=variant_data)
            variant_data = bframe.data
        else:
            return bframe

        #if isinstance(bframe, adagenes.BiomarkerFrame):
        #    variant_data = bframe.data
        #    isbframe = True
        #else:
        #    variant_data = bframe

        # Download liftover files if they cannot be found
        #adagenes.tools.check_liftover_files(conf_reader.__LIFTOVER_DATA_DIR__)

        vcf_lines_new = {}
        variant_count=0
        variants = {}

        #print("liftover annotation: ",genome_version," target ",target_genome)
        # print("liftover ", genome_version, " to", target_genome)
        lo=None

        if target_genome is None:
            if genome_version == "hg19":
                convert_go = "hg38"
                if lo_hg19 is None:
                    #print("load from liftover file (hg19)")
                    lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHg38.over.chain.gz", one_based=True)
                    #lo = LiftOver(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHg38.over.chain.gz")
                else:
                    lo = lo_hg19
            elif genome_version == "t2t":
                convert_go = "hg38"
                if lo_t2t is None:
                    lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hs1ToHg38.over.chain.gz",
                                          one_based=True)
                    #lo = LiftOver(conf_reader.__LIFTOVER_DATA_DIR__ + "/hs1ToHg38.over.chain.gz")
            else:
                convert_go = "hg19"
                liftover_file = conf_reader.__LIFTOVER_DATA_DIR__ + "/hg38ToHg19.over.chain.gz"
                #print(liftover_file)
                if lo_hg38 is None:
                    #print("load liftover from file (hg38)")

                    #adagenes.tools.liftover.check_liftover_files(conf_reader.__LIFTOVER_DATA_DIR__)
                    lo = ChainFile(liftover_file,
                                   one_based=True)
                    #lo = LiftOver(liftover_file)
                else:
                    lo = lo_hg38
        else:
            if target_genome == "hg19":
                convert_go = "hg19"

                if genome_version == "hg38":
                    liftover_file = conf_reader.__LIFTOVER_DATA_DIR__ + "/hg38ToHg19.over.chain.gz"
                elif genome_version == "t2t":
                    #liftover_file =
                    pass

                lo = ChainFile(liftover_file,
                               one_based=True)
                #lo = LiftOver(liftover_file)
            elif target_genome == "hg38":
                convert_go = "hg38"

                if genome_version == "hg19":
                    lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHg38.over.chain.gz",
                                   one_based=True)
                    #lo = LiftOver(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHg38.over.chain.gz")
                elif genome_version == "t2t":
                    lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hs1ToHg38.over.chain.gz",
                                   one_based=True)
                    #lo = LiftOver(conf_reader.__LIFTOVER_DATA_DIR__ + "/hs1ToHg38.over.chain.gz")
            elif target_genome == "t2t":
                convert_go = "t2t"
                if genome_version == "hg38":
                    #print("HG38 to T2T")
                    lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg38ToGCA_009914755.4.over.chain.gz",
                                   one_based=True)
                elif genome_version == "hg19":
                    lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHs1.over.chain.gz", one_based=True)
                    #lo = LiftOver(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg38ToGCA_009914755.4.over.chain.gz")
                #elif self.genome_version == "hg19"
                #

        pos_key = "POS_" + genome_version
        if lo is None:
            #print("LO NONE RETURN")
            return variant_data

        in_var_data = True
        for var in variant_data.keys():
            #print(variant_data[var])

            if "variant_data" not in variant_data[var]:
                variant_data[var]["variant_data"] = {}

            chrom=None
            if "CHROM" in variant_data[var]["variant_data"]:
                chrom = str(variant_data[var]["variant_data"]["CHROM"])
            elif "chrom" in variant_data[var]:
                chrom = str(variant_data[var]["chrom"])
                in_var_data = False

            if "POS" in variant_data[var]["variant_data"]:
                pos = variant_data[var]["variant_data"]["POS"]
                variant_data[var]["variant_data"]["POS_" + genome_version] = pos
            elif "pos" in variant_data[var]:
                pos = variant_data[var]["pos"]
                variant_data[var]["POS_" + genome_version] = pos
                variant_data[var]["variant_data"]["POS_" + genome_version] = pos
            else:
                #print("parse pos ",var)
                chr, ref_seq, pos, ref, alt = adagenes.tools.parse_genomic_data.parse_genome_position(var)
                if chr is not None and pos is not None:
                    if in_var_data is True:
                        variant_data[var]["variant_data"]["CHROM"] = chr
                        variant_data[var]["variant_data"]["POS"] = pos
                        variant_data[var]["variant_data"]["POS_"+genome_version] = pos
                    else:
                        variant_data[var]["CHROM"] = chr
                        variant_data[var]["POS"] = pos
                        variant_data[var]["POS_" + genome_version] = pos
                        variant_data[var]["variant_data"]["CHROM"] = chr
                        variant_data[var]["variant_data"]["POS"] = pos
                        variant_data[var]["variant_data"]["POS_" + genome_version] = pos
                    chrom = chr
                    #variant_data[var]["variant_data"]["REF"] = ref
                    #variant_data[var]["variant_data"]["ALT"] = alt
                else:
                    chrom, mtype, pos, pos2, alt = adagenes.tools.parse_genomic_data.parse_indel(var)
                    if in_var_data is True:
                        variant_data[var]["variant_data"]["CHROM"] = chr
                        variant_data[var]["variant_data"]["POS"] = pos
                        variant_data[var]["variant_data"]["POS2_"+genome_version] = pos2
                    else:
                        variant_data[var]["CHROM"] = chr
                        variant_data[var]["POS"] = pos
                        variant_data[var]["POS2_" + genome_version] = pos2
                        variant_data[var]["variant_data"]["CHROM"] = chr
                        variant_data[var]["variant_data"]["POS"] = pos
                        variant_data[var]["variant_data"]["POS2_" + genome_version] = pos2

            #print("LO transform ",chrom,": ",pos)

            if chrom is None:
                #print("chrom is none ",var)
                continue

            if 'chr' not in chrom:
                chrom = 'chr' + chrom
            if pos is not None:
                try:
                    loc = lo[chrom][int(pos)]
                    if len(loc)>0:
                        if in_var_data is True:
                            variant_data[var]["variant_data"]["POS_"+convert_go] = loc[0][1]
                            variant_data[var]["variant_data"]["strand"] = loc[0][2]
                        else:
                            variant_data[var]["POS_" + convert_go] = loc[0][1]
                            variant_data[var]["strand"] = loc[0][2]
                            variant_data[var]["variant_data"]["POS_" + convert_go] = loc[0][1]
                            variant_data[var]["variant_data"]["strand"] = loc[0][2]
                except:
                    print("Liftover error: Could not retrieve liftover position of ",var,": pos ",pos,": ",traceback.format_exc())
            elif "POS" in variant_data[var]["variant_data"]:
                pos = variant_data[var]["variant_data"]["POS"]
                if "POS_" + genome_version not in variant_data[var]["variant_data"].keys():
                    variant_data[var]["variant_data"]["POS_" + genome_version] = pos
                try:
                    loc = lo[chrom][int(pos)]
                    if len(loc)>0:
                        variant_data[var]["variant_data"]["POS_"+convert_go] = loc[0][1]
                        variant_data[var]["variant_data"]["strand"] = loc[0][2]
                except:
                    print("Liftover error: Could not retrieve liftover position of ",var,": ",traceback.format_exc())

            if "POS2" in variant_data[var]["variant_data"]:
                if variant_data[var]["variant_data"]["POS2"] is not None:
                    pos = variant_data[var]["variant_data"]["POS2"]
                    try:
                        loc = lo[chrom][int(pos)]
                        if len(loc) > 0:
                            variant_data[var]["variant_data"]["POS2_" + convert_go] = loc[0][1]
                            variant_data[var]["variant_data"]["strand"] = loc[0][2]
                    except:
                        print("Liftover error: Could not retrieve liftover position of ", var, ": ", traceback.format_exc())
                        print(variant_data[var]["variant_data"])

        stop_time = time.time() - start_time
        #print("Liftover request: (", genome_version," to " , convert_go,")",stop_time)
        #print(variant_data)

        if isbframe is True:
            bframe.data = variant_data
            return bframe
        else:
            #bframe = adagenes.BiomarkerFrame(data=variant_data, genome_version=genome_version)
            # variant_data = bframe_proc.data
            #return bframe.data
            #print("LO annotation ",variant_data)
            return variant_data

