import requests
import sys
import os
import json
import argparse

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
CACHE_FILE = "cache.json"

def read_from_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE) as f:
        data = f.read()
        return json.loads(data)

def write_to_cache(data):
    with open(CACHE_FILE, "w") as f:
        f.write(json.dumps(data))

def get_refreshed_data():
    try:
        res = requests.get(URL)
        res.raise_for_status()
        return res.json()
    except Exception as err:
        sys.stderr.write(err)
        sys.stderr.write("There was an error fetching data")
        sys.exit(1)

# Get from cache, or failing that, refresh data
def get_cached_data():
    data = read_from_cache()

    if not data:
        data = get_refreshed_data()
        write_to_cache(data)
    
    return data

# Returns whether cache changed
def update_existing_cache():
    updated_data = get_refreshed_data()

    cached_data = read_from_cache()

    if not cached_data:
        write_to_cache(updated_data)
        return True
    
    is_changed = json.dumps(cached_data["features"]) != json.dumps(updated_data["features"])

    if is_changed:
        write_to_cache(updated_data)

    return is_changed

def main():
    parser = argparse.ArgumentParser(description="Earthquake analyzer")
    parser.add_argument("--refresh", action="store_true", help="Refresh the cache")
    
    parser.add_argument("--start", type=int, help="Start timestamp")
    parser.add_argument("--end", type=int, help="End timestamp")

    parser.add_argument("--minmag", type=float, help="Minimum magnitude")
    parser.add_argument("--maxmag", type=float, help="Maximum magnitude")

    args = parser.parse_args()
    
    if args.refresh:
        is_changed = update_existing_cache()
        if is_changed:
            print("Data was changed")
        else:
            print("Data was not changed")
       
    # TODO: exit early if no query params were specified 
    
    # Query 
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
    
    if not events:
        print("No events found matching the query")
        return

    for event in events:
        print(event["properties"]["title"])
    
    
if __name__ == "__main__":
    main()
