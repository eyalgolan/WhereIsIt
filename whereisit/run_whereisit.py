# This is currently a basic runner for debugging purposes.

from arrival_service.train_arrival_service import TrainArrivalService


def main():
    train_service = TrainArrivalService()

    from time import sleep

    while True:
        train_service.get_arrivals()
        sleep(15)


if __name__ == "__main__":
    main()
