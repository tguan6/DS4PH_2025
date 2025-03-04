import streamlit as st
import sys
import subprocess

# Ensure folium and streamlit_folium are installed
try:
    import folium
    from streamlit_folium import folium_static
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "folium", "streamlit-folium"])
    import folium
    from streamlit_folium import folium_static

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
if lat != 0.0 or lon != 0.0:
    folium.Marker([lat, lon], popup="Your location").add_to(m)

# Display the map in the Streamlit app using folium_static
folium_static(m)
