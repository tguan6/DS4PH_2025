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
                gdp_data[source] = df
                break

    return gdp_data

# Complete country-to-continent mapping from the image
continent_map = {
    "Asia": [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia",
        "China", "Cyprus", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",
        "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia",
        "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine", "Philippines", "Qatar",
        "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", "Taiwan", "Tajikistan",
        "Thailand", "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan",
        "Vietnam", "Yemen", "Hong Kong", "Macau"
    ],
    "Europe": [
        "Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria",
        "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany",
        "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein",
        "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands",
        "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia",
        "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom",
        "Vatican City"
    ],
    "North America": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica", "Cuba",
        "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras",
        "Jamaica", "Mexico", "Nicaragua", "Panama", "Saint Kitts and Nevis", "Saint Lucia",
        "Saint Vincent and the Grenadines", "Trinidad and Tobago", "United States", "Puerto Rico"
    ],
    "South America": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru",
        "Suriname", "Uruguay", "Venezuela"
    ],
    "Africa": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroon",
        "Central African Republic", "Chad", "Comoros", "Democratic Republic of the Congo", "Djibouti",
        "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana",
        "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar",
        "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
        "Nigeria", "Republic of the Congo", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles",
        "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia",
        "Uganda", "Zambia", "Zimbabwe"
    ],
    "Oceania": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Zealand",
        "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"
    ],
    "World": ["World"]
}

# Function to map country to continent
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

# Assign Continent
df["Continent"] = df["Country"].apply(get_continent)

# Aggregate GDP by Continent and Country
df_continent = df.groupby(["Continent", "Country"]).sum().reset_index()

# Plot stacked bar chart
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
