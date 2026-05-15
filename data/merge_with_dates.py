import pandas as pd

df_address = pd.read_csv("coordinates_parsed.csv")
df_address['TERMIN001'] = None
df_address['TERMIN002'] = None 
df_address['TERMIN003'] = None
df_dates = pd.read_csv("spermull_only_2026.csv")
df_dates = df_dates[['STRASSE1', 'HNR_GE_AB','HNR_GE_BIS','HNR_UG_AB','HNR_UG_BIS','TERMIN001','TERMIN002','TERMIN003']]

for i, row in df_address.iterrows():
    street = row['Street']
    house_nr = int(row['HouseNr'])  # ensure it's an int
    pin = row['PIN']
    lat = row['Latitude']
    lon = row['Longitude']
    
    # Find matching rows in df_dates
    matches = df_dates[df_dates['STRASSE1'] == street]
    
    if house_nr % 2 == 0:
        matches = matches[
            (matches['HNR_GE_AB'] <= house_nr) &
            (matches['HNR_GE_BIS'] >= house_nr)
        ]
    else:
        matches = matches[
            (matches['HNR_UG_AB'] <= house_nr) &
            (matches['HNR_UG_BIS'] >= house_nr)
        ]

    # Assign back to the original DataFrame using .loc
    if not matches.empty:
        df_address.loc[i, 'TERMIN001'] = matches.iloc[0]['TERMIN001']
        df_address.loc[i, 'TERMIN002'] = matches.iloc[0]['TERMIN002']
        df_address.loc[i, 'TERMIN003'] = matches.iloc[0]['TERMIN003']
df_address.to_csv("coordinates_with_dates.csv", index=False)