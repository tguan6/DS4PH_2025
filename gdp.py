import pandas as pd
import streamlit as st

def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    
    # Explicitly use html5lib parser
    try:
        tables = pd.read_html(url, flavor='html5lib')
    except ImportError:
        st.error("Required HTML parser missing! Please add 'html5lib' to your requirements.")
        raise

    # Find correct tables by column headers
    imf_df = next(df for df in tables if 'IMF' in str(df.columns))
    wb_df = next(df for df in tables if 'World Bank' in str(df.columns))
    un_df = next(df for df in tables if 'United Nations' in str(df.columns))

    # Clean and process data
    for df in [imf_df, wb_df, un_df]:
        df.columns = df.columns.get_level_values(-1)  # Handle multi-index
        if 'Country/Territory' not in df.columns:
            df.rename(columns={df.columns[0]: 'Country/Territory'}, inplace=True)
        if 'GDP' not in df.columns:
            gdp_col = [col for col in df.columns if 'GDP' in str(col)][0]
            df.rename(columns={gdp_col: 'GDP'}, inplace=True)
        
        df['GDP'] = df['GDP'].replace(r'[\$,]', '', regex=True).astype(float)

    return imf_df, wb_df, un_df

def main():
    st.title("GDP Data Analysis")
    imf, wb, un = get_gdp_data()
    
    # Display data
    st.header("IMF GDP Data")
    st.dataframe(imf)
    
    st.header("World Bank GDP Data")
    st.dataframe(wb)
    
    st.header("UN GDP Data")
    st.dataframe(un)

if __name__ == "__main__":
    main()
