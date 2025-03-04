import pandas as pd
import streamlit as st
import urllib.request
import re

def get_gdp_data():
    """Fetch and parse GDP tables from Wikipedia with error handling"""
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            
        # Find tables with GDP data using more specific pattern
        tables = re.findall(r'<table class="wikitable sortable".*?>(.*?)</table>', html, re.DOTALL)
        
        if len(tables) < 3:
            st.error(f"Found only {len(tables)} GDP tables. Expected at least 3.")
            return None, None, None
            
        # Parse tables with error handling
        dfs = []
        required_columns = ['Country/Territory', 'GDP']
        
        for table_html in tables[:3]:
            try:
                df = pd.read_html(table_html)[0]
                
                # Clean and standardize columns
                df.columns = [col.split('[')[0].strip() for col in df.columns]
                df = df.rename(columns={
                    'Country or territory': 'Country/Territory',
                    'Estimate': 'GDP'
                })
                
                # Convert GDP to numeric
                if 'GDP' in df.columns:
                    df['GDP'] = (
                        df['GDP']
                        .astype(str)
                        .str.replace(r'[^\d.]', '', regex=True)
                        .astype(float)
                        .dropna()
                    )
                    dfs.append(df[required_columns])
                    
            except Exception as e:
                st.error(f"Error parsing table: {str(e)}")
                continue
                
        if len(dfs) < 3:
            st.error("Could not find all required GDP tables")
            return None, None, None
            
        return dfs[0], dfs[1], dfs[2]
        
    except Exception as e:
        st.error(f"Failed to retrieve data: {str(e)}")
        return None, None, None

def create_stacked_bar(imf, wb, un):
    """Create stacked bar chart with data validation"""
    if imf is None or wb is None or un is None:
        return
        
    try:
        # Merge data with consistent country names
        merged = (
            imf.rename(columns={'GDP': 'IMF'})
            .merge(wb.rename(columns={'GDP': 'World Bank'}), 
                   on='Country/Territory')
            .merge(un.rename(columns={'GDP': 'UN'}), 
                   on='Country/Territory')
            .head(10)
        )
        
        # Create chart using Streamlit's native function
        st.bar_chart(
            merged.set_index('Country/Territory'),
            height=500
        )
        
    except Exception as e:
        st.error(f"Could not create chart: {str(e)}")

def main():
    st.title("GDP Data Dashboard")
    imf, wb, un = get_gdp_data()
    
    if imf is not None:
        st.header("IMF Data")
        st.dataframe(imf)
        
    if wb is not None:
        st.header("World Bank Data")
        st.dataframe(wb)
        
    if un is not None:
        st.header("UN Data")
        st.dataframe(un)
        
    st.header("GDP Comparison (Top 10 Countries)")
    create_stacked_bar(imf, wb, un)

if __name__ == "__main__":
    main()
