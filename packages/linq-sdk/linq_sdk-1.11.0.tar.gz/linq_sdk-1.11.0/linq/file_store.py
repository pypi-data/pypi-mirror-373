import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, Self, TypeVar

import yaml
from appdirs import user_cache_dir

RawValues = TypeVar("RawValues")


class FileStore(ABC, Generic[RawValues]):
    @classmethod
    def cache_path(cls) -> Path:
        """Get a platform- and user-specific path for storing application data."""
        return Path(user_cache_dir("linq", "Automata", "v1"))

    @classmethod
    @abstractmethod
    def config_file(cls) -> Path:
        ...

    @classmethod
    def file_exists(cls) -> bool:
        """Simple wrapper around Path.exists.

        Mostly only exists for easier/safer mocking, to avoid having to mock
        PosixPath and WindowsPath separately.
        """
        config_file = cls.config_file()
        return config_file.exists()

    @classmethod
    def load(cls) -> Self:
        """Load an existing file store. If none exists, returns an empty one."""

        if not cls.file_exists():
            return cls.empty()

        with open(cls.config_file(), "r") as f:
            return cls.deserialize(yaml.safe_load(f))

    def save(self):
        """Save the CLI configuration."""
        self.cache_path().mkdir(parents=True, exist_ok=True)
        with open(self.config_file(), "w") as f:
            yaml.dump(self.serialize(), f)

    @classmethod
    def delete(cls):
        """Delete any existing CLI configuration. Safe to call even if no config exists."""
        if cls.file_exists():
            shutil.rmtree(cls.cache_path())

    @abstractmethod
    def serialize(self) -> RawValues:
        ...

    @classmethod
    @abstractmethod
    def deserialize(cls, raw_data: RawValues) -> Self:
        ...

    @classmethod
    @abstractmethod
    def empty(cls) -> Self:
        ...
