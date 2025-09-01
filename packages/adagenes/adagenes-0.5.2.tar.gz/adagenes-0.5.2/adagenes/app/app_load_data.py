import os
import pandas as pd
import adagenes as av


def get_variant_search(q, genome_version, output_format):
    """

    :param q:
    :return:
    """
    #__location__ = os.path.realpath(
    #    os.path.join(os.getcwd(), os.path.dirname(__file__)))
    #filepath =  __location__ + "/sample.csv"

    data = { "Genomic location": [], "Transcript":[], "Protein":[], "Mutation type": [] }

    df = pd.DataFrame(data=data)

    return av.app.display_table(df, q, genome_version, output_format)

