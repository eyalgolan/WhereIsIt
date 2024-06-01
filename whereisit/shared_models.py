from enum import Enum
from typing import List, Union

from pydantic import BaseModel


class TubeLine(Enum):
    TRAM = "tram"
    DLR = "dlr"
    BAKERLOO = "bakerloo"
    CENTRAL = "central"
    DISTRICT = "district"
    ELIZABETH = "elizabeth line"
    HAMMERSMITH_AND_CITY = "hammersmith-city"
    JUBILEE = "jubilee"
    METROPOLITAN = "metropolitan"
    NORTHERN = "northern"
    PICCADILLY = "piccadilly"
    VICTORIA = "victoria"
    WATERLOO_AND_CITY = "waterloo-city"


class Location(BaseModel):
    lon: float
    lat: float


class Station(Location):
    natpan_id: str
    name: str


class Route(BaseModel):
    locations: List[Union[Location, Station]] = []
