import unittest, os
import adagenes as ag

def count_lines(file_path):
    """
    Counts the number of lines in a file.

    :param file_path: The path to the file.
    :return: The number of lines in the file.
    """
    try:
        with open(file_path, 'r') as file:
            line_count = sum(1 for _ in file)
        return line_count
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

class TestStreamBasedLiftover(unittest.TestCase):

    def test_stream_based_liftover(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations_cclab_brca.vcf"
        outfile = __location__ + "/../test_files/somaticMutations_cclab_brca.GRCh38.vcf"
        outfile1 = __location__ + "/../test_files/somaticMutations_cclab_brca1.GRCh38.vcf"

        client = ag.LiftoverClient(genome_version="hg19",target_genome="hg38")
        bframe = ag.read_file(infile, genome_version="hg19")
        bframe = client.process_data(bframe)
        ag.write_file(outfile1,bframe)

        ag.process_file(infile, outfile, client, genome_version="hg19")

        #self.assertEqual(count_lines(infile), count_lines(outfile1))
        #self.assertEqual(count_lines(infile), count_lines(outfile), "")
        #self.assertEqual(count_lines(outfile), count_lines(outfile1), "")

    def test_stream_based_liftover_t2t(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations_cclab_brca.vcf"
        outfile = __location__ + "/../test_files/somaticMutations_cclab_brca.T2T.vcf"

        client = ag.LiftoverClient(genome_version="hg19",target_genome="t2t")

        #ag.process_file(infile, outfile, client, genome_version="hg19")
