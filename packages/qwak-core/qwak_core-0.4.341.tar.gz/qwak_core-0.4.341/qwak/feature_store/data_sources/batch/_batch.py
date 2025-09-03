from abc import ABC
from dataclasses import dataclass

from qwak.feature_store.data_sources.base import BaseSource


@dataclass
class BaseBatchSource(BaseSource, ABC):
    date_created_column: str
