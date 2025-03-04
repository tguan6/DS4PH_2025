import pandas as pd
import streamlit as st
import urllib.request
import re
import matplotlib.pyplot as plt

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

def create_stacked_bar(imf, wb, un):
    """Create a stacked bar chart comparing GDP data"""
    # Merge data for top 10 countries
    top_countries = imf.head(10)['Country']
    merged = pd.DataFrame({
        'Country': top_countries,
        'IMF': imf.set_index('Country').loc[top_countries, 'GDP'],
        'World Bank': wb.set_index('Country').loc[top_countries, 'GDP'],
        'UN': un.set_index('Country').loc[top_countries, 'GDP']
    }).fillna(0)
    
    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    merged.set_index('Country').plot(kind='bar', stacked=True, ax=ax)
    ax.set_ylabel('GDP (USD)')
    ax.set_title('Top 10 Countries GDP Comparison (IMF, World Bank, UN)')
    ax.ticklabel_format(style='plain', axis='y')
    st.pyplot(fig)

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
        st.header("GDP Comparison (Top 10 Countries)")
        create_stacked_bar(imf, wb, un)
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()
