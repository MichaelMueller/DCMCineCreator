import sys
import abc
from typing import List, Dict, Tuple


class DataTree:
    @abc.abstractmethod
    def get(self, *keys):
        return None

    @abc.abstractmethod
    def data(self) -> Dict:
        return None

    @abc.abstractmethod
    def set_file_path(self, *keys, value, extensions: List[str] = None, must_exist=True):
        return None

    @abc.abstractmethod
    def set_string(self, *keys, value, regex=None):
        return None
