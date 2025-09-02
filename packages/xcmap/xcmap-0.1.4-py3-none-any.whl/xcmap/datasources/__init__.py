from abc import ABC, abstractmethod


class DataSource(ABC):
    @abstractmethod
    def connect(self, config):
        pass

