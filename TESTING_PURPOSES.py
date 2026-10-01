import pandas as pd

MTA_CSV_DATA_FILE = "../data/mta-est-ridership-simplified-2025-10.csv"

# Change this to test any other station name
STATION = "110 st"

df = pd.read_csv(MTA_CSV_DATA_FILE, dtype={"Estimated Average Ridership": str})

# Keep rows where the station is the origin OR the destination
matches = df[
    df["Origin Station Complex Name"].str.contains(
        STATION, case=False, na=False, regex=False
    )
    |
    df["Destination Station Complex Name"].str.contains(
        STATION, case=False, na=False, regex=False
    )
]

print(f"Rows in file: {len(df):,}")
print(f"Rows mentioning '{STATION}': {len(matches):,}\n")

if matches.empty:
    print(f"'{STATION}' was not found in the simplified CSV.")
    print("This file only has subway station complexes (LIRR is not included).")
else:
    print(matches.head(20).to_string(index=False))
