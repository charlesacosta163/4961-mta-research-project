"""
Central configuration for the station ridership study.

To re-point the entire analysis at a different station complex, either
change ACTIVE_STATION below or pass --station on the command line:

    python main.py --station times-sq
"""

from pathlib import Path


# --------------------------- FILE PATHS --------------------------- #

PROJECT_DIR = Path(__file__).resolve().parent

# The CSV data lives one level up so several projects can share it
# without duplicating a 411 MB file.
DATA_DIR = PROJECT_DIR.parent / "data"

MTA_CSV_DATA_FILE = DATA_DIR / "mta-est-ridership-simplified-2025-10.csv"

INBOUND_RESULTS_DIR = PROJECT_DIR / "INBOUND_RESULTS"
OUTBOUND_RESULTS_DIR = PROJECT_DIR / "OUTBOUND_RESULTS"


# --------------------------- COLUMN NAMES --------------------------- #

ORIGIN_COLUMN = "Origin Station Complex Name"
DESTINATION_COLUMN = "Destination Station Complex Name"
RIDERSHIP_COLUMN = "Estimated Average Ridership"
HOUR_COLUMN = "Hour of Day"
DAY_COLUMN = "Day of Week"
TIMESTAMP_COLUMN = "Timestamp"


# --------------------------- RUSH HOUR WINDOWS --------------------------- #

# The dataset's "Hour of Day" column is a 24-hour integer, so the windows
# below read directly as 7:00am-10:59am and 3:00pm-6:59pm.
MORNING_RUSH_HOURS = [7, 8, 9, 10]
EVENING_RUSH_HOURS = [15, 16, 17, 18]

MORNING_RUSH_LABEL = "Morning Rush (7-10 AM)"
EVENING_RUSH_LABEL = "Evening Rush (3-6 PM)"
ALL_DAY_LABEL = "All Day (Morning + Evening)"

DAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]


# --------------------------- REPORT SIZES --------------------------- #

TOP_N_EXPORT = 25
TOP_N_CHART = 15


# --------------------------- STATION COMPLEXES --------------------------- #

# "search" is matched case-insensitively against the station complex name
# columns, so it only needs to be long enough to be unambiguous.
# "label" is used in table headers, chart titles and printed summaries.
# "slug" is used in exported file names.
STATIONS = {
    "grand-central": {
        "search": "Grand Central-42 St",
        "label": "Grand Central",
        "slug": "grand-central"
    },
    "times-sq": {
        "search": "Times Sq",
        "label": "Times Square",
        "slug": "times-sq"
    },
    "fulton-st": {
        "search": "Fulton St",
        "label": "Fulton St",
        "slug": "fulton-st"
    },
    "union-sq": {
        "search": "14 St-Union Sq",
        "label": "14 St-Union Sq",
        "slug": "union-sq"
    },
    "herald-sq": {
        "search": "34 St-Herald Sq",
        "label": "34 St-Herald Sq",
        "slug": "herald-sq"
    },
    "penn-station": {
        "search": "34 St-Penn Station",
        "label": "34 St-Penn Station",
        "slug": "penn-station"
    },
    "atlantic-av": {
        "search": "Atlantic Av-Barclays Ctr",
        "label": "Atlantic Av-Barclays Ctr",
        "slug": "atlantic-av"
    }
}

# The station this project is currently focused on.
ACTIVE_STATION = "grand-central"


def get_station(station_key=None):
    """
    Looks up one station's configuration.

    Falls back to ACTIVE_STATION when no key is given, so scripts can
    call get_station() and automatically follow the project focus.

    Returns:
        A dictionary containing the station's search text, label and slug.
    """

    key = (station_key or ACTIVE_STATION).strip().lower()

    if key not in STATIONS:
        available = ", ".join(sorted(STATIONS))

        raise KeyError(
            f"Unknown station '{key}'. "
            f"Available stations: {available}. "
            f"Add a new entry to STATIONS in config.py to track another complex."
        )

    return STATIONS[key]
