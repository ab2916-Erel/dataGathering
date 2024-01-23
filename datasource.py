from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def collect_data(self, target):
        pass