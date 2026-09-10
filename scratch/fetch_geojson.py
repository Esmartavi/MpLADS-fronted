import urllib.request
import json
import os

urls = [
    "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
    "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States",
    "https://raw.githubusercontent.com/Anuj-Dutt/India-State-and-Country-Shapefiles-and-GeoJson/master/india_states.geojson"
]

target_file = "scratch/india_states_raw.geojson"

for url in urls:
    print(f"Trying {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=12) as res:
            content = res.read()
            print(f"Downloaded {len(content)} bytes")
            with open(target_file, "wb") as f:
                f.write(content)
            print(f"Saved to {target_file}")
            break
    except Exception as e:
        print(f"Failed: {e}")
