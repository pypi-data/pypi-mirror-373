import traceback
import adagenes


def split_bframe(bframe, size_set1=None, size_set2=None):
    """
    Splits a biomarker frame into 2 bframes containing subsets of the original bframe

    :param bframe:
    :param size_set1:
    :param size_set2:
    :return:
    """
    if (size_set1 is None) or (size_set2 is None):
        print("Error: No subset sizes defined. Define absolute (e.g. size_set1=100, size_set2=150) or "
              "relative sizes of the splitted subsets (e.g. size_set1=0.2p,size_st2=0.8p)"
              "")
        return bframe, None

    try:
        if "p" in size_set1:
            size_set1 = size_set1.replace("p","")
            size_set1 = int(float(size_set1) * len(bframe.data.keys()))
        else:
            size_set1 = size_set1

        if "p" in size_set2:
            size_set2 = size_set2.replace("p","")
            size_set2 = int(float(size_set2) * len(bframe.data.keys()))
        else:
            size_set2 = size_set2

        keys_set1 = list(bframe.data.keys())[0:size_set1]
        keys_set2 = list(bframe.data.keys())[size_set1:(size_set2+size_set1)]

        bframe_sub_data = {key: bframe.data[key] for key in keys_set1}
        bframe_sub = adagenes.BiomarkerFrame(data=bframe_sub_data)

        bframe1_sub_data = {key: bframe.data[key] for key in keys_set2}
        bframe1_sub = adagenes.BiomarkerFrame(data=bframe1_sub_data)

        return bframe_sub, bframe1_sub
    except:
        print(traceback.format_exc())
        return None


def read_file(
              infile_src,
              reader=None,
              input_format=None,
              genome_version="hg38",
              labels=None,
              ranked_labels=None,
              mapping=None,
              level="gene",
              sep=",",
              remove_quotes=True,
              start_row=None,
              end_row=None
            ):
    """
    Reads a biomarker file in any common format. The data format may be specified, otherwise it is automatically
    detected by the input file name

    Mapping example: Read in CSV-formatted data of missense variants with the chromosome set to 17, chromosomal positions are stored
    in a column labeled 'hg38_Chr17_coordinates', and the amino acid exchange in a column 'Description'
    mapping = {

    }

    :param infile_src:
    :param reader:
    :param input_format:
    :param mapping: User-defined mapping of data columns to biomarker features
    :return: Returns a biomarker frame with the parsed input file data
    """
    try:
        if reader is None:
            reader = get_reader(infile_src, file_type=input_format)
    except:
        print(traceback.format_exc())
    bframe = reader.read_file(infile_src, genome_version=genome_version,sep=sep,mapping=mapping, remove_quotes=True, start_row=start_row, end_row=end_row)
    bframe = adagenes.TypeRecognitionClient(genome_version=genome_version).process_data(bframe)
    bframe.data = adagenes.normalize_identifiers(bframe.data, add_refseq=False)
    bframe.data = adagenes.tools.recognize_mutation_types_from_vcf_format(bframe.data)
    return bframe


def write_file(outfile,
               json_obj,
               file_type=None,
               genome_version=None,
               labels=None,
               ranked_labels=None,
               mapping=None,
               export_features=None
               ):
    """
    Writes a biomarker frame to an output file in a given format.

    :param outfile: Output file path
    :param json_obj: biomarker frame
    :param file_type: Data format of the output file:
    :param genome_version: Reference genome, ''hg38' or 'hg19'
    :param mapping: Dictionary including features to export
    :param labels:
    :param ranked_labels: Sorted list that defines the order in which the features are to be exported to CSV
    :return:
    """
    writer = get_writer(outfile, file_type=file_type)
    writer.write_to_file(outfile, json_obj,
                         labels=labels,ranked_labels=ranked_labels,mapping=mapping, export_features=export_features)


def get_reader(infile_src, file_type=None, genome_version=None):
    """
    Identifies the associated file reader for an input file

    :param infile_src:
    :param file_type:
    :param genome_version:
    :return:
    """
    if isinstance(infile_src,str):
        if (file_type is None) or (file_type==""):
            file_type = adagenes.get_file_type(infile_src)

    if file_type == 'vcf':
        return adagenes.VCFReader(genome_version=genome_version)
    if file_type == 'maf':
        return adagenes.MAFReader(genome_version=genome_version)
    elif file_type == 'json':
        return adagenes.JSONReader(genome_version=genome_version)
    elif file_type == 'avf':
        return adagenes.AVFReader(genome_version=genome_version)
    elif file_type == 'tsv':
        return adagenes.TSVReader(genome_version=genome_version)
    elif file_type == 'xlsx':
        return adagenes.XLSXReader(genome_version=genome_version)
    elif file_type == 'txt':
        return adagenes.TXTReader(genome_version=genome_version)
    elif file_type == 'csv':
        return adagenes.CSVReader(genome_version=genome_version)
    elif file_type == 'fasta':
        return adagenes.FASTAReader()
    elif file_type == 'gtf':
        return adagenes.GTFReader()


def get_writer(outfile_src, file_type=None):
    """
    Returns a file writer of a specified data format

    :param outfile_src:
    :param file_type: Data format ('vcf', 'json', 'maf', 'tsv', 'csv', 'maf')
    :return:
    """

    if ((file_type is None) or (file_type=="")) and (isinstance(outfile_src,str)):
        file_type = adagenes.get_file_type(outfile_src)

    if file_type == 'vcf':
        return adagenes.VCFWriter()
    elif file_type == 'json':
        return adagenes.JSONWriter()
    elif file_type == 'tsv':
        return adagenes.TSVWriter()
    elif file_type == 'csv':
        return adagenes.CSVWriter()
    elif file_type == 'maf':
        return adagenes.MAFWriter()
    elif file_type == 'xlsx':
        return adagenes.XLSXWriter()
    elif file_type == 'avf':
        return adagenes.AVFWriter()
    elif file_type == 'bed':
        return adagenes.BEDWriter()
