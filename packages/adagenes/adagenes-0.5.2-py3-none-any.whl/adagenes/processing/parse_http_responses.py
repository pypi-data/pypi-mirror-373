import traceback, datetime
import adagenes


def parse_module_response(q, variant_data, url_pattern, genome_version, srv_prefix, qid_dc):
    """

    :param q:
    :param variant_data:
    :param json_body:
    :param url_pattern:
    :param genome_version:
    :param srv_prefix:
    :return:
    """
    try:
        json_body = adagenes.tools.module_requests.get_connection(q, url_pattern, genome_version)

        for key in json_body.keys():
            json_obj = json_body[key]
            qid = key

            try:
                if "Score" in json_obj:
                    if json_obj['Score'] != '':
                        json_obj['score_percent'] = int(float(json_obj['Score']) * 100)
                    else:
                        json_obj['score_percent'] = 0
                # json_obj.pop('q_id')
                #variant_data[qid][srv_prefix] = json_obj[srv_prefix]
                if qid in qid_dc.keys():
                    qid_orig = qid_dc[qid]
                else:
                    qid_orig = qid
                variant_data[qid_orig][srv_prefix] = json_obj[srv_prefix]
            except:
                cur_dt = datetime.datetime.now()
                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
    except:
        print(": error processing variant response: ;", traceback.format_exc())

    return variant_data