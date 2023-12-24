# Eathquaake Data Query Tool

Lets you query data from USGS earthquake data.

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
$ python main.py
# Lists all earthquakes in the past 30 days. Uses cached data, but fetches new data if cache is not present.

$ python main.py --refresh
# Updates the cache. Also prints whether the data was changed or not.

$ python main.py --start 1703311054980
# Shows only earthquakes after the 1703311054981 (unix timestamp)

$ python main.py --start 1703311054980 --end 1703313461360 --minmag 1 --maxmag 2
# Filters earthquakes that happened between the start and end timestamps, and between 1 and 2 in magnitude

$ python main.py --location aust
# Filters by location. This will be a case-insensitive search.

$ python main.py --save us7000ljw6
# Saves the details of earthquake with the given ID to a JSON file. The IDs are found in the tool's query output.
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
