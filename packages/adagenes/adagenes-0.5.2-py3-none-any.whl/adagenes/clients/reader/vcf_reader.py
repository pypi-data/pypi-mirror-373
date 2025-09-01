import copy
import re, os, gzip
import traceback
import adagenes.clients.reader as reader
import adagenes.conf.read_config as config
from adagenes.tools import parse_vcf
from adagenes.processing.json_biomarker import BiomarkerFrame
import adagenes.conf.vcf_config
from adagenes.tools.json_mgt import generate_variant_data
import adagenes as ag


class VCFReader(reader.Reader):
    """
    Reader for Variant Call Format (VCF)
    """

    def read_file(self, infile, genome_version=None, columns=None,sep="\t",
                  mapping=None, remove_quotes=True,
                  start_row=None, end_row=None
                  ) -> BiomarkerFrame:
        """
        Reads in a VCF file and returns a biomarker frame

        :param infile:
        :param genome_version:
        :param columns:
        :param start_row:
        :param end_row:
        :return:
        """
        #print("load rows ",start_row,"-",end_row)
        if isinstance(infile, str):
            file_name, file_extension = os.path.splitext(infile)
            input_format_recognized = file_extension.lstrip(".")
            print("input format recognized: ",input_format_recognized)
            if input_format_recognized == "gz":
                infile = gzip.open(infile, 'rt')
            else:
                infile = open(infile, 'r')

        json_obj = BiomarkerFrame(src_format='vcf')
        json_obj.header_lines = []
        json_obj.data = {}
        json_obj.info_lines = {}
        json_obj.genome_version = genome_version
        variant_count = 0
        line_count = 0
        json_obj.variants = {}
        line_num_abs = 0
        line_num_all = 0

        for line_num, line in enumerate(infile):
            line_num_abs += 1
            line_num_all += 1
            #print(line_num_abs)

            try:
                if line.startswith('##'):
                    json_obj.header_lines.append(line.strip())
                    if genome_version is None:
                        json_obj.genome_version = self.read_genomeversion(line)
                    line_num_abs = line_num_abs - 1
                    continue
                elif line.startswith('#CHROM'):
                    json_obj.header_lines.append(line.strip())
                    features = line.split("\t")
                    for feature in features:
                        json_obj.orig_features.append(feature)
                    # if genome version is not set yet, use hg38 as default
                    if genome_version is None:
                        json_obj.genome_version = 'hg38'

                    json_obj.info_lines, json_obj.genome_version = parse_vcf.process_vcf_headers(json_obj.header_lines,
                                                                               genome_version)
                    line_num_abs =  line_num_abs - 1
                    continue
                else:
                    variant_count += 1
                    line_count += 1

                if (start_row is not None) and (end_row is not None):
                    #print(line_num, ": ", line_num_abs, ": ", line.strip())
                    if line_num_abs <= start_row:
                        #print("skip ",line.strip())
                        continue
                    elif line_num_abs > end_row:
                        continue

                fields = line.strip().split('\t')
                chromosome, pos, ref_base, alt_base = fields[0], fields[1], fields[3], fields[4]
                info = fields[7]
                chr_prefix = ""
                if not chromosome.startswith("chr"):
                    chr_prefix = "chr"

                # CNVs
                #if alt_base == "<DEL>" or alt_base == "<DUP>":
                #    info_features = info.split(";")
                #    for feature in info_features:
                #        elements = feature.split("=")
                #        if len(elements) > 1:
                #            key = elements[0]
                #            if key == "END":
                #                pos2 = elements[1]
                #                alt_base = pos2 + alt_base

                # TODO inversions, translocations

                variant = chr_prefix + '{}:{}{}>{}'.format(chromosome, pos, ref_base, alt_base)

                if alt_base == "<DEL>" or alt_base == "<DUP>" or alt_base =="<CNV>":
                    endfound=False
                    alt_base = alt_base.replace("<","")
                    alt_base = alt_base.replace(">", "")
                    for info_feature in info.split(";"):
                        elements = info_feature.split("=")
                        if len(elements) > 1:
                            key = elements[0]
                            if key == "END":
                                pos2 = elements[1]
                                endfound = True
                            #elif key == "SVTYPE":
                    if endfound is True:
                        variant = chr_prefix + chromosome + ":" + pos + "-" + pos2 + "_" + alt_base

                chromosome = chromosome.replace("chr", "")
                if alt_base != '.':
                    json_obj.variants[variant_count] = variant

                #if variant in json_obj.data.keys():
                #    print("Variant alreaday there",variant )
                json_obj = generate_variant_data(json_obj, variant, chromosome, pos, fields, ref_base, alt_base, genome_version=genome_version)
                #print(line_count," ",len(list(json_obj.data.keys())), " ",variant)
                json_obj.info_lines = info.strip()
            except:
                print("VCF reader: Error parsing line ",line)
                print(traceback.format_exc())
        infile.close()

        json_obj.data_type="g"
        json_obj.type_recognition(json_obj.data)
        json_obj.max_variants = line_num_abs
        #print("lines ",line_count, ", variants ",len(list(json_obj.data.keys())))
        return json_obj

    def read_file_chunk(self, infile, json_obj: BiomarkerFrame, chunk_size=5000) -> BiomarkerFrame:
        """
        Reads a defined number of lines from a file object, adds them to the given biomarker set and returns the extended biomarker list

        :param infile:
        :type infile:
        :param json_obj:
        :type json_obj: BiomarkerSet
        :return: json_obj
        """

        json_obj.variant_count = 0
        json_obj.line_count = 0
        json_obj.data = {}
        json_obj.info_lines = {}
        json_obj.header_lines = []
        json_obj.c = 0

        for i,line in enumerate(infile):
            if i > chunk_size:
                break

            if line.startswith('##'):
                #if json_obj.output_format == 'vcf':
                #    print(line.strip(), file=json_obj.outfile)
                json_obj.header_lines.append(line.strip())
                if json_obj.genome_version is None:
                    json_obj.genome_version = self.read_genomeversion(line)
                continue
            elif line.startswith('#CHROM'):
                json_obj.header_lines.append(line.strip())
                # if genome version is not set yet, use hg38 as default
                if json_obj.genome_version is None:
                    json_obj.genome_version = 'hg38'

                json_obj.info_lines, json_obj.genome_version = parse_vcf.process_vcf_headers(json_obj.header_lines, json_obj.genome_version, json_obj.info_lines)
                continue
            else:
                json_obj.variant_count += 1
                json_obj.line_count += 1

            fields = line.strip().split('\t')
            chromosome, pos, ref_base, alt_base = fields[0], fields[1], fields[3], fields[4]
            info = fields[7]
            chr_prefix = ""
            if not chromosome.startswith("chr"):
                chr_prefix = "chr"
            variant = chr_prefix + '{}:{}{}>{}'.format(chromosome, pos, ref_base, alt_base)
            chromosome = chromosome.replace("chr", "")
            if alt_base != '.':
                json_obj.variants[json_obj.variant_count] = variant
            json_obj.data[variant] = {}
            json_obj.data[variant][config.variant_data_key] = {
                                  "CHROM": chromosome,
                                  "POS": pos,
                                  "ID": fields[2],
                                  "REF": ref_base,
                                  "ALT": alt_base,
                                  "QUAL": fields[5],
                                  "FILTER": fields[6],
                                  "INFO": fields[7],
                                  "OPTIONAL": fields[8:]
                                  }
            #json_obj.info_lines[variant] = info.strip()

        return json_obj

    def read_genomeversion(self, line):
        if not line.startswith('##reference'):
            return None
        p = re.compile('(##reference=).*GRCh([0-9]+).*')
        m = p.match(line)

        if m and len(m.groups()) > 1:
            genome_version = 'hg' + m.group(2)
            if genome_version == 'hg37':
                genome_version = 'hg19'
            return genome_version

        p = re.compile('(##reference=).*(hg[0-9]+).*')
        m = p.match(line)
        if m and len(m.groups()) > 1:
            return m.group(2)
        return None

    def read_line(self, line, vcf_lines, outfile, header_lines, magic_obj, genome_version, line_count, variant_count,
                  variants, info_lines, is_header_line=False, sep=',', linecount="", columns=[], mapping=None):
        #print("line ",line)
        is_header_line = False
        if line.startswith('##'):
            #print(line.strip(), file=outfile)
            header_lines.append(line.strip())
            if genome_version is None:
                genome_version = self.read_genomeversion(line)
            is_header_line = True
        elif line.startswith('#CHROM'):
            if hasattr(magic_obj, "info_lines"):
                header_lines += magic_obj.info_lines

            header_lines.append(line.strip())
            # if genome version has not set yet, use hg38 as default
            if genome_version is None:
                genome_version = 'hg38'

                lines, genome_version = parse_vcf.process_vcf_headers(header_lines, genome_version)
                # magic_obj.genome_version = "hg38"
                for hline in lines:
                    print(hline, file=outfile)
                is_header_line = True
            else:
                variant_count += 1
                line_count += 1

        if is_header_line is False:
            fields = line.strip().split('\t')

            if len(fields) >= 7:
                chromosome, pos, ref_base, alt_base = fields[0], fields[1], fields[3], fields[4]
                info = fields[7]
                chr_prefix = ""
                if not chromosome.startswith("chr"):
                    chr_prefix = "chr"
                variant = chr_prefix + '{}:{}{}>{}'.format(chromosome, pos, ref_base, alt_base)
                if alt_base != '.':
                    variants[variant_count] = variant
                # print(line)
                vcf_lines[variant] = {"CHROM": chromosome,
                                      "POS": pos,
                                      "ID": fields[2],
                                      "REF": ref_base,
                                      "ALT": alt_base,
                                      "QUAL": fields[5],
                                      "FILTER": fields[6],
                                      "INFO": fields[7],
                                      "OPTIONAL": fields[8:]
                                      }  # line.strip()
                # TODO: add optional columns
                info_lines[variant] = info.strip()
                json_obj = {variant: copy.deepcopy(vcf_lines[variant])}
                json_obj = ag.generate_variant_data(json_obj, variant, chromosome, pos, fields, ref_base, alt_base,
                                                     genome_version=genome_version)
                json_obj = ag.TypeRecognitionClient(genome_version=genome_version).process_data(json_obj)
                variant_new = list(json_obj.keys())[0]
                vcf_lines.pop(variant)
                vcf_lines[variant_new] = json_obj[variant_new]
                #print("read line ",vcf_lines[variant_new])
        #print(vcf_lines)
        return vcf_lines, header_lines, variant_count, line_count,is_header_line, info_lines, variants, []
