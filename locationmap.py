import streamlit as st
import pandas as pd
import pydeck as pdk

# Set the title of the app
st.title("Location Map")

# Sidebar for user input
with st.sidebar:
    st.write("Enter coordinates:")
    lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=37.7749)  # Default: San Francisco
    lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=-122.4194)  # Default: San Francisco

# Create a DataFrame with the input coordinates
map_data = pd.DataFrame({"lat": [lat], "lon": [lon]})

# Define the map using PyDeck for a better visualization
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=10,  # Adjust zoom for better visibility
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position=["lon", "lat"],
            get_color=[255, 0, 0, 160],  # Red marker
            get_radius=20000,
        )
    ],
))
