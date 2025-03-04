import pandas as pd
import streamlit as st
import urllib.request
import re
import plotly.express as px
from pycountry_convert import (
    country_name_to_country_alpha2,
    country_alpha2_to_continent_code,
    convert_continent_code_to_continent_name,
)

# Function to determine a country's continent
def determine_continent(country):
    """Assign a continent to a country using pycountry_convert."""
    try:
        country_code = country_name_to_country_alpha2(country)
        continent_short = country_alpha2_to_continent_code(country_code)
        return convert_continent_code_to_continent_name(continent_short)
    except:
        return "Unspecified"

# Function to retrieve and process GDP data
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
            if len(org_tables) == 3:
                break
    
    required = ['IMF', 'World Bank', 'UN']
    if not all(req in org_tables for req in required):
        # Try alternative parsing if tables are missing
        for table in tables:
            if 'World Bank' not in org_tables:
                org_tables['World Bank'] = parse_gdp_table(html, table)[1]
            if 'UN' not in org_tables:
                org_tables['UN'] = parse_gdp_table(html, table)[1]
    
    if not all(req in org_tables for req in required):
        missing = [req for req in required if req not in org_tables]
        raise ValueError(f"Missing tables: {', '.join(missing)}. Found: {', '.join(org_tables.keys())}")
    
    return (org_tables['IMF'], 
            org_tables['World Bank'], 
            org_tables['UN'])

# Function to parse GDP table
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

# Function to create a stacked bar chart
def create_stacked_bar(imf, wb, un):
    """Create a stacked bar chart comparing GDP data by continent"""
    # Merge data for top 10 countries
    top_countries = imf.head(10)['Country']
    merged = pd.DataFrame({
        'Country': top_countries,
        'IMF': imf.set_index('Country').loc[top_countries, 'GDP'],
        'World Bank': wb.set_index('Country').loc[top_countries, 'GDP'],
        'UN': un.set_index('Country').loc[top_countries, 'GDP']
    }).fillna(0)
    
    # Add continent information
    merged['Continent'] = merged['Country'].apply(determine_continent)
    
    # Melt the DataFrame for Plotly
    melted = merged.melt(id_vars=['Country', 'Continent'], value_vars=['IMF', 'World Bank', 'UN'],
                         var_name='Source', value_name='GDP')
    
    # Create stacked bar chart
    fig = px.bar(
        melted,
        x='Continent',
        y='GDP',
        color='Source',
        title='GDP Comparison by Continent (Top 10 Countries)',
        labels={'GDP': 'GDP (USD)', 'Continent': 'Continent'},
        barmode='stack'
    )
    st.plotly_chart(fig)

def main():
    st.title("GDP Data Dashboard")
    try:
        imf, wb, un = get_gdp_data()
        
        st.header("IMF GDP Rankings")
        st.dataframe(imf)
        
        st.header("World Bank GDP Rankings")
        st.dataframe(wb)
        
        st.header("UN GDP Estimates")
        st.dataframe(un)
        
        # Add stacked bar chart
        st.header("GDP Comparison by Continent (Top 10 Countries)")
        create_stacked_bar(imf, wb, un)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()
