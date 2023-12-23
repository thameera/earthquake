import requests
import sys
import os
import json
import argparse

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
CACHE_FILE = "cache.json"

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
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            data = "\n".join(f.readlines())
            return json.loads(data)
    
    data = get_refreshed_data()
    write_to_cache(data)
        
    return data

# Returns whether cache changed
def update_existing_cache():
    updated_data = get_refreshed_data()
    updated_data_str = json.dumps(updated_data)
    
    if not os.path.exists(CACHE_FILE):
        write_to_cache(updated_data)
        return True
    
    with open(CACHE_FILE) as f:
        cached_data = "\n".join(f.readlines())
        is_changed = cached_data != updated_data_str

        if is_changed:
            write_to_cache(updated_data)

        return is_changed

def main():
    parser = argparse.ArgumentParser(description="Earthquake analyzer")
    parser.add_argument("--refresh", action="store_true", help="Refresh the cache")
    
    parser.add_argument("--start", type=int, help="Start timestamp")
    parser.add_argument("--end", type=int, help="End timestamp")
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
    
    if args.start:
        pass
    if args.end:
        pass
    
    
if __name__ == "__main__":
    main()
