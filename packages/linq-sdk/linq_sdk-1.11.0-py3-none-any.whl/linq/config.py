from dataclasses import dataclass
from pathlib import Path
from typing import Self, TypedDict

from linq.file_store import FileStore


class RawConfiguration(TypedDict):
    # NOTE: This type has to only be updated in a backwards-compatible fashion,
    # or old configuration files may fail.
    domain: str
    client_id: str
    auth0_domain: str


@dataclass(kw_only=True, slots=True)
class Config(FileStore[RawConfiguration]):
    domain: str
    client_id: str
    auth0_domain: str

    def is_configured(self) -> bool:
        return self.domain != "" and self.client_id != "" and self.auth0_domain != ""

    @classmethod
    def config_file(cls) -> Path:
        return cls.cache_path() / "linq.yaml"

    def serialize(self) -> RawConfiguration:
        return {
            "domain": self.domain,
            "client_id": self.client_id,
            "auth0_domain": self.auth0_domain,
        }

    @classmethod
    def deserialize(cls, raw_data: RawConfiguration) -> Self:
        return cls(
            domain=str(raw_data["domain"]),
            client_id=str(raw_data["client_id"]),
            auth0_domain=str(raw_data.get("auth0_domain", "")),
        )

    @classmethod
    def empty(cls) -> Self:
        return cls(
            domain="",
            client_id="",
            auth0_domain="",
        )
