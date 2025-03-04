import pandas as pd
import streamlit as st
import urllib.request
import re

def parse_wiki_table(html, table_index):
    # Extract table content using regex
    tables = re.findall(r'<table class="wikitable".*?>(.*?)</table>', html, re.DOTALL)
    table_content = tables[table_index]
    
    # Parse rows and cells
    rows = re.findall(r'<tr>(.*?)</tr>', table_content, re.DOTALL)
    data = []
    for row in rows:
        cells = re.findall(r'<t[hd].*?>(.*?)</t[hd]>', row, re.DOTALL)
        cleaned = [re.sub(r'\s+', ' ', re.sub(r'<.*?>|\[.*?\]|,|\$', '', cell)).strip() 
                  for cell in cells]
        data.append(cleaned)
    
    # Create DataFrame from first 3 columns
    df = pd.DataFrame(data[1:], columns=data[0][:3]).iloc[:, :2]
    df.columns = ['Country/Territory', 'GDP']
    df['GDP'] = pd.to_numeric(df['GDP'].str.replace(r'[^\d.]', '', regex=True), errors='coerce')
    return df

def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    
    return (
        parse_wiki_table(html, 0),
        parse_wiki_table(html, 1),
        parse_wiki_table(html, 2)
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
