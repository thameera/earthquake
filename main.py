import requests
import sys
import os
import json
import argparse

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
CACHE_FILE = "cache.json"

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
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            data = "\n".join(f.readlines())
            return json.loads(data)
    
    data = get_refreshed_data()
    with open(CACHE_FILE, "w") as f:
        f.write(json.dumps(data))
        
    return data

# Returns whether cache changed
def update_existing_cache():
    updated_data = get_refreshed_data()
    updated_data_str = json.dumps(updated_data)
    
    if not os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            data = "\n".join(f.readlines())
            return True
    
    f = open(CACHE_FILE)
    cached_data = "\n".join(f.readlines())
    f.close()
    
    with open(CACHE_FILE, "w") as writer:
        writer.write(updated_data_str)
    
    return cached_data != updated_data_str

def main():
    parser = argparse.ArgumentParser(description="Earthquake analyzer")
    parser.add_argument("--refresh", action="store_true", help="Refresh the cache")
    
    parser.add_argument("--from", type="int", help="Start timestamp")
    parser.add_argument("--to", type="int", help="End timestamp")
    args = parser.parse_args()
    
    if args.refresh:
        is_changed = update_existing_cache()
        print("Data was changed")
       
    # TODO: exit early if no query params were specified 
    
    # Query 
    data = get_cached_data()
    
    if args.from:
        pass
    if args.to:
        pass
    
    
if __name__ == "__main__":
    main()
