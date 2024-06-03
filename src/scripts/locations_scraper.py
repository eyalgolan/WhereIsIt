# This file holds the logic for getting all the locations and stations info per route per line,
# in order to locate the trains on the map.

import json
from pathlib import Path
from typing import Dict, List

import requests

from src.shared_models import Location, Route, Station, TubeLine

for line in TubeLine:
    url = f"https://api.tfl.gov.uk/line/{line.value}/route/sequence/all"
    response = requests.request("GET", url).json()

    line_stations: Dict[str, Station] = {}
    try:
        stations = response["stations"]
    except KeyError:
        print(f"API call for line {line.value} didn't return any stations")
        continue
    for station in stations:
        s = Station(
            natpan_id=station.get("id"),
            name=station.get("name"),
            lat=station.get("lat"),
            lon=station.get("lon"),
        )
        line_stations[f"{s.lat}_{s.lon}"] = s

    routes: List[Route] = []
    line_strings = response["lineStrings"]
    for raw_line_string in line_strings:
        line_string = json.loads(raw_line_string)[0]
        locations = []
        for segment in line_string:
            lat_lon = f"{segment[1]}_{segment[0]}"
            if lat_lon in line_stations:
                locations.append(line_stations[lat_lon])
            else:
                locations.append(Location(lat=segment[0], lon=segment[1]))
        routes.append(Route(line=line.value, locations=locations))

    json_path = Path("locations", f"{line.value}_locations.json")
    output = [route.model_dump() for route in routes]
    with open(json_path, "w") as json_file:
        json.dump(output, json_file, indent=4)
