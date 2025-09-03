from abc import ABC
from dataclasses import dataclass

from qwak.feature_store.data_sources.base import BaseSource


@dataclass
class BaseStreamingSource(BaseSource, ABC):
    pass
