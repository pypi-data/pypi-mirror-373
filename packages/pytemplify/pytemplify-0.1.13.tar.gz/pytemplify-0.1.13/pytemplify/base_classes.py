"""Base classes for dataclasses and parsers."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Type

from dataclasses_jsonschema import JsonSchemaMixin


@dataclass
class BaseDataClass(JsonSchemaMixin):
    """Base class for dictionary dataclasses."""

    def save(self, filepath: Path) -> None:
        """Save dictionary data into a JSON file"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as json_file:
            json.dump(self.to_dict(), json_file, indent=2)


class BaseParserClass(ABC):
    """Base class for parsing."""

    @abstractmethod
    def parse(self, input_file: Path) -> BaseDataClass:
        """Parse data and return a dataclass."""

    @abstractmethod
    def get_data_class(self) -> Type[BaseDataClass]:
        """Return the data class."""


class BaseParserException(BaseException):
    """Base exception for parser errors."""
