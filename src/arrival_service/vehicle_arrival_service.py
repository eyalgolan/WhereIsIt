from abc import ABC, abstractmethod


class VehicleArrivalService(ABC):
    @abstractmethod
    def get_arrivals():
        raise NotImplementedError
