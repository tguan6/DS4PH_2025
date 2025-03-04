import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to scrape and clean GDP data from Wikipedia
def get_gdp_data():
    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the first table with class "wikitable"
    table = soup.find("table", {"class": "wikitable"})

    # Extract data manually
    data = []
    headers = [header.text.strip() for header in table.find_all("th")]

    for row in table.find_all("tr")[1:]:  # Skip header row
        cols = row.find_all("td")
        if len(cols) >= 2:  # Ensure valid row
            country = cols[0].text.strip()
            gdp = cols[1].text.strip().replace(",", "").split(" ")[0]  # Clean GDP value
            data.append([country, gdp])

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Country", "GDP"])
    
    # Convert GDP to numeric, handling errors
    df["GDP"] = pd.to_numeric(df["GDP"], errors="coerce")

    return df

# Example usage in main()
def main():
    gdp_df = get_gdp_data()
    # Proceed with merging, plotting, etc.
    print("GDP DataFrame:\n", gdp_df.head())

if __name__ == "__main__":
    main()
