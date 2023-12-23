import requests
import sys
import os
import json
import argparse
import re

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
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

def save_detail(event_id):
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

def main():
    parser = argparse.ArgumentParser(description="Earthquake analyzer")
    parser.add_argument("--refresh", "-R", action="store_true", help="Refresh the cache")
    
    parser.add_argument("--start", type=int, help="Start timestamp")
    parser.add_argument("--end", type=int, help="End timestamp")

    parser.add_argument("--minmag", type=float, help="Minimum magnitude")
    parser.add_argument("--maxmag", type=float, help="Maximum magnitude")

    parser.add_argument("--location", "-L", help="Location of the earthquake")

    parser.add_argument("--save", dest="item_id", help="Item ID to save detail")

    args = parser.parse_args()
    
    if args.refresh:
        is_changed = update_existing_cache()
        if is_changed:
            print("Data was changed")
        else:
            print("Data was not changed")
        return

    if args.item_id:
        save_detail(args.item_id)
        return
       
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

    if args.location:
        pattern = re.compile(args.location, re.IGNORECASE)
        events = [event for event in events if pattern.search(event["properties"]["place"].lower())]
    
    if not events:
        print("No events found matching the query")
        return

    print("ID\t\tTime\t\tMag\tLocation")
    for event in events:
        print(f'{event["id"]}\t{event["properties"]["time"]}\t{event["properties"]["mag"]}\t{event["properties"]["place"]}')
    
    
if __name__ == "__main__":
    main()
