import pandas as pd
import streamlit as st
import urllib.request
import re

def get_gdp_data():
    """Fetch and parse GDP tables from Wikipedia"""
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    
    # Simple table extraction using regex
    tables = re.findall(r'<table[^>]*class="wikitable".*?>(.*?)</table>', html, re.DOTALL)
    
    # Parse first 3 tables
    dfs = []
    for table_html in tables[:3]:
        df = pd.read_html(table_html)[0]
        # Clean data
        df.columns = [col.split('[')[0].strip() for col in df.columns]
        df['GDP'] = df.iloc[:, 1].replace({r'[^\d.]': ''}, regex=True).astype(float)
        df = df[['Country/Territory', 'GDP']].dropna()
        dfs.append(df)
    
    return dfs[0], dfs[1], dfs[2]

def create_stacked_bar(imf, wb, un):
    """Create stacked bar chart using Streamlit's native functions"""
    # Merge data for top 10 countries
    top_countries = imf.head(10)['Country/Territory']
    merged = pd.DataFrame({
        'Country': top_countries,
        'IMF': imf.set_index('Country/Territory').loc[top_countries, 'GDP'],
        'World Bank': wb.set_index('Country/Territory').loc[top_countries, 'GDP'],
        'UN': un.set_index('Country/Territory').loc[top_countries, 'GDP']
    }).fillna(0).set_index('Country')
    
    # Display as stacked bar chart
    st.bar_chart(merged)

def main():
    st.title("GDP Data Dashboard")
    try:
        imf, wb, un = get_gdp_data()
        
        st.header("IMF Data")
        st.dataframe(imf)
        
        st.header("World Bank Data")
        st.dataframe(wb)
        
        st.header("UN Data")
        st.dataframe(un)
        
        st.header("GDP Comparison (Top 10 Countries)")
        create_stacked_bar(imf, wb, un)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
