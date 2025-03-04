import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.io as pio
from bs4 import BeautifulSoup

# Wikipedia URL
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"

# Function to fetch GDP data from Wikipedia
@st.cache_data
def fetch_gdp_data():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all("table", {"class": "wikitable"})

    sources = ["IMF", "World Bank", "United Nations"]
    gdp_data = {}

    for source in sources:
        for table in tables:
            if source in table.text:
                df = pd.read_html(str(table))[0]
                df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
                relevant_columns = [col for col in df.columns if "Country" in col or source in col]
                df = df[relevant_columns]
                df = df.rename(columns={df.columns[0]: "Country", df.columns[1]: "GDP (Millions USD)"})
                df = df.dropna(subset=["GDP (Millions USD)"])
                df["GDP (Millions USD)"] = pd.to_numeric(df["GDP (Millions USD)"].astype(str).str.replace(',', '', regex=True), errors='coerce')
                df = df.dropna(subset=["GDP (Millions USD)"])  # Drop any remaining NaN values
                df["Continent"] = df["Country"].apply(get_continent)
                gdp_data[source] = df
                break

    return gdp_data

# Manual country-to-continent mapping
continent_map = {
    "North America": ["United States", "Canada", "Mexico"],
    "South America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru"],
    "Europe": ["Germany", "United Kingdom", "France", "Italy", "Spain", "Russia"],
    "Asia": ["China", "Japan", "India", "South Korea", "Indonesia", "Saudi Arabia"],
    "Africa": ["Nigeria", "South Africa", "Egypt"],
    "Oceania": ["Australia", "New Zealand"],
}

# Function to get continent for a given country
def get_continent(country):
    for continent, countries in continent_map.items():
        if country in countries:
            return continent
    return "Other"

# Streamlit UI
st.title("Global GDP Analysis by Continent")
st.sidebar.header("Settings")

# Fetch Data
gdp_data = fetch_gdp_data()

# User selects data source
selected_source = st.sidebar.selectbox("Select Data Source", list(gdp_data.keys()))
df = gdp_data[selected_source]

# Aggregate GDP by Continent and Country
df_continent = df.groupby(["Continent", "Country"]).sum().reset_index()

# Generate the stacked bar plot
fig = px.bar(
    df_continent,
    x="Continent",
    y="GDP (Millions USD)",
    color="Country",
    title=f"Nominal GDP by Country and Continent ({selected_source} Data)",
    labels={"GDP (Millions USD)": "GDP (Million USD)"},
    barmode="stack"
)

# Display plot
st.plotly_chart(fig)
