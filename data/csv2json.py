import pandas as pd
import json
from collections import defaultdict
import numpy as np
# Load CSV using pandas
df = pd.read_csv("coordinates_with_dates.csv")

# Container for output GeoJSONs
geojson_outputs = {
    "type": "FeatureCollection",
    "features": []
} 

# Create a temporary DataFrame with relevant columns
temp_df = df[[
    "Street", "Latitude", "Longitude", "HouseNr", "TERMIN001", "TERMIN002", "TERMIN003"
]].copy()
temp_df = temp_df.drop_duplicates()
temp_df["TERMIN001"] = pd.to_datetime(temp_df["TERMIN001"]).dt.strftime("%Y%m%d")
temp_df["TERMIN002"] = pd.to_datetime(temp_df["TERMIN002"]).dt.strftime("%Y%m%d")
temp_df["TERMIN003"] = pd.to_datetime(temp_df["TERMIN003"]).dt.strftime("%Y%m%d")
# Group by strasse and date
grouped = temp_df.groupby(["TERMIN001", "Street"])
for (_,strasse), group in grouped:
    coordinates = group[["Longitude", "Latitude"]].values.tolist()
    hausnummern = group["HouseNr"].tolist()
    dates = list(np.unique(group[["TERMIN001", "TERMIN002", "TERMIN003"]].values))

    feature = {
        "type": "Feature",
        "properties": {
            "date": dates,
            "strasse": strasse,
            "hausnummern": hausnummern,
        },
        "geometry": {
            "type": "MultiPoint",
            "coordinates": coordinates
        }
    }
    geojson_outputs["features"].append(feature)


filename = f"merged.geojson"
with open(filename, "w", encoding="utf-8") as f:
    json.dump(geojson_outputs, f, ensure_ascii=False)
print(f"✅ Wrote {filename} with {len(geojson_outputs['features'])} merged features.")

#separators=(",", ":")