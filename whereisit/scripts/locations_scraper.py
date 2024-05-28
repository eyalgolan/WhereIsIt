# This file should hold the logic for getting al the location and station info,
# in order to locate the trains on the map.

from decimal import Decimal
from typing import List

import requests
from pydantic import BaseModel

from whereisit.constants import TubeLine


class Location(BaseModel):
    lon: Decimal
    lat: Decimal


class Station(Location):
    natpan_id: int
    name: str


class Line(BaseModel):
    locations: List[Location]


for line in TubeLine:
    url = f"https://api.tfl.gov.uk/line/{line.name}/route/sequence/all"
    response = requests.request("GET", url).json()
