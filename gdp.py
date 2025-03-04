import pandas as pd
import streamlit as st
import urllib.request
import re

def parse_gdp_table(html, table_num):
    """Parse Wikipedia tables using pure Python/regex"""
    # Extract table content
    tables = re.findall(r'<table class="wikitable".*?>(.*?)</table>', html, re.DOTALL)
    table_content = tables[table_num]
    
    # Parse rows and cells
    rows = re.findall(r'<tr>(.*?)</tr>', table_content, re.DOTALL)
    data = []
    for row in rows:
        cells = re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', row, re.DOTALL)
        cleaned = [
            re.sub(r'\s+', ' ', re.sub(r'<.*?>|\[.*?\]|,|\$|US', '', cell)).strip()
            for cell in cells
        ]
        if len(cleaned) >= 2:
            data.append(cleaned[:2])  # Keep only country and GDP
    
    # Create DataFrame
    df = pd.DataFrame(data[1:], columns=["Country", "GDP"])
    df["GDP"] = pd.to_numeric(
        df["GDP"].str.replace(r'[^\d.]', '', regex=True), 
        errors='coerce'
    )
    return df.dropna()

def get_gdp_data():
    """Fetch and parse GDP data without external dependencies"""
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    
    return (
        parse_gdp_table(html, 0),
        parse_gdp_table(html, 1),
        parse_gdp_table(html, 2)
    )

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
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()
