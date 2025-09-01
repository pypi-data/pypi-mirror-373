import os, json, re
import traceback


def split_filename(input_string):
    if '.ann.' in input_string:
        return input_string.split('.ann.')[0]
    else:
        return input_string


def append_to_file(filepath, string_to_append):
    try:
        with open(filepath, 'a') as file:
            file.write(string_to_append)
        print(f"String appended to {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

def load_log_actions(logfile):
    if not os.path.isfile(logfile):
        return []

    try:
        with open(logfile, 'r') as file:
            lines = file.readlines()

        processed_lines = []
        for line in lines:
            # line = line.split("(")[0]
            processed_lines.append(line.strip())
            # print("entry: ",line.strip())

        return processed_lines
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_active_filter(directory):
    try:
        active_filter_file = directory + "/active_filter.json"
        #active_filter = json.load(active_filter_file)
        with open(active_filter_file, 'r') as file:
            active_filter = json.load(file)
    except:
        active_filter = {}
        print(traceback.format_exc())
    return active_filter


def get_active_sort(directory):
    try:
        active_sort_file = directory + "/active_filter.json"
        with open(active_sort_file, 'r') as file:
            active_sort = json.load(file)
        #active_sort = json.load(active_sort_file)
    except:
        active_sort = {}
        print(traceback.format_exc())
    return active_sort

    #active_sort_file = directory + "/active_sort.json"
    #return active_sort_file

def extract_number(file_path):
    # Split the file path to get the filename
    filename = os.path.basename(file_path)

    # Define the regular expression pattern to match the number at the beginning of the filename
    pattern = r'^(\d+)_'

    # Search for the pattern in the filename
    match = re.search(pattern, filename)

    # If a match is found, return the number; otherwise, return None
    if match:
        return int(match.group(1))
    else:
        return None

def find_file_with_highest_number(file_paths):
    highest_number = None
    highest_file = None

    for path in file_paths:
        number = extract_number(path)
        if number is not None:
            if highest_number is None or number > highest_number:
                highest_number = number
                highest_file = path

    return highest_file

def find_newest_file(directory, filter=False, include_compressed_files=False, genome_version=None):
    """
    Find the newest file in the given directory.

    :param filter: Defines whether to include filters in the returned file

    """
    try:
        # List all files in the directory
        files = [os.path.join(directory, f) for f in os.listdir(directory) if
                 os.path.isfile(os.path.join(directory, f))]

        if not files:
            print("No files found in the directory.")
            return None

        # Find the newest file based on modification time
        #print("FILES ",files)
        #for file in files:
        #    print(os.path.basename(file))
        print("files ",files)
        filtered_files = [file for file in files if os.path.basename(file) != 'log.txt']
        filtered_files = [file for file in filtered_files if os.path.basename(file) != 'filemgt.txt']
        filtered_files = [file for file in filtered_files if os.path.basename(file) != 'active_filter.json']
        filtered_files = [file for file in filtered_files if os.path.basename(file) != 'active_sort.json']

        if include_compressed_files is False:
            filtered_files = [file for file in filtered_files if not file.endswith(('.gz', '.zip', '.bz2'))]

        if genome_version is not None:
            filtered_files = [file for file in filtered_files if not file.startswith(genome_version)]

        print("files1 ",filtered_files)
        if filter is False:
            filtered_files_ann = [file for file in filtered_files if '_processed.vcf' in os.path.basename(file)]
            # if no annotations have been made yet -> go to originally uploaded file
            if (len(filtered_files_ann) == 0) and (len(filtered_files) == 1):
                pass
            elif (len(filtered_files_ann) == 0) and (len(filtered_files) > 1):
                # no annotated file => use originally uploaded file
                filtered_files = [file for file in filtered_files if '_filter.vcf' not in os.path.basename(file)]
                filtered_files = [file for file in filtered_files if '_sort.vcf' not in os.path.basename(file)]
            else:
                filtered_files = filtered_files_ann

        print("files2 ",filtered_files)

        #filename = os.path.basename(file_path)
        newest_file = find_file_with_highest_number(filtered_files)
        #newest_file = max(filtered_files, key=os.path.getmtime)

        print(f"Newest file: {newest_file}")
        return newest_file
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
