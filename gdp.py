import pandas as pd
import streamlit as st
import urllib.request
import re

def get_gdp_data():
    """Fetch GDP tables with updated detection logic"""
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')

        # Updated table pattern for current Wikipedia layout
        tables = re.findall(r'<table class="wikitable sortable".*?>(.*?)</table>', html, re.DOTALL)
        
        if not tables:
            return None, None, None
            
        # Parse IMF, World Bank, and UN tables
        dfs = []
        for table_html in tables[:3]:
            df = pd.read_html(table_html)[0]
            
            # Clean current column names
            df.columns = [col.split('[')[0].strip() for col in df.columns]
            df = df.rename(columns={
                'Country/Territory': 'Country',
                'GDP (US$million)': 'GDP',
                'Estimate': 'GDP',
                'United Nations': 'GDP'
            })
            
            # Convert GDP values
            if 'GDP' in df.columns:
                df['GDP'] = (
                    df['GDP']
                    .astype(str)
                    .str.replace(r'[^\d.]', '', regex=True)
                    .astype(float)
                )
                dfs.append(df[['Country', 'GDP']].dropna())
                
        return dfs[0], dfs[1], dfs[2] if len(dfs) >=3 else (None, None, None)
        
    except Exception as e:
        st.error(f"Data error: {str(e)}")
        return None, None, None

def create_stacked_bar(imf, wb, un):
    """Create visualization from valid data"""
    if imf is None or wb is None or un is None:
        return
        
    try:
        # Merge data for top 10 countries
        merged = (
            imf.rename(columns={'GDP': 'IMF'})
            .merge(wb.rename(columns={'GDP': 'World Bank'}), on='Country')
            .merge(un.rename(columns={'GDP': 'UN'}), on='Country')
            .head(10)
            .set_index('Country')
        )
        
        st.bar_chart(merged, height=400)

    except Exception as e:
        st.error(f"Chart error: {str(e)}")

def main():
    st.title("Live GDP Dashboard")
    imf, wb, un = get_gdp_data()
    
    if imf is not None:
        st.header("IMF GDP Rankings")
        st.dataframe(imf)
        
    if wb is not None:
        st.header("World Bank GDP Rankings")
        st.dataframe(wb)
        
    if un is not None:
        st.header("UN GDP Estimates")
        st.dataframe(un)
        
    st.header("GDP Comparison (Top 10)")
    create_stacked_bar(imf, wb, un)

if __name__ == "__main__":
    main()
