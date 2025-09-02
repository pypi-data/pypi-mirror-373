from collections import defaultdict

from ML_management.singleton_pattern import Singleton


class MetricAutostepper(metaclass=Singleton):
    def __init__(self):
        self._data = defaultdict(int)

    def get_next_step(self, key):
        step = self._data[key]
        self._data[key] += 1
        return step

    def clear(self):
        self._data = defaultdict(int)
