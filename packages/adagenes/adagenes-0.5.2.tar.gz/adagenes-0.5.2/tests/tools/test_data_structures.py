import unittest
import adagenes as ag


class DataStructuresTestCase(unittest.TestCase):

    def test_list_splitting(self):
        uids = [x for x in range(0,2000)]
        sublists = ag.tools.split_list(uids)
        self.assertEqual(len(sublists[0]),100,"")
