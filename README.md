# Project: Visualize ancient IBD connections using circos plots 

*Author: Maria Niki Chatzantoni*

*Class: BINP29*

*Date: March 2026*

# Scope 

This project aims to visualize ancient Identity by Descent (IBD) connections using circos plots. IBD refers to segments of DNA that are inherited from a common ancestor, and visualizing these connections can provide insights into population history and genetic relationships.

# Data

The data used in this project can be found here: [IBD Data](https://zenodo.org/records/8417049)

The dataset contains identity by descent (IBD) segments identified in 4,248 ancient individuals. 

Each row represents an genomic segment shared between two individuals that is inherited from a common ancestor.  

The metadata about the individuals and their Master IDs can be found here: [Metadata](https://static-content.springer.com/esm/art%3A10.1038%2Fs41588-023-01582-w/MediaObjects/41588_2023_1582_MOESM4_ESM.xlsx)

Lastly, the AADR (Ancient Admixture and Relatedness) data, which informs about the populations of the individuals depending on their Master IDs, can be found here: [AADR Data](https://lunduniversityo365-my.sharepoint.com/personal/er2374el_lu_se/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fer2374el%5Flu%5Fse%2FDocuments%2FStudents%2FBINP29%20%2D%20DNA%20Sequencing%20Informatics%20II%2FStudent%20projects%2FProjetcFiles%2FAADR%5F54%2E1&viewid=31986752%2D1a4a%2D4d9b%2D995e%2Db5bbf4dec0b9),  under the name `AADR Annotations 2025.xlsx`

# Software used and Dependencies

Python version 3.10 or higher is required to run the scripts in this project.

Need to install the following Python libraries:
- pandas
- openpyxl
- pycirclize
- matplotlib
- numpy

# Scripts

- `parse_ibd.py`: A Python script that parses the IBD data and extracts the pairs of individuals and their corresponding IBD segment lengths in centiMorgans (cM). The script takes an input TSV file containing the IBD data and produces an output file with the parsed information.
- `parse_metadata.py`: A Python script that parses the metadata and finds the master id for each individual. The script takes an input Excel file containing the metadata and produces an output file with the parsed information.
- `parse_aadr.py`: A Python script that parses the AADR data and converts it into a format with information about individuals and their population, country and year. The script takes an input Excel file containing the AADR data and produces an output file with the parsed information.
- `build_database.py`: A Python script that takes the parsed IBD, metadata, and AADR files and builds a SQLite database. The script merges the information from the three input files based on the individual IDs and creates a database with a table containing the columns: ind1, group1, country1, year1, ind2, group2, country2, year2, and lengthM.
- `circos_plot.py`: A Python script that reads the SQLite database created by `build_database.py` and generates circos plots to visualize the IBD connections between individuals and populations. The script allows for filtering the connections based on various criteria such as population, country, year, and minimum IBD segment length.

# Workflow

1. Run `parse_ibd.py` to parse the IBD data and create an output file with the relevant information.
2. Run `parse_metadata.py` to parse the metadata and create an output file with the master IDs for each individual.
3. Run `parse_aadr.py` to parse the AADR data and create an output file with the population, country and year information for each individual.
4. Run `build_database.py` to merge the parsed IBD, metadata, and AADR files and create a SQLite database with the combined information.
5. `circos_plot.py` contains the functions used to read the database, filter the data, and generate the circos plots. These functions are imported and used by the Streamlit app.



