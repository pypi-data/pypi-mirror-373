import os, configparser
from pathlib import Path
import platform, subprocess

# read in config.ini
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '', 'config.ini'))


def get_config(client_config=None):
    if client_config is None:
        return config
    else:
        # Merge client configuration and default configuration
        return config | client_config


def check_liftover_files(liftover_dir):
    """
    Checks if the liftover files exist. Downloads them if the files cannot be found

    :param liftover_dir: Directory in the host file system where the liftover files are to be stored
    """
    system_platform = platform.system()

    filename = os.path.join(liftover_dir, 'hg19ToHg38.over.chain.gz')
    filename_path = Path(filename)
    #print("check dir ",filename_path)
    if not filename_path.is_file():
        url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg19/liftOver/hg19ToHg38.over.chain.gz"
        if system_platform == "Linux":
            # Use wget on Linux
            cmd = ["wget", "-v", url, "-O", filename]
        elif system_platform == "Windows":
            # Use curl on Windows (included in recent versions of Windows)
            cmd = ["curl", "-L", url, "-o", filename]
        elif system_platform == "Darwin":  # macOS
            # Use curl on macOS (included by default)
            cmd = ["curl", "-L", url, "-o", filename]
        else:
            raise Exception(f"Unsupported OS: {system_platform}")

        print("Could not find Liftover file: ",filename,". Downloading file...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Downloaded {filename} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {filename}. Error: {e}")
    else:
        pass

    filename = os.path.join(liftover_dir, 'hg38ToHg19.over.chain.gz')
    filename_path = Path(filename)
    if not filename_path.is_file():
        url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz"
        if system_platform == "Linux":
            # Use wget on Linux
            cmd = ["wget", "-v", url, "-O", filename]
        elif system_platform == "Windows":
            # Use curl on Windows (included in recent versions of Windows)
            cmd = ["curl", "-L", url, "-o", filename]
        elif system_platform == "Darwin":  # macOS
            # Use curl on macOS (included by default)
            cmd = ["curl", "-L", url, "-o", filename]
        else:
            raise Exception(f"Unsupported OS: {system_platform}")

        print("Could not find Liftover file: ", filename, ". Downloading file...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Downloaded {filename} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {filename}. Error: {e}")
    else:
        pass

    filename = os.path.join(liftover_dir, 'hs1ToHg38.over.chain.gz')
    filename_path = Path(filename)
    if not filename_path.is_file():
        url = "https://hgdownload.soe.ucsc.edu/goldenPath/hs1/liftOver/hs1ToHg38.over.chain.gz"
        if system_platform == "Linux":
            # Use wget on Linux
            cmd = ["wget", "-v", url, "-O", filename]
        elif system_platform == "Windows":
            # Use curl on Windows (included in recent versions of Windows)
            cmd = ["curl", "-L", url, "-o", filename]
        elif system_platform == "Darwin":  # macOS
            # Use curl on macOS (included by default)
            cmd = ["curl", "-L", url, "-o", filename]
        else:
            raise Exception(f"Unsupported OS: {system_platform}")

        print("Could not find Liftover file: ", filename, ". Downloading file...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Downloaded {filename} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {filename}. Error: {e}")
    else:
        pass

    filename = os.path.join(liftover_dir, 'hg38ToGCA_009914755.4.over.chain.gz')
    filename_path = Path(filename)
    if not filename_path.is_file():
        url = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToGCA_009914755.4.over.chain.gz"
        if system_platform == "Linux":
            # Use wget on Linux
            cmd = ["wget", "-v", url, "-O", filename]
        elif system_platform == "Windows":
            # Use curl on Windows (included in recent versions of Windows)
            cmd = ["curl", "-L", url, "-o", filename]
        elif system_platform == "Darwin":  # macOS
            # Use curl on macOS (included by default)
            cmd = ["curl", "-L", url, "-o", filename]
        else:
            raise Exception(f"Unsupported OS: {system_platform}")

        print("Could not find Liftover file: ", filename, ". Downloading file...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Downloaded {filename} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {filename}. Error: {e}")
    else:
        pass

    filename = os.path.join(liftover_dir, 'hg19ToHs1.over.chain.gz')
    filename_path = Path(filename)
    if not filename_path.is_file():
        url = "https://hgdownload.soe.ucsc.edu/gbdb/hg19/liftOver/hg19ToHs1.over.chain.gz"
        if system_platform == "Linux":
            # Use wget on Linux
            cmd = ["wget", "-v", url, "-O", filename]
        elif system_platform == "Windows":
            # Use curl on Windows (included in recent versions of Windows)
            cmd = ["curl", "-L", url, "-o", filename]
        elif system_platform == "Darwin":  # macOS
            # Use curl on macOS (included by default)
            cmd = ["curl", "-L", url, "-o", filename]
        else:
            raise Exception(f"Unsupported OS: {system_platform}")

        print("Could not find Liftover file: ", filename, ". Downloading file...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Downloaded {filename} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {filename}. Error: {e}")
    else:
        pass

    filename = os.path.join(liftover_dir, 'hs1ToHg19.over.chain.gz')
    filename_path = Path(filename)
    if not filename_path.is_file():
        url = "https://hgdownload.soe.ucsc.edu/goldenPath/hs1/liftOver/hs1ToHg19.over.chain.gz"
        if system_platform == "Linux":
            # Use wget on Linux
            cmd = ["wget", "-v", url, "-O", filename]
        elif system_platform == "Windows":
            # Use curl on Windows (included in recent versions of Windows)
            cmd = ["curl", "-L", url, "-o", filename]
        elif system_platform == "Darwin":  # macOS
            # Use curl on macOS (included by default)
            cmd = ["curl", "-L", url, "-o", filename]
        else:
            raise Exception(f"Unsupported OS: {system_platform}")

        print("Could not find Liftover file: ", filename, ". Downloading file...")
        try:
            subprocess.run(cmd, check=True)
            print(f"Downloaded {filename} successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to download {filename}. Error: {e}")
    else:
        pass


if "LIFTOVER_DATA_DIR" in os.environ:
    __LIFTOVER_DATA_DIR__ = os.getenv('LIFTOVER_DATA_DIR')
else:
    #__LIFTOVER_DATA_DIR__ = config['DEFAULT']['LIFTOVER_DATA_DIR']
    try:
        #__location__ = os.path.realpath(os.path.dirname(__file__))
        lo_path = os.path.join(os.getcwd(), os.path.dirname(__file__))
        lo_path = os.path.join(lo_path, 'data')
        __location__ = os.path.realpath(
            lo_path
        )
    except NameError:
        # Fallback if __file__ is not defined (like in interactive mode)
        __location__ = os.getcwd()

    __LIFTOVER_DATA_DIR__ = os.path.join(__location__)

if "ADAGENES_PORT" in os.environ:
    __ADAGENES_PORT__ = os.getenv("ADAGENES_PORT")
else:
    __ADAGENES_PORT__ = "11108"

__LIFTOVER_FILE_HG38 = "hg38ToHg19.over.chain.gz"
__LIFTOVER_FILE_HG19 = "hg19ToHg38.over.chain.gz"

# test if liftover files can be found
check_liftover_files(__LIFTOVER_DATA_DIR__)

__VCF_COLUMNS__ = ["chr", "start", "id", "ref", "var", "qual", "filter", "info", "format", "seq"]
match_types = ["exact_match","any_mutation_in_gene","same_position","same_position_any_mutation"]
variant_data_key = 'variant_data'

extract_keys_list = config["VCF"]["EXTRACT_KEYS"].split(" ")
extract_keys = {}
extract_keys["UTA_Adapter_gene"] = ["hgnc_symbol","aminoacid_exchange"]
extract_keys["UTA_Adapter"] = ["gene_name","variant_exchange"]
extract_keys["revel"] = ["Score"]
extract_keys["dbnsfp"] = ["SIFT_pred"]
extract_keys["vus_predict"] = ["FATHMM","Missense3D","SIFT","Score"]
extract_keys["dbsnp"] = ["rsID", "total"]

__FEATURE_GENE__ = 'gene_name'
__FEATURE_VARIANT__ = 'variant_exchange'
__FEATURE_QID__ = 'q_id'

uta_adapter_srv_prefix = 'UTA_Adapter'
onkopus_aggregator_srv_prefix= "onkopus_aggregator"

gencode_srv_prefix = 'gencode'
drugclass_srv_prefix = 'drugclass'
civic_srv_prefix = 'civic'
dbnsfp_srv_prefix = 'dbnsfp'
mvp_srv_prefix = "mvp"
metakb_srv_prefix = "metakb"
oncokb_srv_prefix = "oncokb"
alphamissense_srv_prefix = "alphamissense"
primateai_srv_prefix = "primateai"
vuspredict_srv_prefix = "vus_predict"
loftool_srv_prefix = "loftool"
revel_srv_prefix = "revel"
clinvar_srv_prefix = "clinvar"
dbsnp_srv_prefix = 'dbsnp'
uta_adapter_genetogenomic_srv_prefix = "UTA_Adapter_gene"
uta_adapter_protein_sequence_srv_prefix = "UTA_Adapter_protein_sequence"

# Flask service
__ID_FILE__= "ids.txt"
__DATA_DIR__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))) + "/uploaded_files"
if not os.path.exists(__DATA_DIR__):
            os.makedirs(__DATA_DIR__)

if "MODULE_SERVER" in os.environ:
    __MODULE_SERVER__ = os.getenv("MODULE_SERVER")
    print("Module server: ",__MODULE_SERVER__)
else:
    __MODULE_SERVER__ = config['DEFAULT']['MODULE_SERVER']

if "MODULE_PROTOCOL" in os.environ:
    __MODULE_PROTOCOL__ = os.getenv("MODULE_PROTOCOL")
    print("Module protocol: ",__MODULE_PROTOCOL__)
else:
    __MODULE_PROTOCOL__ = config['DEFAULT']['MODULE_PROTOCOL']

if "PORTS_ACTIVE" in os.environ:
    __PORTS_ACTIVE__ = os.getenv("PORTS_ACTIVE")
    print("Module ports active: ",__PORTS_ACTIVE__)
else:
    __PORTS_ACTIVE__ = config['DEFAULT']['PORTS_ACTIVE']

if "PROXY_PORT" in os.environ:
    __PROXY_PORT__ = os.getenv("PROXY_PORT")
else:
    __PROXY_PORT__ = config['DEFAULT']['PROXY_PORT']


if "ADAGENES_DB_SERVER" in os.environ:
    __ADAGENES_DB_SERVER__ = os.getenv("ADAGENES_DB_SERVER")
else:
    __ADAGENES_DB_SERVER__ = config['DEFAULT']['ADAGENES_DB_SERVER']

if "ADAGENES_DB_PORT" in os.environ:
    __ADAGENES_DB_PORT__ = os.getenv("ADAGENES_DB_PORT")
else:
    __ADAGENES_DB_PORT__ = config['DEFAULT']['ADAGENES_DB_PORT']

if "ADAGENES_DB_NAME" in os.environ:
    __ADAGENES_DB_NAME__ = os.getenv("ADAGENES_DB_NAME")
else:
    __ADAGENES_DB_NAME__ = config['DEFAULT']['ADAGENES_DB_NAME']

# MODULE PORTS
__PORT_UNIPROT__ = ':10178'

if __PORTS_ACTIVE__ != "1":
    __PORT_UNIPROT__ = ''
elif __PROXY_PORT__ != "":
    __PORT_UNIPROT__ = __PROXY_PORT__

# Uniprot
uniprot_info_lines= [
        '##INFO=<ID=Molecular features,Number=1,Type=String,Description="Molecular features of amino acid exchange">',
    ]
uniprot_src = __MODULE_PROTOCOL__ + "://" + __MODULE_SERVER__ + __PORT_UNIPROT__ + "/uniprot/v1/hg38/UniprotID"
uniprot_srv_prefix= "Uniprot ID"
uniprot_keys = [ 'uniprot-id' ]
uniprot_response_keys= []

sample_file = "/sample/hg38_somaticMutations.l520.vcf"
sample_protein_file = "/sample/hg38_sample_protein.csv"
