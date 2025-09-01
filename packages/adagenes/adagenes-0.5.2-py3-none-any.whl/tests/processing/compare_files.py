
def skip_header_lines(file):
    """
    Skips lines starting with '#' and returns the first non-header line.
    """
    for line in file:
        if not line.strip().startswith('#'):
            return line
    return None

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def write_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(lines)

def get_first_five_columns(line):
    line = line.strip()
    if not line.startswith("#"):
        columns = line.split('\t')
        return tuple(columns[:5])

def read_and_compare_files(file1_path, file2_path, unique_file1_path, unique_file2_path):
    try:
        linenum=0
        with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2, \
                open(unique_file1_path, 'w') as unique_file1, open(unique_file2_path, 'w') as unique_file2:

            # Skip header lines in both files
            line1 = skip_header_lines(file1)
            line2 = skip_header_lines(file2)

            # Compare lines until one of the files is exhausted
            while line1 is not None and line2 is not None:
                linenum +=1
                if get_first_five_columns(line1) != get_first_five_columns(line2):
                    unique_file1.write(str(linenum) + ": " + line1)
                    unique_file2.write(str(linenum) + ": " + line2)

                # Read the next non-header line from both files
                line1 = skip_header_lines(file1)
                line2 = skip_header_lines(file2)

            # Handle the case where files have different lengths
            while line1 is not None:
                unique_file1.write(str(linenum) + ": " + line1)
                line1 = skip_header_lines(file1)

            while line2 is not None:
                unique_file2.write(str(linenum) + ": " + line2)
                line2 = skip_header_lines(file2)

        print(f"Unique lines from {file1_path} written to {unique_file1_path}")
        print(f"Unique lines from {file2_path} written to {unique_file2_path}")

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    file1_path = '/home/nadine/workspace/phd/git/vcfcli/vcfcli/adagenes/conf/uploaded_files/2986632239881/hg38_somaticMutations.l520.vcf'
    file2_path = '/home/nadine/workspace/phd/git/vcfcli/vcfcli/adagenes/conf/uploaded_files/2986632239881/hg38_somaticMutationsl520_hgvs_1.vcf'
    unique_file1_path = '/home/nadine/workspace/phd/git/vcfcli/vcfcli/adagenes/conf/uploaded_files/2986632239881/uniquefile1.txt'
    unique_file2_path = '/home/nadine/workspace/phd/git/vcfcli/vcfcli/adagenes/conf/uploaded_files/2986632239881/uniquefile2.txt'

    read_and_compare_files(file1_path, file2_path, unique_file1_path, unique_file2_path)

if __name__ == "__main__":
    main()
