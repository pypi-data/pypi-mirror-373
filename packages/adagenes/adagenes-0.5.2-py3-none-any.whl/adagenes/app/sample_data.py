import os
import pandas as pd
import adagenes as av


def load_sample_data():
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))
    filepath =  __location__ + "/sample.csv"
    df = pd.read_csv(filepath)

    genome_version="hg38"
    output_format="vcf"

    return av.app.display_table(df,"Sample", genome_version, output_format)