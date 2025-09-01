import adagenes.app.db_client

def generate_report(qid, filter_model, sort_model):
    modified_lines = []

    conn = adagenes.app.db_client.DBConn(qid)
    header_lines = conn.get_header_lines(qid)
    if "genome_version" in header_lines:
        genome_version = header_lines["genome_version"]
    else:
        genome_version = "hg38"
    modified_lines.append("Genome version" + ',' + str(genome_version))

    print("report header ",filter_model)

    # genome version

    # annotations
    if "annotations" in header_lines:
        annotations = header_lines["annotations"]
    else:
        annotations = ""
    modified_lines.append("Annotations: " + str(annotations))

    # filter option
    modified_lines.append("Filter options: " + str(filter_model))

    # sort option
    modified_lines.append("Sorting: " + str(sort_model))

    conn.close_connection()
    modified_content = '\n'.join(modified_lines).encode('utf-8')

    return modified_content

def modify_content(lines):
    # Split the content into lines


    # Process each line to strip everything after '::'
    #modified_lines = [line.split('::')[0] for line in lines]
    modified_lines = []
    for line in lines:
        newline = ''
        action = line.split('::')
        if len(action) > 1:
            newline += action[0]
        else:
            newline += action
        #sort_filter_content = line.split(';;')
        #if len(sort_filter_content) > 1:
        #    newline += "::" + sort_filter_content[1]

        modified_lines.append(newline)

    # Join the modified lines back into a single string
    modified_content = '\n'.join(modified_lines).encode('utf-8')

    return modified_content
