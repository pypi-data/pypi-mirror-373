import os
import adagenes as ag
import time
import unittest


class LoadTestCase(unittest.TestCase):

    def test_load(self):
        infile = os.getenv("INFILE")

        start_time = time.time()
        bframe = ag.read_file(infile, start_row=0, end_row=100)
        #bframe = ag.read_file(infile)
        end_time = time.time() - start_time

        print("Processing time: ",end_time)
        print("bframe size: ",len(list(bframe.data.keys())))
