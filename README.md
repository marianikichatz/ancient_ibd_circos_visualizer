# Project: Visualize ancient IBD connections using circos plots 

*Author: Maria Niki Chatzantoni*

*Class: BINP29*

*Date: March 2026*

# Scope 

This project aims to visualize ancient Identity by Descent (IBD) connections using circos plots. IBD refers to segments of DNA that are inherited from a common ancestor, and visualizing these connections can provide insights into population history and genetic relationships.

# Data

The data used in this project can be found here: [IBD Data](https://zenodo.org/records/8417049)

The dataset contains identity by descent (IBD) segments identified in 4,248 ancient individuals. 

Each row represents a genomic segment shared between two individuals that is inherited from a common ancestor.  

The AADR (Ancient Admixture and Relatedness) data, which informs about the populations of the individuals depending on their Genetic IDs, can be found here: [AADR Data](https://lunduniversityo365-my.sharepoint.com/personal/er2374el_lu_se/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fer2374el%5Flu%5Fse%2FDocuments%2FStudents%2FBINP29%20%2D%20DNA%20Sequencing%20Informatics%20II%2FStudent%20projects%2FProjetcFiles%2FAADR%5F54%2E1&viewid=31986752%2D1a4a%2D4d9b%2D995e%2Db5bbf4dec0b9),  under the name `AADR Annotations 2025.xlsx`

# Software used and Dependencies

Python version 3.10 or higher is required to run the scripts in this project.

Need to install the following Python libraries:
- pandas
- openpyxl
- pycirclize
- matplotlib
- numpy
- streamlit

You can install these libraries in a conda environment using the following command:

```bash
conda create -n ibdconnect python=3.10
conda activate ibdconnect
pip install pandas openpyxl pycirclize matplotlib numpy streamlit
```
Or if you want to be even cleaner, use the `install.sh` script instead, which can be found in the project repository, under `scripts/requirements/`. You can install the dependencies using the following command:

```bash
bash scripts/requirements/install.sh
```

# Scripts

- `parse_ibd.py`: A Python script that parses the IBD data and extracts the pairs of individuals and their corresponding IBD segment lengths in centiMorgans (cM). The script takes an input TSV file containing the IBD data and produces an output file with the parsed information.
- `parse_aadr.py`: A Python script that parses the AADR data and converts it into a format with information about individuals and their population, country and year. The script takes an input Excel file containing the AADR data and produces an output file with the parsed information.
- `build_database.py`: A Python script that takes the parsed IBD, metadata, and AADR files and builds a SQLite database. The script merges the information from the three input files based on the individual IDs and creates a database with a table containing the columns: ind1, group1, country1, year1, ind2, group2, country2, year2, and lengthM.
- `circos_plot.py`: A Python script that reads the SQLite database created by `build_database.py` and generates circos plots to visualize the IBD connections between individuals and populations. The script allows for filtering the connections based on various criteria such as population, country, year, and minimum IBD segment length.
- `app.py`: A Streamlit application that provides an interactive interface for users to explore the IBD connections visualized in the circos plots. The app allows users to select different filtering options and view the corresponding circos plots.

# Project Structure
```
ancient_ibd_circos_visualizer/
├──.streamlit/
│   └── config.toml # Streamlit configuration file
├── data
│   ├── AADR_Annotations_2025.xlsx # raw AADR data
│   └── ibd_data.tsv # raw IBD data
├── results
│   ├── database
│   │   └── ibd_connections.db # SQLite database 
│   ├── parse_aadr
│   │   └── aadr_data.txt # parsed AADR data
│   └── parse_ibd
│       └── ibd_pairs_raw.txt # parsed IBD data
├── scripts
│   ├── app
│   │   ├── app.py # Streamlit app to visualize the circos plots
│   │   └── circos_plot.py # script with circos plot functions
│   ├── data_prep
│   │   ├── build_database.py # script to build the SQLite database
│   │   ├── parse_aadr.py # script to parse the AADR data
│   │   └── parse_ibd.py # script to parse the IBD data
│   └── requirements
│       └── install.sh # script to install required Python packages
├── .gitignore
└── README.md 
```

# Workflow

1. Run `parse_ibd.py` to parse the IBD data and create an output file with the relevant information.
2. Run `parse_aadr.py` to parse the AADR data and create an output file with the population, country and year information for each individual.
3. Run `build_database.py` to merge the parsed IBD and AADR files and create a SQLite database with the combined information.
4. `circos_plot.py` contains the functions used to read the database, filter the data, and generate the circos plots. These functions are imported and used by the Streamlit app.
5. Run `app.py` to start the Streamlit application and explore the IBD connections visualized in the circos plots.

# Example of usage

To run the pipeline, you can use the following commands in your terminal:

```bash
# Step 1: Parse the IBD data
python scripts/data_prep/parse_ibd.py data/ibd_data.tsv 
# Step 2: Parse the AADR data
python scripts/data_prep/parse_aadr.py data/AADR_Annotations_2025.xlsx
# Step 3: Build the SQLite database
python scripts/data_prep/build_database.py results/parsed_ibd/ibd_pairs_raw.txt results/parsed_aadr/aadr_data.txt 
# Step 4: Run the Streamlit app to visualize the circos plots
streamlit run scripts/app/app.py
```
# Output
The output of the project includes:
- Parsed IBD data in a text file.
- Parsed AADR data in a text file.
- A SQLite database containing the merged information from the IBD and AADR data.
- Circos plots visualizing the IBD connections between individuals and populations, accessible through the Streamlit application.

# Limitations and Future Work
## Limitations:
- The app may be slow with very large datasets since all filtering and plotting is done in memory
- Population normalization in population mode assumes each individual belongs to exactly one population, which may not always be the case
- The app currently only supports SQLite databases built with the provided pipeline — custom databases must follow the exact column structure
- The circos plot is limited to a maximum of 200 nodes per plot due to rendering constraints in pycirclize 
## Future Work:
- Add support for exporting the filtered data as a CSV file so researchers can do further analysis
- Add a summary statistics panel showing the number of connections, average IBD length, and most connected individuals/populations
- Add a map visualization showing the geographic distribution of the connections based on country information
- Support multiple database files so users can compare different datasets side by side

# Conclusion
This project provides a pipeline for visualizing ancient IBD connections using circos plots. By parsing the IBD and AADR data, building a database, and creating a Streamlit application, users can explore the genetic relationships between ancient individuals and populations in a user-friendly and easy way. 

# Acknowledgements
- The IBD data was obtained from the Zenodo repository: [IBD Data](https://zenodo.org/records/8417049)
- The AADR data was obtained from the Lund University OneDrive: [AADR Data](https://lunduniversityo365-my.sharepoint.com/personal/er2374el_lu_se/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fer2374el%5Flu%5Fse%2FDocuments%2FStudents%2FBINP29%20%2D%20DNA%20Sequencing%20Informatics%20II%2FStudent%20projects%2FProjetcFiles%2FAADR%5F54%2E1&viewid=31986752%2D1a4a%2D4d9b%2D995e%2Db5bbf4dec0b9)
- The Python libraries used in this project include pandas, openpyxl, pycirclize, matplotlib, numpy, and streamlit.

*If you have any questions, suggestions, or run into any issues, feel free to open an issue on the repository. Happy exploring!*