import requests
from bs4 import BeautifulSoup
import pandas as pd
import ast
from urllib.parse import urljoin

# Base URL
base_url = "https://qvwx.de/sperrmuell-bonn-2024/Termine.html"

# Fetch the HTML and extract Koordinaten.txt links
response = requests.get(base_url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")
links = [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True) if "Koordinaten.txt" in a["href"]]

# Collect parsed data
records = []

for link in links:
    print(f"Fetching {link}")
    try:
        text = requests.get(link).text
        for line in text.strip().splitlines():
            address, lat, lon = ast.literal_eval(line)
            # Example: 'Am Agnesstift 1, 53117 Bonn'
            addr_part, pin_part = address.split(",")
            *street_parts, house_nr = addr_part.strip().rsplit(" ", 1)
            street = " ".join(street_parts)
            pin = pin_part.strip().split()[0]
            records.append((street, house_nr, pin, lat, lon))
    except Exception as e:
        print(f"Failed to process {link}: {e}")

# Create DataFrame
df = pd.DataFrame(records, columns=["Street", "HouseNr", "PIN", "Latitude", "Longitude"])
df = df.drop_duplicates()

# Optionally save
df.to_csv("coordinates_parsed.csv", index=False)
