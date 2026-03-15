#!/usr/bin/env python3
# Documentation Section
'''
Script name: app.py
Version: 1.0
Date: 2026-03-14
Name: Maria Niki Chatzantoni

Description:
This script creates a Streamlit app that allows users to interactively explore the IBD connections between
individuals and populations in the database. Users can select specific populations or individuals, time periods, 
countries, adjust connection thresholds and generate circos plots. The app reads the database, filters data based 
on user input and generates circos plots.

Procedure:

User-defined functions: load_full_database(), load_filtered_database(), get_length_range(), get_filter_options()
Non-standard modules: streamlit, pandas, sqlite3, pycirclize, matplotlib, circos_plot

Input:
- `database_file`: The path to the input database file containing the IBD connections and group information. 
[Example: results/database/ibd_connections.db]

Output:
- An interactive Streamlit app that allows users to explore the IBD connections and generate circos plots.
'''

import streamlit as st
import pandas as pd
import tempfile
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import os
from circos_plot import parse_database, filter_by_selection, get_nodes, create_circos_plot

# load database 
@st.cache_data
def load_full_database(database_path, table_name):
    matrix_ind, matrix_pop = parse_database(database_path, min_length=0, table_name=table_name) # use the function from circos_plot to read the database
    return matrix_ind, matrix_pop

# load database with minimum length filter
@st.cache_data
def load_filtered_database(database_path, min_length, table_name):
    matrix_ind, matrix_pop = parse_database(database_path, min_length, table_name) # use the function from circos_plot to read the database with the minimum length filter
    return matrix_ind, matrix_pop

# get the min and max IBD segment length from the full data 
def get_length_range(matrix_ind):
    length_min = float(matrix_ind["lengthM"].min()) # get the minimum length 
    length_max = float(matrix_ind["lengthM"].max()) # get the maximum length
    return length_min, length_max

# get the filter options for the sidebar dropdowns and year slider
def get_filter_options(matrix_ind, matrix_pop, mode):

# if mode is individuals 
    if mode == "individuals":
        combined_nodes = pd.concat([matrix_ind["ind1"], matrix_ind["ind2"]]) # combine the ind1 and ind2 columns
# if mode is populations do the same for the group1 and group2 columns
    else:
        combined_nodes = pd.concat([matrix_pop["group1"], matrix_pop["group2"]])
    
    # remove empty values and get the unique individuals or populations 
    all_values = sorted(combined_nodes.dropna().unique())

    combined_countries = pd.concat([matrix_ind["country1"], matrix_ind["country2"]]) # combine the country1 and country2 columns 
    all_countries = sorted(combined_countries.dropna().unique()) # remove empty values and get the unique countries

    combined_years = pd.concat([matrix_ind["year1"], matrix_ind["year2"]]) # combine the year1 and year2 columns
    year_min = int(combined_years.min()) # get the minimum year and convert to int
    year_max = int(combined_years.max()) # get the maximum year and convert to int

    return all_values, all_countries, year_min, year_max

# set up the title and layout of the app
st.set_page_config(page_title="IBDConnect", layout="wide")

# write the title and description of the app
st.title("IBDConnect")
st.markdown("##### Visualizing ancient Identity by Descent connections")
st.markdown("---")

# set the sidebar for user input and settings
st.sidebar.title("Settings")
st.sidebar.markdown("Use the options below to customize your visualization.")

st.header("Welcome to IBDConnect!")
st.info("To get started, make sure you have run the pipeline first to generate the database.\n\n"
        "The database will be saved to `results/database/` by default.\n\n"
        "If you want to use your own database, change the path in the sidebar to point to your `.db` file "
        "and enter the name of the table containing your IBD connections.\n\n"
        "Your table must contain the following columns:\n\n"
        "`ind1, ind2, group1, group2, country1, country2, year1, year2, lengthM`\n\n"
        "When ready, click **Generate Circos Plot** to plot the IBD connections!")

# path to the database file 

# default is the one created by build_database.py
database_path = st.sidebar.text_input("Database path", value="results/database/ibd_connections.db",
        help="Path to the SQLite database file created by build_database.py. Change this to use your own database.")

table_name = "ibd_connections"
# user can use a different database file, but they need to specify the table name if it's not the default one
if database_path != "results/database/ibd_connections.db":
    table_name = st.sidebar.text_input("Table name", value="ibd_connections", help="Name of the table in your SQLite database")

# check if the database file exists
if not os.path.exists(database_path):
    st.error(f"Your database wasn't found at `{database_path}`. Please check the path and try again.")
    st.stop()

# load the full database to get the length range for the slider
try:
    matrix_ind_full, matrix_pop_full = load_full_database(database_path, table_name) # use the function to load the full database
except Exception as e:
    st.error(f"Could not load the database: {e}") # if can't load the database show an error message
    st.stop()

# check if the required columns are in the database
required_columns = ["ind1", "ind2", "group1", "group2", "country1", "country2", "year1", "year2", "lengthM"] 

missing_columns = [] # list to store any missing columns
# loop through the required columns
for col in required_columns:
    if col not in matrix_ind_full.columns: # if a column is missing add it to the missing columns list
        missing_columns.append(col)
# if there are missing columns show an error message 
if missing_columns:
    st.error(f"The database is missing the following required columns: {', '.join(missing_columns)}. Please check your database and try again.")
    st.stop()

# get the length range from the full data
length_min_data, length_max_data = get_length_range(matrix_ind_full)

# set up the slider for minimum IBD segment length
min_length = st.sidebar.slider("Minimum IBD segment length (cM)", min_value=length_min_data, max_value=length_max_data, value=length_min_data,
        step=0.5, help="Only show IBD connections with a total length above this threshold")

# load the filtered database based on the minimum length
try:
    # use the function to load the database with the minimum length filter
    matrix_ind, matrix_pop = load_filtered_database(database_path, min_length, table_name) 
    st.success("Filtered database loaded successfully!")
# if there is an error loading the database show an error message
except Exception as e: 
    st.error(f"Could not load the database: {e}")
    st.stop()

# set up the filters section in the sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

# mode -> individuals or populations
mode = st.sidebar.selectbox("Mode", options=["individuals", "populations"],
        help="Choose whether to visualize connections between individuals or populations")

# get the filter options based on the mode
all_values, all_countries, year_min_data, year_max_data = get_filter_options(matrix_ind, matrix_pop, mode)

# multiselect for specific individuals or populations
selected_values = st.sidebar.multiselect(f"Select specific {mode} (optional)", options=list(all_values),
        help=f"Select one or more {mode} to show only their connections. Leave empty to show all.")

# multiselect for country filter
selected_countries = st.sidebar.multiselect("Filter by country (optional)", options=list(all_countries),
        help="Select one or more countries to show only connections involving individuals from those countries. Leave empty to show all.")

# year range slider
selected_year_min, selected_year_max = st.sidebar.slider("Year range (negative = BCE, positive = CE)", min_value=year_min_data, max_value=year_max_data,
        value=(year_min_data, year_max_data), step=50, help="Filter to show only individuals dated within this time range")

# how many nodes to plot
max_nodes = st.sidebar.slider( "Maximum nodes to plot", min_value=2, max_value=200, value=50, step=10, help="Maximum number of individuals/populations to show on the circos plot")

#  if there are more nodes than max choose how to select which ones to plot
ranking_method = st.sidebar.radio( "Ranking method (applied only if nodes exceed maximum)", options=["Strongest connections (longest IBD)", "Most connected nodes (highest total IBD)"],
        help="If there are more nodes than the maximum, choose how to select which ones to plot")

st.sidebar.markdown("---")

# generate button
generate = st.sidebar.button("Generate Circos Plot")

# if the generate button is clicked we filter the data based on the user selections and generate the circos plot
if generate:
    try:
        # if the user selected individuals or populations we use them to filter
        if len(selected_values) > 0:
            use_value = selected_values
        # if not we set them to None to ignore this filter 
        else:
            use_value = None

    # we do the same for the country filter
        if len(selected_countries) > 0:
            use_country = selected_countries
        else:
            use_country = None

        # filter the data based on the user selections
        filtered = filter_by_selection( matrix_ind, matrix_pop, mode, selected_value=use_value, selected_country=use_country,
                selected_year_min=selected_year_min, selected_year_max=selected_year_max)

        # show how many connections are being plotted
        st.write(f"Showing **{len(filtered)} IBD connections** for the selected filters.")

        # create and display the circos plot
        with st.spinner("Generating circos plot, this may take a moment..."):
            fig, big, nodes, node_colors = create_circos_plot(filtered, mode, selected_value=use_value, max_nodes=max_nodes, ranking_method=ranking_method)

        st.pyplot(fig)

        if big:
            st.info(f"Too many connections!! Showing the top {max_nodes} nodes using '{ranking_method}'. "
                    f"You can adjust the number of nodes or the ranking method in the sidebar and regenerate the plot.")

    except ValueError as e:
        st.error(f"Error generating circos plot: {e}")

else:
    st.write("Use the filters in the sidebar to customize your visualization, "
             "then click **Generate Circos Plot** to view the IBD connections!")