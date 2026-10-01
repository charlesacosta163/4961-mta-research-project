# Grand Central Station Ridership Analysis

A research project analyzing weekday rush-hour subway travel patterns at
**Grand Central–42 St**, using MTA origin-destination ridership data.

## Overview

This project studies how subway travel to and from Grand Central changes
between the morning and evening rush hours. For each station that connects
to Grand Central, it compares morning ridership with evening ridership to
find directional changes and possible morning/evening reversal patterns.

- **Outbound:** trips starting at Grand Central, going to all destinations
- **Inbound:** trips ending at Grand Central, coming from all origins

The project began with Times Sq–42 St and moved to Grand Central because
it is a larger station complex with higher ridership. The code is written
so the focus station can be changed to another station complex.

## Data

- **Source:** MTA Open Data, Subway Origin-Destination Ridership Estimates
  ([data.ny.gov](https://data.ny.gov/Transportation/MTA-Open-Data-Catalog/f462-ka72/about_data))
- **Month:** October 2025
- **Days:** Monday to Friday only
- **Morning rush:** 7:00 AM – 10:59 AM
- **Evening rush:** 3:00 PM – 6:59 PM

Estimated ridership is an average by day of week across the month. The
timestamps use a representative date from the first full week of October,
so "October 6" stands for a typical October Monday, not that exact day.

## Station Map

`station-map.png` shows the **425 unique subway station complexes** in the
dataset, with Grand Central highlighted. The dataset covers subway stations
only, so Long Island Rail Road stations are not included.

## Results

Each direction exports top-25 rankings and a chart:

- `INBOUND_RESULTS/`
- `OUTBOUND_RESULTS/`

Each folder contains morning, evening and overall ranking CSV files, plus a
bar chart comparing morning rush, evening rush and all-day ridership.