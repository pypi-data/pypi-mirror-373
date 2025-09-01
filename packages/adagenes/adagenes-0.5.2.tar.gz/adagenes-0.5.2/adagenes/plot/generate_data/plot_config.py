
# Radar plots
default_pathogenicity_labels = [
    "REVEL",
    "MVP",
    "PrimateAI",
    "DANN",
    "DEOGEN2",
    "GERP++",
    "GM12878",
    "H1-hESC",
    "HUVEC",
    "LIST_S2",
    "LRT",
    "M-CAP",
    "MPC",
    "MetaLR",
    "MetaRNN",
    "MetaSVM",
    "MutPred",
    "MutationAssessor",
    "MutationTaster",
    "PROVEAN",
    "SiPhy",
    "bStatistic",
    "fathmm-MKL",
    "fathmm-XF",
    "phastCons17",
    "SIFT",
    "Missense3D",
    "AlphaMissense"
]

default_pathogenicity_modules = [
    "revel",
    "mvp",
    "primateai",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "dbnsfp",
    "vus_predict",
    "alphamissense"
]

default_pathogenicity_features = [
    "Score",
    "Score",
    "Score",
    "DANN_rankscore",
    "DEOGEN2_rankscore",
    "GERP++_RS_rankscore",
    "GM12878_fitCons_rankscore",
    "H1-hESC_fitCons_rankscore",
    "HUVEC_fitCons_rankscore",
    "LIST-S2_rankscore",
    "LRT_converted_rankscore",
    "M-CAP_rankscore",
    "MPC_rankscore",
    "MetaLR_rankscore",
    "MetaRNN_rankscore",
    "MetaSVM_rankscore",
    "MutPred_rankscore",
    "MutationAssessor_rankscore",
    "MutationTaster_converted_rankscore",
    "PROVEAN_converted_rankscore",
    "SiPhy_29way_logOdds_rankscore",
    "bStatistic_converted_rankscore",
    "fathmm-MKL_coding_rankscore",
    "fathmm-XF_coding_rankscore",
    "phastCons17way_primate_rankscore",
    "SIFT_converted_rankscore",
    "Missense3D",
    "score"
]

cat_dc = {
    "machine_learning": ["REVEL","MVP"],
    "conservation": ["PrimateAI","GERP++","phastCons17"],
    "protein_structure": ["Missense3D","AlphaMissense"]
}

#cat_dc = {
#    "machine_learning": ["REVEL","MVP"],
#    "conservation": ["PrimateAI","GERP++"],
#    "protein_structure": ["MutationAssessor", "MIssense3D","PolyPhen2"],
#}

#print(len(default_pathogenicity_labels), ", ", len(default_pathogenicity_modules), ", ", len(default_pathogenicity_features))