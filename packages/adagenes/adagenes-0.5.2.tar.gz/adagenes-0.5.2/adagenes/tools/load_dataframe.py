import traceback
import numpy as np
import pandas as pd

import adagenes.app.app_parse_data


def split_key_value_pairs(df, column_index):
    key_value_column = df.iloc[:, column_index - 1]

    new_columns = {}

    for index, row in key_value_column.items():
        pairs = row.split(';')

        row_dict = {}
        for pair in pairs:
            elements = pair.split('=')
            if len(elements) > 1:
                key, value = pair.split('=')
                row_dict[key] = value

        new_columns[index] = row_dict

    new_df = pd.DataFrame.from_dict(new_columns, orient='index')
    result_df = pd.concat([df, new_df], axis=1)
    return result_df


def load_dataframe(infile):
    """

    :param infile:
    :return:
    """

    if infile.endswith("vcf"):
        lines = []
        columns = []
        column_defs = []
        header_lines = []
        annotation_columns = []

        with open(infile, 'r') as file:
            for line in file:
                if line.startswith("##"):
                    header_lines.append(line.strip())

                    # Read column definitions
                    column_defs, columns = adagenes.app.app_parse_data.get_column_definition(line.strip(),column_defs, columns)

                elif line.startswith("#"):
                    if line.startswith(("#CHROM")):
                        #columns = line.lstrip('#').strip().split("\t")
                        header_lines.append(line.strip())
                        #for column in columns:
                        #    if column not in annotation_columns:
                        #        annotation_columns.append(column)

                else:
                    #lines = [line for line in file if not line.startswith('#')]
                    #lines.append(line.strip())
                    elements = line.strip().split('\t')
                    info_col = elements[7]
                    annos = info_col.split(';')
                    for anno in annos:
                        anno_els = anno.split('=')
                        if len(anno_els) == 2:
                            key = anno_els[0]
                            #if key not in annotation_columns:
                            #    annotation_columns.append(key)

        #annotation_columns = columns
        annotation_columns = []
        for col_dc in column_defs:
            col_orig = col_dc["headerName"]
            annotation_columns.append(col_orig)
        print("annotation columns ",annotation_columns)
        # Create a DataFrame from the lines

        #lines = []
        #for line in lines:
        #    elements = line.strip.split('\t')
        #    info_col = elements[7]
        #    annos = info_col.split(";")
        #    for anno in annos:
        #        anno_els = anno.split("=")
        #        if len(anno_els) ==2:
        #            key,val = anno_els[0], anno_els[1]
        #            if key not in annotation_columns:
        #                annotation_columns.add[key]
        #df = pd.DataFrame([line.strip().split('\t') for line in lines])


        # Sort the annotation columns to maintain consistent order
        #annotation_columns.sort()

        # Second pass: build the data matrix
        data = []
        with open(infile, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue  # Skip header lines
                elements = line.strip().split('\t')
                # Extract the first 7 columns
                row = elements[:7]

                row[0] = row[0].replace("chr","")

                # Extract annotations
                info_col = elements[7]
                annos = info_col.split(';')
                # Create a dictionary for annotations
                anno_dict = {}
                for anno in annos:
                    anno_els = anno.split('=')
                    if len(anno_els) == 2:
                        key, val = anno_els
                        anno_dict[key] = val
                for col in annotation_columns:
                    #print("col in annodict ",col,": ",anno_dict)
                    if col in anno_dict.keys():
                        anno_val = anno_dict[col]
                    else:
                        anno_val = ''
                    row.append(anno_val)

                # Add each annotation value to the row
                #for col in annotation_columns:
                #    row.append(anno_dict.get(col, ''))  # Use empty string if annotation is missing
                data.append(row)

        # Create the DataFrame
        #columns = elements[:7] + annotation_columns
        columns = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER'] + annotation_columns
        #columns = annotation_columns
        #print("columns ",columns)
        #print("DF data ",data)
        df = pd.DataFrame(data, columns=columns)

        # Assign column names based on the header line (assuming the header is the first non-comment line)
        #header = lines[0].strip().split('\t')
        #print("header ",columns, " shape ",df.shape)
        if columns != []:
            #if len(columns) > 8:
            #    columns = columns[0:7]

            df.columns = columns
        else:
            df.columns = ["CHROM","POS","ID","REF","ALT","QUAL","FILTER","INFO"]

        #print("df ",df.columns, "data: ",df)
        #df = split_key_value_pairs(df, 8)
        #df = df.fillna('')
        #df = df.fillna('')
        df = df.replace('.', '')

        #column_defs.append({"field":"CHROM", "filter":"agNumberColumnFilter"})
        column_defs.append({"field": "POS", "filter": "agNumberColumnFilter"})
        column_defs.append({"field":"pos_hg19", "filter": "agNumberColumnFilter"})
        column_defs.append({"field": "pos_hg38", "filter": "agNumberColumnFilter"})

        for column in column_defs:
            data_type = column["filter"]
            if "headerName" in column:
                col = column["headerName"]
                #print("data type of ",col,": ",data_type)
                if col in df.columns:
                    if data_type == "agNumberColumnFilter":
                        print("numeric column ",col)
                        try:
                            #pass
                            df[col] = df[col].replace('', '') #np.nan)
                            df[col] = df[col].replace('.', '')# np.nan)
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                            df[col] = df[col].astype(float)
                        except:
                            print(traceback.format_exc())
                else:
                    raise ValueError(f"Column '{col}' not found in DataFrame.")

        return df, header_lines

def dataframe_to_vcf(df, header_lines, output_file):
    """
    Converts a pandas DataFrame into a VCF file.

    Parameters:
        df (pd.DataFrame): Input DataFrame. First 7 columns correspond to VCF required columns,
                           and additional columns correspond to INFO fields.
        output_file (str): Path to the output VCF file.
    """

    print("sorted df to file: ",df)

    # Open the output file and write the header
    with open(output_file, 'w') as f:
        for line in header_lines:
            f.write(line + '\n')

        for index, row in df.iterrows():
            # Extract first 7 mandatory VCF columns
            chrom, pos, vid, ref, alt, qual, filt = row.iloc[:7]

            # Build the INFO field from the remaining columns
            info_fields = []
            for col in df.columns[7:]:
                if col != "INFO":
                    #print("info features ", col, ": ", row[col])
                    value = row[col]
                    #if pd.notna(value):  # Only include non-NaN values
                    info_fields.append(f"{col}={value}")

            info = "" if not info_fields else ";".join(info_fields)

            # Write the VCF row
            f.write(f"{chrom}\t{pos}\t{vid}\t{ref}\t{alt}\t{qual}\t{filt}\t{info}\n")
