"""
First map: every unique subway station complex in the dataset.

The simplified CSV has no coordinates, so this reads the full CSV, but
only the station columns, and keeps one row per station.

    python map-first-iteration.py
"""

import contextily as ctx
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

import config

FULL_CSV_FILE = config.DATA_DIR / "mta-ridership-est-2025-10.csv"
OUTPUT_FILE = config.PROJECT_DIR / "station-map.png"

# How much extra space to show around the stations, as a fraction of the
# map size. 0.05 is a tight crop, 0.3 shows a wide area around the city.
MAP_PADDING = 0.3


# --------------------------- LOAD UNIQUE STATIONS --------------------------- #

def get_unique_stations(file_path):
    """
    Returns one row per station complex with its name, latitude and longitude.
    Stations are collected from both the origin and destination columns.
    """

    origin_columns = [
        "Origin Station Complex ID",
        "Origin Station Complex Name",
        "Origin Latitude",
        "Origin Longitude"
    ]

    destination_columns = [
        "Destination Station Complex ID",
        "Destination Station Complex Name",
        "Destination Latitude",
        "Destination Longitude"
    ]

    df = pd.read_csv(file_path, usecols=origin_columns + destination_columns)

    new_names = ["Station ID", "Station Name", "Latitude", "Longitude"]

    origins = df[origin_columns].drop_duplicates()
    origins.columns = new_names

    destinations = df[destination_columns].drop_duplicates()
    destinations.columns = new_names

    stations = pd.concat([origins, destinations]).drop_duplicates()

    return stations.reset_index(drop=True)


# --------------------------- BUILD MAP --------------------------- #

stations = get_unique_stations(FULL_CSV_FILE)

print(f"Unique stations: {len(stations)}")
print(f"Unique station IDs: {stations['Station ID'].nunique()}")

# Longitude is x, latitude is y
gdf = gpd.GeoDataFrame(
    stations,
    geometry=gpd.points_from_xy(stations["Longitude"], stations["Latitude"]),
    crs="EPSG:4326"
)

focus_station = config.get_station()

is_focus = gdf["Station Name"].str.contains(
    focus_station["search"],
    case=False,
    regex=False
)

# Basemap tiles use Web Mercator, so convert from lat/lon first
gdf = gdf.to_crs(epsg=3857)

fig, ax = plt.subplots(figsize=(8, 10))

gdf[~is_focus].plot(ax=ax, color="#1f77b4", edgecolor="white", markersize=20)
gdf[is_focus].plot(
    ax=ax,
    color="red",
    edgecolor="white",
    markersize=120,
    label=focus_station["label"]
)

# Widen the view so there is empty space around the outermost stations.
# Must happen before the basemap so the tiles cover the larger area.
ax.margins(MAP_PADDING)

# Light gray basemap (no API key needed, unlike CartoDB)
ctx.add_basemap(ax, source=ctx.providers.Esri.WorldGrayCanvas)

ax.set_title("MTA Subway Station Complexes", fontsize=14, fontweight="bold")
ax.set_axis_off()
ax.legend(loc="upper left")

plt.tight_layout()
plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")

print(f"Map saved to: {OUTPUT_FILE.name}")
