"""
Runs a complete inbound or outbound report for one station complex.

This is the piece that replaces the old test-origin.py / test-destination.py
pair: the same code now handles both directions and any station.
"""

import analysis
import config


def get_results_dir(direction):
    """
    Picks the export folder for a direction and creates it if needed.

    Returns:
        A pathlib Path to the results folder.
    """

    if direction.strip().lower() == "outbound":
        results_dir = config.OUTBOUND_RESULTS_DIR

    else:
        results_dir = config.INBOUND_RESULTS_DIR

    results_dir.mkdir(parents=True, exist_ok=True)

    return results_dir


def export_ranking_report(report, station, direction, top_n=None):
    """
    Writes the morning, evening and all-day rankings to CSV.

    File names follow the station slug and direction, for example
    "morning_grand-central-top-25-outbound.csv".

    Returns:
        A dictionary mapping each period to the file it was written to.
    """

    limit = top_n or config.TOP_N_EXPORT
    results_dir = get_results_dir(direction)

    slug = station["slug"]
    suffix = direction.strip().lower()

    exports = {
        "morning": results_dir / f"morning_{slug}-top-{limit}-{suffix}.csv",
        "evening": results_dir / f"evening_{slug}-top-{limit}-{suffix}.csv",
        "overall": results_dir / f"overall-{slug}-top-{limit}-{suffix}.csv"
    }

    for period, output_path in exports.items():
        report[period].head(limit).to_csv(output_path, index=False)

    return exports


def run_station_report(dataframe, station, direction, top_n=None):
    """
    Filters, ranks, exports and charts one station in one direction.

    Returns:
        A dictionary containing the ranking report, the export paths, the
        chart path and the plotted rows.
    """

    label = station["label"]
    normalized = direction.strip().lower()

    print(f"\nBuilding {normalized} report for {label}...")

    station_trips = analysis.filter_by_station(
        dataframe,
        station["search"],
        normalized
    )

    if station_trips.empty:
        raise ValueError(
            f"No {normalized} trips matched '{station['search']}'. "
            f"Check the search text in config.py against the station "
            f"complex names in the dataset."
        )

    report = analysis.build_ranking_report(station_trips)

    exports = export_ranking_report(report, station, normalized, top_n)

    chart_path = (
        get_results_dir(normalized)
        / f"{station['slug']}-{normalized}-morning-vs-evening.png"
    )

    plotted = analysis.plot_rush_hour_comparison(
        report["overall"],
        label,
        normalized,
        chart_path,
        top_n=config.TOP_N_CHART
    )

    print_summary(plotted, label, normalized, exports, chart_path)

    return {
        "report": report,
        "exports": exports,
        "chart_path": chart_path,
        "plotted": plotted
    }


def print_summary(plotted, station_label, direction, exports, chart_path):
    """
    Prints the headline numbers for a finished report.
    """

    counterpart_noun = (
        "destination" if direction == "outbound" else "origin"
    )

    top_row = plotted.iloc[0]

    print("=" * 60)
    print(f"{station_label.upper()} — {direction.upper()} REPORT")
    print("=" * 60)

    for period, output_path in exports.items():
        print(f"  {period.title():<8} CSV : {output_path.name}")

    print(f"  Chart        : {chart_path.name}")
    print()
    print(f"  Busiest {counterpart_noun}: {top_row['Short Name']}")
    print(
        f"  Morning peak   : "
        f"{plotted['Morning Ridership'].max():,.0f} riders"
    )
    print(
        f"  Evening peak   : "
        f"{plotted['Evening Ridership'].max():,.0f} riders"
    )
    print(
        f"  Overall peak   : "
        f"{plotted[config.RIDERSHIP_COLUMN].max():,.0f} riders"
    )
    print("=" * 60)
