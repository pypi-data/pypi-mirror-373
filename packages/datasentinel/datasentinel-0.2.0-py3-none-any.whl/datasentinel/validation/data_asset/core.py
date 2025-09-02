from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from datasentinel.core import DataSentinelError


T = TypeVar("T")


class DataAssetError(DataSentinelError):
    pass


class AbstractDataAsset(ABC, Generic[T]):
    """Base class for all data asset implementations."""

    def __init__(self, name: str, schema: str | None = None):
        self._name = name
        self._schema = schema

    @property
    def name(self) -> str:
        """Return the name of the data asset"""
        return self._name

    @property
    def schema(self) -> str | None:
        """Return the schema of the data asset"""
        return self._schema

    @abstractmethod
    def load(self) -> T:
        """Load the data asset"""
