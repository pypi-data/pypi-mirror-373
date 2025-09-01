import unittest
import pandas as pd
import adagenes as ag


class TestRemoveDuplicates(unittest.TestCase):

    def test_remove_duplicates(self):
        data = { "PMID": ["1","2","1","1"], "num": [1,1,1,1], "Drug":["o","a","o","o"], "Cancer":["d","d","d","d"]
                 }
        df = pd.DataFrame(data=data)
        subset = ["PMID", "Drug", "Cancer"]
        df_new = ag.remove_duplicate_pmids(df, [])
        print(df_new)
        print(df.columns)
        print(df_new)

