from decimal import Decimal
from typing import List

import requests
from pydantic import BaseModel
from src.constants import TubeLine


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
