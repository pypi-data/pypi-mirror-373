
import os, traceback
from typing import Dict, List
from pathlib import Path
import datetime
import pandas as pd
import string, random, re
from os.path import exists
from adagenes.conf import read_config as config
from adagenes.tools.log import get_current_datetime


def setup():
    from pathlib import Path

    print("Database setup")
    print("Store data in ",config.__DATA_DIR__)
    print("Store temporary data in ",config.__DATA_DIR_PUB__)
    print("Store Onkopus system messages in ",config.__DATA_DIR_SYS__)

    try:
        # create directories if not present
        path = Path(config.__DATA_DIR__)
        if not os.path.isdir(path):
            path.mkdir(parents=True)
        path = Path(config.__DATA_DIR_PUB__)
        if not os.path.isdir(path):
            path.mkdir(parents=True)
        path = Path(config.__DATA_DIR_SYS__)
        if not os.path.isdir(path):
            path.mkdir(parents=True)
    except:
        print("file error")
        print(traceback.format_exc())

    try:
        # create ID file if it does not exist
        id_file = Path(config.__ID_FILE__)
        if not id_file.exists():
            with open(config.__ID_FILE__, 'w') as f:
                pass
            f.close()

        # create public ID file if it does not exist
        id_file = Path(config.__ID_FILE_PUB__)
        if not id_file.exists():
            with open(config.__ID_FILE_PUB__, 'w') as f:
                pass
            f.close()
    except:
        print("Error generating default ID files")
        print(traceback.format_exc())

def annotation_performed(df, id,data_dir,module,sep='\t'):
    #metafile = pd.read_csv(data_dir + '/' + id + '/' + config.__UPLOAD_FILE__, header=0, sep=sep)
    metafile = df
    metafile = metafile.astype(str)

    print("load metafile annotations ",metafile)
    performed_annotations = metafile.iloc[ metafile.shape[0]-1,2].split(';')
    print("annos ",performed_annotations)

    genome_version = metafile.iloc[ metafile.shape[0]-1, 1 ]
    print("preliminary genome version ",genome_version)

    if module in performed_annotations:
        print("module already annotated ",module)
        return True,";".join(performed_annotations), genome_version, metafile
    else:
        return False,";".join(performed_annotations), genome_version, metafile


def locate_newest_vcf_file_regex(base_path: str, extensions:List=None) -> str:
    """
    Locates the newest file in a directory based on the timestamp included in the filename

    :param base_path:
    :param extensions:
    :return:
    """

    #if exists(base_path + "/annotated.vcf"):
    #    return "annotated.vcf"

    if extensions is None:
        variant_extensions = ['.vcf','.annotated']

    print("locate ",base_path)

    #timestamp_reg = "([a-zA-Z]*)_([0-9\-\:_]*)"
    #timestamp_reg = "([a-zA-Z]*)_([0-9][0-9][0-9][0-9])-([0-9]+)-([0-9]+)_([0-9]+):([0-9]+):([0-9]+)"
    timestamp_reg = "([a-zA-Z]*)_([0-9][0-9][0-9][0-9])-([0-9]+)-([0-9]+)_([0-9]+):([0-9]+):([0-9]+)"
    p = re.compile(timestamp_reg)

    f = []
    timestamps = {}
    for (dirpath, dirnames, filenames) in os.walk(base_path):
        for file in filenames:
            filename, file_extension = os.path.splitext(file)
            print(file_extension)
            if file_extension.lower() in variant_extensions:
                f.append(file)

                try:
                    #timestamp = p.match(file).group(2)
                    groups = p.match(file)
                    print("groups ", groups.groups())
                    dt = datetime.datetime( int(groups.group(2)),int(groups.group(3)),int(groups.group(4)),
                                            int(groups.group(5)),int(groups.group(6)),int(groups.group(7)) )
                    timestamps[dt] = file
                except:
                    print("error retrieving timestamp")
                    print(traceback.format_exc())

    # identify newest datetime
    print("files: ",f)
    print("timestamps: ",timestamps)
    newest = max(timestamps.keys())
    print("newest ",newest)

    #newest_variant_file = f[timestamps.index(newest)]
    newest_variant_file = timestamps[newest]
    print("newest file ",newest_variant_file)

    return newest_variant_file

def read_data_from_file(input_file):
    current_dir = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    file_full_path = current_dir+input_file
    with open(file_full_path, 'r') as f:
        data = f.read()
    return data

def _get_assigned_ids(id_file = config.__ID_FILE__) -> List:
    assigned_ids = []
    fle = Path(id_file)
    f = open(fle)
    with open(id_file) as my_file:
        for line in my_file:
            assigned_ids.append(line.strip('\n'))
    #assigned_ids = f.readlines()
    f.close()
    return assigned_ids

def get_id_features(id):
    # get feature data
    pass

def get_id_variants(id):
    pass

def get_id_history(id):
    pass

def update_patient_data(id:str=None,patient_data=None, sep="\t") -> bool:
    """

    :param id:
    :param patient_data:
    :param sep:
    :return:
    """
    pdir = config.__DATA_DIR__ + "/" + id
    if patient_data is not None:
        feature_file = pdir + "/" + config.__FEATURE_FILE__
        df = generate_dataframe_from_dict(patient_data)
        df.to_csv(feature_file, sep=sep)

def generate_new_patient_data_pub(new_id:str=None, genome_version:str='hg38'):
    """
    Generates a new patient data structure in the Onkopus public directory

    :param new_id:
    :return:
    """
    print("generate patient ID in public directory")
    generate_new_patient_data(new_id=new_id, data_dir=config.__DATA_DIR_PUB__, id_file=config.__ID_FILE_PUB__, genome_version=genome_version)

def add_metadata(
        metadata_file:str=None,
        input_file:str=None,
        input_format='vcf',
        genome_version:str=None,
        module=""
    ):
    if Path(metadata_file).exists():
        df = pd.read_csv(metadata_file, sep='\t')
    else:
        df = pd.DataFrame(columns=["input_file",'input_format',"genome_version","annotations"])
    df = pd.concat([df,
               pd.DataFrame({ 'input_file': [input_file], 'input_format': [input_format], 'genome_version': [genome_version], 'annotations': [module] })], axis=0)
    #print("write new meta table ",df)
    #print("write meta information to ",metadata_file)

    df.to_csv(metadata_file,header=True, index=False, sep='\t')

def add_metadata_str(
        metadata_file:str=None,
        datetime:str=None,
        module:str=None,
        module_version:str=None,
        request:str = None,
        input_file:str=None,
        output_file:str=None
                 ):
    """
    Adds metadata to a specific ID. Generates a new file if no data is present yet.

    Returns
    -------

    """
    line = datetime + "\t" + module + "\t" + module_version + "\t" + request + "\t" + input_file + "\t" + output_file + "\n"
    with open (metadata_file, 'a') as f:
        f.write(line)
    f.close()

def generate_new_patient_data(
        new_id:str=None,
        patient_data: Dict=None,
        data_dir = config.__DATA_DIR__,
        id_file = config.__ID_FILE__,
        sep="\t",
        genome_version:str='hg38') -> Dict:
    """
    Creates a new account for a patient with a given ID, directory structure and patient data

    :param new_id:
    :param patient_data:
    :param sep:
    :return:
    """
    print("id file ",id_file)
    success = False
    if new_id is None:
        new_id = generate_new_id(id_file=id_file)
        print("generated new id ",new_id)

    assigned_ids = _get_assigned_ids(id_file=id_file)

    # generate directory
    if new_id not in assigned_ids:
        #with open(config.__ID_FILE__, 'a') as file:
        #    file.write('\n' + new_id)
        fwrt = open(id_file, 'a')
        print("write new id to: ",id_file)
        #fwrt.writelines(['\n' + new_id])
        fwrt.write('\n' + new_id)
        fwrt.close()

    #pdir = config.__DATA_DIR__ + "/" + new_id
    pdir = data_dir + "/" + new_id
    if not os.path.exists(pdir):
        os.makedirs(pdir)

    # add ID history entry
    date = adagenes.tools.log.get_current_datetime()
    msg = "Created new account"
    add_history_entry(new_id, date, msg,data_dir=data_dir)

    # generate uploads metadata file
    meta_df = pd.DataFrame(data={},
                           columns=['input_file', 'genome_version', 'annotations'])
    meta_df.to_csv(data_dir + '/' + new_id + '/' + config.__UPLOAD_FILE__, index=False, sep='\t')

    # generate metadata file
    meta_df = pd.DataFrame(data={}, columns=['datetime','module','module_version','request','input_file','output_file'])
    meta_df.to_csv( data_dir + '/' + new_id + '/' + config.__META_FILE__, index=False, sep='\t')

    # generate patient data file
    feature_file = pdir + "/" + config.__FEATURE_FILE__
    if patient_data is not None:
        print("save to file ",feature_file)
        patient_data["id"] = new_id
        df = generate_dataframe_from_dict(patient_data)
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

def generate_dataframe_from_dict(dc):
    df = pd.DataFrame.from_dict(dc)

    return df

def get_patients(sep="\t"):
    """

    :param sep:
    :return:
    """
    # get patient IDs
    assigned_ids = []
    fle = Path(config.__ID_FILE__)
    fle.touch(exist_ok=True)

    assigned_ids = _get_assigned_ids()
    print("assigned ids: ",assigned_ids)

    pdata = []
    for id in assigned_ids:
        patient_file = config.__DATA_DIR__ + "/" + id + "/" + config.__FEATURE_FILE__
        print("read patient file ",patient_file)
        try:
            df = pd.read_csv(patient_file, sep=sep)
            print("loaded ",df)
            dc = {}
            dc["id"] = id

            if 'surname' in df.columns:
                dc["surname"] = df.loc[:,"surname"].values.item()

            if 'fisrt_name' in df.columns:
                dc["first_name"] = df.loc[:, "first_name"].values.item()

            if 'birth_date' in df.columns:
                dc["birth_date"] = df.loc[:, "birth_date"].values.item()

            pdata.append(dc)
        except:
            print("error loading patient data")
            #traceback.print_exc()

    return pdata

def generate_new_id(id_file = config.__ID_FILE__):
    id_generated =False
    assigned_ids = _get_assigned_ids(id_file = id_file)

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
            #with open(config.__ID_FILE__, 'a') as file:
            #    file.write('\n' + new_id)
            id_generated = True

    return new_id

def add_history_entry(id, date, msg,data_dir=config.__DATA_DIR__):
    outfile = data_dir + "/" + str(id) + "/" + config.__HIST_FILE__
    print("outfile ",outfile)

    row = date + "\t" + msg
    with open(outfile,'a') as fd:
        fd.write(row + '\n')
    fd.close()


