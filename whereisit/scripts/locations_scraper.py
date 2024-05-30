# This file should hold the logic for getting al the location and station info,
# in order to locate the trains on the map.

import json
from typing import Dict, List

import requests
from pydantic import BaseModel

from whereisit.constants import TubeLine


class Location(BaseModel):
    lon: float
    lat: float


class Station(Location):
    natpan_id: str
    name: str

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "natpan_id": self.natpan_id,
            "lon": self.lon,
            "lat": self.lat,
        }


class Line(BaseModel):
    locations: List[Location]


for line in TubeLine:
    line_stations = []
    url = f"https://api.tfl.gov.uk/line/{line.value}/route/sequence/all"
    response = requests.request("GET", url).json()

    sub_lines = response["lineStrings"]

    # TODO create a object that describes the order of locations in each subline.
    # The object should also detail for each location if it's a station.

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
        line_stations.append(s.to_dict())

    # TODO save jsons in assets folder
    with open(f"{line.value}_stations.json", "w") as json_file:
        json.dump(line_stations, json_file, indent=4)
