import argparse
import json
import os
import re
import sys

import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
CACHE_FILE = "cache.json"

def read_from_cache():
    """
    Reads data from the cache

    Returns:
        dict: The data from the cache, or None if the cache does not exist
    """
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE) as f:
        data = f.read()
        return json.loads(data)


def write_to_cache(data):
    """
    Writes data to the cache

    Args:
        data: JSON dict to write
    """
    with open(CACHE_FILE, "w") as f:
        f.write(json.dumps(data))


def get_refreshed_data():
    """
    Fetches the latest data from the USGS API

    Returns:
        dict: JSON dict (complete JSON response from API)
    """
    try:
        res = requests.get(URL)
        res.raise_for_status()
        return res.json()
    except Exception as err:
        sys.stderr.write(err)
        sys.stderr.write("There was an error fetching data")
        sys.exit(1)


def get_cached_data():
    """
    Get data from cache, or refresh cache if it doesn't exist

    Returns:
        dict: JSON data
    """
    data = read_from_cache()

    if not data:
        data = get_refreshed_data()
        write_to_cache(data)
    
    return data


def update_cache():
    """
    Force-updates the cache and prints whether the data was changed.
    Note: It only checks the features array when determining changes, to avoid counting metadata.generated timestamp.
    """
    updated_data = get_refreshed_data()

    cached_data = read_from_cache()

    if not cached_data:
        write_to_cache(updated_data)
        return True
    
    is_changed = json.dumps(cached_data["features"]) != json.dumps(updated_data["features"])

    if is_changed:
        write_to_cache(updated_data)
        print("Data was changed")
    else:
        print("Data was not changed")


def save_detail(event_id):
    """
    Saves the detail JSON of a given ID to a JSON file

    Args:
        event_id: Event ID
    """
    data = get_cached_data()
    events = data["features"]

    event = [event for event in events if event["id"] == event_id]
    if not event:
        sys.stderr.write("No event found matching the ID")
        sys.exit(1)

    try:
        res = requests.get(event[0]["properties"]["detail"])
        res.raise_for_status()

        detail = res.json()
        filename = f"{event_id}.json"

        with open(filename, "w") as f:
            f.write(json.dumps(detail))

        print(f"Saved detail to {filename}")
    except Exception as err:
        sys.stderr.write(err)
        sys.stderr.write("There was an error fetching data")
        sys.exit(1)


def query(args):
    """
    Queries the earthquake data from cache

    Args:
        args: Parsed arguments from argparse
    """
    data = get_cached_data()
    events = data["features"]
    
    if args.start:
        events = [event for event in events if event["properties"]["time"] >= args.start]
    if args.end:
        events = [event for event in events if event["properties"]["time"] <= args.end]

    if args.minmag:
        events = [event for event in events if event["properties"]["mag"] >= args.minmag]
    if args.maxmag:
        events = [event for event in events if event["properties"]["mag"] <= args.maxmag]

    if args.location:
        pattern = re.compile(args.location, re.IGNORECASE)
        events = [event for event in events if pattern.search(event["properties"]["place"].lower())]
    
    if not events:
        print("No events found matching the query")
        return

    print("ID\t\tTime\t\tMag\tLocation")
    for event in events:
        print(f'{event["id"]}\t{event["properties"]["time"]}\t{event["properties"]["mag"]}\t{event["properties"]["place"]}')


def parse_args():
    """
    Parses the command line arguments

    Returns:
        args: Dict of parsed args
    """
    parser = argparse.ArgumentParser(description="Earthquake analyzer")

    parser.add_argument("--refresh", "-R", action="store_true", help="Refresh the cache")

    parser.add_argument("--start", type=int, help="Start timestamp")
    parser.add_argument("--end", type=int, help="End timestamp")

    parser.add_argument("--minmag", type=float, help="Minimum magnitude")
    parser.add_argument("--maxmag", type=float, help="Maximum magnitude")

    parser.add_argument("--location", "-L", help="Location of the earthquake")

    parser.add_argument("--save", dest="item_id", help="Item ID to save detail")

    return parser.parse_args()


def main():
    args = parse_args()
    
    if args.refresh:
        update_cache()

    elif args.item_id:
        save_detail(args.item_id)

    else:
        query(args)
    

if __name__ == "__main__":
    main()
