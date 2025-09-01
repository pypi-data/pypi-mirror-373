import unittest, time
import adagenes
import adagenes.conf.read_config as conf_reader

class TestLiftoverAnnotationClientClass(unittest.TestCase):

    def test_liftover_annotation_hg38tohg19(self):
        data = { "chr7:140753336A>T": { "variant_data":{ "CHROM":"7", "POS_hg38":"140753336" } },
                 "chr7:21784210insG": {}}
        bframe = adagenes.BiomarkerFrame(data=data, genome_version="hg38")
        genome_version="hg38"

        import time
        start_time = time.time()

        print(bframe.data)
        client = adagenes.LiftoverAnnotationClient(genome_version)
        print("Liftover (hg38tohg19)...")
        bframe = client.process_data(bframe, target_genome="hg19")

        stop_time = time.time() - start_time
        print(stop_time)

        print(bframe.data)
        self.assertEqual(bframe.data["chr7:140753336A>T"]["variant_data"]["POS_hg19"],140453136,"Error retrieving hg19 position")
        self.assertEqual(int(bframe.data["chr7:140753336A>T"]["variant_data"]["POS_hg38"]), 140753336,
                         "Error retrieving hg38 position")
        self.assertEqual(int(bframe.data["chr7:140753336A>T"]["variant_data"]["POS"]), 140753336,
                         "Error retrieving default position")
        self.assertEqual(int(bframe.data["chr7:21784210insG"]["variant_data"]["POS_hg19"]), 21823828,"")

    def test_liftover_annotation_hg19tohg38(self):
        data = { "chr7:140453136A>T": { "variant_data":{ "CHROM":"7", "POS_hg19":"140453136" } },
                 "chr10:8115914C>.": {"variant_data": {"CHROM": "10", "POS_hg19": "8115914"}}
                 }
        genome_version="hg19"

        import time
        start_time = time.time()
        client = adagenes.LiftoverAnnotationClient(genome_version)
        bframe = adagenes.BiomarkerFrame(data=data)

        print("Liftover (hg19tohg38)...")
        bframe = client.process_data(bframe, target_genome="hg38")

        stop_time = time.time() - start_time
        print(stop_time)

        print(bframe.data)
        self.assertEqual(int(bframe.data["chr7:140453136A>T"]["variant_data"]["POS_hg19"]),140453136,"Error retrieving hg19 position")
        self.assertEqual(int(bframe.data["chr7:140453136A>T"]["variant_data"]["POS_hg38"]), 140753336,
                         "Error retrieving hg38 position")
        self.assertEqual(int(bframe.data["chr7:140453136A>T"]["variant_data"]["POS"]), 140453136,
                         "Error retrieving default position")
        self.assertEqual(int(bframe.data["chr10:8115914C>."]["variant_data"]["POS_hg38"]), 8073951,
                         "Error retrieving default position")

    def test_liftover_annotation_with_passed_lo_obj(self):
        data = { "chr7:140453136A>T": { "variant_data":{ "CHROM":"7", "POS_hg19":"140453136" } }}
        bframe = adagenes.BiomarkerFrame(data=data)
        genome_version="hg19"
        from liftover import ChainFile
        lo = ChainFile(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHg38.over.chain.gz", one_based=True)
        #lo=LiftOver(conf_reader.__LIFTOVER_DATA_DIR__ + "/hg19ToHg38.over.chain.gz")

        import time
        start_time = time.time()
        client = adagenes.LiftoverAnnotationClient(genome_version)
        print("Liftover (hg19tohg38) with preloaded liftover files...")
        bframe = client.process_data(bframe,lo_hg19=lo,lo_hg38=None, target_genome="hg38")

        stop_time = time.time() - start_time
        print("time: ",stop_time)
        print(bframe.data)

    def test_liftover_annotation_t2t_to_hg38(self):
        # TODO
        pass

    def test_liftover_annotation_hg38_to_t2t(self):
        data = {"chr7:140753336A>T": {"variant_data": {"CHROM": "7", "POS_hg38": "140753336"}}}
        genome_version = "hg38"

        start_time = time.time()
        client = adagenes.LiftoverAnnotationClient(genome_version)
        bframe = adagenes.BiomarkerFrame(genome_version=genome_version, data=data)

        print("Liftover (t2ttohg38)...")
        bframe = client.process_data(bframe, target_genome="t2t")

        stop_time = time.time() - start_time
        print(stop_time)

        print(bframe.data)
        self.assertEqual(int(bframe.data["chr7:140753336A>T"]["variant_data"]["POS_t2t"]), 142067515,
                         "Error retrieving t2t position")
        self.assertEqual(int(bframe.data["chr7:140753336A>T"]["variant_data"]["POS_hg38"]), 140753336,
                         "Error retrieving hg38 position")
        self.assertEqual(int(bframe.data["chr7:140753336A>T"]["variant_data"]["POS"]), 140753336,
                         "Error retrieving default position")
