import unittest, os
import adagenes as ag
#import onkopus as op


class TestCSVWriter(unittest.TestCase):

    def test_csv_writer_without_mapping(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/tp53_sample.avf"
        bframe = ag.read_file(infile)
        #print(bframe)
        outfile = __location__ + "/../test_files/tp53_sample.out.csv"
        ag.write_file(outfile, bframe)

        file = open(outfile)
        contents = file.read()
        #print(contents[0:50])
        self.assertEqual(contents[0:50], "QID,CHROM,POS,POS_hg38,REF,ALT,type_desc,type,muta", "")
        #contents_expected = """genomic_location_hg38,chrom,pos_hg38,pos_hg19,ref,alt,mutation_type,hgnc_gene_symbol,aa_exchange,aa_exchange_long,ncbi_transcript_mane_select,ncbi_cdna_string,ncbi_cds_start,ncbi_cds_end,ncbi_cds_strand,ncbi_prot_location,ncbi_protein_id,clinvar_clinical_significance,clinvar_review_status,clinvar_cancer_type,clinvar_id,dbsnp_population_frequency,dbsnp_rsid,gnomAD_exomes_ac,gnomAD_exomes_af,1000genomes_af,1000genomes_ac,alfa_total_af,alfa_total_ac,ExAC_AF,ExAC_AC,revel_score,alphamissense_score,mvp_score,loftool_score,vuspredict_score,missense3D_pred,CADD_score_raw,Polyphen2_HDIV_score,Polyphen2_HDIV_pred,Polyphen2_HVAR_score,Polyphen2_HVAR_pred,SIFT_score,SIFT_pred,GERP++_score,MetaLR_score,MetaSVM_score,phastCons17way_primate_score,phyloP17way_primate,MutationAssessor_score,MutationTaster_score,fathmm-MKL_coding_score,fathmm-XF_coding_score,uniprot_id,alphamissense_class,Interpro_domain,protein_sequence_MANE_Select,Secondary_protein_structure,RelASA,BLOSUM62
        #,7,140753336,,A,T,,BRAF,V600E,Val600Glu,NM_004333.6,,,,,,,,,,,,,1,3.979940e-06,.,.,.,.,1.647e-05,2,,,,,,,4.2,0.97,D (probably damaging),0.94,D (probably damaging),0.0,,5.65,0.2357,-0.7685,0.999000,0.750000,0.65,1.0,0.99,0.91,,,|Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain|,,,,\n"""
        #self.assertEqual(contents, contents_expected, "")
        file.close()

    def test_annotate_with_molfeat(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.csv"
        bframe = ag.read_file(infile)
        print(bframe.data)
        outfile = __location__ + "/../test_files/somaticMutations.ln50.molfeat.csv"
        genome_version="hg19"

        bframe = ag.LiftoverClient(genome_version=genome_version, target_genome="hg38").process_data(bframe)
        genome_version="hg38"

        #bframe.data = op.UTAAdapterClient(genome_version=genome_version).process_data(bframe.data)
        #bframe.data = op.MolecularFeaturesClient(genome_version=genome_version).process_data(bframe.data)

        #ag.write_file(outfile, bframe)

    def test_annotate_with_molfeat_stream(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.hg38.uta.vcf"
        bframe = ag.read_file(infile)
        print(bframe.data)
        outfile = __location__ + "/../test_files/somaticMutations.ln50.hg38.uta.molfeat.csv"
        genome_version="hg38"
        #client = op.MolecularFeaturesClient(genome_version=genome_version)

        #ag.process_file(infile, outfile, client)
