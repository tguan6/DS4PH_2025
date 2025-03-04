import streamlit as st
import folium
from streamlit_folium import folium_static
import subprocess
import sys

# Ensure folium is installed (for Streamlit Cloud compatibility)
def install_missing_packages():
    try:
        import folium
    except ModuleNotFoundError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "streamlit-folium"])
        import folium

install_missing_packages()

# Set the title of the app
st.title("Location Map")

# Add input fields in the sidebar
with st.sidebar:
    st.write("Enter coordinates:")
    lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0)
    lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0)

# Create a Folium map centered at the user-specified coordinates
m = folium.Map(location=[lat, lon], zoom_start=10)

# Add a marker at the specified location with a popup
folium.Marker([lat, lon], popup="Your location").add_to(m)

# Display the map in the Streamlit app using folium_static
folium_static(m)
