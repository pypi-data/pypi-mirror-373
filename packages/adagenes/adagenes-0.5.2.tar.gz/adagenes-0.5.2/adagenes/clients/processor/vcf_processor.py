import re, gzip, os
import requests, datetime, json
import adagenes.tools.parse_vcf as parse_vcf
import adagenes as ag
from adagenes.tools.json_mgt import generate_variant_data


class VCFProcessor:

    def get_connection(self,variants, url_pattern, genome_version):
        url = url_pattern.format(genome_version) + variants
        print(url)
        r = requests.get(url)
        return r.json()


    def query_service(self,vcf_lines, variant_dc, outfile, extract_keys, srv_prefix, url_pattern, genome_version, qid_key="q_id", error_logfile=None):
        variants = ','.join(variant_dc.values())

        try:
            json_body = self.get_connection(variants, url_pattern, genome_version)

            # for i, l in enumerate(variant_dc.keys()):
            for i, l in enumerate(json_body):
                if json_body[i]:
                    annotations = []

                    if qid_key not in json_body[i]:
                        continue
                    qid = json_body[i][qid_key]

                    for k in extract_keys:
                        if k in json_body[i]:
                            annotations.append('{}-{}={}'.format(srv_prefix, k, json_body[i][k]))

                    try:
                        splits = vcf_lines[qid].split("\t")
                        splits[7] = splits[7] + ";" + ';'.join(annotations)
                        vcf_lines[qid] = "\t".join(splits)
                    except:
                    # print("error in query response ",qid,'  ,',variant_dc)
                        if error_logfile is not None:
                            cur_dt = datetime.datetime.now()
                            date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                            print(cur_dt, ": error processing variant response: ", qid, file=error_logfile)

        except:
            # print("error in whole service query ",variant_dc)
            if error_logfile is not None:
                print("error processing request: ", variants, file=error_logfile)

        for line in vcf_lines:
            print(vcf_lines[line], file=outfile)


    def read_genomeversion(self,line):
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

    def process_file(self,
                     infile,
                     outfile,
                     magic_obj,
                     reader=None,
                     writer=None,
                     input_format=None,
                     output_format=None,
                     variant_batch_size=100,
                     line_batch_size=5000,
                     genome_version=None,
                     error_logfile=None,
                     output_type='file',
                     filter=None,
                     mapping=None,
                     labels=None,
                     ranked_labels=None,
                     read_mapping=None,
                     client_mapping=None):
        """

        :param infile:
        :param outfile:
        :param magic_obj:
        :param input_format:
        :param output_format:
        :param variant_batch_size:
        :param line_batch_size:
        :param genome_version:
        :param error_logfile:
        :param output_type:
        :param filter:
        :return:
        """
        generate_mapping=False

        infile_str = False
        outfile_str = False
        if isinstance(infile, str):
            if input_format is None:
                input_format = ag.get_file_type(infile)

            if ag.tools.data_io.is_gzip(infile):
                infile = gzip.open(infile, "rb")
            else:
                infile = open(infile, "r")

            infile_str = True
        if isinstance(outfile, str):
            if output_format is None:
                output_format = ag.get_file_type(outfile)
            outfile = open(outfile, "w")
            outfile_str = True

        if input_format == 'csv':
            reader = ag.CSVReader(mapping=read_mapping)
        else:
            reader = ag.VCFReader()

        if writer is None:
            if output_format == 'csv':
                writer = ag.CSVWriter()
                if mapping is None:
                    generate_mapping = True
                    print("generate mapping")
            else:
                writer = ag.VCFWriter()
        else:
            print("writer not none")
        print("start processing ",reader, ": ",writer, " client ",magic_obj)



        variants_written=False

        variants = {}
        #if input_format == 'vcf':
        variant_count = 0
        line_count = 0
        vcf_lines = {}
        info_lines = {}
        first_chunk = True
        last_chunk=False
        line_count_abs = 0

        header_lines = []
        c=0
        columns = []
        csv_columns = []

        if writer is not None:
            writer.pre_process(outfile,ranked_labels=ranked_labels)

        first_chunk=True
        for line in infile:
            line_count_abs += 1
            if line_count_abs == 1:
                is_header_line=True
            else:
                is_header_line=False

            vcf_lines, header_lines, variant_count, line_count, is_header_line, info_lines, variants,columns = \
                reader.read_line(line, vcf_lines, outfile, header_lines, magic_obj, genome_version, line_count,
                                 variant_count, variants, info_lines, is_header_line=is_header_line,
                                 linecount=line_count_abs,columns=columns, mapping=client_mapping)


            #print(vcf_lines)

            # query the service either after 100 ("variant_batch_size") variants
            # or 5000 ("line_batch_size") lines are collected
            #if (len(variants) >= variant_batch_size) or (len(vcf_lines) >= line_batch_size):
            if (len(vcf_lines) >= variant_batch_size) or (len(vcf_lines) >= line_batch_size):
                if output_format == 'json' and variants_written:
                    print(',', file=outfile, end='')


                # Process
                if magic_obj is not None:
                    vcf_lines = magic_obj.process_data(vcf_lines)
                    #print("Annotated: ",vcf_lines)


                # Writer
                if output_type == 'file':

                    if generate_mapping is True:
                        ranked_labels = []
                        mapping = {}
                        for var in vcf_lines.keys():
                            for feature in vcf_lines[var].keys():
                                if (feature != "variant_data") and (feature != "info_features") and (isinstance(vcf_lines[var][feature], str)) and (
                                        feature not in ranked_labels):
                                    mapping[feature] = ""
                                    ranked_labels.append(feature)
                            if "info_features" in vcf_lines[var].keys():
                                if "info_features" not in mapping.keys():
                                    mapping["info_features"] = []
                                for feature in vcf_lines[var]["info_features"].keys():
                                    mapping["info_features"].append(feature)
                        generate_mapping = False
                        if first_chunk is True:
                            csv_columns = writer.generate_columns(outfile, mapping)

                    c = 1
                    for var in vcf_lines.keys():
                            if writer is not None:
                                #print("WRITE")
                                writer.write_line_to_file(outfile, var, vcf_lines, magic_obj,
                                                            save_headers=False, variants_written=False,
                                                           mapping=mapping,
                                                           ranked_labels=ranked_labels,
                                                           labels=labels,
                                                          first_chunk=first_chunk,
                                                          columns=csv_columns
                                                          )
                                first_chunk = False
                            elif output_format == 'json':
                                #print(vcf_lines)
                                #print(json.dumps(vcf_lines), file=outfile)
                                json_str = json.dumps(vcf_lines[var])
                                #json_str = json_str.lstrip('{').rstrip('}')
                                json_str = "\"" + var + "\"" + ":" + json_str
                                if c < len(vcf_lines):
                                    json_str = json_str + ','
                                #else:
                                #    json_str = json_str + '}'

                                c += 1

                                print(json_str, file=outfile)

                    #if output_format == 'vcf':
                    variants = {}
                    vcf_lines = {}
                    variant_count = 0
                    line_count = 0
                    info_lines = {}
                    #c=0
                    variants_written = True
                    first_chunk = False


        #else:
        #    vcf_lines = json.load(infile)
        #    for i, key in enumerate(vcf_lines.keys()):
        #        variants[i] = key
        #    #print("loaded ",vcf_lines)

        # query the service with the remaining lines
        c=1
        if len(vcf_lines) > 0:
            #if genome_version != "hg38":
            #    vcf_lines = ag.LiftoverClient(genome_version=genome_version).process_data(vcf_lines, target_genome="hg38")

            if magic_obj is not None:
                vcf_lines = magic_obj.process_data(vcf_lines)
            #print("after process ",vcf_lines)

            if output_format == 'json' and variants_written :
                print(',', file=outfile, end='')

            if generate_mapping is True:
                ranked_labels = []
                mapping = {}
                for var in vcf_lines.keys():
                    for feature in vcf_lines[var].keys():
                        if (feature != "variant_data") and (isinstance(vcf_lines[var][feature], str)) and (
                                feature not in ranked_labels):
                            mapping[feature] = ""
                            ranked_labels.append(feature)
                    if "info_features" in vcf_lines[var].keys():
                        if "info_features" not in mapping.keys():
                            mapping["info_features"] = []
                        for feature in vcf_lines[var]["info_features"].keys():
                            mapping["info_features"].append(feature)
                generate_mapping = False
                if first_chunk is True:
                    csv_columns = writer.generate_columns(outfile, mapping)

            if isinstance(vcf_lines, ag.BiomarkerFrame):
                vcf_lines = vcf_lines.data
            for var in vcf_lines.keys():
                #print(vcf_lines[line])

                if output_type == 'file':
                    if writer is not None:
                        #outfile, var, vcf_lines, magic_obj, save_headers=False, variants_written=False
                        #writer.write_chunk_to_file(outfile, vcf_lines, c, magic_obj.srv_prefix, magic_obj.extract_keys,
                        #                           first_chunk=first_chunk, last_chunk=last_chunk)
                        #writer.write_line_to_file(outfile, var, vcf_lines, magic_obj,
                        #                                    save_headers=False, variants_written=False,
                        #                                   mapping=mapping,
                        #                                   ranked_labels=ranked_labels,
                        #                                   labels=labels)
                        #print("WRITE1")



                        writer.write_line_to_file(outfile, var, vcf_lines, magic_obj,
                                                            save_headers=False, variants_written=False,
                                                           mapping=mapping,
                                                           ranked_labels=ranked_labels,
                                                           labels=labels,first_chunk=first_chunk, columns=csv_columns)
                    else:
                        if output_format == 'json':
                            json_str = json.dumps(vcf_lines[var])
                            #json_str = json_str.lstrip('{').rstrip('}')
                            json_str = "\"" + var + "\"" + ":" + json_str
                            if c < len(vcf_lines):
                                json_str = json_str + ','
                            #else:
                            #    json_str = json_str + '}'
                            #print(len(vcf_lines))
                            print(json_str, file=outfile)
                            #print(json.dumps(vcf_lines))
                            #print(json.dumps(vcf_lines), file=outfile)
                            #print(line, file=outfile)
                            c+=1

        #if writer is not None:
        #    last_chunk=True
        #    writer.write_chunk_to_file(outfile, vcf_lines, c, magic_obj.srv_prefix, magic_obj.extract_keys,
        #                               first_chunk=first_chunk, last_chunk=last_chunk)

        #if ((output_format == 'avf') or(output_format == 'json') and (output_type=='file')):
        #    print('}', file=outfile)
        #    #print("{", file=outfile)
        #    #if output_format == 'json':
        #    print(json.dumps(vcf_lines), file=outfile)
        #    #print("}", file=outfile)
        if writer is not None:
            writer.post_process(outfile)

        if infile_str is True:
            infile.close()
        if outfile_str is True:
            outfile.close()


        if output_type == 'obj':
            return vcf_lines

    #def to_vcf(self,vcf_obj, srv_prefix, extract_keys, outfile):
    #    for json_obj in vcf_obj:
    #        print(self.to_single_vcf_line(json_obj, srv_prefix, extract_keys), file = outfile)

    #def to_json(self, json_obj, outfile_str:str):
    #    outfile = open(outfile_str, 'rw')
    #    json.dumps(json_obj, file=outfile)
    #    outfile.close()


