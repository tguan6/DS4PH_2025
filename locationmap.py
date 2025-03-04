import streamlit as st
import pandas as pd

# Set the title of the app
st.title("Location Map")

# Sidebar for user input
with st.sidebar:
    st.write("Enter coordinates:")
    lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0)
    lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0)

# Create a DataFrame with the input coordinates
map_data = pd.DataFrame({"lat": [lat], "lon": [lon]})

# Display the map
st.map(map_data)
