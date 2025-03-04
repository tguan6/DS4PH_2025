import pandas as pd
import streamlit as st
import requests

try:
    from bs4 import BeautifulSoup
except ModuleNotFoundError:
    st.error("The required module `beautifulsoup4` is missing. Please add `beautifulsoup4` to `requirements.txt` and redeploy.")

def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    
    # Manual HTML parsing
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all tables
    tables = []
    for table in soup.find_all('table', {'class': 'wikitable'}):
        df = pd.read_html(str(table))[0]
        tables.append(df)
    
    # Extract relevant tables
    imf_df = tables[0].iloc[:, :3]
    wb_df = tables[1].iloc[:, :3]
    un_df = tables[2].iloc[:, :2]

    # Clean data
    for df in [imf_df, wb_df, un_df]:
        df.columns = ['Country/Territory', 'GDP', 'Year'] if df.shape[1] == 3 else ['Country/Territory', 'GDP']
        df['GDP'] = df['GDP'].astype(str).str.replace(r'[\$,a-zA-Z]', '', regex=True).astype(float)
    
    return imf_df, wb_df, un_df

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
        st.error(f"An error occurred while fetching GDP data: {e}")

if __name__ == "__main__":
    main()
