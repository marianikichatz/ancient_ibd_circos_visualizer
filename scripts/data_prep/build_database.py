#!/usr/bin/env python3
# Documentation Section
'''
Script name: build_database.py

Version: 2.00
Date: 2026-03-11
Name: Maria Niki Chatzantoni

Description:
This script combines the two parsed output files (aadr_data.txt and ibd_pairs_raw.txt)
into a single SQLite database with a table that contains the IBD connections between 
individuals, along with their group information.

Procedure:
1. Read command line arguments and check for input files
2. Read the input files into pandas dataframes
3. Merge the dataframes to combine the IBD connections with the group, country and year information for each individual
4. Save the merged dataframe to a SQLite database

User-defined functions: get_arguments(), add_group_column(), main()
Non-standard modules: pandas, sqlite3

Table:
- `ibd_connections` [default name]: 
This table contains the IBD connections between individuals,
with columns for ind1, group1, country1, year1, ind2, group2, country2, year2, and lengthM. 

Usage:
python build_database.py table_name[optional] or
python3 build_database.py table_name[optional]
'''

import pandas as pd
import numpy as np
import sqlite3
import os
import sys
import glob

def get_arguments():

	script_name = sys.argv[0] # get the name of the script
	print(f"You are using the script: {script_name}. "
		"This script does not require any command line arguments and only takes an optional table name as an argument.\n"
		"It will read the input files from the results folder and create a database in the results/database folder.\n"
		"Thank you for your patience while the database is being built!")

	# check if the useer gave unnecessary command line arguments
	if len(sys.argv) != 1 and len(sys.argv) != 2:
		raise ValueError("This script does not require any command line arguments and only takes an optional table name as an argument.\n "
			"Please run the script without any arguments or with a single argument for the table name. Thank you!")
		
	# search for the aadr parsed output file in the results/parse_aadr folder
	aadr_search = glob.glob(os.path.join("results", "parse_aadr", "*.txt"))
	# if not found raise an error
	if not aadr_search:
		raise FileNotFoundError("No text file found in 'results/parse_aadr/'. Please run parse_aadr.py first. Thank you!")

	aadr_file = aadr_search[0] # get the first file found in the search (there should only be one file in the folder)

	# do the same for the ibd parsed output file in the results/parse_ibd folder
	ibd_search = glob.glob(os.path.join("results", "parse_ibd", "*.txt"))
	if not ibd_search:
		raise FileNotFoundError("No text file found in 'results/parse_ibd/'. Please run parse_ibd.py first. Thank you!")
	
	ibd_file = ibd_search[0]

	# set the input files 
	input_files = {"aadr_file": aadr_file, "ibd_file": ibd_file}
	 
	print(f"Input files found: \nAADR file: {aadr_file}\nIBD file: {ibd_file}\n")
	
	# set the output directory 
	output_dir = "results/database" 
	os.makedirs(output_dir, exist_ok=True)

	if len(sys.argv) == 2:
		table_name = sys.argv[1]  # get table name 
	else:
		table_name = "ibd_connections"  # set default table name

	# check if the database already exists and if yes ask the user if they want to overwrite it
	if os.path.isfile(os.path.join(output_dir, f"{table_name}.db")):
		response = input("The database already exists in the results/database folder. Do you want to overwrite it? (Y/N) ").strip().upper()
		if response != "Y":
			print("The database was not overwritten. The program will stop.")
			sys.exit(0)
		else:
			print("Overwriting existing database...")
	
	print(f"Table name: {table_name}.db")
		
	return input_files, table_name, script_name

# function for one individual column and to add its group, country and year columns
def add_group_column(ibd_df, aadr_df, individual, group_column, country_column, year_column):

	# merge ibd df with aadr df on the individual column and the Genetic ID column and add the population, country and year info for the individual
	df = ibd_df.merge(aadr_df, left_on=individual, right_on="Genetic ID", how="left") 
	df = df.drop(columns=["Genetic ID"]) # drop the Genetic ID column
	# rename the columns to the new names for group, country and year 
	df = df.rename(columns={"Group ID": group_column, "country": country_column, "year": year_column})

	return df

# main function for building the database
def main():
	try:
		# first get the input files, table name and the script name
		input_files, table_name, script_name = get_arguments()

		# set output db path
		output_dir = "results/database"
		os.makedirs(output_dir, exist_ok=True)
		db_file = os.path.join(output_dir, f"{table_name}.db")

		# read the input files
		aadr_df = pd.read_csv(input_files["aadr_file"], sep="\t")
		ibd_df = pd.read_csv(input_files["ibd_file"], sep="\t")

		# add group, country and year information for ind1 and ind2
		merged = add_group_column(ibd_df, aadr_df, "ind1", "group1", "country1", "year1")
		merged = add_group_column(merged, aadr_df, "ind2", "group2", "country2", "year2")

		# deduplicate the rows in the merged dataframe
		swap = merged["ind1"] > merged["ind2"] # swap the individuals in the pairs so that ind1 is always first alphabetically
		cols = ["ind", "group", "country", "year"] # the columns to swap for ind1 and ind2

		for col in cols:
			col1, col2 = f"{col}1", f"{col}2"
			merged.loc[swap, [col1, col2]] = merged.loc[swap, [col2, col1]].values

		# group by the merged dataframe to sum the lengthM for duplicate pairs and keep the first values for the other columns 
		merged = merged.groupby(["ind1", "ind2", "group1", "group2", "country1", "country2", "year1", "year2"], dropna=False, as_index=False)["lengthM"].sum()

		# keep only the columns we need
		merged = merged[["ind1", "group1", "country1", "year1", "ind2", "group2", "country2", "year2", "lengthM"]]

		print(f"Combined table has {len(merged)} rows")

		# save to sqlite database
		print(f"Building SQLite database: {table_name}.db. You can find it in the results/database folder")
		conn = sqlite3.connect(db_file)
		merged.to_sql(table_name, conn, if_exists="replace", index=False)
		conn.close()

		# if there are any missing info we print a message regarding that and how many individuals have missing info
		missing_group = merged["group1"].isnull().sum() + merged["group2"].isnull().sum()

		if missing_group > 0:
			print(f"There is some missing information for some individuals in the database.\n"
				"This is because we don't have complete data for all individuals in the AADR data. They are shown as NULL in the database.\n"
				f"Rows with missing group: {missing_group}.")

		print(f"Database successfully created at {table_name}.db\nThank you for using the script!")

	except Exception as e:
		print("An error occurred:", e)

if __name__ == "__main__":
	main()
