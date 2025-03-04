import pandas as pd
import streamlit as st
import urllib.request
import re

def parse_gdp_table(html, table_content):
    """Parse individual GDP table with validation"""
    # Parse organization from header
    header = re.search(r'<th colspan="\d".*?>(.*?)</th>', table_content, re.DOTALL)
    org = header.group(1) if header else ''
    
    # Match specific titles (IMF, UN, World Bank)
    if 'IMF' in org:
        org_match = 'IMF'
    elif 'World Bank' in org:
        org_match = 'World Bank'
    elif 'United Nations' in org or 'UN' in org:
        org_match = 'UN'
    else:
        return None, None
    
    # Parse rows and cells
    rows = re.findall(r'<tr>(.*?)</tr>', table_content, re.DOTALL)
    data = []
    for row in rows:
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL)
        cleaned = [
            re.sub(r'\s+', ' ', re.sub(r'<.*?>|\[.*?\]|,|\$|US', '', cell)).strip()
            for cell in cells
        ]
        if len(cleaned) >= 2 and not any('world' in cell.lower() for cell in cleaned):
            data.append(cleaned[:2])  # Keep only country and GDP

    if len(data) < 2:
        return None, None
    
    # Create DataFrame
    df = pd.DataFrame(data[1:], columns=["Country", "GDP"])
    df["GDP"] = pd.to_numeric(
        df["GDP"].str.replace(r'[^\d.]', '', regex=True), 
        errors='coerce'
    ).dropna()
    
    return org_match, df

def get_gdp_data():
    """Fetch and parse GDP tables with organization detection"""
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    
    # Find all candidate tables
    tables = re.findall(r'<table[^>]*class="wikitable[^>]*>.*?</table>', html, re.DOTALL)
    
    # Parse and identify tables
    org_tables = {}
    for table in tables:
        org, df = parse_gdp_table(html, table)
        if org and df is not None:
            org_tables[org] = df
            if len(org
