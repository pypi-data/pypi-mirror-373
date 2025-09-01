from urllib.parse import urlparse, parse_qs, unquote
#import adagenes.app.annotate
#import adagenes as ag


def get_transform_model(qid, output_format, request, genome_version):

    transform_model = {}
    print("request ",request)

    if output_format == "vcf":

        # custom to VCF
        if ("chrom" in request):
            transform_model["chrom"] = request.get("chrom")
            transform_model["pos"] = request.get("pos")
            transform_model["ref"] = request.get("ref")
            transform_model["alt"] = request.get("alt")
        elif ("gene" in request):
            # protein to VCF
            print("protein to VCF")

            # Annotate with SeqCAT
            gene_col = request.get("gene")
            aa_col = unquote(request.get("aa_exchange"))
            print("Annotate with SeqCAT: Use columns ",gene_col,":",aa_col)
            transform_model["gene"] = gene_col
            transform_model["aa_exchange"] = aa_col


    return output_format, transform_model