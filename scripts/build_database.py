#!/usr/bin/env python3

'''

Script name: build_database.py

Version: 1.00
Date: 2026-03-11
Name: Maria Niki Chatzantoni

Description:
This script combines the three parsed output files (aadr_data.txt, metadata.txt, ibd_pairs_raw.txt)
into a single SQLite database with a table that contains the IBD connections between 
individuals, along with their group information.

User-defined functions: get_arguments(), add_group_column(), main()
Non-standard modules: pandas, sqlite3

Table:
- `ibd_connections` [default name]: 
This table contains the IBD connections between individuals,
with columns for ind1, group1, ind2, group2, and lengthM. 

Usage:
python build_database.py table_name[optional] or
python3 build_database.py table_name[optional]
'''

import pandas as pd
import sqlite3
import os
import sys

def get_arguments():

	script_name = sys.argv[0] # get the name of the script
	print(
		f"You are using the script: {script_name}. "
		"This script does not require any command line arguments and only takes an optional table name as an argument.\n"
		"It will read the input files from the results folder and create a database in the results/database folder.\n"
		"Thank you for your patience while the database is being built!"
	)

	# check if the useer gave unnecessary command line arguments
	if len(sys.argv) != 1 and len(sys.argv) != 2:
		raise ValueError(
			"This script does not require any command line arguments and only takes an optional table name as an argument.\n "
			"Please run the script without any arguments or with a single argument for the table name. Thank you!"
		)
		
	
	# set the input files
	input_files = {'aadr_file': "results/parse_aadr/aadr_data.txt", 'metadata_file': "results/parse_metadata/metadata.txt",
		'ibd_file': "results/parse_ibd/ibd_pairs_raw.txt"}
	
	# check if the input files exist
	for file in input_files.values():

		# if a file doesn't exist raise an error
		if not os.path.isfile(file):
			raise FileNotFoundError(f"Input file {file} not found. Please make sure you read the README and"
             "run the parsing scripts to create the input files.\n Thank you!")
	
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
		if response != 'Y':
			print("The database was not overwritten. The program will stop.")
			sys.exit(0)
		else:
			print("Overwriting existing database...")
	
	print(f"Table name: {table_name}.db")
		
	return input_files, table_name, script_name

# function for one individual column and to add its group column
def add_group_column(ibd_df, metadata_df, aadr_df, individual, group_column):

	column = f"{individual}" # name of the column with the individual (ind1 or ind2)
	column_master_id = f"{individual}_master_id" # name of the column with the Master ID for the individual

	# merge the df with the metadata to get the Master ID for each individual
	# we merge on the individual column (ind1 or ind2) and the 'ind' column in the metadata
	# we keep all rows from the ibd data even if we don't find a match in the metadata
	df = ibd_df.merge(metadata_df, left_on=individual, right_on='ind', how='left')
	
	# rename the Master ID column to be specific for the individual 
	df = df.rename(columns={'Master ID': column_master_id})

	# we drop the ind column as we have the specific individual column 
	df = df.drop(columns=['ind'])

	# merge the df with the aadr data to get the group information for each individual
	# we merge on the Master ID column for the individual and the 'Master ID' column in the aadr data
	# we keep all rows from the ibd data even if we don't find a match in the aadr data
	df = df.merge(aadr_df, left_on=column_master_id, right_on='Master ID', how='left')

	# rename the Group ID column to be specific for the individual 
	df = df.rename(columns={'Group ID': group_column})

	# we drop the Master ID column as we have the specific group column
	df = df.drop(columns=['Master ID', column_master_id])

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
		aadr_df = pd.read_csv(input_files['aadr_file'], sep='\t')
		metadata_df = pd.read_csv(input_files['metadata_file'], sep='\t')
		ibd_df = pd.read_csv(input_files['ibd_file'], sep='\t')

		# add group information for ind1 and ind2
		merged = add_group_column(ibd_df, metadata_df, aadr_df, 'ind1', 'group1')
		merged = add_group_column(merged, metadata_df, aadr_df, 'ind2', 'group2')

		# keep only the columns we need
		merged = merged[['ind1', 'group1', 'ind2', 'group2', 'lengthM']]

		print(f"Combined table has {len(merged)} rows")

		# save to sqlite database
		print(f"Building SQLite database: {table_name}.db. You can find it in the results/database folder")
		conn = sqlite3.connect(os.path.join("results/database", table_name + ".db"))
		merged.to_sql(table_name, conn, if_exists="replace", index=False)
		conn.close()

		# if there are any missing info we print a message regarding that and how many individuals have missing info
		if merged['group1'].isnull().sum() + merged['group2'].isnull().sum() > 0: 
			missing_rows = merged['group1'].isnull().sum() + merged['group2'].isnull().sum()
			print(f"There is some missing group information for some individuals in the database.\n"
				"This is because we don't have group information for all individuals in the AADR data. They are shown as NULL in the database.\n"
				f"The number of rows with missing group information is {missing_rows}.")

		print(f"Database successfully created at {table_name}.db\nThank you for using the script!")

	except Exception as e:
		print("An error occurred:", e)

if __name__ == "__main__":
	main()
