"""
Reusable analysis functions for MTA origin-destination ridership.

Every function takes the station complex as an argument instead of
hard-coding it, so the same code can analyse any station in config.STATIONS.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

import config


# --------------------------- UTILITY FUNCTIONS --------------------------- #

def load_data(file_path=None):
    """
    Loads the MTA CSV file into a pandas DataFrame.

    Also cleans the "Estimated Average Ridership" column by:
    - converting values to strings,
    - removing commas,
    - converting the values to floats.

    Returns:
        pandas DataFrame containing the cleaned dataset.
    """

    path = file_path or config.MTA_CSV_DATA_FILE

    # The ridership column mixes plain numbers with comma-grouped text, so
    # it is read as text and cleaned below rather than guessed per chunk.
    df = pd.read_csv(path, dtype={config.RIDERSHIP_COLUMN: str})

    df[config.RIDERSHIP_COLUMN] = (
        df[config.RIDERSHIP_COLUMN]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

    return df


def get_direction_columns(direction):
    """
    Maps a travel direction onto the two station name columns.

    For outbound trips the focus station is the origin, and the station
    that varies from row to row is the destination. Inbound is the reverse.

    Returns:
        A tuple of (focus_column, counterpart_column).
    """

    normalized = direction.strip().lower()

    if normalized == "outbound":
        return config.ORIGIN_COLUMN, config.DESTINATION_COLUMN

    if normalized == "inbound":
        return config.DESTINATION_COLUMN, config.ORIGIN_COLUMN

    raise ValueError("direction must be 'inbound' or 'outbound'")


# --------------------------- FILTER FUNCTIONS --------------------------- #

def filter_by_station(dataframe, station_search, direction):
    """
    Keeps only the trips that start from or arrive at one station complex.

    Passing direction="outbound" filters on the origin column, and
    direction="inbound" filters on the destination column.

    Returns:
        A filtered DataFrame.
    """

    focus_column, _ = get_direction_columns(direction)

    return dataframe[
        dataframe[focus_column].str.contains(
            station_search,
            regex=False,
            na=False,
            case=False
        )
    ]


def filter_origin_destination(dataframe, origin, destination):
    """
    Filters the dataset for one specific origin-to-destination
    station combination.

    The search is:
    - case-insensitive,
    - treated as literal text instead of regular expressions,
    - safe against missing values.

    Returns:
        A filtered DataFrame containing only rows where:
        Origin Station contains the requested origin, and
        Destination Station contains the requested destination.
    """

    return dataframe[
        (
            dataframe[config.ORIGIN_COLUMN].str.contains(
                origin,
                regex=False,
                na=False,
                case=False
            )
        )
        &
        (
            dataframe[config.DESTINATION_COLUMN].str.contains(
                destination,
                regex=False,
                na=False,
                case=False
            )
        )
    ]


def filter_rush_hours(dataframe, period_of_day):
    """
    Keeps only the rows that fall inside a rush-hour window.

    Uses the dataset's 24-hour "Hour of Day" column, so "morning" means
    7:00am-10:59am and "evening" means 3:00pm-6:59pm.

    Returns:
        A filtered DataFrame.
    """

    normalized = period_of_day.strip().lower()

    if normalized == "morning":
        rush_hours = config.MORNING_RUSH_HOURS

    elif normalized == "evening":
        rush_hours = config.EVENING_RUSH_HOURS

    else:
        raise ValueError("period_of_day must be 'morning' or 'evening'")

    hours = pd.to_numeric(dataframe[config.HOUR_COLUMN], errors="coerce")

    return dataframe[hours.isin(rush_hours)]


# --------------------------- RANKING FUNCTIONS --------------------------- #

def rank_station_pairs(dataframe):
    """
    Totals ridership for every origin-destination pair and ranks them.

    Returns:
        A DataFrame sorted from busiest to quietest, with a "Rank" column
        starting at 1.
    """

    ranked = (
        dataframe
        .groupby([
            config.ORIGIN_COLUMN,
            config.DESTINATION_COLUMN
        ])[config.RIDERSHIP_COLUMN]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    ranked["Rank"] = ranked.index + 1

    return ranked


def get_rush_hour_ridership(dataframe, period_of_day):
    """
    Ranks origin-destination pairs using only one rush-hour window.

    Returns:
        A ranked DataFrame for the requested period.
    """

    return rank_station_pairs(
        filter_rush_hours(dataframe, period_of_day)
    )


def get_overall_ridership(dataframe):
    """
    Ranks origin-destination pairs across every hour in the dataset.

    Returns:
        A ranked DataFrame covering the full day.
    """

    return rank_station_pairs(dataframe)


def build_ranking_report(dataframe):
    """
    Builds the combined ranking table for one station and direction.

    Starts from the all-day totals, then joins on the morning and evening
    ridership and ranks for the same origin-destination pair. Joining on
    both station columns keeps the numbers aligned even when a search term
    matches more than one complex.

    Returns:
        A dictionary containing the "morning", "evening" and "overall"
        DataFrames, where "overall" also carries the rush-hour columns.
    """

    morning = get_rush_hour_ridership(dataframe, "morning")
    evening = get_rush_hour_ridership(dataframe, "evening")
    overall = get_overall_ridership(dataframe)

    pair_columns = [config.ORIGIN_COLUMN, config.DESTINATION_COLUMN]

    morning_columns = morning[
        pair_columns + [config.RIDERSHIP_COLUMN, "Rank"]
    ].rename(
        columns={
            config.RIDERSHIP_COLUMN: "Morning Ridership",
            "Rank": "Morning Rank"
        }
    )

    evening_columns = evening[
        pair_columns + [config.RIDERSHIP_COLUMN, "Rank"]
    ].rename(
        columns={
            config.RIDERSHIP_COLUMN: "Evening Ridership",
            "Rank": "Evening Rank"
        }
    )

    overall = (
        overall
        .merge(morning_columns, on=pair_columns, how="left")
        .merge(evening_columns, on=pair_columns, how="left")
    )

    overall[["Morning Ridership", "Evening Ridership"]] = (
        overall[["Morning Ridership", "Evening Ridership"]].fillna(0)
    )

    return {
        "morning": morning,
        "evening": evening,
        "overall": overall
    }


# --------------------------- DAILY COMPARISON --------------------------- #

def get_ridership_totals_daily(dataframe):
    """
    Calculates total morning and evening rush-hour ridership
    for each weekday in the provided DataFrame.

    Returns:
        A list of dictionaries containing:
        - day
        - morning_rush total
        - evening_rush total
    """

    daily_totals_list = []

    morning_totals = (
        filter_rush_hours(dataframe, "morning")
        .groupby(config.DAY_COLUMN)[config.RIDERSHIP_COLUMN]
        .sum()
    )

    evening_totals = (
        filter_rush_hours(dataframe, "evening")
        .groupby(config.DAY_COLUMN)[config.RIDERSHIP_COLUMN]
        .sum()
    )

    days_present = set(morning_totals.index) | set(evening_totals.index)

    for day in config.DAY_ORDER:
        if day not in days_present:
            continue

        daily_totals_list.append({
            "day": day,
            "morning_rush": float(morning_totals.get(day, 0)),
            "evening_rush": float(evening_totals.get(day, 0))
        })

    return daily_totals_list


def get_ridership_totals_by_date(dataframe, date):
    """
    Calculates the morning and evening rush-hour ridership totals
    for one specific representative date.

    The date is matched against the leading "MM/DD/YYYY" portion of the
    Timestamp column, for example "10/06/2025".

    Returns:
        A dictionary containing:
        - date
        - morning_rush total
        - evening_rush total
    """

    row_dates = (
        dataframe[config.TIMESTAMP_COLUMN]
        .astype(str)
        .str.split()
        .str[0]
    )

    one_day = dataframe[row_dates == date]

    morning_rush = (
        filter_rush_hours(one_day, "morning")[config.RIDERSHIP_COLUMN].sum()
    )

    evening_rush = (
        filter_rush_hours(one_day, "evening")[config.RIDERSHIP_COLUMN].sum()
    )

    return {
        "date": date,
        "morning_rush": float(morning_rush),
        "evening_rush": float(evening_rush)
    }


# --------------------------- DISPLAY FUNCTIONS --------------------------- #

def display_ridership_comparison(
    route1_data,
    route2_data,
    station1,
    station2
):
    """
    Displays a side-by-side comparison of morning and evening
    rush-hour ridership for two opposite travel directions.

    Example:
        Grand Central -> Fulton St
        Fulton St -> Grand Central

    Days are matched by name rather than by position, so a weekday that is
    missing from one direction cannot shift the other column out of line.

    Uses the tabulate library to print the formatted table.
    """

    route2_by_day = {row["day"]: row for row in route2_data}

    table = []

    for route1_day in route1_data:
        day = route1_day["day"]
        route2_day = route2_by_day.get(day, {})

        table.append([
            day,
            route1_day["morning_rush"],
            route1_day["evening_rush"],
            route2_day.get("morning_rush", 0),
            route2_day.get("evening_rush", 0)
        ])

    headers = [
        "Day",
        f"{station1} → {station2} AM",
        f"{station1} → {station2} PM",
        f"{station2} → {station1} AM",
        f"{station2} → {station1} PM"
    ]

    print(
        tabulate(
            table,
            headers=headers,
            tablefmt="grid",
            floatfmt=".2f"
        )
    )


def shorten_station_names(series):
    """
    Trims the route list from a station complex name so chart labels stay
    readable, turning "Fulton St (A,C,J,Z,2,3,4,5)" into "Fulton St".

    Returns:
        A pandas Series of shortened names.
    """

    return series.str.split("(").str[0].str.strip()


def plot_rush_hour_comparison(
    overall_report,
    station_label,
    direction,
    output_path,
    top_n=None
):
    """
    Draws a grouped horizontal bar chart comparing morning rush, evening
    rush and all-day ridership for the busiest counterpart stations.

    For an outbound report the bars are labelled with destinations, and for
    an inbound report they are labelled with origins.

    Returns:
        The DataFrame of plotted rows, busiest first.
    """

    limit = top_n or config.TOP_N_CHART
    _, counterpart_column = get_direction_columns(direction)

    top_pairs = overall_report.head(limit).reset_index(drop=True).copy()
    top_pairs["Short Name"] = shorten_station_names(
        top_pairs[counterpart_column]
    )

    # Reverse the order so the busiest station sits at the top of the chart.
    plotted = top_pairs.iloc[::-1]

    labels = plotted["Short Name"].values
    morning_ridership = plotted["Morning Ridership"].values
    evening_ridership = plotted["Evening Ridership"].values
    all_day_ridership = plotted[config.RIDERSHIP_COLUMN].values

    fig, ax = plt.subplots(figsize=(14, 10))

    x = np.arange(len(labels))
    width = 0.25

    ax.barh(
        x - width,
        morning_ridership,
        width,
        label=config.MORNING_RUSH_LABEL,
        color="#1f77b4",
        alpha=0.85
    )

    ax.barh(
        x,
        evening_ridership,
        width,
        label=config.EVENING_RUSH_LABEL,
        color="#ff7f0e",
        alpha=0.85
    )

    ax.barh(
        x + width,
        all_day_ridership,
        width,
        label=config.ALL_DAY_LABEL,
        color="#2ca02c",
        alpha=0.85
    )

    counterpart_noun = (
        "Destinations" if direction.lower() == "outbound" else "Origins"
    )

    ax.set_yticks(x)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Estimated Average Ridership", fontsize=12)
    ax.set_title(
        f"{station_label} {direction.title()}: "
        f"Morning vs Evening vs All Day\n"
        f"Top {limit} {counterpart_noun} (October 2025)",
        fontsize=14,
        fontweight="bold"
    )
    ax.legend(loc="lower right", fontsize=11)
    ax.grid(axis="x", alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    return top_pairs
