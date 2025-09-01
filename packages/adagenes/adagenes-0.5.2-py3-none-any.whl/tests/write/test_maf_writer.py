import unittest, os
import adagenes as ag
#import onkopus as op


class TestMAFWriter(unittest.TestCase):

    def test_maf_writer_without_mapping(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/tp53_sample.avf"
        bframe = ag.read_file(infile)
        outfile = __location__ + "/../test_files/tp53_sample.out.maf"
        ag.write_file(outfile, bframe)

        #file = open(outfile)
        #contents = file.read()
        #contents_expected = """genomic_location_hg38,chrom,pos_hg38,pos_hg19,ref,alt,mutation_type,hgnc_gene_symbol,aa_exchange,aa_exchange_long,ncbi_transcript_mane_select,ncbi_cdna_string,ncbi_cds_start,ncbi_cds_end,ncbi_cds_strand,ncbi_prot_location,ncbi_protein_id,clinvar_clinical_significance,clinvar_review_status,clinvar_cancer_type,clinvar_id,dbsnp_population_frequency,dbsnp_rsid,gnomAD_exomes_ac,gnomAD_exomes_af,1000genomes_af,1000genomes_ac,alfa_total_af,alfa_total_ac,ExAC_AF,ExAC_AC,revel_score,alphamissense_score,mvp_score,loftool_score,vuspredict_score,missense3D_pred,CADD_score_raw,Polyphen2_HDIV_score,Polyphen2_HDIV_pred,Polyphen2_HVAR_score,Polyphen2_HVAR_pred,SIFT_score,SIFT_pred,GERP++_score,MetaLR_score,MetaSVM_score,phastCons17way_primate_score,phyloP17way_primate,MutationAssessor_score,MutationTaster_score,fathmm-MKL_coding_score,fathmm-XF_coding_score,uniprot_id,alphamissense_class,Interpro_domain,protein_sequence_MANE_Select,Secondary_protein_structure,RelASA,BLOSUM62
        #,7,140753336,,A,T,,BRAF,V600E,Val600Glu,NM_004333.6,,,,,,,,,,,,,1,3.979940e-06,.,.,.,.,1.647e-05,2,,,,,,,4.2,0.97,D (probably damaging),0.94,D (probably damaging),0.0,,5.65,0.2357,-0.7685,0.999000,0.750000,0.65,1.0,0.99,0.91,,,|Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain;Serine-threonine/tyrosine-protein kinase  catalytic domain||Protein kinase domain||Protein kinase domain|,,,,\n"""
        #self.assertEqual(contents, contents_expected, "")
        #file.close()

    def test_maf_writer_onkopus_mapping(self):
        tsv_feature_ranking = ['genomic_location_hg38', 'chrom', 'pos_hg38', 'pos_hg19', 'ref', 'alt', 'mutation_type',
                               'hgnc_gene_symbol', 'aa_exchange', 'aa_exchange_long', 'ncbi_transcript_mane_select',
                               'ncbi_cdna_string', 'ncbi_cds_start', 'ncbi_cds_end', 'ncbi_cds_strand',
                               'ncbi_prot_location', 'ncbi_protein_id', 'clinvar_clinical_significance',
                               'clinvar_review_status', 'clinvar_cancer_type', 'clinvar_id',
                               'dbsnp_population_frequency', 'dbsnp_rsid', 'gnomAD_exomes_ac', 'gnomAD_exomes_af',
                               '1000genomes_af', '1000genomes_ac', 'alfa_total_af', 'alfa_total_ac', 'ExAC_AF',
                               'ExAC_AC', 'revel_score', 'alphamissense_score', 'mvp_score', 'loftool_score',
                               'vuspredict_score', 'missense3D_pred', 'CADD_score_raw', 'Polyphen2_HDIV_score',
                               'Polyphen2_HDIV_pred', 'Polyphen2_HVAR_score', 'Polyphen2_HVAR_pred', 'SIFT_score',
                               'SIFT_pred', 'GERP++_score', 'MetaLR_score', 'MetaSVM_score',
                               'phastCons17way_primate_score', 'phyloP17way_primate', 'MutationAssessor_score',
                               'MutationTaster_score', 'fathmm-MKL_coding_score', 'fathmm-XF_coding_score',
                               'uniprot_id', 'alphamissense_class', 'Interpro_domain', 'protein_sequence_MANE_Select',
                               'Secondary_protein_structure', 'RelASA', 'BLOSUM62']

        tsv_labels = {
            "mutation_type": "variant_data_type",
            "genomic_location_hg38": "qid",
            "chrom": "variant_data_CHROM",
            "pos_hg38": "variant_data_POS_hg38",
            "pos_hg19": "variant_data_POS_hg19",
            "ref": "variant_data_REF",
            "alt": "variant_data_ALT",
            "hgnc_gene_symbol": "UTA_Adapter_gene_name",
            "aa_exchange": "UTA_Adapter_variant_exchange",
            "aa_exchange_long": "UTA_Adapter_variant_exchange_long",
            "ncbi_transcript_mane_select": "UTA_Adapter_transcript",
            "ncbi_cdna_string": "UTA_Adapter_gene_c_dna_string",
            "ncbi_cds_start": "UTA_Adapter_gene_cds_start",
            "ncbi_cds_end": "UTA_Adapter_gene_cds_end",
            "ncbi_cds_strand": "UTA_Adapter_gene_strand",
            "ncbi_prot_location": "UTA_Adapter_gene_prot_location",
            "ncbi_protein_id": "UTA_Adapter_protein_sequence_protein_id",
            "clinvar_clinical_significance": "clinvar_CLNSIG",
            "clinvar_review_status": "clinvar_CLNREVSTAT",
            "clinvar_cancer_type": "clinvar_CLNDN",
            "clinvar_id": "clinvar_CLINVARID",
            "dbsnp_population_frequency": "dbsnp_freq_total",
            "dbsnp_rsid": "dbsnp_rsID",
            "gnomAD_exomes_ac": "dbnsfp_gnomAD_exomes_AC",
            "gnomAD_exomes_af": "dbnsfp_gnomAD_exomes_AF",
            "1000genomes_af": "dbnsfp_1000Gp3_AF",
            "1000genomes_ac": "dbnsfp_1000Gp3_AC",
            "alfa_total_af": "dbnsfp_ALFA_Total_AF",
            "alfa_total_ac": "dbnsfp_ALFA_Total_AC",
            "ExAC_AF": "dbnsfp_ExAC_AF",
            "ExAC_AC": "dbnsfp_ExAC_AC",
            "revel_score": "revel_Score",
            "alphamissense_score": "alphamissense_score",
            "mvp_score": "mvp_Score",
            "loftool_score": "loftool_Score",
            "vuspredict_score": "vus_predict_Score",
            "missense3D_pred": "vus_predict_Missense3D",
            "CADD_score_raw": "dbnsfp_CADD_raw_aggregated_value",
            "Polyphen2_HDIV_score": "dbnsfp_Polyphen2_HDIV_score_aggregated_value",
            "Polyphen2_HDIV_pred": "dbnsfp_Polyphen2_HDIV_pred_formatted",
            "Polyphen2_HVAR_score": "dbnsfp_Polyphen2_HVAR_score_aggregated_value",
            "Polyphen2_HVAR_pred": "dbnsfp_Polyphen2_HVAR_pred_formatted",
            "SIFT_score": "dbnsfp_SIFT_score_aggregated_value",
            "SIFT_pred": "dbnsfp_SIFT_pred_formatted",
            "GERP++_score": "dbnsfp_GERP++_RS",
            "MetaLR_score": "dbnsfp_MetaLR_score",
            "MetaSVM_score": "dbnsfp_MetaSVM_score",
            "phastCons17way_primate_score": "dbnsfp_phastCons17way_primate",
            "phyloP17way_primate": "dbnsfp_phyloP17way_primate",
            "MutationAssessor_score": "dbnsfp_MutationAssessor_score_aggregated_value",
            "MutationTaster_score": "dbnsfp_MutationTaster_score_aggregated_value",
            "fathmm-MKL_coding_score": "dbnsfp_fathmm-MKL_coding_score",
            "fathmm-XF_coding_score": "dbnsfp_fathmm-XF_coding_score",
            "uniprot_id": "alphamissense_uniprot_id",
            "alphamissense_class": "alphamissense_alphamissense_class",
            "Interpro_domain": "dbnsfp_Interpro_domain",
            "protein_sequence_MANE_Select": "UTA_Adapter_protein_sequence_protein_sequence",
            "Secondary_protein_structure": "protein_features_DSSP",
            "RelASA": "protein_features_RSA",
            "BLOSUM62": "variant_data_blosum62"
        }

        tsv_mappings = {
            "variant_data": ["CHROM", "POS_hg38", "POS_hg19", "REF", "ALT", "type", "blosum62"],
            "UTA_Adapter": ["gene_name", "variant_exchange", "transcript", "variant_exchange_long"],
            "UTA_Adapter_gene": ["c_dna_string", "cds_start", "cds_end", "strand", "prot_location"],
            "UTA_Adapter_protein": ["protein_id", "protein_sequence"],
            "dbnsfp": ["gnomAD_exomes_AC", "gnomAD_exomes_AF", "1000Gp3_AF", "1000Gp3_AC", "ALFA_Total_AF",
                                "ALFA_Total_AC",
                                "ExAC_AC", "ExAC_AF",
                                "CADD_raw_aggregated_value", "Polyphen2_HDIV_score_aggregated_value",
                                "Polyphen2_HDIV_pred_formatted",
                                "Polyphen2_HVAR_score_aggregated_value", "Polyphen2_HVAR_pred_formatted",
                                "SIFT_score_aggregated_value", "SIFT_pred_formatted",
                                "GERP++_RS", "MetaLR_score", "MetaSVM_score",
                                "phastCons17way_primate", "phyloP17way_primate",
                                "MutationAssessor_score_aggregated_value",
                                "MutationTaster_score_aggregated_value",
                                "fathmm-MKL_coding_score", "fathmm-XF_coding_score",
                                "Interpro_domain"
                                ],
            "revel": ["Score"],
            "alphamissense": ["score", "uniprot_id", "alphamissense_class"],
            "mvp": ["Score"],
            "clinvar": ["CLNSIG", "CLNREVSTAT", "CLNDN", "CLINVARID"],
            "dbsnp": ["freq_total", "rsID"],
            "loftool": ["Score"],
            "vus-predict": ["Missense3D"],
            "protein_features": ["DSSP", "RSA"]
        }


        __location__ = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/somaticMutations.ln50.dbnsfp.avf"
        bframe = ag.read_file(infile)
        outfile = __location__ + "/../test_files/somaticMutations.ln50.dbnsfp.out.maf"
        ag.write_file(outfile, bframe, labels=tsv_labels,
                          ranked_labels=tsv_feature_ranking,
                          mapping=tsv_mappings)

    def test_maf_writer(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.ln50.txt"
        outfile = __location__ + '/../test_files/somaticMutations.ln50.vcf.out.maf'

        #outfile = open(outfile_src, "w")
        mapping = {
            "chrom": 1,
            "pos": 2,
            "ref": 4,
            "alt": 5
        }
        bframe = ag.read_file(input_file, sep="\t", mapping=mapping)

        #print(bframe.data)
        ag.write_file(outfile, bframe)

        #self.assertEqual(bframe.data,"","")
        with open(outfile, 'r') as file:
            contents = file.read()
        #print(contents)

        self.assertEqual(
            contents[200:400],
            '\tProtein_Change\ti_TumorVAF_WU\ti_transcript_name\n'
            '.\t.\t.\t.\t7\t21784211\t21784211\t.\tIn_Frame_Ins\tINS\t.\t.\t.\t.\t.\t.\t'
            '.\n'
            '.\t.\t.\t.\t10\t8115913\t8115913\t.\tMissense_Mutation\tSNP\t.\t.\t.\t.\t.\t'
            '.\t.\n'
            '.\t.\t.\t.\t17\t7681744\t7681744'
            ,
            ""
        )

    def test_maf_writer_file_object(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.ln_4.vcf"
        outfile_src = __location__ + '/../test_files/somaticMutations.ln_4.vcf.out.maf'
        outfile = open(outfile_src, "w")

        reader = ag.VCFReader()
        writer = ag.MAFWriter()
        data = reader.read_file(input_file)
        writer.write_to_file(outfile, data)

        outfile.close()

        with open(outfile_src, 'r') as file:
            contents = file.read()
        print(contents)

        self.assertEqual(contents[:400],
                         'Hugo_Symbol\tEntrez_Gene_Id\tCenter\tNCBI_Build\tChromosome\tStart_Position\t'
                         'End_Position\tStrand\tVariant_Classification\tVariant_Type\t'
                         'Reference_Allele\tTumor_Seq_Allele1\tTumor_Seq_Allele2\t'
                         'Tumor_Sample_Barcode\tProtein_Change\ti_TumorVAF_WU\ti_transcript_name\n'
                         '.\t.\t.\t.\t12\t25245350\t25245350\t.\tMissense_Mutation\tSNP\t.\t.\t.\t.\t'
                         '.\t.\t.\n'
                         '.\t.\t.\t.\t12\t47236180\t47236180\t.\tMissense_Mutation\tSNP\t.\t.\t.\t.\t'
                         '.\t.\t.\n'
                         '.\t.\t.\t.\t12\t7705610'
        , "")

    def test_info_feature_mapping(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/sample_brca.vcf"
        outfile = __location__ + '/../test_files/sample_brca.maf'

        bframe = ag.read_file(input_file, sep="\t")

        print(bframe.data)
        ag.write_file(outfile, bframe)

        # self.assertEqual(bframe.data,"","")
        with open(outfile, 'r') as file:
            contents = file.read()
        #print(contents)

        self.assertEqual(
            contents[200:400],
            '\tProtein_Change\ti_TumorVAF_WU\ti_transcript_name\n'
            '.\t.\t.\t.\t7\t21784211\t21784211\t.\tIn_Frame_Ins\tINS\t.\t.\t.\t123\t.\t.\t'
            '.\n'
            '.\t.\t.\t.\t10\t8115913\t8115913\t.\tMissense_Mutation\tSNP\t.\t.\t.\t123\t'
            '.\t.\t.\n'
            '.\t.\t.\t.\t17\t7681744\t768'
            ,
            ""
        )

    def test_maf_writer_annotated_object(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))

        input_file = __location__ + "/../test_files/somaticMutations.ln_4.vcf"
        outfile_src = __location__ + '/../test_files/somaticMutations.ln_4.seqcat.maf'
        outfile = open(outfile_src, "w")

        reader = ag.VCFReader()
        writer = ag.MAFWriter()
        data = reader.read_file(input_file)

        bframe = ag.LiftoverAnnotationClient(genome_version="hg19", target_genome="hg38").process_data(data)
        #bframe.data = op.UTAAdapterClient(genome_version="hg38").process_data(bframe.data)
        #writer.write_to_file(outfile, data)
        outfile.close()

        #with open(outfile_src, 'r') as file:
        #    contents = file.read()
        #print(contents)

        #self.assertEqual(contents[:400],
        #                 'Hugo_Symbol\tEntrez_Gene_Id\tCenter\tNCBI_Build\tChromosome\tStart_Position\t'
        #                 'End_Position\tStrand\tVariant_Classification\tVariant_Type\t'
        #                 'Reference_Allele\tTumor_Seq_Allele1\tTumor_Seq_Allele2\t'
        #                 'Tumor_Sample_Barcode\tProtein_Change\ti_TumorVAF_WU\ti_transcript_name\n'
        #                 'KRAS\t.\t.\t.\t12\t25245350\t25245350\t.\tMissense_Mutation\tSNP\t.\t.\t.\t'
        #                 '.\t.\t.\t.\n'
        #                 'PCED1B\t.\t.\t.\t12\t47236180\t47236180\t.\tMissense_Mutation\tSNP\t.\t.\t.\t'
        #                 '.\t.\t.\t.\n'
        #                 'E2F7\t.\t.\t.'
        #, "")

    def test_csv_to_maf(self):
        q=["TP53:R282W","BRAF:V600E","GATA3:T421M"]
        bframe = ag.BiomarkerFrame(q)
        print("Q keys: ",bframe.data)