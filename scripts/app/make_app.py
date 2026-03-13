#!/usr/bin/env python3

# Documentation Section

'''

Script name: make_app.py
Version: 1.0
Date: 2026-03-12
Name: Maria Niki Chatzantoni

Description:
This script creates a Streamlit app that allows users to interactively explore the IBD connections between
individuals and populations in the database. Users can select specific populations or individuals, time periods, 
countries, adjust connection thresholds and generate circos plots. The app reads the database, filters data based 
on user input and generates circos plots.

User-defined functions: 
Non-standard modules: streamlit, pandas, sqlite3, pycirclize, matplotlib, circos_plot

Input:
- `database_file`: The path to the input database file containing the IBD connections and group information. 
[Example: results/database/ibd_connections.db]

Output:
- An interactive Streamlit app that allows users to explore the IBD connections and generate circos plots.

'''

import streamlit as st
import pandas as pd
from circos_plot import parse_database, filter_by_selection, create_circos_plot
 
st.set_page_config( page_title="IBDConnect", page_icon="🫆", layout="wide")

