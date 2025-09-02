from abc import ABC
from dataclasses import dataclass
from typing import Optional

from frogml.core.exceptions import FrogmlException
from frogml.feature_store.data_sources.batch._batch import BaseBatchSource


@dataclass
class JdbcSource(BaseBatchSource, ABC):
    username_secret_name: Optional[str] = None
    password_secret_name: Optional[str] = None
    url: Optional[str] = None
    db_table: Optional[str] = None
    query: Optional[str] = None
    repository: Optional[str] = None

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if not (bool(self.db_table) ^ bool(self.query)):
            raise FrogmlException("Only one of query and db_table must be set")
