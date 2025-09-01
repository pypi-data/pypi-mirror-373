import os, datetime
import adagenes as ag
import adagenes.app.app_io
import adagenes.app.app_tools

def liftover_annotation(qid, genome_version, output_genome_version, data_dir=None, output_format='vcf'):
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

    infile = adagenes.app.io.find_newest_file(data_dir)
    if qid == "sample-vcf":
        infile = data_dir + ag.conf_reader.sample_file
    if qid == "sample-protein":
        infile = data_dir + ag.conf_reader.sample_protein_file

    infile_name = ag.app.io.split_filename(infile)
    outfile = adagenes.app.tools.update_filename_with_current_datetime(infile_name, action="processed")
    datetime_str = str(datetime.datetime.now())

    magic_obj = ag.LiftoverAnnotationClient(genome_version = genome_version, target_genome=output_genome_version)
    #print("liftover annotation: ",genome_version," to ", output_genome_version,": ",infile, ": ",outfile)
    ag.process_file(infile, outfile, magic_obj)

    annotation_key = 'Liftover annotation:' + genome_version + " to " + output_genome_version + "(" + datetime_str + ")::" + outfile
    ag.app.io.append_to_file(logfile, annotation_key + '\n')

def perform_liftover_annotation(qid, data_dir, genome_version):
    if genome_version != "hg38":
        # test if newest file is hg38
        #data_dir = data_dir + "/" + qid
        infile = adagenes.app.io.find_newest_file(data_dir + "/" + qid, filter=False)
        file_name = os.path.basename(infile)

        # Extract the first part of the file name
        newest_file_genome_version = file_name.split("_")[0]
        #newest_file_genome_version = infile.split("_")[0].split("/")[-1]

        print("newest genome version: ",newest_file_genome_version)

        if (newest_file_genome_version == "hg19") or (newest_file_genome_version == "t2t"):
            logfile = data_dir + '/qid' + '/log.txt'
            previous_actions = ag.app.io.load_log_actions(logfile)
            annotation_key = 'Liftover annotation:' + newest_file_genome_version + " to hg38"
            contains_substring = any(annotation_key in entry for entry in previous_actions)
            #print(logfile,"::",annotation_key,"::",previous_actions)
            #print("contains ",str(contains_substring))
            if contains_substring is False:
                print("automated liftover annotation:", newest_file_genome_version + " to hg38")
                liftover_annotation(qid, newest_file_genome_version, "hg38", data_dir=data_dir)