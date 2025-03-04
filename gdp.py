import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup

# Wikipedia URL
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"

# Function to determine a country's continent
def determine_continent(country):
    """Assign a continent to a country using a manual mapping."""
    continent_map = {
        "Asia": [...],  # Keep your existing list
        "Europe": [...],
        "North America": [...],
        "South America": [...],
        "Africa": [...],
        "Oceania": [...],
    }
    return next((continent for continent, countries in continent_map.items() if country in countries), "Other")

# Function to fetch GDP data manually
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
                rows = table.find_all("tr")
                data = []
                for row in rows[1:]:  # Skip the header row
                    cols = row.find_all(["th", "td"])
                    cols = [col.text.strip() for col in cols]
                    if len(cols) >= 2:
                        data.append(cols[:2])  # Keep only country & GDP columns
                
                df = pd.DataFrame(data, columns=["Country", "GDP (Millions USD)"])
                df["GDP (Millions USD)"] = pd.to_numeric(df["GDP (Millions USD)"].str.replace(",", ""), errors="coerce")
                df = df.dropna(subset=["GDP (Millions USD)"])  # Drop any remaining NaN values
                df["Continent"] = df["Country"].apply(determine_continent)

                # Debugging: Check continent assignment
                st.write("Unique Continents:", df["Continent"].unique())
                st.write(df.head())

                df = df[df["Continent"] != "Other"]  # Exclude unclassified countries
                gdp_data[source] = df
                break

    return gdp_data

# Streamlit UI
st.title("Global GDP Analysis by Continent")
st.sidebar.header("Settings")

# Fetch Data
gdp_data = fetch_gdp_data()

# User selects data source
selected_source = st.sidebar.selectbox("Select Data Source", list(gdp_data.keys()))
df = gdp_data[selected_source]

# Debugging: Check DataFrame before plotting
st.write("Final Data Before Plotting:")
st.write(df.head())

# Aggregate GDP by Continent and Country
df_continent = df.groupby(["Continent", "Country"], as_index=False).sum()

# Debugging: Check Aggregated Data
st.write("Aggregated Data Before Plotting:")
st.write(df_continent.head())

# Generate the stacked bar plot
fig = px.bar(
    df_continent,
    x="Continent",
    y="GDP (Millions USD)",
    color="Country",
    title=f"GDP Distribution by Continent ({selected_source} Estimates)",
    labels={"GDP (Millions USD)": "GDP (Million USD)"},
    barmode="stack"
)

# Display plot
st.plotly_chart(fig)
