import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from bs4 import BeautifulSoup
from io import StringIO

# Wikipedia URL
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"

# Function to determine a country's continent
def determine_continent(country):
    """Assign a continent to a country using a more comprehensive manual mapping."""
    continent_map = {
        "North America": ["United States", "Canada", "Mexico", "Guatemala", "Honduras", "El Salvador", "Nicaragua", "Costa Rica", "Panama", "Jamaica", "Dominican Republic", "Haiti", "Cuba"],
        "South America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru", "Venezuela", "Ecuador", "Bolivia", "Paraguay", "Uruguay", "Guyana", "Suriname"],
        "Europe": ["Germany", "United Kingdom", "France", "Italy", "Spain", "Russia", "Netherlands", "Switzerland", "Sweden", "Poland", "Belgium", "Austria", "Norway", "Denmark", "Ireland", "Finland", "Portugal", "Czech Republic", "Romania", "Greece", "Hungary", "Slovakia", "Ukraine", "Serbia", "Croatia", "Lithuania", "Slovenia", "Bulgaria", "Latvia", "Estonia", "Cyprus", "Luxembourg", "Malta", "Iceland"],
        "Asia": ["China", "Japan", "India", "South Korea", "Indonesia", "Saudi Arabia", "Turkey", "Iran", "Thailand", "United Arab Emirates", "Israel", "Malaysia", "Singapore", "Pakistan", "Vietnam", "Philippines", "Bangladesh", "Kazakhstan", "Iraq", "Qatar", "Kuwait", "Oman", "Sri Lanka", "Lebanon", "Myanmar", "Uzbekistan", "Jordan", "Bahrain", "Nepal", "Turkmenistan", "Yemen", "Afghanistan", "Mongolia", "Brunei"],
        "Africa": ["Nigeria", "South Africa", "Egypt", "Algeria", "Morocco", "Ethiopia", "Kenya", "Ghana", "Angola", "Tanzania", "Tunisia", "Ivory Coast", "Democratic Republic of the Congo", "Sudan", "Senegal", "Uganda", "Zambia", "Botswana", "Namibia", "Mauritius"],
        "Oceania": ["Australia", "New Zealand", "Papua New Guinea", "Fiji", "Solomon Islands", "Vanuatu", "Samoa", "Tonga", "Kiribati", "Micronesia", "Palau", "Tuvalu", "Marshall Islands"],
    }
    for continent, countries in continent_map.items():
        if country in countries:
            return continent
    return "Other"

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

# Aggregate GDP by Continent and Country
df_continent = df.groupby(["Continent", "Country"]).sum().reset_index()

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
