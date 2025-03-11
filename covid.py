import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO
import requests

# Cache data to avoid reloading on every interaction
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    response = requests.get(url)
    return pd.read_csv(StringIO(response.text))

def process_data(df, countries, cumulative=True):
    """Process data for selected countries and case type"""
    filtered = df[df['Country/Region'].isin(countries)]
    melted = filtered.melt(
        id_vars=['Province/State', 'Country/Region', 'Lat', 'Long'],
        var_name='Date',
        value_name='Cases'
    )
    melted['Date'] = pd.to_datetime(melted['Date'])
    
    if not cumulative:
        melted = melted.groupby(['Country/Region', 'Date'])['Cases'].sum().groupby(level=0).diff().reset_index()
    
    return melted.groupby(['Country/Region', 'Date'])['Cases'].sum().reset_index()

# Streamlit app layout
st.title("COVID-19 Data Dashboard")
st.write("Select countries and case type to display COVID-19 trends")

# Load data once
df = load_data()

# Get unique countries
countries = st.multiselect(
    'Select countries',
    options=sorted(df['Country/Region'].unique()),
    default=['US', 'India']
)

# Case type selector
case_type = st.radio(
    "Case type:",
    ("Cumulative", "Daily"),
    horizontal=True
)

# Generate plot when countries are selected
if countries:
    processed_df = process_data(df, countries, cumulative=(case_type == "Cumulative"))
    
    fig = px.line(
        processed_df,
        x='Date',
        y='Cases',
        color='Country/Region',
        title=f'COVID-19 {case_type} Cases'
    )
    st.plotly_chart(fig)
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(processed_df)
else:
    st.warning("Please select at least one country")
