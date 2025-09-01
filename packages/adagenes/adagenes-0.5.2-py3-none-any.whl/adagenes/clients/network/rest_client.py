import traceback
from adagenes.clients import client


class RESTClient(client.Client):
    def __init__(self, error_logfile=None):
        pass

    def process_data(self, vcf_lines, variant_dc, outfile, input_format='vcf'):
        variants = ','.join(variant_dc.values())

        try:
            pass

        except:
            print(traceback.format_exc())

        return vcf_lines
