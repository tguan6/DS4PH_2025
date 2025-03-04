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
        "Asia": ["Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", 
                 "China", "Cyprus", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",
                 "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia",
                 "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine", "Philippines", "Qatar",
                 "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", "Taiwan", "Tajikistan",
                 "Thailand", "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan",
                 "Vietnam", "Yemen", "Hong Kong", "Macau"],
        "Europe": ["Albania", "Andorra", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria",
                   "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany",
                   "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Liechtenstein",
                   "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands",
                   "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia",
                   "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Ukraine", "United Kingdom",
                   "Vatican City"],
        "North America": ["Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica", "Cuba",
                          "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras",
                          "Jamaica", "Mexico", "Nicaragua", "Panama", "Saint Kitts and Nevis", "Saint Lucia",
                          "Saint Vincent and the Grenadines", "Trinidad and Tobago", "United States", "Puerto Rico"],
        "South America": ["Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru",
                          "Suriname", "Uruguay", "Venezuela"],
        "Africa": ["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroon",
                   "Central African Republic", "Chad", "Comoros", "Democratic Republic of the Congo", "Djibouti",
                   "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana",
                   "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar",
                   "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
                   "Nigeria", "Republic of the Congo", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles",
                   "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia",
                   "Uganda", "Zambia", "Zimbabwe"],
        "Oceania": ["Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Zealand",
                    "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"]
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
st.write("Final Data Before Plotting:", df.shape)
st.write(df.head())

# Aggregate GDP by Continent and Country
df_continent = df.groupby(["Continent", "Country"], as_index=False).sum()

# Debugging: Check Aggregated Data
st.write("Aggregated Data Before Plotting:", df_continent.shape)
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
