#!/usr/bin/env python3

#Documentation Section

'''

Script name: parse_ibd.py

Version: 1.00
Date: 2026-03-09
Name: Maria Niki Chatzantoni

Description: 
This script is designed to parse IBD (Identity by Descent) data
from a specified input file and convert it into a format suitable
for later analysis. The script reads the IBD data, processes it
and outputs a file that can be used for further analysis.

Procedure:
1. Read command line arguments  
2. Parse the IBD data
3. Write the output file with the pairs and their lengths in cM

User-defined functions: get_arguments(), parse_ibd(), write_output(), main()
Non-standard modules: pandas

Input:
- `input_file`: The path to the input TSV file containing IBD data. [Example: ibd220.ibd.v54.1.pub.tsv]
Output:
- `output_file`: The path to the output file where the parsed IBD pairs and their lengths in cM will be written. [Example: results/parse_ibd/ibd_pairs_raw.txt]

Useage: 
python parse_ibd.py ibd220.ibd.v54.1.pub.tsv output_file.txt[optional] or
python3 parse_ibd.py ibd220.ibd.v54.1.pub.tsv output_file.txt[optional] 

'''

import pandas as pd
import sys
import os

# function to get the arguments from the command line and check if they are valid
def get_arguments():

    # check if the number of arguments is correct
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        raise ValueError("Wrong number of arguments! The correct usage is: python parse_ibd.py input_file.tsv [output_file.txt]")

    script_name = sys.argv[0] # get the name of the script
    input_file = sys.argv[1]  # get the name of the input file
    
    # check if the input file is a .tsv file
    if input_file.endswith('.tsv'): 
        pass
    else:
        raise ValueError("The input file must be a .tsv file. Please provide a valid .tsv file as input. Thank you!")

    # set output directory and output file name
    output_dir = os.path.join("results", "parse_ibd")

    # if the user provided an output file name we use it, otherwise we use the default 
    if len(sys.argv) == 3:
        output_name = os.path.basename(sys.argv[2])
    else:
        output_name = "ibd_pairs_raw.txt"

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

# function to parse the ibd data and create a dictionary with the pairs and their lengths
def parse_ibd(input_file, output_file):

    # check if the input file is tab separated and if it has the required columns
    with open(input_file, 'r') as f:
        header = f.readline().strip().split('\t') # read the header and split by tab
        required_columns = ['iid1', 'iid2', 'lengthM'] # define the required columns
        
        # check if the needeed columns are in the header
        for column in required_columns:
            if column not in header:
                raise ValueError(f"The input file must contain the following columns: {', '.join(required_columns)}. Please provide a valid input file. Thank you!")

    # read the input file using pandas 
    df = pd.read_csv(input_file, sep='\t') # seperate by tab
    # get the columns of the individuals and length in cM
    ind1 = df['iid1']
    ind2 = df['iid2']
    length_cm = df['lengthM']
    # if the pair is repeated we will add the lengths together
    ibd_pairs = {} # dictionary to store the pairs and their lengths
    # loop trhough the rows of the dataframe 
    for i in range(len(ind1)): 
        # make a dictionary for the pair and their length 
        pair = {ind1[i]: {ind2[i]: length_cm[i]}} 
        # if the pair is repeated we will add the lengths together
        # check if ind1 is already in the dictionary
        if ind1[i] in ibd_pairs: 
            
            # check if ind2 is the value of ind1 in the dictionary
            if ind2[i] in ibd_pairs[ind1[i]]: 
                ibd_pairs[ind1[i]][ind2[i]] += length_cm[i] # add the length to the existing length
            
            # if ind2 is not in the dictionary we will add it as the value of ind1 
            # and the length as the value of ind2
            else:
                ibd_pairs[ind1[i]][ind2[i]] = length_cm[i]
        
        # if ind1 is not in the dictionary we will add it as a key 
        # and the value will be a dictionary with ind2 as the key and the length as the value
        else:
            ibd_pairs[ind1[i]] = {ind2[i]: length_cm[i]}
    
    return ibd_pairs

# function to write the output file
def write_output(ibd_pairs, output_file):
    with open(output_file, 'w') as f:
        f.write("ind1\tind2\tlengthM\n") # write the header
        for ind1, second_dict in ibd_pairs.items():
            for ind2, length in second_dict.items():
                # write the pair and their length to the output file
                f.write(f"{ind1}\t{ind2}\t{length}\n") 
    
    return output_file

# main function 
def main():
    try:
        # first get the arguments from the command line
        script_name, input_file, output_file = get_arguments()

        # parse the ibd data and create a dictionary with the pairs and their lengths
        ibd_pairs = parse_ibd(input_file, output_file)

        # write the output file
        output_file = write_output(ibd_pairs, output_file)

        print(f"IBD pairs and their lengths have been successfully written to {output_file} and can be found in the results/parse_ibd directory. Thank you for using this script!")

    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    main()

