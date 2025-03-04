import streamlit as st
import requests
import pandas as pd

# Attempt to import Plotly, and handle if it's missing
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ModuleNotFoundError:
    PLOTLY_AVAILABLE = False

# Streamlit UI
st.title("Global GDP Analysis by Continent")

if not PLOTLY_AVAILABLE:
    st.error("The required module `plotly` is missing. Please add `plotly` to `requirements.txt` and redeploy.")
else:
    # (Continue with the rest of your code, assuming plotly is available)
    pass
