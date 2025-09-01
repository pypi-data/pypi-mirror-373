import adagenes as ag
import adagenes.tools.seqcat_genetogenomic_client


def protein_to_genomic(bframe):
    """

    :param bframe:
    :return:
    """

    client = adagenes.tools.seqcat_genetogenomic_client.SeqCATProteinClient(genome_version="hg38")
    data_new = client.process_data(bframe.data)

    bframe_new = ag.BiomarkerFrame(data = data_new, genome_version=bframe.genome_version, data_type="g")
    return bframe_new
