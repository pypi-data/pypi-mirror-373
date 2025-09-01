import subprocess
import datetime
import traceback
from multiprocessing import Pool, cpu_count
import onkopus as op
import adagenes as ag
from adagenes.app.app_io import find_newest_file, load_log_actions, append_to_file, split_filename
import adagenes.conf
import os
import json # for parsing the dict data
import multiprocessing
import adagenes.app.app_tools
import adagenes.app.db_client
import adagenes.app.app_analyze
import time
import pymongo


expected_n_files_dict = {} # global variable

def modify_global_expected_n_files_dict(key, value):
    '''
    modify the global variable expected_n_files_dict- add a key key with value value in the expected_n_files_dict
    '''
    global expected_n_files_dict  # Declare that we are using the global variable
    expected_n_files_dict[key] = value  # Modify the global variable

def update_file(key, value):
    data_dir = adagenes.conf.read_config.__DATA_DIR__
    file_path = data_dir + "/dict.json"
    with open(file_path, "r") as data:
        dictionary = json.load(data)
    dictionary[key]= value
    print(dictionary)
    with open(file_path, "w") as file:
        json.dump(dictionary, file, indent=4)



def get_magic_obj(key, genome_version, transform_model = None):
    if key == "clinvar":
        return op.ClinVarClient(genome_version=genome_version)
    elif key == 'protein':
        return [op.UTAAdapterClient(genome_version=genome_version), op.GENCODECNAClient(genome_version=genome_version)]
    elif key == 'protein-to-gene':
        return op.CCSGeneToGenomicClient(genome_version=genome_version)
    elif key == 'transcripts':
        return op.GENCODEGenomicClient(genome_version=genome_version)
    elif key == 'dbsnp':
        return op.DBSNPClient(genome_version=genome_version)
    elif key == 'patho':
        return op.DBNSFPClient(genome_version=genome_version)
    elif key == 'molecular':
        return op.MolecularFeaturesClient(genome_version=genome_version)
    elif key == 'proteinfeatures':
        return op.ProteinFeatureClient(genome_version=genome_version)
    elif key == 'geneexpression':
        return op.GeneExpressionClient()
    elif key == 'proteinseq':
        return op.UTAAdapterProteinSequenceClient(genome_version=genome_version)
    elif key == 'functionalregions':
        return op.GENCODEGenomicClient(genome_version=genome_version)
    elif key == 'drug-gene-interactions':
        return op.DGIdbClient(genome_version=genome_version)
    elif key == 'clinical-evidence':
        return op.ClinSigClient(genome_version=genome_version)
    elif key == 'filter_text':
        return ag.TextFilter()
    elif key == 'filter_number':
        return ag.NumberFilter()
    elif key == 'hgvs':
        return ag.HGVSClient(genome_version=genome_version)
    elif key == 'transform-vcf':
        return ag.VCFTransformator(transform_model)
    else:
        return None


def annotate_qid(qid: str, annotations: dict, genome_version=None, data_dir=None,
                 output_format='vcf',
                 mapping=None):
    """
    Annotate variant data with selected filters, and stores the annotated data in a new file

    :param qid:
    :param annotations: Dictionary containing annotations as keys and true if the annotation should be performed, e.g. { 'clinvar' true, 'protein': true }
    :param genome_version:
    :param data_dir:
    :param output_format:
    :return:
    """

    annotation_requirements = {
        "transcripts": ["protein"]
    }

    print("Annotations ",annotations)
    print(qid)
    print(data_dir)
    if data_dir is None:
        data_dir = adagenes.conf.read_config.__DATA_DIR__
    data_dir = data_dir + "/" + qid
    logfile = data_dir + '/log.txt'

    for key in annotations.keys():
        if annotations[key]:
            print("Annotate: ", key, " ", qid)


            infile = find_newest_file(data_dir)
            if qid == "sample-vcf": # TO DO : this should not work - with multiple annotations there should be problems?
                infile= data_dir + ag.conf_reader.sample_file
            if qid == "sample-protein":
                infile= data_dir + ag.conf_reader.sample_protein_file

            #infile = split_filename(infile)
            infile_name = split_filename(infile)

            previous_actions = load_log_actions(logfile)
            print("loaded logfile ",logfile)
            print("previous actions: ",previous_actions)

            annotation_key = 'Annotation:'+key
            contains_substring = any(annotation_key in entry for entry in previous_actions)
            if contains_substring is False:
                datetime_str = str(datetime.datetime.now())
                print("infile ",infile)
                output_format = output_format.lstrip(".")
                outfile = infile_name + ".ann."  + datetime_str + "." + output_format
                outfile = outfile.replace(" ", "_")
                outfile = outfile.replace(":", "-")

                magic_obj = get_magic_obj(key, genome_version)
                print("annotate with magic obj ",magic_obj, " mapping ",mapping)
                ag.process_vcf(qid, magic_obj, mapping=mapping)

                append_to_file(logfile, annotation_key + "(" + datetime_str + ")::" + outfile + '\n')

                print("File annotated: ",outfile)
            else:
                print("Annotation already found: ",annotation_key)


    # Generate new column definitions:
    #, cellClass: "rag-blue"


def build_file_name(base_name, annotation, file_count):
    return f"{base_name}_{annotation}_{file_count}.vcf"

def split_large_file(input_file, base_name, stage_name, lines_per_file=2500):
    """
    Splits a large file into multiple smaller files, each containing a specified number of lines - less than lines_per_file

    :param input_file: Path to the input file.
    :param base_name: Base name base don the input_file name
    :param stage_name: Name of the stage, ususally "start"
    :param lines_per_file: Number of lines per output file (default is 2500).

    return the names of the small files
    """
    output_files = []
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            file_count = 1
            lines = []

            for line in infile:
                lines.append(line)
                if len(lines) >= lines_per_file:
                    output_file = build_file_name(base_name, stage_name, file_count)
                    with open(output_file, 'w', encoding='utf-8') as outfile:
                        outfile.writelines(lines)
                    print(f"Created {output_file}")
                    file_count += 1
                    lines = []
                    output_files.append(output_file)

            # Write remaining lines if any
            if len(lines) > 0:
                output_file = build_file_name(base_name, stage_name, file_count)
                with open(output_file, 'w', encoding='utf-8') as outfile:
                    outfile.writelines(lines)
                print(f"Created {output_file}")
                output_files.append(output_file)
            else:
                # reduce the number of files for 1, so that the file_count is how many new files were made
                file_count = file_count -1
        return output_files, file_count
    except Exception as e:
        print(f"Error: {e}")

def needed_annotations(annotations, logfile):
    '''
    For a annotation dictionary: remove the annotation keys of the annotations that were already done
    TO DO: this function could be probably cleaned? When is false in dict?
    '''

    previous_actions = load_log_actions(logfile)
    print("loaded logfile ", logfile)
    print("previous actions: ", previous_actions)

    new_annotations = {}
    for key in annotations.keys():
        if annotations[key]:
            annotation_key = 'Annotation:' + key
            contains_substring = any(annotation_key in entry for entry in previous_actions)
            if contains_substring is False:
                new_annotations[key] = True
            else:
                print("Annotation already found: ", annotation_key)
    return new_annotations

def merge_files(outfile, n_chunks, last_step, base_name):
    """
    Merges multiple small files back into a single file.

    :param outfile: Path to the merged file at the ned
    :param n_chunks: Number of chunks, which were processed with all annotations
    :param last_step: the name of the last step - which word is used in the naming of the  output files
    :param base_name: the base name of the original file
    """
    print(outfile, n_chunks, last_step, base_name)
    try:
        with open(outfile, 'w', encoding='utf-8') as outfile:
            for n in range(1, n_chunks+1):
                file_name = build_file_name(base_name, last_step, n)
                with open(file_name, 'r', encoding='utf-8') as infile:
                    outfile.writelines(infile.readlines())
        print(f"Merged files into {outfile}")
    except Exception as e:
        print(f"Error while merging files: {e}")

def get_base_file_name(infile):
    if ".vcf" in infile:
        original_name = "".join(infile.split(".")[:-1])
    else:
        original_name = infile
    return original_name

def get_annotation_steps(annotations, start = "start"):
    '''
    Order the annotation keys  the first should be start, then protein (SeqCAT) - if it is inside
    TO DO: SeqCAt should be added in some cases?
    Args:
        annotations: dictionary with annotation names as keys
        start: the name of the starting phase - how the chunks of input file are named

    Returns:

    '''
    annotation_stages = [start]
    if "protein" in annotations:
        annotation_stages.append("protein")
        del annotations["protein"]
    annotation_stages = annotation_stages+ list(annotations.keys())
    print("Ordered annotation stages", annotation_stages)
    return annotation_stages

def annotate_one_file(annotation_key, qid, genome_version, mapping, original_name, number, prev_step):
    '''
    Calculate the name of the input file and then process it with the service named "annotation_key" and save the result in the calculated outfiel
    Args:
        annotation_key: annotation key - which annotation should be done
        genome_version:
        mapping:
        original_name: original name of the input file - without .vcf at the end
        number: the "chunk" number - which ofthe chunks should be used?
        prev_step: which step was beforehand? it should be "start" or the name of the previous annotation
    '''

    input_file = build_file_name(original_name, prev_step, number)
    outfile = build_file_name(original_name, annotation_key, number) # original_name + "_" + annotation_key + "_" + number + ".vcf"

    magic_obj = get_magic_obj(annotation_key, genome_version)
    #print("annotate with magic obj ", magic_obj, " mapping ", mapping)
    ag.process_vcf(qid, magic_obj, mapping=mapping)

    print("file_number", number, "with annotation", annotation_key, "File annotated: ", outfile)

def execute_annotations_for_file(number, steps, genome_version, mapping, original_name, qid):
    '''
    Args:
        pool:
        number: number of the file chunk - identifier for input and output file
        steps:
        genome_version:
        mapping:
        n_step:
        original_name:

    Returns:

    '''
    for n_step in range(1, len(steps)):
          annotate_one_file(steps[n_step], qid, genome_version, mapping, original_name, number, steps[n_step-1])


def generate_outfile_name(infile_name):
    infile_name = infile_name.replace("_processed", "")
    outfile_name = infile_name + "_processed.vcf"
    new_file_name = adagenes.app.app_tools.increment_file_number(outfile_name, increase_count=True)
    return new_file_name

def parallel_requests(annotated_data, genome_version,modules, run=0, oncokb_key=None, include_clinical_data=True):

    start_time=time.time()

    thread_list = []

    if run == 0:
        if "protein" in modules:
            task = op.UTAAdapterClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "patho" in modules:
            task = op.DBNSFPClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "dbsnp" in modules:
            task = op.DBSNPClient(genome_version=genome_version).process_data
            thread_list.append(task)
    elif run == 1:
        if "clinvar" in modules:
            task = op.ClinVarClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "hgvs" in modules:
            task = ag.HGVSClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "molecular" in modules:
            task = op.MolecularFeaturesClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "proteinfeatures" in modules:
            task = op.ProteinFeatureClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "geneexpression" in modules:
            task = op.GeneExpressionClient().process_data
            thread_list.append(task)
        if "drug-gene-interactions" in modules:
            task = op.DGIdbClient(genome_version=genome_version).process_data
            thread_list.append(task)
        if "proteinseq" in modules:
            task = op.UTAAdapterProteinSequenceClient(genome_version=genome_version).process_data
            thread_list.append(task)

    #task1 = onkopus.onkopus_clients.UTAAdapterClient(genome_version=genome_version).process_data
    #task2 = onkopus.onkopus_clients.DBNSFPClient(genome_version=genome_version).process_data

    task_list = []
    #t1 = adagenes.app.app_tools.ThreadWithReturnValue(target=task1, args=[annotated_data])
    #t2 = adagenes.app.app_tools.ThreadWithReturnValue(target=task2, args=[annotated_data])

    for thread in thread_list:
        task_list.append(adagenes.app.app_tools.ThreadWithReturnValue(target=thread, args=[annotated_data]))

    for task in task_list:
        task.start()
        #t1.start()
        #t2.start()

    data_list = []
    #data1 = t1.join()
    #data2 = t2.join()
    for task in task_list:
        data = task.join()
        data_list.append(data)

    print("Merging dicts...")
    start_time_merge = time.time()
    for thread_data in data_list:
        annotated_data = adagenes.merge_dictionaries(annotated_data, thread_data)
    end_time_merge = time.time() - start_time_merge
    print("Merge time ",end_time_merge)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data1)
    #annotated_data = adagenes.merge_dictionaries(annotated_data, data2)

    stop_time = time.time() - start_time
    print("Time for parallel annotation requests: ", stop_time)

    return annotated_data

#def annotate_qid_db(qid, annotate):
def process_batch(batch, file_id, annotations, genome_version, mapping, batch_size,update_annotation_progress, transform):

    print("Add annotations ",annotations)
    updated_documents = []
    #for doc in batch:
    # load variant in bframe
    #print("doc data ",batch)
    #vcf_data, orig_ids = adagenes.app.db_client.load_bframe_from_db_data(batch, "hg38", mapping=mapping)
    vcf_data, orig_ids = adagenes.app.db_client.load_bframe_from_db_data(batch, genome_version, mapping=mapping)

    #print("batch ",vcf_data.keys())
    #print("process batch ",len(list(vcf_data.keys())))

    conn = adagenes.app.db_client.DBConn(file_id)

    start_time = time.time()

    # first annotation
    magic_obj_list = []
    module_list = []
    start_time_anno0=time.time()
    if "protein" in annotations:
        module_list.append("protein")
        #magic_obj_list.append(op.UTAAdapterClient(genome_version=genome_version))
    if "patho" in annotations:
        module_list.append("patho")
        magic_obj_list.append(op.DBNSFPClient(genome_version=genome_version))
    if "dbsnp" in annotations:
        module_list.append("dbsnp")
        magic_obj_list.append(op.DBSNPClient(genome_version=genome_version))
    #if "protein-to-gene" in annotations:
    #    module_list.append("protein-to-gene")
    #    magic_obj_list.append(op.CCSGeneToGenomicClient(genome_version=genome_version, data_type="p"))
    vcf_data = parallel_requests(vcf_data, genome_version, module_list, run=0, oncokb_key=None, include_clinical_data=True)
    print("time anno0 ",time.time()-start_time_anno0)
    if len(list(vcf_data.keys())) > 0:
        print("batch ",list(vcf_data.keys())[0],", update 1")
        conn.update_vcf(vcf_data, genome_version, magic_obj_list)
    else:
        print("empty batch, update 1")


    # second annotation
    magic_obj_list = []
    module_list = []
    start_time_anno01=time.time()
    if "clinvar" in annotations:
        module_list.append("clinvar")
        magic_obj_list.append(op.ClinVarClient(genome_version=genome_version))
    if "hgvs" in annotations:
        magic_obj_list.append(ag.HGVSClient(genome_version=genome_version))
        module_list.append("hgvs")
    if "molecular" in annotations:
        magic_obj_list.append(op.MolecularFeaturesClient(genome_version=genome_version))
        module_list.append("molecular")
    if "proteinfeatures" in annotations:
        magic_obj_list.append(op.ProteinFeatureClient(genome_version=genome_version))
        module_list.append("proteinfeatures")
    if "geneexpression" in annotations:
        magic_obj_list.append(op.GeneExpressionClient())
        module_list.append("geneexpression")
    if "drug-gene-interactions" in annotations:
        magic_obj_list.append(op.DGIdbClient(genome_version=genome_version))
        module_list.append("drug-gene-interactions")
    if "proteinseq" in annotations:
        magic_obj_list.append(op.UTAAdapterProteinSequenceClient(genome_version=genome_version))
        module_list.append("proteinseq")
    vcf_data = parallel_requests(vcf_data, genome_version, module_list, run=1, oncokb_key=None,
                                 include_clinical_data=True)

    end_time_anno1=time.time()-start_time_anno01
    print("time anno1 ",end_time_anno1)
    if len(list(vcf_data.keys())) > 0:
        print("batch ", list(vcf_data.keys())[0], ", update 2")
        conn.update_vcf(vcf_data, genome_version, magic_obj_list)
    else:
        print("empty batch, update 2")


    end_time = time.time() - start_time
    print("Batch annotation time: ",end_time)

    # annotate batch
    #print("Batch annotations: ",annotations, " genome version ",genome_version)
    #for annotation_key in annotations:
    #    magic_obj = get_magic_obj(annotation_key, genome_version)
    #    print("Annotate batch ", list(vcf_data.keys())[0], " with ",magic_obj)
    #    if not isinstance(magic_obj, list):
    #        vcf_data = adagenes.process_vcf(file_id, magic_obj, vcf_data=vcf_data, genome_version="hg38", conn=conn, transform=transform)
    #    else:
    #        for mobj in magic_obj:
    #            vcf_data = adagenes.process_vcf(file_id, mobj, vcf_data=vcf_data, genome_version="hg38", conn=conn, transform=transform)


    # regenerate orig ids

    # update processing status
    update_annotation_progress(conn, file_id, batch_size)
    print("Progress updated")

    conn.close_connection()
    #print("Batch completed ",list(vcf_data.keys())[0])


def extract_info_ids(vcf_header_lines):
    info_ids = []

    if vcf_header_lines is not None:
        for line in vcf_header_lines:
            if line.startswith("##INFO="):
                # Extract the ID part from the INFO line
                start_index = line.find("ID=") + 3
                end_index = line.find(",", start_index)
                if end_index == -1:
                    end_index = line.find(">", start_index)
                info_id = line[start_index:end_index]
                info_ids.append(info_id)

    return info_ids

def get_new_annotations(annotations, existing_annotations):
    """

    :param annotations:
    :param existing_annotations:
    :return:
    """

    # get new annotations
    #print("existing annotations ",existing_annotations," new annotations: ",annotations)
    anno_mapping = {"dbnsfp": "patho", "uta": "protein", "proteinseq":"proteinseq", "gtex":"geneexpression",
                    "dgidb":"drug-gene-interactions","protein_features":"proteinfeatures"}

    existing_annotations_list = []
    for anno in existing_annotations:
            underscore_index = anno.find('_')
            if underscore_index != -1 or anno == 'protein_features_RSA':
                first_part = anno[:underscore_index]

                if anno =="UTA_Adapter_protein_sequence_protein_sequence":
                    anno = "proteinseq"
                elif anno == 'protein_features_RSA':
                    anno = "protein_features"
                else:
                    anno = first_part.lower()

                if anno in anno_mapping.keys():
                    existing_annotations_list.append(anno_mapping[anno])
                else:
                    existing_annotations_list.append(anno)

    #print("existing annotations list ",existing_annotations_list)
    new_annotations = []
    for anno in annotations.keys():
        if annotations[anno] is True:
            if anno not in existing_annotations_list:
                new_annotations.append(anno)

    # sort new annotations
    new_annotations = list(set(new_annotations))

    if "protein" in new_annotations:
        #protein_index = next((i for i, x in enumerate(new_annotations) if 'protein' in x), None)
        #if protein_index is not None:
        #    new_annotations.insert(0, new_annotations.pop(protein_index))
        newa = []
        newa.append("protein")
        for anno in new_annotations:
            if anno != "protein":
                newa.append(anno)
        new_annotations = newa

    print("add new annotations: ", new_annotations)

    return new_annotations

def update_annotation_progress(conn, file_id, total_batches):
    """
    Update the progress in the MongoDB database.
    """

    # get current progress
    result = adagenes.app.app_analyze.get_progress_status(file_id)
    #print("progress ",result)
    progress = int(result["progress"])

    # write updated progress to database
    my_progress = int(100 / total_batches)
    progress += my_progress

    progress_msg = "Annotating variants"
    progress_val = progress
    buffer_val = progress + 10
    adagenes.app.app_analyze.update_progress_status(file_id, progress_msg, progress_val, buffer_val)

    #progress = (batch_id + 1) / total_batches * 100
    #collection.update_one(
    #    {'_id': 'progress'},
    #    {'$set': {'progress': progress}},
    #    upsert=True
    #)
    #print(f"Progress: {progress:.2f}%")

def generate_new_header_lines(file_id, mapping=None):
    conn = adagenes.app.db_client.DBConn(file_id)

    conn.generate_new_header_lines(mapping)

    conn.close_connection()

def annotate_qid_db(file_id, annotations, batch_size=5000,mapping=None, transform=False):
    start_time = time.time()
    conn = adagenes.app.db_client.DBConn(file_id)

    # get genome version
    genome_version, header_lines = conn.get_header(conn.db, file_id)
    #print("header ",genome_version,": ",header_lines)
    annotation_ids = extract_info_ids(header_lines)

    new_annotations = get_new_annotations(annotations, annotation_ids)
    #print("new annotations: ",new_annotations," old: ",annotations)
    new_fields = []

    if len(new_annotations)>0:
        # Initialize a cursor with the desired batch size
        #cursor = collection.find().batch_size(batch_size)
        cursor = conn.collection.find(batch_size=batch_size)

        batches = []
        batch = []
        for doc in cursor:
            #print("batch doc ",doc)
            batch.append(doc)
            if len(batch) == batch_size:
                batches.append(batch)
                batch = []
        if batch:
            batches.append(batch)

        print("processes ",cpu_count())
        print("batches ",len(batches))

        progress_msg = "Annotating variants"
        progress_val = 0
        buffer_val = 10
        adagenes.app.app_analyze.update_progress_status(file_id, progress_msg, progress_val, buffer_val)

        # update header lines
        for annotation_key in new_annotations:
            magic_obj = get_magic_obj(annotation_key, genome_version)
            if not isinstance(magic_obj, list):
                conn.update_header_lines(file_id, magic_obj.info_lines)
            else:
                for mobj in magic_obj:
                    conn.update_header_lines(file_id, mobj.info_lines)

            #annotation_keys = mobj.info_lines

        # update annotations
        if transform is False:
            conn.update_annotations(file_id, new_annotations)

        conn.client.close()

        # Use multiprocessing to process batches in parallel
        print("Starting ",len(batches), " batches")
        with Pool(processes=cpu_count()) as pool:
            pool.starmap(process_batch, [(batch, file_id, new_annotations, genome_version, mapping, len(batches),update_annotation_progress,transform) for batch in batches])
            pool.close()
            pool.join()
        print("processing finished")
    else:
        print("No new annotations added. Skipping annotation requests.")

    # Build indices for new annotation features
    conn = adagenes.app.db_client.DBConn(file_id)
    print("Generating indexes....",new_annotations)
    start_time_index_gen = time.time()

    for annotation in new_annotations:
        magic_obj = get_magic_obj(annotation, genome_version=genome_version)
        if isinstance(magic_obj,list):
            for mobj in magic_obj:
                fields = adagenes.app.app_tools.get_ids(mobj.info_lines)
                if fields is not None:
                    for field in fields:
                        if field not in new_fields:
                            new_fields.append(field)
        else:
            mobj = magic_obj
            fields = adagenes.app.app_tools.get_ids(mobj.info_lines)
            if fields is not None:
                for field in fields:
                    if field not in new_fields:
                        new_fields.append(field)

    print("Generate feature indices for ",new_fields)
    max_indices = 61
    print("Add ",len(new_fields), " new indices")
    for i,key in enumerate(new_fields):
        if i < max_indices:
            try:
                conn.collection.create_index([(key, pymongo.ASCENDING)], background=True)
            except:
                print(traceback.format_exc())
    #print("Index generation done")

    #print("Update complete.")
    conn.close_connection()
    end_time_index_gen = time.time() - start_time_index_gen

    end_time = time.time() - start_time
    print("Time for whole annotation: ",end_time)
    print("Time for feature index generation: ",end_time_index_gen)


def annotate_qid_chunks_parallel(qid: str, annotations: dict, genome_version=None, data_dir=None,
                 output_format='vcf',
                 mapping=None, lines_per_file = 2500):
    """
    Annotate variant data with selected filters, and stores the annotated data in a new file
        - with splitting the file in smaller files
    :param qid:
    :param annotations: Dictionary containing annotations as keys and true if the annotation should be performed, e.g. { 'clinvar' true, 'protein': true }
    :param genome_version:
    :param data_dir:
    :param output_format:
    :return:
    """

    annotation_requirements = {
        "transcripts": ["protein"]
    }

    print("Annotations ",annotations)
    print(qid)
    print(data_dir)
    if data_dir is None:
        data_dir = adagenes.conf.read_config.__DATA_DIR__
        data_dir = data_dir + "/" + qid
    logfile = data_dir + '/log.txt'

    # input_file is the file that was changed the last in the data_dir
    infile = find_newest_file(data_dir)
    print("Newest file ",infile)
    if qid == "sample-vcf": # TO DO check if it can be deleted
        infile = data_dir + ag.conf_reader.sample_file
    if qid == "sample-protein":
        infile = data_dir + ag.conf_reader.sample_protein_file

    # get the current number of files in the directory
    starting_n_of_files = len([name for name in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, name))])

    # take care of the naming of temp files
    original_name= get_base_file_name(infile)

    # split file in chunks
    # the files will be kept in chunks and processed in every chunk, then afterwards the files will be combined
    # the files are named like: [original_name_might_have_underscores]_[start/annotation_key]_[chunk_part].vcf
    files_names, file_count = split_large_file(infile, original_name, "start", lines_per_file=lines_per_file)

    # clean the annotations - delete the entries that have the value false
    #new_annotations = needed_annotations(annotations, logfile)
    new_annotations = annotations
    print("Needed annotations: ", new_annotations)

    # prepare the dictionary: to get the name of the outputfile for the input file

    # calculate the expected number of files
    expected_n_files = file_count * (len(new_annotations.keys())+1) + starting_n_of_files + 1  # +1: output file
    modify_global_expected_n_files_dict(qid, expected_n_files)
    update_file(qid, expected_n_files)
    print(expected_n_files_dict)

    # organise annotations in the ordered list, first is "start", then annotations follow
    steps = get_annotation_steps(new_annotations, start = "start")

    # process the files with annotations with parellel executions across different files, but sequential executing for annotations for one file
    with multiprocessing.Pool() as pool:
        pool.starmap(execute_annotations_for_file, [(n, steps, genome_version, mapping, original_name,qid) for n in range(1, file_count +1)])

    # collect the files together again
    # TO DO: get the names of the output files! - in the correct order!
    outfile_name =  generate_outfile_name(original_name)
    merge_files(outfile_name, file_count, steps[-1], original_name)

    # add information about processing to the log file
    datetime_str = str(datetime.datetime.now())
    #append_to_file(logfile, "Annotation:" + ",Annnotation:".join(annotations.keys()) + qid + "(" + datetime_str + ")::" + outfile_name + '\n')
    append_to_file(logfile, "Annotation:" + ",Annotation:".join(
        annotations.keys()) + "(" + datetime_str + ")::" + outfile_name + '\n')

    # update annotations file
    anno_file = data_dir + "/annotations.txt"

    ## increment file number
    #most_annotated_file = adagenes.app.io.find_newest_file(data_dir, filter=False)
    #print("Update annotated file name: ", most_annotated_file)
    #symlink_file = adagenes.app.tools.update_filename_with_current_datetime(most_annotated_file, action="processed",
    #                                                                        increase_count=True)
    #cmd = ["ln", "-sv", most_annotated_file, symlink_file]
    # print(cmd)
    #subprocess.run(cmd)


