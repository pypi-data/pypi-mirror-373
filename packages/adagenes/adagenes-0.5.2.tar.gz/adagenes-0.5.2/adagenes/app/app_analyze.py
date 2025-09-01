import os, datetime, re, json, copy, subprocess
import traceback
import time
import adagenes as ag
import adagenes.tools.load_dataframe
import adagenes.app.app_tools
from adagenes.app.app_annotate import get_magic_obj
import adagenes.app.app_io
import adagenes.conf
import adagenes.app.app_parse_data
import adagenes.app.run_liftover
import adagenes.app.db_client
import adagenes.app.stats



def update_progress_status(qid, progress_msg, progress_val, buffer_val):
    conn = adagenes.app.db_client.DBConn(qid)
    conn.update_progress_msg(progress_msg, progress_val, buffer_val)
    conn.close_connection()

def get_progress_status(qid):

    # get progress status
    conn = adagenes.app.db_client.DBConn(qid)
    progress_msg, progress_val, buffer_val = conn.query_progress_msg()
    conn.close_connection()

    #result = {"progress": progress, "current_files": current_files, "expected_files": expected_n_files,
    #          "last_steps": last_steps, "step_name": step_name, "current_size": current_size}
    result = {"progress": progress_val,
              "buffer": buffer_val,
              "progressMsg": progress_msg
              }

    return result

def recognize_column_types(list):
    column_type = None
    consistent_type = None

    for value in list:

        if value is None:
            continue
        elif value == "":
            continue

        try:
            val = int(value)
            column_type = 'integer'
            continue
        except:
            pass

        try:
            val = float(value)
            column_type = 'float'
            continue
        except:
            pass

        column_type = 'string'

        if column_type is not None:
            if column_type != consistent_type:
                if (column_type=="integer") and (consistent_type == "float"):
                    column_type = "float"
                elif ((column_type == "integer") or (column_type == "float")) and (consistent_type == "string"):
                    column_type = "string"

        consistent_type = column_type

    return column_type


def download_newest_file_as_csv(data_dir):
    infile = adagenes.app.io.find_newest_file(data_dir)
    outfile = infile + ".csv"

    # generate csv
    print("vcf to csv ",outfile)
    ag.process_file(infile, outfile, None)
    return outfile


def load_file(qid, data_dir, filter_model=None, sort_model=None, start_row=None, end_row=None, genome_version=None):
    """

    :param qid:
    :param data_dir:
    :return:
    """
    data_dir = data_dir + "/" + qid
    #files = [f for f in listdir(data_dir) if isfile(join(data_dir, f))]
    #infile = data_dir + "/" + files[0]
    #print("data dir ",data_dir)
    #print("load file with filter ",str(filter))
    #infile = adagenes.app.app_io.find_newest_file(data_dir, filter=filter, genome_version=genome_version)

    #if qid == "sample-vcf":
    #    infile = data_dir + ag.conf_reader.sample_file
    #elif qid == "sample-protein":
    #    infile = data_dir + ag.conf_reader.sample_protein_file
    #file_type = ag.get_file_type(infile)
    #print("load file ",infile)

    #bframe = ag.read_file(infile, start_row=start_row, end_row=end_row)
    #print(bframe.data)

    progress_msg = "Filter variants"
    progress = 80
    progress_val = progress
    buffer_val = progress + 10
    adagenes.app.app_analyze.update_progress_status(qid, progress_msg, progress_val, buffer_val)

    conn = adagenes.app.db_client.DBConn(qid)
    data_page, count, header_lines, stats = conn.query_vcf(qid, filter_model=filter_model, sort_model=sort_model,
                                                    start_row=start_row, end_row=end_row)
    conn.close_connection()

    #return bframe, file_type
    return data_page, count, header_lines, stats


def get_column_defs(output_format):
    pass



def get_previous_filters(previous_actions):
    previous_filters = []
    if isinstance(previous_actions, list):
        for action in previous_actions:
            if str(action).startswith("Filter:"):
                pattern = r'\[(.*?)\]'

                # Search for the pattern in the text
                match = re.search(pattern, action)

                # If a match is found, return the text within the brackets
                if match:
                    filter = match.group(1)
                    previous_filters.append([filter, action])
    return previous_filters



#qid, transform_output_format, transform_model, genome_version=genome_version, data_dir=data_dir

def transform_data(qid, transform_output_format, transform_model, genome_version=None, data_dir=None):
    """
    Annotate variant data with selected filters, and stores the annotated data in a new file

    :param qid:
    :param annotations:
    :param genome_version:
    :param data_dir:
    :param output_format:
    :return:
    """


    print("Transform ",transform_model)
    data_dir = adagenes.conf.read_config.__DATA_DIR__
    data_dir = data_dir + "/" + qid
    logfile = data_dir + '/log.txt'

    if (transform_output_format == 'vcf') and (transform_model != {}):
        print("Transform to VCF ")

        if "gene" not in transform_model.keys():


            key = "transform-vcf"

            infile = adagenes.app.io.find_newest_file(data_dir)
            if qid == "sample-vcf":
                infile = data_dir + ag.conf_reader.sample_file
            if qid == "sample-protein":
                infile = data_dir + ag.conf_reader.sample_protein_file

            # infile = split_filename(infile)
            infile_name = ag.app.io.split_filename(infile)

            previous_actions = ag.app.io.load_log_actions(logfile)
            print("loaded logfile ", logfile)
            print("previous actions: ", previous_actions)

            out_filetype = "csv"
            if key == "transform-vcf":
                out_filetype = "vcf"
            print("out filetype ")

            annotation_key = 'Transformation:VCF'
            contains_substring = any(annotation_key in entry for entry in previous_actions)
            if contains_substring is False:
                datetime_str = str(datetime.datetime.now())
                print("infile ", infile)
                outfile = infile_name + ".tf." + datetime_str + "." + '.' + out_filetype
                outfile = outfile.replace(" ", "_")
                outfile = outfile.replace(":", "-")

                magic_obj = adagenes.app.annotate.get_magic_obj(key, genome_version, transform_model=transform_model)
                ag.process_file(infile, outfile, magic_obj, output_format=out_filetype)

                ag.app.io.append_to_file(logfile, annotation_key + "(" + datetime_str + ")::" + outfile + '\n')

                print("File annotated: ", outfile)
            else:
                print("Annotation already found: ", annotation_key)
        else:
            # Protein2DNA conversion
            print("Protein to VCF")


            annotations = { 'protein-to-gene': True }
            mapping = { "gene": transform_model["gene"], "variant": transform_model["aa_exchange"] }

            magic_obj = get_magic_obj("protein-to-gene", genome_version)
            #print(magic_obj)
            #print("transfrom ",annotations)

            #adagenes.app.annotate.annotate_qid(qid, annotations,genome_version=genome_version, mapping=mapping)
            #adagenes.app.app_annotate.annotate_qid_db(qid, annotations, mapping=mapping, transform=True)

            file_id = qid
            conn = adagenes.app.db_client.DBConn(file_id)

            cursor = conn.collection.find()
            batch = []
            for doc in cursor:
                # print("batch doc ",doc)
                batch.append(doc)

            vcf_data, orig_ids = adagenes.app.db_client.load_bframe_from_db_data(batch, genome_version, mapping=mapping)

            vcf_data = ag.process_vcf(qid, magic_obj, genome_version=genome_version, vcf_data=vcf_data, transform=True)

            # print("batch ",vcf_data.keys())
            # print("process batch ",len(list(vcf_data.keys())))




            conn.close_connection()

            # generate column defs
            adagenes.app.app_annotate.generate_new_header_lines(qid,mapping=mapping)


def liftover(qid, genome_version, output_genome_version, data_dir=None, output_format='vcf'):
    """

    :param output_format:
    :param data_dir:
    :param qid:
    :param genome_version:
    :param output_genome_version:
    :return:
    """
    data_dir = data_dir + "/" + qid
    logfile = data_dir + '/log.txt'

    #infile = adagenes.app.io.find_newest_file(data_dir)
    #if qid == "sample-vcf":
    #    infile = data_dir + ag.conf_reader.sample_file
    #if qid == "sample-protein":
    #    infile = data_dir + ag.conf_reader.sample_protein_file

    #infile = ag.app.io.split_filename(infile)
    datetime_str = str(datetime.datetime.now())
    #outfile = infile + ".ann." + datetime_str + "." + output_format
    #outfile = outfile.replace(" ", "_")
    #outfile = outfile.replace(":", "-")
    #outfile = adagenes.app.tools.update_filename_with_current_datetime(qid, action="processed")
    #outfile = outfile.replace(genome_version,output_genome_version)

    magic_obj = ag.LiftoverAnnotationClient(genome_version = genome_version, target_genome=output_genome_version)
    print("liftover: ",genome_version," to ", output_genome_version,": ",qid)
    ag.process_vcf(qid, magic_obj, genome_version=genome_version)

    # update header lines
    conn = adagenes.app.db_client.DBConn(qid)
    conn.update_header_lines(qid, magic_obj.info_lines)
    conn.close_connection()

    annotation_key = 'Liftover:' + genome_version + " to " + output_genome_version + "(" + datetime_str + ")::"
    ag.app.app_io.append_to_file(logfile, annotation_key + '\n')


def is_filter(action):
    if str(action).startswith("Filter:"):
        return True
    else:
        return False

def compare_dictionaries(a, b):
    added = {}
    removed = {}

    # Check for added keys
    for key in b:
        if key not in a:
            added[key] = b[key]

    # Check for removed keys
    for key in a:
        if key not in b:
            removed[key] = a[key]

    return added, removed


def apply_filter_sort(qid, filter_model, sort_model, data_dir=None, genome_version=None):
    """

    :param qid:
    :param filter_model:
    :param sort_model:
    :param data_dir:
    :return:
    """
    apply_new_filter_sort = True
    # load newest filter file
    #infile = adagenes.app.io.find_newest_file(data_dir, filter=True)
    data_dir = data_dir + "/" + qid
    active_filter = adagenes.app.app_io.get_active_filter(data_dir)

    active_sort = adagenes.app.app_io.get_active_sort(data_dir)

    # check if filtering/sorting has changed
    print("compare prev filter model ", active_filter, " with new filter model ",filter_model)
    if active_filter != filter_model:
        apply_new_filter_sort = True

    print("compare prev sort model ",active_sort, " with new sort model ",sort_model)
    if active_sort != sort_model:
        apply_new_filter_sort = True

    if apply_new_filter_sort is True:
        print("apply new filter")

        # Apply filtering
        if filter_model is not None:
            filter_model = apply_filters(qid, filter_model, sort_model=sort_model, data_dir=data_dir, genome_version=genome_version)
        # update active filter

        # Apply sorting
        print("filter model ",filter_model)
        print("sort model ",sort_model)
        if sort_model is not None:
            apply_sorting(qid, sort_model, filter_model=filter_model, data_dir=data_dir, genome_version=genome_version)
        # update active sort

    return apply_new_filter_sort


def apply_filters(qid, filter_model, sort_model=None, data_dir=None, output_format='vcf', genome_version=None):
    """
        Apply AG Grid filterModel to the dataset.

        :param data
        :param filter_model
    """
    if sort_model is None:
        sort_model = {}

    print("Filters: ",filter_model)
    #bframe = load_file(qid, data_dir)
    #data = bframe.data
    #data_dir = data_dir + "/" + qid
    logfile = data_dir + '/log.txt'

    fallback_file = ""
    previous_actions = ag.app.app_io.load_log_actions(logfile)
    # print("loaded logfile ", logfile)
    print("previous actions: ", previous_actions)
    # find out if filter was removed
    previous_filters_list = get_previous_filters(previous_actions)
    print("previous filters ",previous_filters_list)

    columns_to_find = []
    columns_found = []
    first_filter_found = False
    reverse_data = False

    for i,prev_action in enumerate(reversed(previous_actions)):
        #if is_filter(prev_action):

            pattern = r';;.*?##'
            match = re.search(pattern, prev_action)

            if match:
                prev_filter_model = match.group(0)
                prev_filter_model = prev_filter_model.lstrip(";;").rstrip("##")
                print("prev filter model ",prev_filter_model)
                try:
                    prev_filter = json.loads(prev_filter_model)
                except:
                    print("Could not load JSON: ",prev_filter_model)
                    print(traceback.format_exc())
                    prev_filter = {}
            else:
                prev_filter = {}

            #if len(prev_action.split(";;")) > 1:
            #    prev_filter = json.loads(prev_action.split(";;")[1])
            #else:
            #    prev_filter = {}

            if first_filter_found is False:
                #print("Last entry ",prev_action)
                columns_to_find = list(prev_filter.keys())
                #print("prev action ", prev_action," columns to find: ",columns_to_find)
                #print("compare ",prev_filter," fm ",filter_model)

                if prev_filter != filter_model:
                    Added, removed = compare_dictionaries(prev_filter, filter_model)
                    if removed != {} :
                        reverse_data = True
                        print("Filter changed: Reverse data , filter model: ",filter_model," last saved model: ",prev_filter)
                else:
                    break
                first_filter_found = True

            #print("Search for last fitting model: ", filter_model, " saved model: ", prev_filter)
            #if (prev_filter == filter_model) and (reverse_data is True):
                    #print("Filter removed: ", prev_filter, ",", i, "Fallback to file: ", prev_action)
                    #fallback_file = prev_action.split("::")[1]
                    #fallback_file_nofilter = fallback_file.split(";;")
                    #if len(fallback_file_nofilter)>1:
                    #    fallback_file = fallback_file_nofilter[0]
                    #print(fallback_file)
                    #filter_model = prev_filter
                    #print("Loaded previous filter model: ", filter_model)
                    #infile_name = ag.app.io.split_filename(fallback_file)
                    #datetime_str = str(datetime.datetime.now())
                    #outfile = infile_name.strip() + ".filter." + datetime_str + "." + output_format
                    #outfile = outfile.replace(" ", "_")
                    #outfile = outfile.replace(":", "-")
                    #cmd = "cp -v " + fallback_file.strip() + " " + outfile
                    #print(cmd)
                    #os.system(cmd)
                    #annotation_key = "Filter removed: " + "(" + datetime_str + ")::" + outfile + ";;" + json.dumps(
                    #    str(filter_model) + "##" + json.dumps(sort_model) )
                    #ag.app.io.append_to_file(logfile, annotation_key + '\n')
                    #break

    if (reverse_data is True) and (fallback_file == ""):
        filter_model = {}
        reversed(previous_actions)
        #fallback_file = previous_actions[0].split("::")[1]
        #print("no fitting prefilter found. Setting filter to zero ",fallback_file)
        #infile_name = ag.app.io.split_filename(fallback_file)
        #datetime_str = str(datetime.datetime.now())
        #outfile = infile_name.strip() + ".ann." + datetime_str + "." + output_format
        #outfile = outfile.replace(" ","_")
        #outfile = outfile.replace(":","-")
        #print("outfile ",outfile)
        #print("ff ",fallback_file)
        #cmd = "cp -v " + fallback_file.strip() + " " + outfile
        #print(cmd)
        #os.system(cmd)

        #annotation_key = "Filter removed: " + "(" + datetime_str + ")::" + outfile + ";;" + json.dumps(filter_model) + \
        #    json.dumps(sort_model)
        #ag.app.io.append_to_file(logfile, annotation_key + '\n')

            #for pcol in columns_to_find:
            #    if pcol in filter_model.keys():
            #        if prev_filter[pcol] == filter_model[pcol]:
            #            columns_to_find.pop(pcol)


        #if len(columns_to_find) > 0:
        #        print("Filter removed: ", prev_filter, ",", i, "Fallback to file: ", previous_actions[i+1])
        #        fallback_file = previous_actions[i+1].split("::")[1]
        #        fallback_file_nofilter = fallback_file.split(";;")
        #        if len(fallback_file_nofilter)>1:
        #            fallback_file = fallback_file_nofilter[0]
        #        print(fallback_file)
        #        # load previous filters
        #        pfilter = previous_actions[i+1].split(";;")
        #        if len(pfilter) > 1:
        #            prev_filter_str = json.loads(previous_actions[i-1].split(";;")[1])
        #        else:
        #            prev_filter_str = {}
        #        filter_model = prev_filter_str
        #        print("Loaded previous filter model: ", filter_model)

    #for filter_item in filter_model.keys():
    #    column = filter_item
    #    filter_data = filter_model(filter_item)

    # Apply new filters
    count_filters = 0
    use_filtered_file = False
    for column, filter_data in filter_model.items():
        if count_filters > 0:
            use_filtered_file = True
        #print("column ",column,", ",filter_data)
        filter_type = filter_data.get("filterType")

        #if fallback_file == "":

        if use_filtered_file is False:
            infile = adagenes.app.app_io.find_newest_file(data_dir, filter=use_filtered_file, genome_version=genome_version)
        else:
            infile = copy.deepcopy(outfile)

        print("Apply filter ", str(count_filters), " with filter ", str(use_filtered_file), " use file ",infile)
        #else:
        #    infile = fallback_file
        if qid == "sample-vcf":
            infile = data_dir + ag.conf_reader.sample_file
        if qid == "sample-protein":
            infile = data_dir + ag.conf_reader.sample_protein_file

        #print("Filter: ", filter_type, " ", qid, ": ",infile)
        infile_name = ag.app.app_io.split_filename(infile)

        magic_obj = get_magic_obj("filter_" + filter_type, None)
        filter = []
        #filter_value = filter_data["filter"]
        filter.append(column)
        #filter.append(filter_value)
        #filter_type = filter_data['type']
        #filter.append(filter_type)
        filter.append(filter_data)
        print("Filter ",filter_data)
        annotation_key = 'Filter:' + str(filter) #+ "(" + datetime_str + ")"
        count_filters += 1

        if annotation_key not in previous_actions:
            #datetime_str = str(datetime.datetime.now())

            outfile = adagenes.app.app_tools.update_filename_with_current_datetime(infile_name, action="filter",
                                                                               increase_count=True)
            print("Applied filter: infile ", infile, " outfile ", outfile)
            #outfile = infile_name + ".ann." + datetime_str + "." + output_format
            #outfile = outfile.replace(" ", "_")
            #outfile = outfile.replace(":", "-")
            datetime_str = str(datetime.datetime.now())
            #outfile = infile + datetime_str + "_" + ".ann." + output_format
            annotation_key = annotation_key + "(" + datetime_str + ")::" + outfile + ";;" + json.dumps(filter_model) + \
                "##" + json.dumps(sort_model)

            magic_obj.filter = filter
            print(magic_obj.filter)
            ag.process_vcf(qid, magic_obj, genome_version=genome_version)
            print("Filtered file: ", outfile)

            ag.app.app_io.append_to_file(logfile, annotation_key + '\n')

        else:
            print("Filter already found: ",annotation_key)

        # Update active filter
        filter_file = data_dir + '/active_filter.json'
        with open(filter_file, 'w') as file:
            file.write(json.dumps(filter_model))

        #if filter_type == "text":
        #    data = [
        #        row
        #        for row in data
        #        if str(filter_data["filter"]).lower() in str(row[column]).lower()
        #    ]
        #elif filter_type == "number":
        #    filter_value = filter_data["filter"]
        #    if filter_data["type"] == "equals":
        #        data = [row for row in data if row[column] == filter_value]
        #    elif filter_data["type"] == "greaterThan":
        #        data = [row for row in data if row[column] > filter_value]
        #    elif filter_data["type"] == "lessThan":
        #        data = [row for row in data if row[column] < filter_value]
    #return data

    if count_filters == 0:
        # no filter found => create redirection to last annotated file
        most_annotated_file = adagenes.app.app_io.find_newest_file(data_dir, filter=False)
        print("No filters found. Using most annotated file: ",most_annotated_file)
        symlink_file = adagenes.app.app_tools.update_filename_with_current_datetime(most_annotated_file, action="processed", increase_count=True)
        cmd = ["ln","-sv",most_annotated_file, symlink_file]
        #print(cmd)
        #subprocess.run(cmd)

        cmd_update_timestamp = ["touch", symlink_file]
        #subprocess.run(cmd_update_timestamp, check=True)

        # remove former filter and sort files
        #adagenes.app.tools.delete_files_with_higher_number(data_dir, most_annotated_file)

    return filter_model





def apply_sorting(qid, sort_model, filter=True, filter_model=None, data_dir=None, genome_version=None):
    """
    Apply AG Grid sortModel to the dataset.

    :param data:
    :param sort_model:
    """
    if filter_model is None:
        filter_model = {}

    #print("Sort: ",sort_model)

    #bframe = load_file(qid, data_dir)
    #data = bframe.data
    #data = generate_dataframe_from_dict(data)
    #data_dir = data_dir + "/" + qid
    logfile = data_dir + '/log.txt'
    sort_str = ""

    if sort_model:
        sort_found = False
        for sort in reversed(sort_model):  # AG Grid supports multi-column sorting
            if sort["sort"] is not None:
                sort_found = True
                if sort["sort"] == "asc":
                    asc = True
                else:
                    asc = False

                infile = adagenes.app.app_io.find_newest_file(data_dir, filter=filter, genome_version=genome_version)
                infile_name = ag.app.app_io.split_filename(infile)
                print("load sorting file ",infile)
                df, header_lines = adagenes.tools.load_dataframe.load_dataframe(infile)
                cols_orig = copy.deepcopy(df.columns)
                #print("loaded df before sorting ", df)

                #print("Sort ",sort["field"], ": ",sort["sort"],", ")
                #print("Order: ", data)
                column = sort["colId"]
                order = sort["sort"]
                reverse = order == "desc"
                #data.sort(key=lambda x: x[column], reverse=reverse)
                #data.sort(key=lambda x: (math.isnan(x[column]) if isinstance(x[column], float) else False, x[column]),
                #          reverse=reverse)

                #data.sort(key=lambda x: (x.get(column, None) is None, x.get(column, None)), reverse=reverse)
                columns_lower = [x.lower() for x in list(df.columns)]
                df.columns = columns_lower

                print("df columns ",df.columns, " sort by ",column)
                df = df.sort_values(by=column, ascending = asc)
                sort_str += column + "," + str(asc) + ","
        sort_str = sort_str.rstrip(",")

        if sort_found is False:
            pass
            #infile = find_newest_file(data_dir)
            #infile_name = split_filename(infile)
            #df = adagenes.tools.load_dataframe.load_dataframe(infile)
            #cols_orig = copy.deepcopy(df.columns)
        else:
            datetime_str = str(datetime.datetime.now())
            df.columns = cols_orig
            output_format="vcf"

            #outfile = infile_name + ".ann." + datetime_str + "." + output_format
            #outfile = outfile.replace(" ", "_")
            #outfile = outfile.replace(":", "-")

            #infile_name = ag.app.io.split_filename(fallback_file)
            try:
                infile_name = ag.app.app_io.split_filename(infile)
                datetime_str = str(datetime.datetime.now())

                outfile = adagenes.app.app_tools.update_filename_with_current_datetime(infile_name, action="sort")
                print("sorted file outfile ", outfile)
                adagenes.tools.load_dataframe.dataframe_to_vcf(df, header_lines, outfile)

                # Add log file entry
                #annotation_key = "Sort model: " + "(" + datetime_str + ")::" + outfile + ";;" + json.dumps(
                #    filter_model) + "##" + json.dumps(sort_model)
                annotation_key = "Sort model: " + "(" + datetime_str + ")::" + outfile + ";;" + json.dumps(
                    filter_model) + "##" + sort_str
                ag.app.app_io.append_to_file(logfile, annotation_key + '\n')

                # Update active sort
                sort_file = data_dir + '/active_sort.json'
                with open(sort_file, 'w') as file:
                    file.write(json.dumps(sort_model))

            except:
                print(traceback.format_exc())

    #return data


def generate_table_data_from_bframe(variants, max_rows, header_lines, output_format='vcf',
                                    genome_version=None):
    """
    Generates an AG Grid data table from a biomarker frame. Utilized to display variant data in the
    AdaGenes web front end.

    :param bframe:
    :param output_format:
    :return:
    """
    #print("variants ",variants)

    column_defs = []
    table_data = []

    #print("output format ",output_format)
    columns = []

    if output_format == "vcf":
        table_data = []

        min_width = 200
        min_width=200

        columns = ['CHROM', 'POS','ID','REF','ALT','QUAL','FILTER']
        column_defs = [
            {'headerName': 'CHROM', 'field': 'chrom', 'filter': "agTextColumnFilter", 'floatingFilter': 'true',
             'minWidth': min_width},
            {'headerName': 'POS', 'field': 'pos', 'filter': "agNumberColumnFilter", 'floatingFilter': 'true',
             'minWidth': min_width},
            {'headerName': 'ID', 'field': 'id', 'filter': 'agTextColumnFilter', 'floatingFilter': 'true',
             'minWidth': min_width},
            {'headerName': 'REF', 'field': 'ref', 'filter': "agTextColumnFilter", 'floatingFilter': 'true',
             'minWidth': min_width},
            {'headerName': 'ALT', 'field': 'alt', 'filter': "agTextColumnFilter", 'floatingFilter': 'true',
             'minWidth': min_width},
            {'headerName': 'QUAL', 'field': 'qual', 'filter': 'agNumberColumnFilter', 'floatingFilter': 'true',
             'minWidth': min_width},
            {'headerName': 'FILTER', 'field': 'filter', 'filter': 'agTextColumnFilter', 'floatingFilter': 'true',
             'minWidth': min_width}
        ]

        # get column identifiers
        #print("BFRAME HEADERS ", bframe.header_lines)
        for header_line in header_lines:
            #pass
            column_defs, columns = adagenes.app.app_parse_data.get_column_definition(header_line, column_defs, columns)
            column_defs = adagenes.app.app_parse_data.remove_column_def_duplicates(column_defs)
        #print("HEADER LINES ",columns,": ",column_defs)

        for var in variants:
            # base VCF columns
            if "variant_data" in var:
                if "ID" in var["variant_data"]:
                    id_data = var["variant_data"]['ID']
                else:
                    id_data = "."

                if "QUAL" in var["variant_data"]:
                    qual_data = var['variant_data']['QUAL']
                else:
                    qual_data = '.'

                if "FILTER" in var["variant_data"]:
                    filter_data = var['variant_data']['FILTER']
                else:
                    filter_data = '.'

            #print("table_data_from_bframe ",var)

            if "CHROM" in var:
                chrom = var["CHROM"]
            elif "chrom" in var:
                chrom = var["chrom"]
            else:
                chrom = ""

            #print("output genome version ",genome_version)
            if genome_version == "hg38" and "POS_hg38" in var:
                pos = var["POS_hg38"]
            elif genome_version == "hg19" and "POS_hg19" in var:
                pos = var["POS_hg19"]
            elif genome_version == "t2t" and "POS_t2t" in var:
                pos = var["POS_t2t"]
            else:
                print("no pos found ",var)
                if "POS" in var:
                    pos = var["POS"]
                elif "pos" in var:
                    pos = var["pos"]
                else:
                    pos = ""

            if "REF" in var:
                ref = var["REF"]
            elif "ref" in var:
                ref = var["ref"]
            else:
                ref = ""

            if "ALT" in var:
                alt = var["ALT"]
            elif "alt" in var:
                alt = var["alt"]
            else:
                alt = ""

            if "id" in var:
                id_data = var['id']
            else:
                id_data = "."

            if "qual" in var:
                qual_data = var['qual']
            else:
                qual_data = '.'

            if "filter" in var:
                filter_data = var['filter']
            else:
                filter_data = '.'

            dc = {
                'chrom': chrom,
                'pos': pos,
                'id': id_data,
                'ref': ref,
                'alt': alt,
                'qual': qual_data,
                'filter': filter_data
            }

            #print("load cols ",var.keys())
            default_cols = ['chrom','pos','ref','alt','id','qual','filter','row_number','_id']
            for key in var.keys():
                if key not in default_cols:
                    key_lower = key.lower()
                    #print("key in columns ",key,": ",columns)
                    if key_lower in columns:
                        dc[key_lower] = var[key]
            #print("loaded dc ",dc)

            # Preexisting features
            #print(bframe.data)
            #info_features = bframe.data[var]["header_lines"].keys() #bframe.data[var]["info_features"].keys()
            #print("INFO Features ",info_features)
            #print(bframe.data[var]["info_features"])

            #for inf in info_features:
            #    column_type = recognize_column_types([bframe.data[var]["info_features"][inf]])
            #    if column_type == "float":
            #        filter_type = "agNumberColumnFilter"
            #    elif column_type == "integer":
            #        filter_type = "agNumberColumnFilter"
            #    else:
            #        filter_type = "agTextColumnFilter"

            #    column_id = inf.lower()
            #    dc[column_id] = bframe.data[var]["info_features"][inf]

            #    inf_column = { 'headerName': inf, 'field': column_id, 'filter': filter_type, 'floatingFilter': 'true',
            #                   'minWidth': min_width}

            #    if column_id not in columns:
            #        column_defs.append(inf_column)
            #        columns.append(column_id)

            table_data.append(dc)

    else:
        # Load CSV
        print("output unspecified")

        reserved_features = ['_id','row_number', 'type','mutation_type', 'mdesc','orig_identifier']

        #for header_line in header_lines:
        #    #pass
        #    column_defs, columns = adagenes.app.app_parse_data.get_column_definition(header_line, column_defs, columns)
        #column_defs = default_column_defs + column_defs
        #print("HEADER LINES ",columns,": ",column_defs)

        for var in variants:
            # base VCF columns
            if "variant_data" in var:
                if "ID" in var["variant_data"]:
                    id_data = var["variant_data"]['ID']
                else:
                    id_data = "."

                if "QUAL" in var["variant_data"]:
                    qual_data = var['variant_data']['QUAL']
                else:
                    qual_data = '.'

                if "FILTER" in var["variant_data"]:
                    filter_data = var['variant_data']['FILTER']
                else:
                    filter_data = '.'

            #print(var)

            dc = {}

            # Preexisting features
            #print(variants)
            #info_features = var["info_features"].keys()
            info_features = var.keys()
            #print("INFO Features ",info_features)
            #print(var["info_features"])
            for inf in info_features:
                column_type = recognize_column_types([var[inf]])
                if column_type == "float":
                    filter_type = "agNumberColumnFilter"
                elif column_type == "integer":
                    filter_type = "agNumberColumnFilter"
                else:
                    filter_type = "agTextColumnFilter"

                min_width=200

                inf_column = { 'headerName': inf, 'field': inf.lower(), 'filter': filter_type, 'floatingFilter': 'true',
                               'minWidth': min_width}

                column_id = inf.lower()
                #dc[column_id] = var["info_features"][inf]

                #dc[column_id] = var[inf]
                if inf not in reserved_features:
                    dc[column_id] = var[inf]
                    if column_id not in columns:
                        column_defs.append(inf_column)
                        columns.append(column_id)
                #newdc={}
                #for feature in var[inf]:
                #    if feature not in reserved_features:
                #        newdc[feature] = var[inf]

                #if inf not in columns:



            table_data.append(dc)

    #print("Columns ", columns)
    #print("Columns defs: ",column_defs)
    #print(table_data)

    return column_defs, table_data


def analyze_uploaded_file(qid, data_dir = None,
                          start_row=None, end_row=None,
                          genome_version="hg38",
                          output_genome_version='',
                          output_format="vcf",
                          annotate=None,
                          sort_model=None,
                          filter_model = None,
                          transform_output_format = None,
                          transform_model = None):
    """

    :param qid:
    :param data_dir:
    :param genome_version:
    :param output_format:
    :return:
    """
    stats_outfile = open("/home/nadine/adagenes_performance.txt","a")

    adagenes.app.app_analyze.update_progress_status(qid, "Started request...", 100, 100)

    # Liftover annotation
    #adagenes.app.run_liftover.perform_liftover_annotation(qid, data_dir, genome_version)

    # Liftover
    #print("Genome ",genome_version,", output ", output_genome_version)
    #if (output_genome_version != '') and (output_genome_version != genome_version):
    #    print("Liftover: ",genome_version," to ",output_genome_version)
    #    liftover(qid, genome_version, output_genome_version, data_dir=data_dir)

    # Transform
    if transform_model is not None:
        transform_data(qid, transform_output_format, transform_model, genome_version=genome_version, data_dir=data_dir)

    # Annotate
    start_time_annotate = time.time()
    if annotate is not None:
        if len(list(annotate.keys())) > 0:

            print("Genome ", genome_version, ", output ", output_genome_version)
            print("annotations ",annotate)
            # if (output_genome_version != '') and (output_genome_version != genome_version):
            #if data_dir is None:
            #    data_dir = adagenes.conf.read_config.__DATA_DIR__
            #data_dir = data_dir + "/" + qid
            #infile = adagenes.app.find_newest_file(data_dir)
            #current_genome_version =
            #if output_genome_version != "hg38":
            #    print("Liftover before annotation: ", genome_version, " to ", output_genome_version)
            #    # liftover(qid, genome_version, output_genome_version, data_dir=data_dir)
            #    liftover(qid, output_genome_version, "hg38", data_dir=data_dir)

            #adagenes.app.annotate.annotate_qid(qid, annotate, genome_version=genome_version, data_dir=data_dir)
            #adagenes.app.annotate.annotate_qid_chunks(qid, annotate, genome_version=genome_version, data_dir=data_dir)
            #adagenes.app.annotate.annotate_qid_chunks_parallel(qid, annotate, genome_version=genome_version, data_dir=data_dir)
            #adagenes.app.app_annotate.annotate_qid_chunks_parallel(qid, annotate, genome_version="hg38",
            #                                                   data_dir=data_dir)
            #pass

            adagenes.app.app_annotate.annotate_qid_db(qid, annotate)
    end_time_annotate = time.time() - start_time_annotate
    print(qid, " Time annotation: ",end_time_annotate, file=stats_outfile)

    # Liftover
    output_genome_version_str = ""
    if output_genome_version =="hg19":
        output_genome_version_str = "GRCh37"
    elif output_genome_version == "t2t":
        output_genome_version_str = "T2T"

    print("Genome ",genome_version,", output ", output_genome_version)
    if (output_genome_version != '') and (output_genome_version != genome_version) and output_genome_version != "hg38":
        print("Liftover: ",genome_version," to ",output_genome_version)
        #liftover(qid, genome_version, output_genome_version, data_dir=data_dir)
        #liftover(qid, "hg38", output_genome_version, data_dir=data_dir)

        #qid = pid
        #adagenes.app.run_liftover.perform_liftover_annotation(qid, data_dir, genome_version)
        progress_msg = "Performing LiftOver to " + output_genome_version_str
        progress_val = 60
        buffer_val = 70
        adagenes.app.app_analyze.update_progress_status(qid, progress_msg, progress_val, buffer_val)
        start_time_liftover = time.time()
        adagenes.app.app_analyze.liftover(qid, genome_version, output_genome_version, data_dir=data_dir)
        end_time_liftover = time.time() - start_time_liftover
        print(qid, " Liftover time: ",end_time_liftover,file=stats_outfile)

    #filter_changed = apply_filter_sort(qid, filter_model, sort_model, data_dir=data_dir, genome_version=output_genome_version)


    # load saved file
    #if filter_changed is False:
    #    filter_file = False
    #else:
    #    filter_file = True
    #print("load processed file ", qid, " ", data_dir,": ",str(filter_file),", ",start_row,"-",end_row)

    variants, max_rows, header_lines, stats = load_file(qid, data_dir, filter_model=filter_model, sort_model=sort_model,
                                                        start_row=start_row, end_row=end_row, genome_version=output_genome_version)

    #print("loaded variants ",variants)

    output_format="vcf"
    if header_lines is not None:
        if len(header_lines) == 1:
            if header_lines[0] == "CSV":
                print("load CSV")
                output_format = "csv"
    else:
        print("Error: could not retrieve header lines")

    #stats = adagenes.app.stats.generate_stats(variants)

    #max_rows = bframe.max_variants
    column_defs, table_data = generate_table_data_from_bframe(variants, max_rows, header_lines,
                                                              genome_version=output_genome_version, output_format=output_format)

    #print("loaded file ", table_data)
    #print("column defs ",column_defs)
    #print("max rows ",max_rows)

    adagenes.app.app_analyze.update_progress_status(qid, "Completed", 100, 100)

    print("return column defs ",column_defs)
    #print("return table data ",table_data)

    stats_outfile.close()

    return column_defs, table_data, max_rows, filter_model, output_genome_version, stats

def analyze_search():

    column_defs = []
    table_data = []

    return column_defs, table_data

