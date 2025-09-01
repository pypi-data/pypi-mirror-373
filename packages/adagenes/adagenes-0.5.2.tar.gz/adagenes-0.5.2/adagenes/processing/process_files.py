import re, traceback, copy, json, gzip
import adagenes as ag
import adagenes.conf.read_config as config
from adagenes.processing.json_biomarker import BiomarkerFrame
from adagenes.tools.client_mgt import get_reader, get_writer
import adagenes.app.db_client
#from adagenes.app.db_client import query_vcf, clear_collection

def dc_to_vcf(dc, vcf_lines):

    dc_tmp = {}
    print("dc ", dc)
    for key in dc:
        if key != '_id':
            dc_tmp[key] = dc[key]

    vcf_lines[dc_tmp['qid']] = dc_tmp

    return vcf_lines

def get_processor(infile, file_type=None):
        """
        Identifies the associated file reader for an input file

        :param infile_src:
        :param file_type:
        :param genome_version:
        :return:
        """
        if isinstance(infile, str):
            if (file_type is None) or (file_type == ""):
                file_type = ag.get_file_type(infile)

        if file_type == 'vcf':
            return ag.VCFProcessor()
        elif file_type == 'csv':
            return ag.CSVProcessor()
        elif file_type == 'avf':
            return ag.AVFProcessor()


def data_list_to_bframe(data_page):
    vcf_lines = {}

    default_cols = ["chrom","pos","ref","alt"]
    for item in data_page:
        qid = item["qid"]
        vcf_lines[qid] = item
        try:
            vcf_lines["variant_data"] = {"CHROM":item["chrom"], "POS": item["pos"], "REF": item["ref"], "ALT": item["alt"]}
        except:
            print("Could not convert to bframe: ",item)
    return vcf_lines

def process_vcf(qid,
                magic_obj,
                variant_batch_size=100,
                line_batch_size=5000,
                mapping=None,
                genome_version=None,
                vcf_data=None,
                conn=None,
                transform=False
                ):
    """

    :param qid:
    :param magic_obj:
    :param variant_batch_size:
    :param line_batch_size:
    :param mapping:
    :param genome_version:
    :param vcf_data:
    :param conn:
    :param transform:
    :return:
    """
    generate_mapping = False
    if conn is None:
        conn = adagenes.app.db_client.DBConn(qid)

    variants_written = False

    variants = {}
    # if input_format == 'vcf':
    variant_count = 0
    line_count = 0
    vcf_lines = {}
    info_lines = {}
    first_chunk = True
    last_chunk = False
    line_count_abs = 0

    header_lines = []
    c = 0
    columns = []
    csv_columns = []

    # get variants from DB
    if vcf_data is None:
        print("query vcf ",qid, " with ", genome_version)
        data_page, count, header_lines, stats = conn.query_vcf(qid, genome_version=genome_version)
        data = data_list_to_bframe(data_page)
    else:
        data = vcf_data
    #print("dc data ",data)
    #ag.app.db_client.clear_collection(qid)

    first_chunk = True
    for dc in data.keys():
        line_count_abs += 1

        #vcf_lines, header_lines, variant_count, line_count, is_header_line, info_lines, variants, columns = \
        #    reader.read_line(line, vcf_lines, outfile, header_lines, magic_obj, genome_version, line_count,
        #                     variant_count, variants, info_lines, is_header_line=is_header_line,
        #                     linecount=line_count_abs, columns=columns, mapping=client_mapping)
        #vcf_lines = dc_to_vcf(dc, vcf_lines)
        vcf_lines[dc] = data[dc]
        # print(vcf_lines)

        # query the service either after 100 ("variant_batch_size") variants
        # or 5000 ("line_batch_size") lines are collected
        # if (len(variants) >= variant_batch_size) or (len(vcf_lines) >= line_batch_size):
        #if (len(vcf_lines) >= variant_batch_size) or (len(vcf_lines) >= line_batch_size):
        if len(vcf_lines) >= line_batch_size:

            # Process
            if magic_obj is not None:

                vcf_lines = magic_obj.process_data(vcf_lines)
                #print("Annotated liftover: ",vcf_lines)

            # Writer
                if generate_mapping is True:
                    ranked_labels = []
                    mapping = {}
                    for var in vcf_lines.keys():
                        for feature in vcf_lines[var].keys():
                            if (feature != "variant_data") and (feature != "info_features") and (
                            isinstance(vcf_lines[var][feature], str)) and (
                                    feature not in ranked_labels):
                                mapping[feature] = ""
                                ranked_labels.append(feature)
                        if "info_features" in vcf_lines[var].keys():
                            if "info_features" not in mapping.keys():
                                mapping["info_features"] = []
                            for feature in vcf_lines[var]["info_features"].keys():
                                mapping["info_features"].append(feature)
                    generate_mapping = False

                c = 1

                if transform is False:
                    conn.update_vcf(vcf_lines, genome_version, magic_obj)
                else:
                    conn.transform_vcf(vcf_lines, "hg38")

                # if output_format == 'vcf':
                variants = {}
                vcf_lines = {}
                variant_count = 0
                line_count = 0
                info_lines = {}
                # c=0
                variants_written = True
                first_chunk = False

    # query the service with the remaining lines
    c = 1
    if len(vcf_lines) > 0:
        # if genome_version != "hg38":
        #    vcf_lines = ag.LiftoverClient(genome_version=genome_version).process_data(vcf_lines, target_genome="hg38")

        if magic_obj is not None:
            #print("annotate NEW", vcf_lines)
            vcf_lines = magic_obj.process_data(vcf_lines)
            #print("li")

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

        if isinstance(vcf_lines, ag.BiomarkerFrame):
            vcf_lines = vcf_lines.data

        #print("generate annotations ", magic_obj, ": ", vcf_lines)
        if transform is False:
            conn.update_vcf(vcf_lines, genome_version, magic_obj)
        else:
            conn.transform_vcf(vcf_lines, "hg38")

    if vcf_data is not None:
        return vcf_data



def process_file(
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
        input_type='file',
        output_type='file',
        save_headers=True,
        features=None,
        lo_hg19=None,
        lo_hg38=None,
        filter=None,
        mapping=None
    ):
    infile_str = False
    outfile_str = False

    # get processor
    #print("filter processing")
    try:
        if isinstance(infile, str):  # TO DO
            if input_format is None:
                input_format = ag.get_file_type(infile)
                #print("GET NEW INPUT FORMAT ",input_format)
            if ag.tools.data_io.is_gzip(infile):
                infile = gzip.open(infile, "rt")
            else:
                infile = open(infile, "r")
            infile_str = True
        else:
            #print("RECEIVED OPEN FILE")
            pass
        if isinstance(outfile, str):
            if output_format is None:
                output_format = ag.get_file_type(outfile)
            outfile = open(outfile, "w")
            outfile_str = True

        if input_format is None:
            input_format = "vcf"
        if output_format is None:
            output_format = "vcf"

        #processor = get_processor(infile, file_type=input_format)
        processor = ag.VCFProcessor()
        processor.process_file(infile, outfile, magic_obj,
                               input_format=input_format,
                               output_format=output_format,
                               reader=reader,
                               writer=writer,
                               variant_batch_size=variant_batch_size,
                               line_batch_size=line_batch_size,
                               genome_version=genome_version,
                               error_logfile=error_logfile,
                               output_type='file', filter=filter,
                               read_mapping=None,
                               client_mapping=mapping)

    except:
        print(traceback.format_exc())

    if infile_str is True:
        infile.close()
    if outfile_str is True:
        outfile.close()


def process_file_dep(
                 infile_src,
                 outfile_src,
                 generic_obj,
                 input_format=None,
                 output_format=None,
                 variant_batch_size=100,
                 line_batch_size=5000,
                 genome_version=None,
                 error_logfile=None,
                 input_type='file',
                 output_type='file',
                 save_headers=True,
                 features=None,
                 lo_hg19=None,
                 lo_hg38=None
                 ):
    reader = get_reader(infile_src, file_type=input_format)
    reader.infile_src = infile_src

    #reader.open_file(infile_src)

    writer = get_writer(outfile_src, file_type=output_format)
    writer.outfile_src = outfile_src
    #writer.open_file(outfile_src)

    if isinstance(infile_src, str):
        infile = open(infile_src, "r")
    else:
        infile = infile_src

    if isinstance(outfile_src, str):
        outfile = open(outfile_src, "r")
    else:
        outfile = outfile_src

    process_dep(
        reader,
        writer,
        generic_obj,
        infile,
        outfile,
        input_format='vcf',
        output_format='vcf',
        variant_batch_size=100,
        line_batch_size=5000,
        genome_version=None,
        error_logfile=None,
        input_type='file',
        output_type='file',
        save_headers=True,
        features=None,
        lo_hg19=lo_hg19,
        lo_hg38=lo_hg38
    )

    reader.close_file()
    writer.close_file()


def process_dep(
            reader,
            writer,
            module,
            infile,
            outfile,
            input_format='vcf',
            output_format='vcf',
            variant_batch_size=100,
            line_batch_size=5000,
            genome_version=None,
            error_logfile=None,
            input_type='file',
            output_type='file',
            save_headers=True,
            features=None,
            lo_hg19=None,
            lo_hg38=None
            ):
    """
        Reads a file of genetic mutations in multiple formats (VCF, JSON), calls a specific processing function that edits the contents of the input file and saves the results in an output file

        :param infile:
        :param outfile:
        :param generic_obj:
        :param input_format:
        :param output_format:
        :param variant_batch_size:
        :param line_batch_size:
        :param genome_version:
        :param output_type:
        :param save_headers
        :return:
        """

    json_obj = BiomarkerFrame()
    json_obj.infile = reader.infile
    json_obj.outfile = writer.outfile
    json_obj.module = module
    json_obj.variants_written = False
    json_obj.variant_batch_size = variant_batch_size
    json_obj.line_batch_size = line_batch_size
    json_obj.genome_version = genome_version
    json_obj.error_logfile = error_logfile
    json_obj.input_type = input_type
    json_obj.output_type = output_type
    json_obj.save_headers = save_headers
    json_obj.output_format = output_format
    json_obj.input_format = input_format
    json_obj.features = features
    json_obj.variants = {}
    json_obj.row = 0
    json_obj.data = {}
    print_headers = True

    writer.write_to_file_start(json_obj.outfile)

    # process
    #if (len(json_obj.variants) >= json_obj.variant_batch_size) or (len(json_obj.data) >= json_obj.line_batch_size):

    json_obj = reader.read_file_chunk(json_obj.infile,json_obj)

    if module=="liftover":
        json_obj.data = module.process_data(json_obj.data,lo_hg19=lo_hg19,lo_hg38=lo_hg38)
    else:
        json_obj.data = module.process_data(json_obj.data)

    writer.write_chunk_to_file(json_obj.outfile, json_obj,variants_written=json_obj.variants_written, save_headers=print_headers)
    print_headers = False

    json_obj.variants = {}
    json_obj.data = {}
    json_obj.variant_count = 0
    json_obj.line_count = 0
    json_obj.info_lines = {}
    json_obj.variants_written = True


    writer.write_to_file_finish(json_obj.outfile)

    # if input_format == 'vcf':
    #    self._read_vcf_file_chunk()
    # elif input_format == 'json':
    #    self.data = json.load(infile)
    #    if 'vcf_header' in self.data.keys():
    #        self.data.pop('vcf_header')
    #    for i, key in enumerate(self.data.keys()):
    #        self.variants[i] = key
    # elif input_format == 'tsv':
    #     self.data = self.load_table_file(infile)
    #     for i, key in enumerate(self.data.keys()):
    #        self.variants[i] = key

    # query the service with the remaining lines
    # self._module_requests()
    # self._vcf_to_json()

    # if output_type == 'obj':
    #    return self.data

def _write_chunk_to_file(self):
    #if self.output_format == 'json' and self.variants_written:
    #    print(',', file=self.outfile, end='')
    # elif output_format == 'tsv':
    #    print("f ",'\t'.join(get_feature_keys(data, generic_obj.extract_keys)))
    #    print('\t'.join(get_feature_keys(data, generic_obj.extract_keys)),file=outfile)

    try:
        self.data = self.generic_obj.process_data(self.data, self.variants, self.outfile,
                                                       input_format=self.input_format)
    except:
        print("error calling object-specific function")
        print(traceback.format_exc())

    if self.output_type == 'file':
        c = 1

        for var in self.data.keys():
            self.row = self.row + 1
            if self.output_format == 'vcf':
                print(self.to_single_vcf_line(self.data[var], self.generic_obj.srv_prefix,
                                              self.generic_obj.extract_keys),
                      file=self.outfile)
            elif self.output_format == 'json':
                json_str = json.dumps(self.data[var])
                json_str = "\"" + var + "\"" + ":" + json_str
                if c < len(self.data):
                    json_str = json_str + ','
                c += 1
                print(json_str, file=self.outfile)
            elif self.output_format == 'tsv':
                if self.row == 1:
                    # add column labels in 1st row
                    print(self.get_feature_keys(self.data, self.generic_obj.extract_keys), file=self.outfile)
                tsv_str = self.to_single_tsv_line(self.data[var], self.generic_obj.srv_prefix,
                                                  self.generic_obj.extract_keys)
                print(tsv_str, file=self.outfile)

        self.variants = {}
        self.data = {}
        self.variant_count = 0
        self.line_count = 0
        self.info_lines = {}
        self.variants_written = True


def _module_requests(self):
    c = 1
    if len(self.data) > 0:
        try:
            self.data = self.generic_obj.process_data(self.data, self.variants, self.outfile,
                                                           input_format=self.input_format)
        except:
            print("error calling object-specific function")
            print(traceback.format_exc())
        if self.output_format == 'json' and self.variants_written:
            print(',', file=self.outfile, end='')
        for var in self.data.keys():
            self.row = self.row + 1
            if self.output_type == 'file':
                if self.output_format == 'vcf':
                    # print("write to file ",self.data)
                    print(self._to_single_vcf_line(self.data[var], self.generic_obj.srv_prefix,
                                                   self.generic_obj.extract_keys),
                          file=self.outfile)
                elif self.output_format == 'json':
                    json_str = json.dumps(self.data[var])
                    json_str = "\"" + var + "\"" + ":" + json_str
                    if c < len(self.data):
                        json_str = json_str + ','
                    print(json_str, file=self.outfile)
                    c += 1
                elif self.output_format == 'tsv':
                    # add column labels in 1st row
                    if self.row == 1:
                        print(self.get_feature_keys(self.data, self.generic_obj.extract_keys),
                              file=self.outfile)
                    tsv_str = self.to_single_tsv_line(self.data[var], self.generic_obj.srv_prefix,
                                                      self.generic_obj.extract_keys)
                    print(tsv_str, file=self.outfile)

def transform_file_format(input_file, input_format=None, output_format=None):

    pass
