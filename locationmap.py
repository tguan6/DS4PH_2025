import streamlit as st
import plotly.graph_objects as go

# Set the title of the app
st.title("Interactive Map with Marker")

# Add input fields for latitude and longitude
lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=0.0, step=0.01)
lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=0.0, step=0.01)

# Create a Plotly figure for the map
fig = go.Figure()

# Add a marker at the specified latitude and longitude
fig.add_trace(go.Scattergeo(
    lon=[lon],
    lat=[lat],
    mode='markers',
    marker=dict(
        size=12,
        color='red',
        symbol='circle'
    ),
    name='Your Location'
))

# Customize the map layout
fig.update_layout(
    geo=dict(
        projection_type='mercator',
        center=dict(lat=lat, lon=lon),
        scope='world',
        resolution=50,
    ),
    margin={"r":0, "t":0, "l":0, "b":0},
    height=600,
    width=800
)

# Display the map in the Streamlit app
st.plotly_chart(fig, use_container_width=True)

# Optional: Display the coordinates below the map
st.write(f"Marker Location: Latitude {lat}, Longitude {lon}")
