#!/usr/bin/env python3
#Documentation Section
'''
Script name: parse_aadr.py

Version: 2.00
Date: 2026-03-10
Name: Maria Niki Chatzantoni

Description:
This script parses AADR (Ancient Admixture and Relatedness) data from a specified input file 
and converts it into a format with information about individuals and their populations. 
The script reads the AADR data, processes it, and outputs a file that can be used for further analysis.

Procedure:
1. Read command line arguments to get the input file and output file paths
2. Parse the AADR data to extract Genetic ID, Group ID, country, and year
3. Write the parsed data to a tab separated output file

Input:
- `input_file`: The path to the input Excel file containing AADR data. [Example: aadr.xlsx]

Output:
- `output_file`: The path to the output file where the parsed AADR data will be written. [Example: results/parse_aadr/aadr_data.txt]

Useage:
python parse_aadr.py input_file.xlsx output_file.txt[optional] or 
python3 parse_aadr.py input_file.xlsx output_file.txt[optional] 
'''

import numpy as np
import pandas as pd
import sys
import os

# function to get the arguments from the command line and check if they are valid
def get_arguments():

    # check if the number of arguments is correct
    if len(sys.argv) != 3 and len(sys.argv) != 2:
        raise ValueError("Wrong number of arguments! The correct usage is: python parse_aadr.py input_file.xlsx [output_file.txt]")

    script_name = sys.argv[0] # get the name of the script
    input_file = sys.argv[1]  # get the name of the input file
    
    # check if the input file is an .xlsx file
    if input_file.endswith(".xlsx"):
        pass
    else:
        raise ValueError("The input file must be an .xlsx file. Please provide a valid .xlsx file as input. Thank you!")

    # set output directory and output file name
    output_dir = os.path.join("results", "parse_aadr")

    if len(sys.argv) == 3:
        output_name = os.path.basename(sys.argv[2])  # get the name of the output file from the command line argument
    else:
        output_name = "aadr_data.txt"  # set default output file name

    # set the full path for the output file
    output_file = os.path.join(output_dir, output_name)  

    # create the output directory if it doesn"t exist
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

def parse_aadr_data(input_file):

    # we check the first 3 rows for a valid header with Master ID and iid
    check_df = pd.read_excel(input_file, header=None, nrows=3)
    header_row = None # set a flag to check if we found the header row

    # loop through the first 3 rows and check if they have the Master ID and iid columns 
    for row in range(len(check_df)):
        # make all values in the row lowercase and remove leading and trailing whitespaces
        row_values = check_df.iloc[row].astype(str).str.strip().str.lower().tolist()
        
        # check if the row has the Genetic ID and Group ID columns 
        if "genetic id" in row_values and "group id" in row_values:
            header_row = row # set the header row to the current row 
            break

    # if we don"t find the Genetic ID and Group ID columns in the first 3 rows we raise an error       
    if header_row is None:
        raise ValueError("Couldn"t find "Genetic ID" and "Group ID" in the first 3 rows of the file. Please provide a valid input file with the required columns. Thank you!")

    # read the excel file with the correct header row
    df = pd.read_excel(input_file, header=header_row)

    # clean the data
    df["Genetic ID"] = df["Genetic ID"].astype(str).str.strip()
    df["Political Entity"] = df["Political Entity"].astype(str).str.strip()
    df["Political Entity"] = df["Political Entity"].str.replace("Gernamy", "Germany", case=False) # fix typo in country name

    # clean the Group ID column by removing any suffixes that indicate family relationships, removing the .SG suffix that indicates shotgun sequencing data
    # removing the .DG suffix that indicates double capture data, removing the .possible suffix that indicates possible contamination 
    # and removing the .LHO001 suffix that indicates a specific individual that is not assigned to a group
    tags_to_remove = r"[_.]?(mother|father|son|daughter|brother|sister|sibling|relative|rel|dup|contam|possible|1d|2d|LHO001|SG|DG|enhanced|noUDG|genotyping|in\.preparation).*"
    df["Group ID"] = (df["Group ID"].astype(str).str.strip().str.replace(tags_to_remove, "", regex=True, case=False))

    df["Group ID"] = (df["Group ID"].replace(["I","","nan","None","NULL"], np.nan)) # replace empty strings and other values with NaN

    # check if required columns are here
    required_columns = ["Genetic ID", "Group ID", "Political Entity"]

    for column in required_columns:
        column = column.strip().lower() # remove leading and trailing whitespaces and make lowercase
        if column not in df.columns.str.strip().str.lower():
            raise ValueError(f"The input file must contain the following columns: {", ".join(required_columns)}. Please provide a valid input file. Thank you!")

    # find the BP date column by searching for the column that starts with "Date mean in BP"
    date_col = None
    for col in df.columns:
        if str(col).strip().startswith("Date mean in BP"):
            date_col = col
            break
    
    if date_col is None:
        raise ValueError("Could not find the "Date mean in BP" column in the input file. Please provide a valid input file. Thank you!")

    genetic_id = df["Genetic ID"] # get the Genetic ID column from the dataframe
    group_id = df["Group ID"] # get the Group ID column from the dataframe
    country = df["Political Entity"].str.strip() # get the country column from the dataframe
    
    # convert BP (years before 1950) to actual year: actual_year = 1950 - BP
    # negative values mean BCE, positive mean CE
    date_bp = pd.to_numeric(df[date_col], errors="coerce")
    year = 1950 - date_bp

    # create a dictionary to store the parsed AADR data
    aadr_dict = {}

    # loop through the rows of the dataframe and add the genetic id, group id, country and year to the dictionary
    for i in range(len(genetic_id)):
        aadr_dict[genetic_id[i]] = {"Group ID": group_id[i], "country": country[i], "year": year[i]}
    
    return aadr_dict

# function to write the output to a file
def write_output(aadr_dict, output_file):
    with open(output_file, "w") as f:
        f.write("Genetic ID\tGroup ID\tcountry\tyear\n") # write the header
        for genetic_id, values in aadr_dict.items():
            f.write(f"{genetic_id}\t{values["Group ID"]}\t{values["country"]}\t{values["year"]}\n") # write the data
    
    return output_file

# main function:
def main():
    try:
        # first get the arguments from the command line
        script_name, input_file, output_file = get_arguments()

        # we parse the AADR data and get the group id for every master id
        aadr_dict = parse_aadr_data(input_file)

        # write the output file
        output_file = write_output(aadr_dict, output_file)

        print(f"The AADR data was successfully parsed and written to {output_file}. It can be found in the results/parse_aadr directory. Thank you for using this script!")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

