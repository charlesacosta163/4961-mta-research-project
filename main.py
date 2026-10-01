"""
Entry point for the station ridership study.

    python main.py                          # both directions, station from config
    python main.py --direction inbound      # one direction only
    python main.py --station times-sq       # analyse a different complex
    python main.py --list-stations          # show the configured stations

The dataset is a little over 400 MB, so it is loaded once here and reused
for every direction rather than re-read per report.
"""

import argparse

import analysis
import config
import station_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Analyse morning and evening rush-hour ridership "
                    "for one MTA station complex."
    )

    parser.add_argument(
        "--station",
        default=None,
        help=f"Station key from config.STATIONS "
             f"(default: {config.ACTIVE_STATION})"
    )

    parser.add_argument(
        "--direction",
        choices=["inbound", "outbound", "both"],
        default="both",
        help="Travel direction to report on (default: both)"
    )

    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help=f"How many rows to export per CSV "
             f"(default: {config.TOP_N_EXPORT})"
    )

    parser.add_argument(
        "--list-stations",
        action="store_true",
        help="Print the configured station keys and exit"
    )

    return parser.parse_args()


def list_stations():
    print("\nConfigured station complexes:\n")

    for key, station in sorted(config.STATIONS.items()):
        marker = "*" if key == config.ACTIVE_STATION else " "

        print(f" {marker} {key:<14} {station['label']:<26} "
              f"matches: {station['search']!r}")

    print("\n * = current ACTIVE_STATION in config.py\n")


def main():
    args = parse_args()

    if args.list_stations:
        list_stations()
        return

    station = config.get_station(args.station)

    print(f"Loading {config.MTA_CSV_DATA_FILE.name} "
          f"(this takes a moment)...")

    df = analysis.load_data()

    print(f"Loaded {len(df):,} rows.")

    directions = (
        ["outbound", "inbound"]
        if args.direction == "both"
        else [args.direction]
    )

    for direction in directions:
        station_report.run_station_report(
            df,
            station,
            direction,
            top_n=args.top
        )


if __name__ == "__main__":
    main()
