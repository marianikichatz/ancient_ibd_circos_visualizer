#!/usr/bin/env python3

#Documentation Section

'''

Script name: parse_metadata.py

Version: 1.00
Date: 2026-03-10
Name: Maria Niki Chatzantoni

Description:
This script parses metadata from a specified input file and finds the master id for each individual. 
The script reads the metadata, processes it, and outputs a file that can be used for further analysis.

Procedure:
1. Read command line arguments
2. Parse the metadata 
3. Write the output file with the individual and their master id

User-defined functions: get_arguments(), parse_metadata(), write_output(), main()
Non-standard modules: pandas

Input:
- `input_file`: The path to the input Excel file containing metadata. [Example: metadata.xlsx]

Output:
- `output_file`: The path to the output file where the parsed metadata will be written. [Example: results/parse_metadata/metadata.txt]

Useage:
python parse_metadata.py input_file.xlsx output_file.txt[optional] or 
python3 parse_metadata.py input_file.xlsx output_file.txt[optional] 

'''

import pandas as pd
import sys
import os

# function to get the arguments from the command line and check if they are valid
def get_arguments():

    # check if the number of arguments is correct
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        raise ValueError("Wrong number of arguments! The correct usage is: python parse_metadata.py input_file.xlsx [output_file.txt]")

    script_name = sys.argv[0] # get the name of the script
    input_file = sys.argv[1]  # get the name of the input file
    
    # check if the input file is a .tsv file
    if input_file.endswith('.xlsx'):
        pass
    else:
        raise ValueError("The input file must be a .xlsx file. Please provide a valid .xlsx file as input. Thank you!")

     # set output directory and output file name
    output_dir = os.path.join("results", "parse_metadata")

    # if the user provided an output file name we use it, otherwise we use the default 
    if len(sys.argv) == 3:
        output_name = os.path.basename(sys.argv[2])
    else:
        output_name = "metadata.txt"
    
    # set the full path for the output file
    output_file = os.path.join(output_dir, output_name)

    # create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # check if the output file already exists and if yes ask the user if they want to overwrite it
    if os.path.exists(output_file):
        response = input("Hey, the output file already exists. Do you want to overwrite it? (Y/N): ").strip().upper()
        if response != "Y":
            print("The output file was not overwritten. The program will stop.")
            sys.exit(0)
        else:
            print("Overwriting existing file...")
    
    print("Python script name:", script_name) 
    print("Input file names:", input_file)
    print("Output file name:", output_file)

    return script_name, input_file, output_file

# function to parse the metadata and create a dictionary with the master id for each individual
def parse_metadata(input_file):

    # we check the first 3 rows for a valid header with Master ID and iid
    check_df = pd.read_excel(input_file, header=None, nrows=3)
    header_row = None # set a flag to check if we found the header row

    # loop through the first 3 rows and check if they have the Master ID and iid columns 
    for row in range(len(check_df)):
        # make all values in the row lowercase and remove leading and trailing whitespaces
        row_values = check_df.iloc[row].astype(str).str.strip().str.lower().tolist()
        
        # check if the row has the Master ID and iid columns 
        if 'master id' in row_values and 'iid' in row_values:
            header_row = row # set the header row to the current row 
            break

    # if we don't find the Master ID and iid columns in the first 3 rows we raise an error       
    if header_row is None:
        raise ValueError("Couldn't find 'Master ID' and 'iid' in the first 3 rows of the file. Please provide a valid input file with the required columns. Thank you!")

    # read the excel file with the correct header row
    df = pd.read_excel(input_file, header=header_row)

    # check if required columns are here
    required_columns = ['Master ID', 'iid']
    
    for column in required_columns:
        column = column.strip().lower() # remove leading and trailing whitespaces and make lowercase
        if column not in df.columns.str.strip().str.lower():
            raise ValueError(f"The input file must contain the following columns: {', '.join(required_columns)}. Please provide a valid input file. Thank you!")
    
    ind = df['iid'] # get the iid column from the dataframe
    master_id = df['Master ID'] # get the Master ID column from the dataframe

    master_id_dict = {} # make an empty dictionary to store the master id for each individual

    # loop through the iid and master id columns and add the master id for each individual to the dictionary
    for i in range(len(ind)):
        master_id_dict[ind[i]] = master_id[i]

    return master_id_dict

# function to write the output to a file
def write_output(master_id_dict, output_file):
    with open(output_file, 'w') as f:
        f.write("ind\tMaster ID\n") # write the header
        for ind, master_id in master_id_dict.items():
            f.write(f"{ind}\t{master_id}\n") # write the individual and their master id to the output file
    
    return output_file

def main():

    # first we get the arguments from the command line
    script_name, input_file, output_file = get_arguments()

    # we parse the metadata and get the master id for each individual
    master_id_dict = parse_metadata(input_file)

    # we write the output to a file
    output_file = write_output(master_id_dict, output_file)

    print(f"The parsed metadata has been written to {output_file} and can be found in the results/parse_metadata directory. Thank you for using this script!")

if __name__ == "__main__":
    main()
    