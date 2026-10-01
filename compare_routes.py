"""
Compares one route against itself in the opposite direction.

    python compare_routes.py
    python compare_routes.py --other fulton-st
    python compare_routes.py --station times-sq --other union-sq

Prints a weekday table of morning and evening rush-hour ridership for
both travel directions, which shows whether a route is commuter-inbound
in the morning and commuter-outbound in the evening.
"""

import argparse

import analysis
import config


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compare rush-hour ridership in both directions "
                    "between two station complexes."
    )

    parser.add_argument(
        "--station",
        default=None,
        help=f"The focus station key "
             f"(default: {config.ACTIVE_STATION})"
    )

    parser.add_argument(
        "--other",
        default="fulton-st",
        help="The station key to compare against (default: fulton-st)"
    )

    return parser.parse_args()


def compare_routes(dataframe, station, other_station):
    """
    Builds and prints the two-direction weekday comparison table.

    Returns:
        A tuple of the two daily-total lists, focus-to-other first.
    """

    outbound_route = analysis.filter_origin_destination(
        dataframe,
        station["search"],
        other_station["search"]
    )

    inbound_route = analysis.filter_origin_destination(
        dataframe,
        other_station["search"],
        station["search"]
    )

    outbound_totals = analysis.get_ridership_totals_daily(outbound_route)
    inbound_totals = analysis.get_ridership_totals_daily(inbound_route)

    analysis.display_ridership_comparison(
        outbound_totals,
        inbound_totals,
        station["label"],
        other_station["label"]
    )

    return outbound_totals, inbound_totals


def main():
    args = parse_args()

    station = config.get_station(args.station)
    other_station = config.get_station(args.other)

    print(f"Loading {config.MTA_CSV_DATA_FILE.name} "
          f"(this takes a moment)...")

    df = analysis.load_data()

    print(
        f"\n{station['label']} ↔ {other_station['label']} "
        f"rush-hour ridership by weekday\n"
    )

    compare_routes(df, station, other_station)


if __name__ == "__main__":
    main()
