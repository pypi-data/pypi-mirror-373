import os, gzip
from io import StringIO
import pandas as pd
from adagenes.conf import read_config as config
import datetime
#import magic

def get_current_datetime():
    current_time = datetime.datetime.now()
    dt = str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day) + "_" + str(
        current_time.hour) + ":" + str(current_time.minute) + ":" + str(current_time.second)
    return dt

def open_infile(infile_src):
    if infile_src.endswith('.gz'):
        infile = gzip.open(infile_src, 'rt')
    else:
        infile = open(infile_src, 'r')
    return infile

def open_outfile(outfile_src):
    outfile = open(outfile_src, 'w')
    return outfile

def write_full_interpretation_to_files(variant_data, findings, recommendation, out_dir, output_format='tsv'):
    if output_format == 'tsv':
        sep='\t'
    elif output_format == 'csv':
        sep=','

    # create output directory
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    # write variant_interpretation_files

    # write findings to file

    # write treatment recommendation to file


def is_gzip(file_src):
    elements = file_src.split(".")
    file_extension = elements[len(elements) - 1]
    #print("FILE EXTENSION ",file_extension)
    if file_extension == 'gz':
        return True
    else:
        return False


def get_file_type(file_src, type='single'):
    """

    :param file_name:
    :param type:
    :return:
    """
    elements = file_src.split(".")
    file_extension = elements[len(elements) - 1]

    if file_extension == 'gz':
        file_extension = elements[len(elements) - 2]

    if os.path.exists(file_src):
        #mime = magic.Magic(mime=True)
        #file_type = mime.from_file(file_src)

        #if file_type == 'text/csv':
        if file_extension == "vcf":
                return "vcf"
        elif file_extension == "maf":
                return "maf"
        elif file_extension == "fa":
                return "fasta"
        #else:
        #        return file_extension
        #elif file_type == 'text/tab-separated-values':
        elif file_extension == "tsv":
                return "tsv"
        else:
                return file_extension
        #else:
        #    return file_extension

    return file_extension


def load_dataframe_from_vcf_file(infile:str, columns=config.__VCF_COLUMNS__) -> pd.DataFrame:
    """
    Loads a DataFrame from a VCF file. Works both with a plain VCF file as well as the annotated VCF version

    :param infile:
    :param columns
    :return:
    """
    file_name, file_extension = os.path.splitext(infile)
    if file_extension == '.gz':
        try:
            data = gzip.open(file_name, 'rt')
            #test = data.read(2)
        except:
            data = open(infile)
    else:
        data = open(infile)

    vcf_lines = []
    c = 0
    for line in data:
        if line.startswith('#'):
            if line.startswith('##reference'):
                print('##reference=')
            continue
        else:
            vcf_lines.append(line)

    if columns is None:
        if file_extension == 'annotated':
            columns = config.__VCF_COLUMNS_ANNOTATED__
        elif file_extension == 'filtered':
            columns = config.__VCF_COLUMNS_ANNOTATED__
        else:
            columns = config.__VCF_COLUMNS__
    #print("loaded lines: ",vcf_lines)
    vcf_data = generate_dataframe_from_vcf_array(vcf_lines, columns)

    data.close()

    return vcf_data

def generate_dataframe_from_json_array(json_arr:str, columns, sep="\t",vcf_data=None) -> pd.DataFrame:
    """
    Generates a dataframe a list of strings containing VCF data

    Parameters
    ----------
    vcf_lines
    columns
    sep

    Returns
    -------

    """

    data = ""
    for line in json_arr:
        line = line.rstrip('\n')
        fields = line.split('\t')
        # data += str(fields[0])+sep+str(fields[1])+sep+str(fields[2]) + sep +str(fields[3])+sep +str(fields[4])+sep + +str(fields[1])+sep +"\n"
        for j in range(0, len(fields)):
            if j > 0:
                data += sep
            data += str(fields[j])

        data += '\n'



    # add column labels
    column_labels = ""
    for cp,c in enumerate(columns):
        if cp>0:
            column_labels += sep
        column_labels += c
    data = column_labels + '\n' + data

    dataio = StringIO(data)
    #df = pd.read_csv(data, sep=";")
    df = pd.read_csv(dataio, sep=sep)
    df = df.astype("str")

    if vcf_data is not None:
        # merge new dataframe with previous data
        return pd.concat((vcf_data, df),axis=0)
    else:
        return df

def generate_dataframe_from_vcf_array(vcf_lines, columns, sep="\t",vcf_data=None) -> pd.DataFrame:
    """
    Generates a dataframe a list of strings containing VCF data

    Parameters
    ----------
    vcf_lines
    columns
    sep

    Returns
    -------

    """
    #print("get df from lines ",vcf_lines)
    data = ""
    for line in vcf_lines:
        line = line.rstrip('\n')
        fields = line.split('\t')
        #data += str(fields[0])+sep+str(fields[1])+sep+str(fields[2]) + sep +str(fields[3])+sep +str(fields[4])+sep + +str(fields[1])+sep +"\n"
        for j in range(0, len(fields)):
            if j>0:
                data += sep
            data += str(fields[j])

        data += '\n'

    # add column labels
    column_labels = ""
    for cp,c in enumerate(columns):
        if cp>0:
            column_labels += sep
        column_labels += c
    data = column_labels + '\n' + data

    dataio = StringIO(data)
    #df = pd.read_csv(data, sep=";")
    df = pd.read_csv(dataio, sep=sep)
    df = df.astype("str")

    if vcf_data is not None:
        # merge new dataframe with previous data
        return pd.concat((vcf_data, df),axis=0)
    else:
        return df

def load_sample_vcf() -> pd.DataFrame:
    """
        Load a sample VCF file and returns a data frame

        Parameters
        ----------

        Returns
        -------
        df:     pd.DataFrame
            DataFrame that contains the VCF file with the following columns: CHR, POS, ID, REF, ALT
        """

    df = pd.DataFrame ({'chr': ['chr9', 'chr14', 'chr5'], 'start': ['35075025', '104773487', '180603376'], 'ref': ['C', 'A', 'C'],
     'var': ['T', 'C', 'G'] , "qual":["","",""],"filter":["","",""],"info":["","",""],"format":["","",""],"add":["","",""]})
    #        columns=['chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'format','add' )
    print("samples vcf dimensions: ", df.shape)
    return df


def filter_n_variants(vcf: pd.DataFrame, var_col=None, var_col_index=None) -> pd.DataFrame:
    print("columns ",vcf.columns)

    if var_col is not None:
        vcf = vcf[vcf[var_col]!='.']
        vcf = vcf.reset_index(drop=True)
    elif var_col_index is not None:
        vcf = vcf.loc[vcf.iloc[:,var_col_index] != '.']
        vcf = vcf.reset_index(drop=True)
    return vcf
