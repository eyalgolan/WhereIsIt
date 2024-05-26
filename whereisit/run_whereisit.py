from arrival_service.train_arrival_service import TrainArrivalService


def main():
    train_service = TrainArrivalService(relative_train_locations={})

    from time import sleep

    while True:
        train_service.get_arrivals()
        sleep(15)


if __name__ == "__main__":
    main()
