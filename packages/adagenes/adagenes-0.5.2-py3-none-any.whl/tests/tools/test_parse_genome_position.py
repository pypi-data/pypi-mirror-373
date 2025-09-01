import unittest
import adagenes as ag


class TestParseGenomePosition(unittest.TestCase):

    def test_parse_genome_position_deletion(self):
        var = "chr17:g.7675152del"
        #parse_genome_position
