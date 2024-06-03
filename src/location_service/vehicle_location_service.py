from abc import ABC, abstractmethod


class LocationService(ABC):
    @abstractmethod
    def get_locations():
        raise NotImplementedError
