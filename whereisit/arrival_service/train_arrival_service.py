from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional

import requests
from pydantic import BaseModel

from whereisit.arrival_service.vehicle_arrival_service import VehicleArrivalService
from whereisit.constants import TubeLine


class TrainArrivalFromAPI(BaseModel):
    # The tfl api response contains multiple results for the same vehicleId,
    # Each one describing the distance from it to a different station in it's journey.
    id: int  # Not to be confused with vehicleId from tlf api
    vehicle_id: Optional[int]
    line: TubeLine
    next_station_natpan_id: Optional[str]
    last_visited_station_natpan_id: Optional[
        str
    ] = None  # natpan = National Public Transport Access Nodes
    platform: str
    direction: Optional[str]
    destination: Optional[str]
    time_to_destination: int


class RelativeTrainArrival(BaseModel):
    id: int
    vehicle_id: Optional[int]
    line: TubeLine
    next_station_natpan_id: Optional[str]
    last_visited_station_natpan_id: Optional[str] = None
    platform: str
    direction: Optional[str]
    destination: Optional[str]
    time_from_previous_station_to_next_station: int
    percent_traveled_to_station: Decimal


@dataclass
class TrainArrivalService(VehicleArrivalService):
    relative_train_locations: Dict[int, RelativeTrainArrival]

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
                    last_visited_station_natpan_id=item.get("naptanId"),
                    platform=item["platformName"],
                    direction=item.get("direction"),
                    destination=item.get("destinationName"),
                    time_to_destination=item["timeToStation"],
                )
                train_locations[train_location.id] = train_location
        return train_locations

    def _update_all_relative_train_arrivals(
        self, train_locations: Dict[int, TrainArrivalFromAPI]
    ) -> None:
        for train_location_id, train_location in train_locations.items():
            # As we don't know the distance between stations,
            # when We "discover" a new item representing a train's trip between stations ,
            # we set it's total trip time between these stations as the time left.
            # This means that when the program starts,
            # it will take a few minutes to show accurate locations of the trains.
            # A solution to this can be to write a script that will save the times/distances between # stations, and use that. For now this will do.

            if train_location_id not in self.relative_train_locations:
                self.relative_train_locations[train_location_id] = RelativeTrainArrival(
                    id=train_location_id,
                    vehicle_id=train_location.vehicle_id,
                    line=train_location.line,
                    next_station_natpan_id=train_location.line,
                    current_location=train_location.last_visited_station_natpan_id,
                    platform=train_location.platform,
                    direction=train_location.direction,
                    destination=train_location.destination,
                    time_from_previous_station_to_next_station=train_location.time_to_destination,
                    percent_traveled_to_station=Decimal("0.00"),
                )
            else:
                # handle delays
                if (
                    train_location.time_to_destination
                    > self.relative_train_locations[
                        train_location_id
                    ].time_from_previous_station_to_next_station
                ):
                    self.relative_train_locations[
                        train_location_id
                    ].time_from_previous_station_to_next_station = (
                        train_location.time_to_destination
                    )

                total_time_to_next_station = self.relative_train_locations[
                    train_location_id
                ].time_from_previous_station_to_next_station
                self.relative_train_locations[
                    train_location_id
                ].percent_traveled_to_station = (
                    100
                    - (train_location.time_to_destination / total_time_to_next_station)
                    * 100
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

    def get_arrivals(self) -> Dict[int, RelativeTrainArrival]:
        train_locations = self._get_train_arrivals_from_api()
        self._update_all_relative_train_arrivals(train_locations)
        self._remove_obsolete_train_arrivals(train_locations)

        return self.relative_train_locations
        # WIP for debugging purposes
        for key, value in self.relative_train_locations.items():
            print(f"{key}:{value.percent_traveled_to_station}")
        print("==============================")
        # relative_train_locations_next_station = TrainLocationService._get_relative_next_station_locations(relative_train_locations)
