# Eathquake Data Query Tool

Lets you query data from USGS earthquake data.

Data source: [Raw data](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson) - [JSON schema](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)

## Installation

```sh
pip install -r requirements.txt
```

## Usage

```
python main.py [-h] [--refresh] [--start START] [--end END] [--minmag MINMAG] [--maxmag MAXMAG] [--location LOCATION] [--save ITEM_ID]

options:
  -h, --help            show this help message and exit
  --refresh, -R         Refresh the cache
  --start START         Start timestamp
  --end END             End timestamp
  --minmag MINMAG       Minimum magnitude
  --maxmag MAXMAG       Maximum magnitude
  --location LOCATION, -L LOCATION Location of the earthquake
  --save ITEM_ID        Item ID to save detail
```

## Examples:

```
# List all earthquakes in the past 30 days. Uses cached data, but fetches new data if cache is not present.
python main.py

# Update the cache. Also prints whether the data was changed or not.
python main.py --refresh

# Show only earthquakes after the 1703311054981 (unix timestamp)
python main.py --start 1703311054980

# Filter earthquakes that happened between the start and end timestamps, and between 1 and 2 in magnitude
python main.py --start 1703311054980 --end 1703313461360 --minmag 1 --maxmag 2

# Filter by location. This will be a case-insensitive search.
$ python main.py --location aust

# Save the details of earthquake with the given ID to a JSON file. The IDs are found in the tool's query output.
python main.py --save us7000ljw6
```

## Example output

```
$ python main.py -L aust
ID          Time            Mag Location
us7000lk4c  1702512575963   4.1 24 km NNW of Leinster, Australia
us7000ljw6  1702396582344   4.2 107 km NNE of Fitzroy Crossing, Australia
```

## Assumptions

* The response JSON format does not change.
* The IDs of the features are unique.
