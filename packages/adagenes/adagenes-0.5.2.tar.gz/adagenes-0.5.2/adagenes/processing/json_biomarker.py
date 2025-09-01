import adagenes as ag


class BiomarkerFrame:
    """
    Main class for storing biomarker information

    Attributes
    ----------
    data_type: str
        Data type of the source biomarker data. May be "g" (genomic), "t" (transcriptomic) or "p" (proteomic).
        "g" describes data where biomarker data is defined a genomic locations (e.g. VCF format),
        "t" describes transcriptomic identifiers (e.g. "NM_006015.4:c.5336A>G" in CSV-format),
        and "p" describes proteomic identifiers (e.g. "BRAF:V600E" in CSV-format)

    Methods
    -------

    """

    infile = ''
    outfile = ''
    generic_obj = None
    variants_written = False
    variant_batch_size = 5000
    line_batch_size = 100
    genome_version = None
    error_logfile = None
    input_type = ''
    output_type = ''
    save_headers = True
    output_format = 'file'
    input_format = 'file'
    features = None
    variants = {}
    row = 0
    columns = []
    header_lines = []
    orig_features = []
    biomarker_pos = {}
    data_type = ""
    max_variants = 0

    is_sorted = False
    sorted_variants = []

    data = {}

    def __init__(self, data=None, genome_version="hg38", src=None,
                 header_lines=[], src_format=None, columns=[], data_type="", preexisting_features=[]):
        """

        :param data:
        :param genome_version: Reference genome ("hg38","hg19")
        :param src: Source biomarker file. Stores the file path if variant data has been loaded from a file
        :param src_format: Source data format. Stores the data type if variant has been loaded from a file
        """
        if isinstance(data, list):
            dc = {}
            for el in data:
                dc[el] = {}
            self.data = dc
        elif isinstance(data, dict):
            self.data = data
        elif isinstance(data, str):
            dc = {}
            dc[data] = {}
            self.data = dc

        self.genome_version = genome_version
        if self.genome_version is None:
            self.genome_version = ""
        self.type_recognition(self.data)
        self.src = src
        self.header_lines = header_lines
        self.src_format = src_format
        self.columns = columns
        self.data_type = data_type
        self.preexisting_features = preexisting_features

    def __str__(self):
        if self.genome_version is None:
            self.genome_version = ""
        tostr = "{data type: " + str(self.data_type) + ", genome_version: " + str(self.genome_version), ", data:" + str(self.data) + "}"
        return str(tostr)

    def get_ids(self):
        """
        Returns a list of all biomarker IDs stored in the biomarker frame

        :return:
        """
        return list(self.data.keys())

    def type_recognition(self, data):
        """

        :param data:
        :return:
        """
        if data is not None:
            if isinstance(data, dict):
                self.data = data
                self.data = ag.TypeRecognitionClient(self.genome_version).process_data(self.data)
            elif isinstance(data, str):
                self.data = {data: {}}
                self.data = ag.TypeRecognitionClient(self.genome_version).process_data(self.data)
            else:
                print("Could not identify data type ",type(data))

