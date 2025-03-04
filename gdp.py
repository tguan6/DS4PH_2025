import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from bs4 import BeautifulSoup
from io import StringIO
from pycountry_convert import country_name_to_country_alpha2, country_alpha2_to_continent_code, convert_continent_code_to_continent_name

# Function to determine a country's continent
def determine_continent(country):
    """Assign a continent to a country using pycountry_convert."""
    try:
        country_code = country_name_to_country_alpha2(country)
        continent_short = country_alpha2_to_continent_code(country_code)
        return convert_continent_code_to_continent_name(continent_short)
    except:
        return "Unspecified"

# Retrieve GDP data from Wikipedia
def retrieve_gdp(source):
    source_map = {
        "IMF": 0,
        "World Bank": 1,
        "UN": 2
    }
    page_url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    page_content = requests.get(page_url).text
    parsed_page = BeautifulSoup(page_content, "html.parser")
    wiki_tables = parsed_page.select("table.wikitable")
    return pd.read_html(StringIO(str(wiki_tables[source_map[source]])), header=0)[0]

# Process the GDP data
def process_gdp_data(df, source):
    column_map = {
        "IMF": "Est_IMF",
        "World Bank": "Est WB",
        "UN": "United Nations[14]"
    }
    df.columns = ["Country/Territory", "Forecast", "Year_F", "Est_F", "Yr_IMF", "Est_IMF", "Yr_Other", "Est_Other"]
    df = df[df["Country/Territory"] != "World"]
    df["GDP (US$ million)"] = pd.to_numeric(
        df[column_map[source]].astype(str).str.replace(",", ""), errors="coerce"
    )
    df = df.dropna(subset=["GDP (US$ million)"])
    df["Continent"] = df["Country/Territory"].apply(determine_continent)
    return df

# Generate interactive plot
def generate_gdp_plot(df, source):
    fig = px.bar(
        df,
        x="Continent",
        y="GDP (US$ million)",
        color="Country/Territory",
        title=f"GDP Distribution by Continent ({source} Estimates)",
        labels={'GDP (US$ million)': 'GDP (USD Million)'},
        height=600
    )
    fig.update_layout(barmode='stack')
    st.plotly_chart(fig)

# Streamlit app
def main():
    st.title("Global GDP Visualization")
    st.write("Interactive comparison of GDP estimates by international organizations")
    
    source = st.selectbox(
        "Select Data Source",
        ["IMF", "World Bank", "UN"],
        index=0
    )
    
    with st.spinner("Loading GDP data..."):
        try:
            raw_df = retrieve_gdp(source)
            processed_df = process_gdp_data(raw_df, source)
            generate_gdp_plot(processed_df, source)
            
            st.subheader("Raw Data Preview")
            st.dataframe(processed_df.sort_values("GDP (US$ million)", ascending=False))
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")

if __name__ == "__main__":
    main()
