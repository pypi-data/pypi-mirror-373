import base64
import datetime
import io, re, gzip, os
import adagenes as ag
import zipfile
import tarfile
import gzip
import bz2


def uncompress_file(infile):
    """
    Uncompresses a packaged file

    :param infile:
    :return:
    """
    file_name, file_extension = os.path.splitext(infile)
    input_format_recognized = file_extension.lstrip(".")
    file_extension = os.path.splitext(infile)[1].lower()
    print("Uncompress ",file_extension)

    if file_extension == '.zip':
        with zipfile.ZipFile(infile, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(infile))
    elif file_extension in ['.tar.gz', '.tgz']:
        with tarfile.open(infile, 'r:gz') as tar_ref:
            tar_ref.extractall(os.path.dirname(infile))
    elif file_extension == '.tar.bz2':
        with tarfile.open(infile, 'r:bz2') as tar_ref:
            tar_ref.extractall(os.path.dirname(infile))
    elif file_extension == '.gz':
        with gzip.open(infile, 'rb') as f_in:
            with open(infile[:-3], 'wb') as f_out:
                f_out.write(f_in.read())
    elif file_extension == '.bz2':
        with bz2.open(infile, 'rb') as f_in:
            with open(infile[:-4], 'wb') as f_out:
                f_out.write(f_in.read())


def remove_column_def_duplicates(column_defs):
    seen = set()
    unique_list = []

    for col in column_defs:
        field = col['field']
        if field not in seen:
            seen.add(field)
            unique_list.append(col)
    return unique_list

def get_column_definition(header_line, column_defs, columns):
    """
    Parses annotation definitions in INFO header lines and adds them to the lists column_defs and columns

    :param header_line:
    :param column_defs:
    :param columns:
    :return:
    """
    if header_line.startswith('##INFO'):
        # Extract the INFO field definition
        match = re.match(r'##INFO=<ID=([^,]+),Number=([^,]+),Type=([^,]+),Description="([^"]+)"', header_line)
        if match:
            column_id, number, type_, description = match.groups()

            # Determine the filter type based on the Type field
            #print("LOADED field ",column_id," type ",type_)
            if type_ in ['Integer', 'Float']:
                filter_type = 'agNumberColumnFilter'
            else:
                filter_type = 'agTextColumnFilter'

            column_id_lower = column_id.lower()
            # if column_id_lower in bframe.data[var]["info_features"].keys():
            #   dc[column_id] = bframe.data[var]["info_features"][column_id_lower]

            # Create the dictionary for the INFO feature
            inf_column = {
                'headerName': column_id,
                'field': column_id_lower,
                'filter': filter_type,
                'floatingFilter': 'true',
                'minWidth': 200  # You can adjust the minWidth as needed
            }
            # print("add column from header: ", inf_column)

            # info_features.append(info_feature)
            if column_id not in columns:
                column_defs.append(inf_column)
                columns.append(column_id_lower)
        else:
            # print("no match ",header_line)
            pass
    return column_defs, columns

