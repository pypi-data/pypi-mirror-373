import re, gzip
import adagenes.clients.reader as reader
import adagenes.conf.read_config as config
from adagenes.tools import parse_vcf
import adagenes
import adagenes.conf.vcf_config


class GTFReader(reader.Reader):
    """
    Reader for reading data in General Transfer Format (GTF)
    """

    def generate_variant_data(self,json_obj, qid, seqname, source, feature, start, end, score, strand, frame, attributes_dc):

        json_obj[qid] = {}
        json_obj[qid]["features"] = {}
        json_obj[qid]["features"]["seqname"] = seqname
        json_obj[qid]["features"]["source"] = source
        json_obj[qid]["features"]["feature"] = feature
        json_obj[qid]["features"]["start"] = start
        json_obj[qid]["features"]["end"] = end
        json_obj[qid]["features"]["score"] = score
        json_obj[qid]["features"]["strand"] = strand
        json_obj[qid]["features"]["frame"] = frame
        json_obj[qid]["attributes"] = attributes_dc

        return json_obj

    def process_gtf_headers(self, lines):
        return lines

    def read_file(self, infile, file_reader=None, genome_version=None,
                  columns=None,start_row=None, end_row=None):
        """

        :param infile:
        :param file_reader:
        :param genome_version:
        :param columns:
        :param start_row:
        :param end_row:
        :return:
        """

        if type(infile) is str:
            file_extension = adagenes.tools.get_file_type(infile)
            print(file_extension)
            if file_reader is not None:
                if file_reader == 'gtf':
                    infile = open(infile, 'r')
                else:
                    infile = open(infile, 'r')
            else:
                if file_extension == 'gz':
                    infile = gzip.open(infile, 'rt')
                else:
                    infile = open(infile, 'r')

        json_obj = adagenes.BiomarkerFrame()
        json_obj.header_lines = []
        json_obj.data = {}
        json_obj.info_lines = {}
        json_obj.genome_version = genome_version
        variant_count = 0
        line_count = 0
        json_obj.variants = {}

        for line in infile:
            if line.startswith('##'):
                json_obj.header_lines.append(line.strip())
                continue

                json_obj.info_lines, json_obj.genome_version = self.process_gtf_headers(json_obj.header_lines)
                continue
            else:
                variant_count += 1
                line_count += 1

            fields = line.strip().split('\t')
            #print(fields)
            seqname, source, feature, start, end, score, strand, frame, attribute = \
                fields[0], fields[1], fields[2], fields[3], fields[4], fields[5], fields[6], fields[7], fields[8]
            qid = fields[0] + ":" + fields[3] + "-" + fields[4] + "_" + fields[1] + "_" + fields[2]
            attributes = attribute.split("; ")
            attributes_dc = {}
            for a in attributes:
                key, value = a.split(" ")
                value = value[1:-1]
                attributes_dc[key] = value

            json_obj.data = self.generate_variant_data(json_obj.data, qid, seqname, source, feature, start, end, score, strand, frame,attributes_dc)
        infile.close()

        return json_obj

    def read_file_chunk(self, infile, json_obj):
        """
        Processes VCF data line by line with a given batch size. Returns a JSON object of the loaded biomarker data

        :param infile:
        :param json_obj:
        :return:
        """

        json_obj.variant_count = 0
        json_obj.line_count = 0
        json_obj.data = {}
        json_obj.info_lines = {}
        json_obj.header_lines = []
        json_obj.c = 0

        for line in json_obj.infile:
            if line.startswith('##'):
                #if json_obj.output_format == 'vcf':
                #    print(line.strip(), file=json_obj.outfile)
                json_obj.header_lines.append(line.strip())
                if json_obj.genome_version is None:
                    json_obj.genome_version = json_obj.read_genomeversion(line)
                continue
            elif line.startswith('#CHROM'):
                json_obj.header_lines.append(line.strip())
                # if genome version is not set yet, use hg38 as default
                if json_obj.genome_version is None:
                    json_obj.genome_version = 'hg38'

                json_obj.info_lines, json_obj.genome_version = parse_vcf.process_vcf_headers(json_obj.header_lines, json_obj.genome_version, json_obj.generic_obj.info_lines)
                json_obj.generic_obj.genome_version = json_obj.genome_version
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
            json_obj.info_lines[variant] = info.strip()

            # query the service either after 100 ("variant_batch_size") variants
            # or 5000 ("line_batch_size") lines are collected
            #if (len(json_obj.variants) >= json_obj.variant_batch_size) or (len(json_obj.data) >= json_obj.line_batch_size):
            #    json_obj._write_chunk_to_file()

        return json_obj

