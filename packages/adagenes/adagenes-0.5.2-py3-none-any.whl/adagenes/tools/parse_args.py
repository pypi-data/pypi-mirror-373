import argparse, sys, gzip

def parse_args():
    """
    Argument parsing for Batch mode: Reads in user-defined arguments for Onkopus VCF clients

    :return:
    """
    parser = argparse.ArgumentParser("Argument parser for Onkopus VCF clients")
    parser.add_argument('action', choices=['run', 'install', 'list-modules', 'start', 'stop'])
    parser.add_argument('-i', '--infile',nargs='?', default='-',
                        help="Path to the input file, can be a gzipped file")
    parser.add_argument('-o','--outfile', nargs='?', default=sys.stdout,
                        help="Path to the output file")
    parser.add_argument('-g', '--genome_version', choices=['hg19', 'hg38', 'GRCh37', 'GRCh38'],
                        help="The genome version used as reference", default='hg38')
    parser.add_argument('-ot', '--output_type', choices=['vcf', 'json'],
                        help = "File type of generated output file (Options: vcf, json)", default = 'json')
    parser.add_argument('-it', '--input_type', choices=['vcf', 'json','tsv','csv','xlsx','txt'],
                        help = "File type of generated input file (Options: vcf, json, tsv, csv, xlsx, txt)", default = 'vcf')
    parser.add_argument('-m', '--module', choices=['all', 'dbsnp','clinvar','ccs','metakb','civic','oncokb',
                                                   'revel','loftool','vuspredict','aggregator','interpreter'],
                        help="Onkopus module to be consulted (default: all (full biomarker interpretation) )", default='all')
    parser.add_argument('-err', '--error_file', type=argparse.FileType('w'), default=None)

    args = parser.parse_args()
    action = args.action
    infile = args.infile
    outfile = args.outfile
    otype = args.output_type
    itype = args.input_type
    error_logfile = args.error_file
    module = args.module

    genome_version = args.genome_version
    if args.genome_version == "GRCh37":
        genome_version = 'hg19'
    if args.genome_version == "GRCh38":
        genome_version = 'hg38'

    return action, infile, outfile, genome_version, itype, otype, error_logfile, module
