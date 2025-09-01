import os, copy, json
from typing import Dict, List
from pathlib import Path
import random, string
import pandas as pd
import adagenes.conf.read_config as config
import adagenes as ag
import datetime
import adagenes.app.db_client


def copy_sample_file(file, pid, genome_version, data_dir=None):
    outfile_vcf = data_dir + "/" + pid + "/"

    if not os.path.exists(data_dir + "/" + pid):
        os.mkdir(data_dir + "/" + pid)
        print("Created directory: ",data_dir + "/" + pid)

    if file == "sample-vcf":
        sample_file = data_dir + config.sample_file
        sample_outfile = "hg38_somaticMutations.l520.vcf"
    elif file == "sample-protein":
        sample_file = data_dir + config.sample_protein_file
        sample_outfile = "hg38_sample_protein.csv"

    sample_outfile = "1_" + sample_outfile
    #cmd = "cp -v " + sample_file + " " + outfile_vcf
    cmd = "cp -v " + sample_file + " " + outfile_vcf + sample_outfile
    #print(cmd)
    os.system(cmd)

    # add data to database
    bframe = ag.read_file(outfile_vcf + sample_outfile)
    conn = adagenes.app.db_client.DBConn(pid)

    if file == "sample-vcf":
        conn.import_vcf(bframe, pid, genome_version)
    elif file == "sample-protein":
        conn.import_csv(bframe, pid, genome_version)

    conn.close_connection()

    # create filter/sort file
    filter_file = data_dir + "/" + pid + "/" + "active_filter.json"
    sort_file = data_dir + "/" + pid + "/" + "active_sort.json"

    with open(filter_file, 'w') as file:
        file.write(json.dumps({}))

    with open(sort_file, 'w') as file:
        file.write(json.dumps({}))

    # create log file
    logfile = data_dir + "/" + pid + "/" + "log.txt"
    datetime_str = str(datetime.datetime.now())
    annotation_key = "File uploaded "
    string_to_append = annotation_key + "(" + datetime_str + ")::" + outfile_vcf + config.sample_file.split("/")[2] + '\n'
    filepath = logfile
    try:
        with open(filepath, 'a') as file:
            file.write(string_to_append)
        print(f"String appended to {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

def is_vcf(filename, bframe):
    extension = adagenes.get_file_type(filename)
    if extension == "vcf":
        return True
    elif extension == "maf":
        return True

    for var in bframe.data.keys():
        if "CHROM" in bframe.data[var]:
            return True

    return False

def upload_variant_data(
                        file,
                        pid: str,
                        dc,
                        data_dir: str = config.__DATA_DIR__,
                        data_dir_orig: str = None,
                        genome_version=''
                        ) -> str:
    """
    Saves an uploaded variant file within the mounted data directory. Returns the file path of the saved file

    :param file:
    :param pid:
    :return:
    """
    if not os.path.exists(data_dir + "/" + pid):
        os.mkdir(data_dir + "/" + pid)
        print("Created directory: ",data_dir + "/" + pid)

    if file is not None:
        outfile_name = file.filename
        outfile_vcf = data_dir + "/" + pid + "/"+ "1_" + genome_version + '_' + file.filename
        file.save(outfile_vcf)
        bframe = ag.read_file(outfile_vcf, genome_version=genome_version)
        #print("bframe first ",genome_version,": ",bframe.data)

        vcf = is_vcf(file.filename, bframe)
        #print("IS VCF ",vcf)

        conn = adagenes.app.db_client.DBConn(pid)

        if vcf is True:
            conn.import_vcf(bframe, pid, genome_version)
        else:
            #print("IMPORT csv")
            conn.import_csv(bframe, pid, genome_version)

        conn.close_connection()

    # create filter, sort file
    filter_file = data_dir + "/" + pid + "/" + "active_filter.json"
    sort_file = data_dir + "/" + pid + "/" + "active_sort.json"

    with open(filter_file, 'w') as file_log:
        file_log.write(json.dumps({}))

    with open(sort_file, 'w') as file_log:
        file_log.write(json.dumps({}))

    # create log file
    if file is not None:
        logfile = data_dir + "/" + pid + "/" + "log.txt"
        datetime_str = str(datetime.datetime.now())
        annotation_key = "File uploaded "
        string_to_append = annotation_key + "(" + datetime_str + ")::" + outfile_vcf + '\n'
        filepath = logfile
        try:
            with open(filepath, 'a') as file:
                file.write(string_to_append)
            print(f"String appended to {filepath}")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Add biomarkers to database
    #datetime_str = str(datetime.datetime.now())
    #bframe = ag.read_file(outfile_vcf,genome_version=genome_version)
    #print("identified biomarkers: ",list(bframe.data.keys()))

    # Convert variant data on protein level to genomic level
    #bframe = onkopus.ProteinToGenomic().process_data(bframe)
    #variant_data = bframe.data
    #print("prot level data ", variant_data)

    # hg38 transformation
    #if (genome_version == "hg19":
    #    print("liftover: ", genome_version)
    #    variant_data = ag.clients.LiftoverClient(genome_version).process_data(variant_data,target_genome="hg38")
    #    print("keys after liftover: ", variant_data.keys())
    #    #variant_data = adagenes.tools.transform_hg19_in_hg38_bframe(variant_data,genome_version)

    #biomarker_str = ",".join(list(variant_data.keys()) )
    #print("Identified biomarkers: ",biomarker_str)

    #onkopus_server.processing.db_requests.add_biomarkers(data_dir_orig,pid,biomarker_str,datetime_str,genome_version,file.filename)

    #save_uploaded_file(file, data_dir + "/" + pid + "/" + "annotations.json")
    # Add entry to files metadata file
    #file_type = get_file_type(file.filename, type="all")
    #meta_file = data_dir + "/" + pid + "/" + config.__UPLOAD_FILE__
    #print("write metafile ",meta_file)
    #onkopus_server.processing.data_mgt.add_metadata(metadata_file=meta_file,
    #                                    input_file=file.filename, genome_version=genome_version,
    #                                    input_format=file_type)
    repository = data_dir_orig
    patient_id = pid
    datetime_str = str(datetime.datetime.now())
    type_str = "upload"
    event = "File uploaded"
    #onkopus_server.processing.db_requests.add_metadata_entry(repository, patient_id, genome_version,
    #                                                         datetime_str, type_str, event)

    #transform_input_file_to_biomarker_set(pid, data_dir, dc, outfile_name, outfile_vcf, genome_version)



def load_default_id_data(pid, data_dir=None):
    if pid == '':
        # generate new ID if no argument is given
        dc = generate_new_id_files()
        print("new id: ", dc)
    else:
        dc = {
            "id": pid,
            "dir": data_dir + "/" + pid
        }

    return dc

def add_biomarker_file_to_id(file, pid, data_dir, genome_version, file_src=None, id_file=config.__ID_FILE__,
                                 src_dir=None) -> str:
    """
    Uploads a biomarker file and adds it to an existing account. Generates a new account if no ID is passed

    :param file:
    :param pid:
    :param data_dir:
    :param genome_version:
    :param file_src:
    :param id_file:
    :param src_dir:
    :return: pid
    """
    print("data dir ",data_dir)
    data_dir_orig=copy.copy(data_dir)
    #data_dir = get_data_dir(data_dir)
    data_dir = config.__DATA_DIR__
    pid = generate_new_id_data(pid, data_dir=data_dir, data_dir_orig=data_dir_orig,id_file=id_file)
    print("new id generated: ",pid)
    dc = load_default_id_data(pid, data_dir)
    print("upload file for ID ", pid, " data dir ",data_dir)
    if isinstance(file, str):
        if file == "sample-vcf":
            copy_sample_file(file, pid, genome_version, data_dir=data_dir)
        if file == "sample-protein":
            copy_sample_file(file, pid, genome_version, data_dir=data_dir)
    else:
        if file is not None:
            print("Upload variant data")
            upload_variant_data(file, pid, dc, data_dir=data_dir, data_dir_orig=data_dir_orig,genome_version=genome_version)
    #elif file is None:
    #    print("Copy file from host file system")
    #    outfile = get_filename(file_src)
    #    print("outfile ",outfile)
    #    copy_file_from_host_system(file_src, pid, dc, data_dir, data_dir_orig=data_dir_orig, genome_version=genome_version, src_file=src_dir, src_filename=outfile)

    #print("data dir ",data_dir)

    # Variant data section
    #datetime_str = str(datetime.datetime.now())
    #genome_version = "hg38"

    return pid

def generate_new_id_files(
        new_id:str=None,
        id_data: Dict=None,
        data_dir = None,
        id_file = None,
        sep="\t") -> Dict:
    """
    Creates a new account with a given ID, directory structure and metadata

    :param new_id:
    :param it_data:
    :param sep:
    :return:
    """

    if data_dir is not None:
        id_file = data_dir + "/ids.txt"
    else:
        data_dir = config.__DATA_DIR__
        id_file = data_dir + "/" + config.__ID_FILE__

    print("id file ",id_file)
    success = False
    if new_id is None:
        new_id = generate_new_id(id_file=id_file)
        print("generated new id ",new_id)

    assigned_ids = _get_assigned_ids(id_file=id_file)

    # generate directory
    if new_id not in assigned_ids:
        fwrt = open(id_file, 'a')
        print("write new id to: ",id_file)
        fwrt.write('\n' + new_id)
        fwrt.close()

    pdir = data_dir + "/" + new_id
    print("generating new files in ", pdir)
    if not os.path.exists(pdir):
        os.makedirs(pdir)

    # add ID history entry
    #date = get_current_datetime()

    # generate uploads metadata file
    meta_df = pd.DataFrame(data={},
                           columns=['input_file', 'genome_version', 'annotations'])
    meta_df.to_csv(data_dir + '/' + new_id + '/' + config.__UPLOAD_FILE__, index=False, sep='\t')

    # generate patient data file
    feature_file = pdir + "/" + config.__FEATURE_FILE__
    if id_data is not None:
        print("save to file ",feature_file)
        id_data["id"] = new_id
        df = generate_dataframe_from_dict(id_data)
        print("generated df ",df)
        df.to_csv(feature_file, sep=sep)
    else:
        dc = {"id":[new_id]}
        df = generate_dataframe_from_dict(dc)
        df.to_csv(feature_file, sep=sep)

    dc = {}
    dc["id"] = new_id
    dc["dir"] = pdir

    return dc

def setup_id_file(id_file):
    # create ID file if it does not exist
    id_file = Path(id_file)
    if not id_file.exists():
        with open(id_file, 'w') as f:
            pass
        f.close()

def _get_assigned_ids(id_file = None) -> List:
    assigned_ids = []
    print("config file ",id_file)
    setup_id_file(id_file)
    fle = Path(id_file)

    f = open(fle)
    with open(id_file) as my_file:
        for line in my_file:
            assigned_ids.append(line.strip('\n'))
    #assigned_ids = f.readlines()
    f.close()
    return assigned_ids

def generate_new_id(id_file=None, data_dir=None):
    """
    Generates a new patient ID

    :param id_file:
    :return:
    """
    id_generated =False

    if data_dir is None:
        data_dir="loc"
    #pdata = onkopus_server.processing.db_requests.get_ids(data_dir=data_dir)

    if id_file is None:
        id_file = config.__DATA_DIR__ + "/" + config.__ID_FILE__

    assigned_ids = _get_assigned_ids(id_file=id_file)

    while id_generated is False:
        length = random.randint(9, 12)
        #random_source = string.ascii_lowercase + string.digits
        random_source = string.digits
        #new_id = random.choice(string.ascii_lowercase)
        #new_id += random.choice(string.digits)
        new_id = random.choice(string.digits)
        for i in range(length):
            new_id += random.choice(random_source)
        new_id_list = list(new_id)
        random.SystemRandom().shuffle(new_id_list)
        new_id = ''.join(new_id_list)

        # test if ID is already assigned
        if new_id not in assigned_ids:
            id_generated = True

    return new_id

def generate_new_id_data(pid, data_dir=None,data_dir_orig=None,id_file=None, generate_dirs=False):
    """
     Generates a new account and base data structures

     :param pid:
     :param data_dir:
     :param id_file:
     :param generate_dirs:
     :return:
     """
    if (pid is None) or (pid == ''):
        if data_dir_orig is None:
            data_dir_orig="loc"
        pid = generate_new_id(id_file=id_file,data_dir=data_dir_orig)
        print("new id: ",pid)
        #onkopus_server.processing.data_mgt.generate_new_id_files(new_id=pid, data_dir=data_dir)
        #datetime_str = str(datetime.datetime.now())
    elif generate_dirs is True:
        generate_new_id_files(new_id=pid, data_dir=data_dir)
    return pid

def generate_dataframe_from_dict(dc):
    df = pd.DataFrame.from_dict(dc, orient="index")
    return df

