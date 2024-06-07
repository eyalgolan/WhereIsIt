from enum import Enum
from typing import Dict, List, Literal, Union

from pydantic import BaseModel, Field


class TubeLine(Enum):
    TRAM = "tram"
    DLR = "dlr"
    BAKERLOO = "bakerloo"
    CENTRAL = "central"
    DISTRICT = "district"
    # ELIZABETH = "elizabeth line"
    HAMMERSMITH_AND_CITY = "hammersmith-city"
    JUBILEE = "jubilee"
    METROPOLITAN = "metropolitan"
    NORTHERN = "northern"
    PICCADILLY = "piccadilly"
    VICTORIA = "victoria"
    WATERLOO_AND_CITY = "waterloo-city"


class Junction(BaseModel):
    location_type: Literal["Junction"] = "Junction"
    lon: float
    lat: float


class Station(BaseModel):
    location_type: Literal["Station"] = "Station"
    natpan_id: str
    name: str
    lon: float
    lat: float


class RouteLocation(BaseModel):
    location: Union[Junction, Station] = Field(discriminator="location_type")


class Route(BaseModel):
    line: str
    locations: List[RouteLocation]
