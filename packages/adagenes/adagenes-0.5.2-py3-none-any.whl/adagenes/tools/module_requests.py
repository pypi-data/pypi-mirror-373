import requests, datetime, copy, re, json, math
import adagenes.tools.hgvs_re
import adagenes as ag


def get_connection(variants, url_pattern, genome_version, headers=None, verbose=True):
    """
        Requests a module over a HTTP GET request

        :param variants:
        :param url_pattern:
        :param genome_version:
        :param headers: HTTP request header
        :return:
    """
    url = url_pattern.format(genome_version) + variants
    try:
        if headers is None:
            r = requests.get(url, timeout=60)
            if verbose:
                print(r.elapsed," , ",url)
        else:
            r = requests.get(url, headers=headers, timeout=60)
            if verbose:
                print(r.elapsed," , ",url)
    except:
        print("Error ",url)
        return {}
    return r.json()


def handle_non_compliant_floats(obj):
    if isinstance(obj, float):
        if math.isnan(obj):
            return None  # or any appropriate default value
        if math.isinf(obj):
            return None  # or any appropriate default value
    raise TypeError

def post_connection_params(params, url, tumor_type=None):
    """
        Requests a module over a HTTP POST request

        :param biomarker_data:
        :param url:
        :param genome_version:
        :return:
        """
    if tumor_type is not None:
        params['tumor_type'] = tumor_type
    print(url)
    r = requests.post(url, params=params)
    print(r.elapsed, " , ", url)
    return r.text

def post_connection(biomarker_data, url, genome_version, tumor_type=None, type=None):
    """
    Requests a module over a HTTP POST request

    :param biomarker_data:
    :param url:
    :param genome_version:
    :return:
    """
    if tumor_type is not None:
        params = {
            'tumor_type': tumor_type
        }
        print(url)
        #json_data = json.dumps(biomarker_data, default=str)
        json_data = json.dumps(biomarker_data, default=handle_non_compliant_floats)
        r = requests.post(url, params=params, json=json_data)
    else:
        print(url)
        json_data = json.dumps(biomarker_data, default=handle_non_compliant_floats)
        r = requests.post(url, json = json_data)
    print(r.elapsed, " , ", url)
    return r.text


def query_service(vcf_lines, variant_dc, outfile, extract_keys, srv_prefix, url_pattern, genome_version, qid_key="q_id", error_logfile=None):
    variants = ','.join(variant_dc.values())

    try:
        json_body = get_connection(variants, url_pattern, genome_version)

        # for i, l in enumerate(variant_dc.keys()):
        for i, l in enumerate(json_body):
            if json_body[i]:
                annotations = []

                if qid_key not in json_body[i]:
                    continue
                qid = json_body[i][qid_key]

                for k in extract_keys:
                    if k in json_body[i]:
                        annotations.append('{}-{}={}'.format(srv_prefix, k, json_body[i][k]))

                try:
                    splits = vcf_lines[qid].split("\t")
                    splits[7] = splits[7] + ";" + ';'.join(annotations)
                    vcf_lines[qid] = "\t".join(splits)
                except:
                # print("error in query response ",qid,'  ,',variant_dc)
                    if error_logfile is not None:
                        cur_dt = datetime.datetime.now()
                        date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                        print(cur_dt, ": error processing variant response: ", qid, file=error_logfile)

    except:
        # print("error in whole service query ",variant_dc)
        if error_logfile is not None:
            print("error processing request: ", variants, file=error_logfile)

    for line in vcf_lines:
        print(vcf_lines[line], file=outfile)


def generate_variant_dictionary(variant_data):
    variant_dc = {}
    for i,genompos in enumerate(variant_data.keys()):
        variant_dc[i] = genompos

    return variant_dc


def filter_wildtype_variants(json_obj: dict) -> dict:
    """
    Returns the variant object that contains only variants

    :param json_obj:
    :return:
    """
    new_list = []
    for var in json_obj.keys():
        req = ag.get_variant_request_type(var)
        #print(var,": ",req)
        if ">" in var:
            #print(json_obj[var].keys())
            if "variant_data" in json_obj[var]:
                #print(json_obj[var]["variant_data"])
                if "ALT" in json_obj[var]["variant_data"]:
                    #print("ok0 ",json_obj[var]["variant_data"])
                    #print("filter wildtype json obj ",json_obj[var])
                    alt = json_obj[var]["variant_data"]["ALT"]
                    if alt != ".":
                        #print("alt ",var)
                        new_list.append(var)
                elif "alt" in json_obj[var]:
                    #print("ok1 ",json_obj[var]["variant_data"])
                    alt = json_obj[var]["alt"]
                    if alt != ".":
                        new_list.append(var)
                elif "POS2" in json_obj[var]["variant_data"]:
                    if json_obj[var]["variant_data"]["POS2"] != "":
                        new_list.append(var)
                elif "pos2" in json_obj[var]["variant_data"]:
                    if json_obj[var]["variant_data"]["pos2"] != "":
                        new_list.append(var)
            else:
                chr, ref_seq, pos, ref, alt = adagenes.parse_genome_position(var)
                #print("els ",var,": ",chr, ", ",ref_seq,", ",pos,", ",ref,", ",alt)
                if (alt != ".") and (alt is not None):
                    #print("alt2 ",alt)
                    new_list.append(var)
        else:
            new_list.append(var)
    #print("new list ",new_list)
    json_obj_variants = { key: json_obj[key] for key in new_list if key in json_obj }
    return json_obj_variants


def filter_alternate_alleles(variant_data_keys):
    """
    Filters variants with multiple alternate alleles

    :param variant_data_keys:
    :return:
    """
    var_list = []
    for var in variant_data_keys:
        if '>' in var:
            alt = var.split(">")[1]
            if "," not in alt:
                var_list.append(copy.deepcopy(var))
            else:
                print("alt allele: ",alt)
        elif '%3E' in var:
            alt = var.split("%3E")[1]
            if "," not in alt:
                var_list.append(copy.deepcopy(var))
            else:
                print("alt allele: ",alt)
        else:
            var_list.append(copy.deepcopy(var))
    return var_list


def filter_unparseable_variants(variant_data_keys):
    """
    Filters out genomic locations that are not parseable by the Onkopus clients

    :param variant_data_keys:
    :return:
    """
    var_list = []
    pattern = re.compile(adagenes.tools.gencode.exp_genome_positions)
    for var in variant_data_keys:
        if pattern.match(var):
            var_list.append(var)
        else:
            print("No parseable variant: ",var)
    return var_list
