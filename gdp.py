import pandas as pd
import subprocess
import sys

# Ensure lxml is installed (for Streamlit Cloud compatibility)
try:
    import lxml
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lxml"])
    import lxml

# Function to scrape and clean GDP data from Wikipedia
def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    tables = pd.read_html(url)

    # Extract tables
    imf_df = tables[0]  # IMF table
    wb_df = tables[1]   # World Bank table
    un_df = tables[2]   # UN table

    # Clean IMF and World Bank DataFrames (drop 'Rank' if present)
    imf_df = imf_df.drop(columns=['Rank'], errors='ignore')
    wb_df = wb_df.drop(columns=['Rank'], errors='ignore')

    # Flatten UN DataFrame multi-level columns
    un_df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in un_df.columns]
    
    # Select and rename relevant columns
    un_df = un_df[['Country/Territory_Country/Territory', 'United Nations[14]_Estimate']]
    un_df = un_df.rename(columns={
        'Country/Territory_Country/Territory': 'Country/Territory',
        'United Nations[14]_Estimate': 'GDP'
    })  # Reassign to avoid view/copy issues

    # Clean GDP columns across all DataFrames
    for df in [imf_df, wb_df, un_df]:
        if 'GDP' in df.columns:
            # Remove brackets and commas
            df['GDP'] = df['GDP'].astype(str).str.replace(r"\[.*\]", "", regex=True).str.replace(",", "")
            # Convert to float, coercing non-numeric values to NaN
            df['GDP'] = pd.to_numeric(df['GDP'], errors='coerce')

    return imf_df, wb_df, un_df

# Example usage in main()
def main():
    imf_df, wb_df, un_df = get_gdp_data()
    # Proceed with merging, plotting, etc.
    print("IMF DataFrame:\n", imf_df.head())
    print("World Bank DataFrame:\n", wb_df.head())
    print("UN DataFrame:\n", un_df.head())

if __name__ == "__main__":
    main()
