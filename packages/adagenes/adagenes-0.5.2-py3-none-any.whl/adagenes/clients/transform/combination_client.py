import traceback
import adagenes as ag


def merge_bframes(bframe1, bframe2, target_genome="hg38", target_level="g"):
    """
    Combines 2 biomarker frames in a merged biomarker frame

    :param bframe1:
    :param bframe2:
    :param target_genome: Reference genome of the merged biomarker frame
    :param target_level: Mutation level of the merged biomarker frame ('g' = DNA level, 't' = transcript level, 'p' = protein level (default:'g'))
    :return:
    """
    client = Combination()
    return client.process_data(bframe1, bframe2, target_genome=target_genome, target_level=target_level)


class Combination:
    def __init__(self, error_logfile=None):
        pass

    def process_data(self, biomarker_data1, biomarker_data2, target_genome="hg38", target_level="g") -> ag.BiomarkerFrame:
        """

        :param biomarker_data1:
        :param biomarker_data2:
        :param target_genome:
        :param target_level:
        :return:
        """
        try:
            if isinstance(biomarker_data1, ag.BiomarkerFrame):
                if biomarker_data1.genome_version != target_genome:
                    biomarker_data1 = ag.LiftoverClient().process_data(biomarker_data1, target_genome=target_genome)
                data1 = biomarker_data1.data
            elif isinstance(biomarker_data1, dict):
                data1 = biomarker_data1
            else:
                data1 = {}

            if isinstance(biomarker_data2, ag.BiomarkerFrame):
                if biomarker_data2.genome_version != target_genome:
                    biomarker_data2 = ag.LiftoverClient().process_data(biomarker_data2, target_genome=target_genome)
                data2 = biomarker_data2.data
            elif isinstance(biomarker_data2, dict):
                data2 = biomarker_data2
            else:
                data2 = {}

            # TODO: Add level transformation

            merged_data = ag.merge_dictionaries(data1, data2)
            bframe = ag.BiomarkerFrame(merged_data, genome_version=target_genome, data_type=target_level)
            return bframe
        except:
            print(traceback.format_exc())

        return None
