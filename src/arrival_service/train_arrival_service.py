from decimal import ROUND_HALF_DOWN, Decimal
from typing import Dict, List, Optional

import requests
from pydantic import BaseModel

from src.arrival_service.vehicle_arrival_service import VehicleArrivalService
from src.shared_models import TubeLine


class TrainArrivalFromAPI(BaseModel):
    # The tfl api response contains multiple results for the same vehicleId,
    # Each one describing the distance from it to a different station in it's journey.
    id: int  # Not to be confused with vehicleId from tlf api
    vehicle_id: Optional[int]
    line: TubeLine
    # natpan = National Public Transport Access Nodes
    next_station_natpan_id: Optional[str]
    last_station_natpan_id: Optional[str] = None
    platform: str
    direction: Optional[str]
    destination: Optional[str]
    time_remaining: int


class RelativeTrainArrival(BaseModel):
    id: int
    vehicle_id: Optional[int]
    line: TubeLine
    # natpan = National Public Transport Access Nodes
    next_station_natpan_id: Optional[str]
    last_station_natpan_id: Optional[str] = None
    platform: str
    direction: Optional[str]
    destination: Optional[str]
    travel_time: int
    percent_traveled: Decimal


class TrainArrivalService(VehicleArrivalService):
    relative_train_locations: Dict[int, RelativeTrainArrival]

    def __init__(self):
        self.relative_train_locations = {}

    def _get_train_arrivals_from_api(self) -> Dict[int, TrainArrivalFromAPI]:
        train_locations: Dict[int, TrainArrivalFromAPI] = {}
        for line in TubeLine:
            url = f"https://api.tfl.gov.uk/Line/{line.name}/Arrivals"
            response = requests.request("GET", url).json()

            for item in response:
                if isinstance(item, str):
                    continue
                train_location = TrainArrivalFromAPI(
                    id=int(item["id"]),
                    vehicle_id=int(item.get("vehicleId"))
                    if item.get("vehicleId")
                    else None,
                    line=TubeLine(item["lineName"].lower()),
                    next_station_natpan_id=item.get("destinationNaptanId"),
                    last_station_natpan_id=item.get("naptanId"),
                    platform=item["platformName"],
                    direction=item.get("direction"),
                    destination=item.get("destinationName"),
                    time_remaining=item["timeToStation"],
                )
                train_locations[train_location.id] = train_location
        return train_locations

    def _update_all_relative_train_arrivals(
        self, train_locations: Dict[int, TrainArrivalFromAPI]
    ) -> None:
        for train_location_id, train_location in train_locations.items():
            # As we don't know the distance between stations and the trains speed,
            # when we "discover" a new item representing a train's trip between stations,
            # we set it's total trip time between these stations as the time left.
            # This means that when the program starts,
            # it will take a few minutes to show accurate locations of the trains.
            # A solution to this can be to write a script that will save the times/distances between stations, and use that.
            # For now this will do.

            if train_location_id not in self.relative_train_locations:
                self.relative_train_locations[train_location_id] = RelativeTrainArrival(
                    id=train_location_id,
                    vehicle_id=train_location.vehicle_id,
                    line=train_location.line.value,
                    next_station_natpan_id=train_location.next_station_natpan_id,
                    last_station_natpan_id=train_location.last_station_natpan_id,
                    platform=train_location.platform,
                    direction=train_location.direction,
                    destination=train_location.destination,
                    travel_time=train_location.time_remaining,
                    percent_traveled=Decimal("0.00"),
                )
            else:
                # handle delays
                if (
                    train_location.time_remaining
                    > self.relative_train_locations[train_location_id].travel_time
                ):
                    self.relative_train_locations[
                        train_location_id
                    ].travel_time = train_location.time_remaining

                total_time = self.relative_train_locations[
                    train_location_id
                ].travel_time
                percent_traveled_to_station = Decimal(
                    100 - (train_location.time_remaining / total_time) * 100
                )
                self.relative_train_locations[
                    train_location_id
                ].percent_traveled = percent_traveled_to_station.quantize(
                    Decimal("0.00"), rounding=ROUND_HALF_DOWN
                )

    def _remove_obsolete_train_arrivals(
        self, train_locations: Dict[int, TrainArrivalFromAPI]
    ) -> None:
        entries_to_delete = []
        for train_id in self.relative_train_locations:
            if train_id not in train_locations:
                entries_to_delete.append(train_id)
        for entry in entries_to_delete:
            self.relative_train_locations.pop(entry)

    def get_arrivals(self) -> List[RelativeTrainArrival]:
        train_locations = self._get_train_arrivals_from_api()
        self._update_all_relative_train_arrivals(train_locations)
        self._remove_obsolete_train_arrivals(train_locations)

        return list(self.relative_train_locations.values())
        # WIP for debugging purposes
        for key, value in self.relative_train_locations.items():
            print(f"{key}:{value.percent_traveled_to_station}")
        print("==============================")
        # relative_train_locations_next_station = TrainLocationService._get_relative_next_station_locations(relative_train_locations)
