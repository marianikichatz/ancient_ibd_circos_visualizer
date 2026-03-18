#!/usr/bin/env python3
# Documentation Section
'''
Script name: circos_plot.py
Version: 1.0
Date: 2026-03-14
Name: Maria Niki Chatzantoni

Description:
This script creates circos plots for the IBD connections between individuals/populations in the database.
Users can select specific populations or individuals, adjust connection thresholds, and generate circos plots.
The script reads the database, filters data based on user input, and generates publication-quality circos plots.

Procedure:
1. Read the database
2. Create matrices for individuals and populations
3. Filter the matrices based on user selections
4. Get the nodes to plot based on the filtered data and user selection for max nodes and ranking method
5. Create circos plots for the filtered data

User-defined functions: parse_database(), filter_by_selection(), get_nodes(), normalize_data(), create_circos_plot()
Non-standard modules: pycirclize, pandas, sqlite3, matplotlib

Input:
- `database_file`: The path to the input database file containing the IBD connections and group information.
  [Example: results/database/ibd_connections.db]

Output:
- Returns filtered dataframes and circos plots to display in Streamlit.
'''

from pycirclize import Circos
import matplotlib.pyplot as plt
import holoviews as hv
from holoviews import opts
hv.extension("bokeh")
import pandas as pd
import sqlite3

# function to read the database and make the matrices for individuals and populations
def parse_database(input_file, min_length, table_name="ibd_connections"):

    # read the database file into a pandas dataframe
    conn = sqlite3.connect(input_file)
    query = f"SELECT ind1, ind2, group1, group2, country1, year1, country2, year2, lengthM FROM {table_name}"
    matrix = pd.read_sql_query(query, conn)
    conn.close()

    # make the lengthM column numeric
    matrix["lengthM"] = matrix["lengthM"].astype(float)

    # if any connection is below the minimum length we drop it from the matrix
    matrix = matrix[matrix["lengthM"] >= min_length]

    # keep all columns for both matrices and we will filter them later based on the mode 
    matrix_ind = matrix.copy()
    matrix_pop = matrix.copy()

    # for population mode, drop rows with missing group info
    matrix_pop = matrix_pop.dropna(subset=["group1", "group2"])

    return matrix_ind, matrix_pop

# function to filter the matrices based on the user"s choices
def filter_by_selection(matrix_ind, matrix_pop, mode, selected_value=None, selected_country=None, selected_year_min=None, selected_year_max=None):

# if the mode is individuals
    if mode == "individuals":
        # start with the full matrix and then filter it based on the choices of the user
        filtered = matrix_ind.copy()

        # if the user selects specific individuals we filter to keep only their connections
        if selected_value is not None and len(selected_value) > 0:
            # check if the choosen individuals are in the ind1 or ind2 columns 
            cond1 = filtered["ind1"].isin(selected_value)
            cond2 = filtered["ind2"].isin(selected_value)
            # we keep the connections where either ind1 or ind2 is in the selected individuals
            filtered = filtered[cond1 | cond2]

        # if the user selects specific countries we filter to keep only connections involving those countries
        if selected_country is not None and len(selected_country) > 0:
            # we check if the choosen countries are in the country1 or country2 columns
            cond1 = filtered["country1"].isin(selected_country)
            cond2 = filtered["country2"].isin(selected_country)
            # we keep the connections where either country1 or country2 is in the selected countries
            filtered = filtered[cond1 | cond2]

        # if the user selects a year range we filter to keep only individuals dated within that range
        if selected_year_min is not None and selected_year_max is not None:
            # we check if the year of either individual in the connection is in the selected year range
            cond1 = filtered["year1"].between(selected_year_min, selected_year_max)
            cond2 = filtered["year2"].between(selected_year_min, selected_year_max)
            # we keep the connections where either year1 or year2 is in the selected year range
            filtered = filtered[cond1 | cond2]

# if the mode is populations we do the same but for populations instead of individuals
    elif mode == "populations":
        # start with the full matrix and then filter it based on the choices of the user
        filtered = matrix_pop.copy()

        # if the user selects specific populations we filter to keep only their connections
        if selected_value is not None and len(selected_value) > 0:
            cond1 = filtered["group1"].isin(selected_value)
            cond2 = filtered["group2"].isin(selected_value)
            filtered = filtered[cond1 | cond2]

        # if the user selects specific countries we filter to keep only connections involving those countries
        if selected_country is not None and len(selected_country) > 0:
            cond1 = filtered["country1"].isin(selected_country)
            cond2 = filtered["country2"].isin(selected_country)
            filtered = filtered[cond1 | cond2]

        # if the user selects a year range we filter to keep only individuals dated within that range
        if selected_year_min is not None and selected_year_max is not None:
            cond1 = filtered["year1"].between(selected_year_min, selected_year_max)
            cond2 = filtered["year2"].between(selected_year_min, selected_year_max)
            filtered = filtered[cond1 | cond2]

    # if the mode is not valid we raise an error
    else:
        raise ValueError("Mode must be either individuals or populations. Please select a valid mode and try again.")

    # if after filtering there are no connections left we raise an error
    if filtered.empty:
        raise ValueError("No connections found for this selection. Please adjust your filters and try again.")

    return filtered

# function to get the nodes to plot based on mode, user selection and max nodes. 
# if the nodes are more than the max nodes there are two options: 
# either keep the strongest connections (longest IBD) or keep the most connected nodes (total IBD per node)
def get_nodes(filtered, mode, selected_value, max_nodes, ranking_method):
    # get the nodes from the filtered data
# if the mode is individuals
    if mode == "individuals":
        # get the names of the individuals from both ind1 and ind2 columns
        col1 = "ind1"
        col2 = "ind2"
# if the mode is populations we do the same but for populations 
    else:
        col1 = "group1"
        col2 = "group2"

    names1 = filtered[col1] # set the names from the first column (ind1 or group1) to names1
    names2 = filtered[col2] # set the names from the second column (ind2 or group2) to names2

    # combine the names from both columns
    all_names = pd.concat([names1, names2])
    nodes = sorted(all_names.unique()) # set the nodes as the unique names from both columns and sort them 
    nodes = list(nodes)

# if there are too many nodes we cut them to the max nodes

    big = False # set a flag so we know if we have to cut the nodes or not
    
    if len(nodes) > max_nodes:
        big = True # set the flag to true so we know we have to cut the nodes

        # if user choose to visualize the strongest connections 
        if ranking_method == "Strongest connections (longest IBD)":

            filtered = filtered.nlargest(max_nodes, "lengthM") 
            # get the nodes from the matrix after filtering to the strongest connections
            names1 = filtered[col1] # set the names from the first column (ind1 or group1) to names1
            names2 = filtered[col2] # set the names from the second column (ind2 or group2) to names2
            all_names = pd.concat([names1, names2]) # combine the names from both columns
            nodes = sorted(all_names.unique()) # set the nodes as the unique names from both columns and sort them

# if user choose to visualize the most connected nodes 
        else:
            sum1 = filtered.groupby(col1)["lengthM"].sum() # group by the column with the nodes and sum the lengthM for each node
            sum2 = filtered.groupby(col2)["lengthM"].sum() # group by the column with the nodes and sum the lengthM for each node
            all_nodes = sum1.add(sum2, fill_value=0) # add the sums from column 1 and column 2 to get the total IBD per node

            top = all_nodes.nlargest(max_nodes) # get the top nodes based on total IBD per node
            nodes = list(top.index) # set the nodes as the index of the top nodes
            what_keep1 = filtered[col1].isin(nodes) # check if the ind or pop in column 1 is in the top nodes
            what_keep2 = filtered[col2].isin(nodes) # same for column 2
            filtered = filtered[what_keep1 & what_keep2] # keep only the connections where both nodes are in the top nodes
            
    return nodes, filtered, big

# function to normalize the IBD values by population size
def normalize_data(df):
    norm_df = df.copy() # make a copy of the dataframe
    # count the number of individuals in each population by creating a dataframe with one row per individual and their population 
    ind_to_group = pd.concat([norm_df[["ind1", "group1"]].rename(columns={"ind1": "ind", "group1": "group"}),
        norm_df[["ind2", "group2"]].rename(columns={"ind2": "ind", "group2": "group"})]).drop_duplicates()

    pop_counts = ind_to_group["group"].value_counts() # count the number of individuals in each population

    n1 = norm_df["group1"].map(pop_counts) # get the population size for group1 by mapping the group1 column 
    n2 = norm_df["group2"].map(pop_counts) # get the population size for group2 by mapping the group2 column

    norm_df["lengthM"] = norm_df["lengthM"] / (n1 * n2) # normalize the lengthM by dividing it by the product of the population sizes 

    return norm_df

# function to create the circos plot for individuals or populations based on the mode
def create_circos_plot(filtered, mode, selected_value=None, max_nodes=50, ranking_method="Strongest connections (longest IBD)"):

# if the mode is populations 
    if mode == "populations":
        filtered = normalize_data(filtered) # normalize the IBD values by population size 

        group_cols = ["group1", "group2"] # set the group columns for grouping

        # loop through the country columns 
        for col in ["country1", "country2"]:
            # if they are in the filtered dataframe we add them to the group columns for grouping
            if col in filtered.columns:
                group_cols.append(col)
        # sum the lengthM to get the total IBD between each pair and keep the country info for each pair 
        filtered = filtered.groupby(group_cols, as_index=False)["lengthM"].sum()

    # get the nodes to plot usin gthe function above
    nodes, filtered_data, big = get_nodes(filtered, mode, selected_value, max_nodes, ranking_method)

    temp_df = filtered_data.copy() # make a copy of the filtered data for the circos plot

# if mode is individuals 
    if mode == "individuals":
        # to get unique connections we keep only the rows where ind1 is less than ind2
        remove_same = temp_df["ind1"].astype(str) < temp_df["ind2"].astype(str) 
# if mode is populations we do the same but for populations 
    else:
        remove_same = temp_df["group1"].astype(str) < temp_df["group2"].astype(str)

    unique_connections = temp_df[remove_same] # set the unique connections as the rows without the duplicate connections
    num_conn = len(unique_connections) # get the number of unique connections 

    if num_conn == 0:
        return None, False, [], [], 0

    cmap = plt.get_cmap("spring") # set colormap for the nodes and connections
    node_colors = [] # makae a list to store the colors for each node
    number_of_nodes = len(nodes) # get the number of nodes

    # loop through the nodes 
    for i in range(number_of_nodes):
        position = i / number_of_nodes # get the position of the node in the circle 
        color = cmap(position) # set the color for the node based on its position 
        node_colors.append(color) # add the color to the list of node colors

    # matrix full of 0s to store the IBD connections between the nodes
    matrix = pd.DataFrame(0.0, index=nodes, columns=nodes)

    # loop through the filtered data 
    for index, row in unique_connections.iterrows():

# for individuals
        if mode == "individuals":
            name1 = row["ind1"] # set name1 as the individual in the ind1 column
            name2 = row["ind2"] # set name2 as the individual in the ind2 column
# for populations we do the same but for populations
        else:
            name1 = row["group1"] 
            name2 = row["group2"] 

        length = row["lengthM"] # get how long the IBD connection for this row

        # if the 1st node and the 2nd node are in the list of nodes 
        if name1 in nodes and name2 in nodes:
                matrix.at[name1, name2] = length # add the length of the IBD connection to the matrix at the position of name1 and name2
    
    num_conn = len(unique_connections) # get the number of unique connections 

    number_of_nodes = len(nodes) # get the number of nodes
    space = 300/number_of_nodes # set the space between the nodes based on the number of nodes

    if space > 5: # if the space is more than 5 
        space = 5 # set it to 5 so that the plot looks better and the nodes are not too far apart
    if space < 1: # if the space is less than 1
        space = 1 # set it to 1 so that the plot looks better and the nodes are not too close 

    # set the label based on the mode
    if mode == "individuals":
        group_label = "Individuals"
    else:
        group_label = "Populations"

    # create the circos plot

    fig = plt.figure(figsize=(16, 22)) # set the figure size
    ax = fig.add_subplot(111, projection="polar") # make the plot a circular plot 

    color_dict = {} # dictionary to store the color for each node

    # loop through the nodes and their colors 
    for i in range(len(nodes)):
        node_name = nodes[i] # get the name of the node
        node_color = node_colors[i] # get the color of the node based on its position 
        color_dict[node_name] = node_color # add the color to the color dictionary with the node name as the key

    # make the circos plot using the pycirclize library
    circos = Circos.chord_diagram(matrix, space=space, cmap=color_dict, label_kws=dict(size=10, orientation="vertical"), link_kws=dict(lw=0, alpha=0.8))
    circos.plotfig(ax=ax) 
    ax.set_title(f"IBD connections — colored by {group_label}", fontsize=14, fontweight="bold", pad=350) # set the title

    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    return fig, big, nodes, node_colors, num_conn
