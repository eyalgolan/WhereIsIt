# This is currently a basic runner for debugging purposes.

from arrival_service.train_arrival_service import TrainArrivalService
from location_service.train_location_service import TrainLocationService


def main():
    train_service = TrainArrivalService()

    from time import sleep

    while True:
        arrivals = train_service.get_arrivals()
        TrainLocationService(train_arrivals=arrivals)
        sleep(15)


if __name__ == "__main__":
    main()
