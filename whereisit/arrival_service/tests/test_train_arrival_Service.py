from decimal import Decimal
from typing import Dict
from unittest.mock import Mock, patch

from whereisit.arrival_service.train_arrival_service import (
    RelativeTrainArrival,
    TrainArrivalFromAPI,
    TrainArrivalService,
    TubeLine,
)


@patch("requests.request")
def test_get_train_arrivals_from_api(mock_api_response):
    mock_api_response.return_value = Mock()
    mock_api_response.return_value.json.return_value = [
        {
            "$type": "Tfl.Api.Presentation.Entities.Prediction, Tfl.Api.Presentation.Entities",
            "id": "318684779",
            "vehicleId": "437",
            "naptanId": "940GZZLUHOH",
            "lineName": "Metropolitan",
            "platformName": "Northbound Fast - Platform 3",
            "direction": "inbound",
            "destinationNaptanId": "940GZZLUUXB",
            "destinationName": "Uxbridge Underground Station",
            "timeToStation": "145",
        }
    ]

    result = TrainArrivalService()._get_train_arrivals_from_api()

    assert len(result) == 1
    assert 318684779 in result
    train_arrival = result[318684779]
    assert train_arrival.id == 318684779
    assert train_arrival.vehicle_id == 437
    assert train_arrival.line.value == "metropolitan"
    assert train_arrival.platform == "Northbound Fast - Platform 3"
    assert train_arrival.direction == "inbound"
    assert train_arrival.destination == "Uxbridge Underground Station"
    assert train_arrival.time_remaining == 145


def test_update_all_relative_train_arrivals_new_train():
    # Setup
    service = TrainArrivalService()
    train_locations: Dict[int, TrainArrivalFromAPI] = {
        1: TrainArrivalFromAPI(
            id=1,
            vehicle_id=101,
            line=TubeLine("metropolitan"),
            next_station_natpan_id="natpan_id_station_1",
            last_station_natpan_id="natpan_id_station_0",
            platform="Platform 1",
            direction="North",
            destination="Destination 1",
            time_remaining=300,
        )
    }

    # Execute
    service._update_all_relative_train_arrivals(train_locations)

    # Verify
    assert 1 in service.relative_train_locations
    relative_arrival = service.relative_train_locations[1]
    assert relative_arrival.id == 1
    assert relative_arrival.vehicle_id == 101
    assert relative_arrival.line.value == "metropolitan"
    assert relative_arrival.next_station_natpan_id == "natpan_id_station_1"
    assert relative_arrival.last_station_natpan_id == "natpan_id_station_0"
    assert relative_arrival.platform == "Platform 1"
    assert relative_arrival.direction == "North"
    assert relative_arrival.destination == "Destination 1"
    assert relative_arrival.travel_time == 300
    assert relative_arrival.percent_traveled == Decimal("0.00")


def test_update_all_relative_train_arrivals_existing_train():
    # Setup
    service = TrainArrivalService()
    service.relative_train_locations = {
        1: RelativeTrainArrival(
            id=1,
            vehicle_id=101,
            line=TubeLine("metropolitan"),
            next_station_natpan_id="station_1",
            current_location="station_0",
            platform="Platform 1",
            direction="North",
            destination="Destination 1",
            travel_time=300,
            percent_traveled=Decimal("50.00"),
        )
    }

    train_locations: Dict[int, TrainArrivalFromAPI] = {
        1: TrainArrivalFromAPI(
            id=1,
            vehicle_id=101,
            line=TubeLine("metropolitan"),
            next_station_natpan_id="station_1",
            last_station_natpan_id="station_0",
            platform="Platform 1",
            direction="North",
            destination="Destination 1",
            time_remaining=200,
        )
    }

    # Execute
    service._update_all_relative_train_arrivals(train_locations)

    # Verify
    relative_arrival = service.relative_train_locations[1]
    assert relative_arrival.travel_time == 300
    assert relative_arrival.percent_traveled == Decimal("33.33")


def test_update_all_relative_train_arrivals_delay():
    # Setup
    service = TrainArrivalService()
    service.relative_train_locations = {
        1: RelativeTrainArrival(
            id=1,
            vehicle_id=101,
            line=TubeLine("metropolitan"),
            next_station_natpan_id="station_1",
            current_location="station_0",
            platform="Platform 1",
            direction="North",
            destination="Destination 1",
            travel_time=300,
            percent_traveled=Decimal("50.00"),
        )
    }

    train_locations: Dict[int, TrainArrivalFromAPI] = {
        1: TrainArrivalFromAPI(
            id=1,
            vehicle_id=101,
            line=TubeLine("metropolitan"),
            next_station_natpan_id="station_1",
            last_station_natpan_id="station_0",
            platform="Platform 1",
            direction="North",
            destination="Destination 1",
            time_remaining=350,
        )
    }

    # Execute
    service._update_all_relative_train_arrivals(train_locations)

    # Verify
    relative_arrival = service.relative_train_locations[1]
    assert relative_arrival.travel_time == 350
    assert relative_arrival.percent_traveled == Decimal("0.00")
