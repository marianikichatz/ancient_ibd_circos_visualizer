'''
Script name: plotCircos.py
Version: 1.0
Date: 2026-03-12
Name: Maria Niki Chatzantoni

Description:
This script creates interactive circos plots for the IBD connections between individuals/populations in the database.
Users can select specific populations or individuals, adjust connection thresholds, and generate circos plots.
The script reads the database, filters data based on user input, and generates publication-quality circos plots.

User-defined functions: parse_database(), filter_by_selection(), create_circos_plot()
Non-standard modules: pycirclize, pandas, sqlite3, matplotlib

Input:
- `database_file`: The path to the input database file containing the IBD connections and group information.
  [Example: results/database/ibd_connections.db]

Output:
- Returns filtered dataframes and circos plots for display in Streamlit.

'''

from pycirclize import Circos
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3


# function to read the database and create the matrices for individuals and populations
def parse_database(input_file, min_length):

    # read the database file into a pandas dataframe
    conn = sqlite3.connect(input_file)
    query = "SELECT ind1, ind2, group1, group2, country1, year1, country2, year2, lengthM FROM ibd_connections"
    matrix = pd.read_sql_query(query, conn)
    conn.close()

    # make the lengthM column numeric
    matrix["lengthM"] = matrix["lengthM"].astype(float)

    # if any connection is below the minimum length we drop it from the matrix
    matrix = matrix[matrix["lengthM"] >= min_length]

# matrix for individuals and their connections
    # keep all columns for both matrices for flexible filtering and metadata use
    matrix_ind = matrix.copy()
    matrix_pop = matrix.copy()
    # for population mode, drop rows with missing group info
    matrix_pop = matrix_pop.dropna(subset=["group1", "group2"])
    return matrix_ind, matrix_pop

# function to filter the matrices based on the user selections
def filter_by_selection(matrix_ind, matrix_pop, mode, selected_value=None, selected_country=None, selected_year_min=None, selected_year_max=None):

# if the mode is individuals 

    if mode == "individuals":
        filtered = matrix_ind.copy() # create a copy of the matrix to filter
        
        # if the user selects a specific individual we filter the matrix to keep only the connections of that individual
        if selected_value is not None and selected_value != "":
            filtered = filtered[(filtered["ind1"] == selected_value) | (filtered["ind2"] == selected_value)]

        # if the user selects a specific country we filter the matrix to keep only the connections of that country
        if selected_country is not None and selected_country != "":
            filtered = filtered[(filtered["country1"] == selected_country) | (filtered["country2"] == selected_country)]

        # if the user selects a specific year range we filter the matrix to keep only the connections of that year range
        if selected_year_min is not None and selected_year_max is not None:
            filtered = filtered[((filtered["year1"] >= selected_year_min) & (filtered["year1"] <= selected_year_max)) |
                ((filtered["year2"] >= selected_year_min) & (filtered["year2"] <= selected_year_max))]

# if the mode is populations

    elif mode == "populations":

        filtered = matrix_pop.copy() # create a copy of the matrix to filter
        
        # if the user selects a specific population we filter the matrix to keep only the connections of that population
        if selected_value is not None and selected_value != "":
            filtered = filtered[(filtered["group1"] == selected_value) | (filtered["group2"] == selected_value)]
        
        # if the user selects a specific country we filter the matrix to keep only the connections of that country
        if selected_country is not None and selected_country != "":
            filtered = filtered[(filtered["country1"] == selected_country) | (filtered["country2"] == selected_country)]
        
        # if the user selects a specific year range we filter the matrix to keep only the connections of that year range
        if selected_year_min is not None and selected_year_max is not None:
            filtered = filtered[((filtered["year1"] >= selected_year_min) & (filtered["year1"] <= selected_year_max)) |
                ((filtered["year2"] >= selected_year_min) & (filtered["year2"] <= selected_year_max))]
   
    else:
        raise ValueError("Mode must be either individuals or populations. Please select a valid mode and try again.")

    # if after filtering there are no connections left we raise an error 
    if filtered.empty:
        raise ValueError("No connections found for this selection. Please adjust your filters and try again.")
    
    return filtered


# function to create the circos plot for individuals or populations based on the mode
def create_circos_plot(filtered, mode):

    # save a copy before groupby for the country matrix later
    filtered_og = filtered.copy()

# if the mode is individuals

    if mode == "individuals":
        # use the individual ids as nodes for the circos plot
        nodes = sorted(pd.concat([filtered["ind1"], filtered["ind2"]]).unique())
    else:
        # if the mode is populations use the population ids as nodes for the circos plot
        # we group by the population pairs and sum the lengthM values to get the total connection 
        filtered = filtered.groupby(["group1", "group2"], as_index=False)["lengthM"].sum()
        nodes = sorted(pd.concat([filtered["group1"], filtered["group2"]]).unique())

    # symmetric matrix for the connections between individuals or populations
    matrix = pd.DataFrame(0.0, index=nodes, columns=nodes)

    # loop through the filtered matrix and fill the connection values in the symmetric matrix
    for i, data in filtered.iterrows():
        # if the mode is individuals we fill the matrix with the lengthM values for the connections between individuals
        if mode == "individuals": 
            matrix.at[data["ind1"], data["ind2"]] += data["lengthM"]
            matrix.at[data["ind2"], data["ind1"]] += data["lengthM"]
        else:
            # if the mode is populations we fill the matrix with the lengthM values for the connections between populations
            matrix.at[data["group1"], data["group2"]] += data["lengthM"]
            matrix.at[data["group2"], data["group1"]] += data["lengthM"]

# do the same for the countries 

    # group by the country pairs and sum the lengthM values to get the total connection between countries
    add_countries = filtered_og.groupby(["country1", "country2"], as_index=False)["lengthM"].sum()
    # get the unique countries as nodes for the country matrix
    countries = sorted(pd.concat([add_countries["country1"], add_countries["country2"]]).unique())

    # symmetric matrix for the connections between countries
    country_matrix = pd.DataFrame(0.0, index=countries, columns=countries)
    for i, data in add_countries.iterrows():
        country_matrix.at[data["country1"], data["country2"]] += data["lengthM"]
        country_matrix.at[data["country2"], data["country1"]] += data["lengthM"]

# create the circos plot

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 9)) # have 2 plots side by side

    # set the group label based on the mode for the title of the plot
    if mode == "individuals":
        group_label = "Individuals"
    else:
        group_label = "Populations"
    
    # make the plot for the connections between individuals or populations 
    circos1 = Circos.chord_diagram(matrix, space=5, cmap="Set3", label_kws=dict(size=12), link_kws=dict(ec="black", lw=0.5, direction=1))
    circos1.plotfig(ax=ax1)
    ax1.set_title(f"IBD connections — colored by {group_label}", fontsize=11, pad=10)

    # make the plot for the connections between countries
    circos2 = Circos.chord_diagram(country_matrix, space=5, cmap="Pastel2",
        label_kws=dict(size=12), link_kws=dict(ec="black", lw=0.5, direction=1))
    circos2.plotfig(ax=ax2)
    ax2.set_title("IBD connections — colored by country", fontsize=11, pad=10)

    fig.tight_layout() # fix the layout to not have overlap 

    return fig

