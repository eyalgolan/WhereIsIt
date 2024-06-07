# Given a vehicle's relative location between stations gathered by the arrival_service,
# And the locations of the stations gathered by the locations_scraper,
# This file should hold the logic for calculating the location of the vehicle on the map.

import json
from pathlib import Path
from typing import List

from src.arrival_service.train_arrival_service import RelativeTrainArrival
from src.location_service.vehicle_location_service import LocationService
from src.shared_models import Route, RouteLocation, TubeLine


class TrainLocationService(LocationService):
    routes: List[Route]
    trains_arrivals: List[RelativeTrainArrival]

    def _load_routes(self) -> None:
        self.routes = []
        for line in TubeLine:
            json_path = Path("locations", f"{line.value}_locations.json")
            with open(json_path, "r") as json_file:
                data = json.load(json_file)
                for data_route in data:
                    print(data_route)
                    locations = data_route.get("locations")
                    route = Route(
                        line=data_route.get("line"),
                        locations=[RouteLocation(**location) for location in locations],
                    )
                self.routes.append(route)
        print(self.routes)

    def __init__(self, train_arrivals):
        self.routes = self._load_routes()
        self.trains_arrivals = train_arrivals

    def get_locations(self):
        pass
