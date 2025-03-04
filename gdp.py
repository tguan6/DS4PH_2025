import pandas as pd
import streamlit as st
import urllib.request
import re

def get_gdp_data():
    """Fetch and parse GDP tables with updated detection logic"""
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')

        # Updated table detection pattern
        tables = re.findall(r'<table[^>]*class="wikitable[^>]*>.*?</table>', html, re.DOTALL)
        
        if not tables:
            st.error("No tables found on the page")
            return None, None, None
            
        # Parse tables with error handling
        dfs = []
        for table_html in tables:
            try:
                df = pd.read_html(table_html)[0]
                
                # Standardize column names
                df.columns = [col.split('[')[0].strip() for col in df.columns]
                df = df.rename(columns={
                    'Country or territory': 'Country',
                    'Country/Territory': 'Country',
                    'United Nations[14]': 'GDP',
                    'Estimate': 'GDP'
                })
                
                # Extract GDP values
                if 'GDP' in df.columns:
                    df['GDP'] = (
                        df['GDP']
                        .astype(str)
                        .str.replace(r'[^\d.]', '', regex=True)
                        .astype(float)
                    )
                    df = df[['Country', 'GDP']].dropna()
                    dfs.append(df)
                    
            except Exception as e:
                continue
                
        if len(dfs) < 3:
            st.warning(f"Found {len(dfs)} valid tables. Using first 3 available.")
            dfs = dfs[:3]  # Use available tables
            
        return dfs if dfs else (None, None, None)
        
    except Exception as e:
        st.error(f"Data retrieval failed: {str(e)}")
        return None, None, None

def create_stacked_bar(tables):
    """Create visualization from available data"""
    if not tables or len(tables) == 0:
        return
        
    try:
        # Merge available tables
        merged = tables[0].rename(columns={'GDP': 'Source 1'})
        for i, table in enumerate(tables[1:3], 2):
            merged = merged.merge(
                table.rename(columns={'GDP': f'Source {i}'}),
                on='Country',
                how='outer'
            )
            
        # Clean and display
        merged = merged.head(10).fillna(0)
        st.bar_chart(
            merged.set_index('Country'),
            height=500
        )
        
    except Exception as e:
        st.error(f"Visualization error: {str(e)}")

def main():
    st.title("GDP Data Dashboard")
    tables = get_gdp_data()
    
    if tables:
        for i, table in enumerate(tables[:3], 1):
            st.header(f"Source {i} Data")
            st.dataframe(table)
            
        st.header("GDP Comparison (Top 10)")
        create_stacked_bar(tables)
    else:
        st.error("No GDP data available")

if __name__ == "__main__":
    main()
