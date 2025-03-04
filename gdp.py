import pandas as pd
import streamlit as st

def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    
    # Directly read tables with pandas
    tables = pd.read_html(url)
    
    # Extract relevant tables by position
    imf_df = tables[0].iloc[:, :3]
    wb_df = tables[1].iloc[:, :3]
    un_df = tables[2].iloc[:, :2]

    # Clean data
    for df in [imf_df, wb_df, un_df]:
        if df.shape[1] == 3:
            df.columns = ['Country/Territory', 'GDP', 'Year']
        else:
            df.columns = ['Country/Territory', 'GDP']
        
        df['GDP'] = df['GDP'].astype(str).str.replace(r'[^\d.]', '', regex=True).astype(float)
    
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
