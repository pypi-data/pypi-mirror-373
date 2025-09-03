from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Self, TypedDict

import jwt

from linq.file_store import FileStore

EXPIRY_TOKEN_KEY = "exp"
CURRENT_ORG_TOKEN_KEY = "https://linq.cloud/org_id"


class RawCredentials(TypedDict):
    # NOTE: This type has to only be updated in a backwards-compatible fashion,
    # or old credentials files may fail.
    access_token: str


@dataclass(kw_only=True, slots=True)
class Credentials(FileStore[RawCredentials]):
    access_token: str

    def is_configured(self) -> bool:
        return self.access_token != ""

    def is_expired(self) -> bool:
        expiry_epoch = self._jwt()[EXPIRY_TOKEN_KEY]
        return datetime.fromtimestamp(expiry_epoch) < datetime.now()

    def current_org_auth0_id(self) -> str:
        return self._jwt()[CURRENT_ORG_TOKEN_KEY]

    def _jwt(self):
        return jwt.decode(self.access_token, options={"verify_signature": False})

    @classmethod
    def config_file(cls) -> Path:
        return cls.cache_path() / "credentials.yaml"

    def serialize(self) -> RawCredentials:
        return {
            "access_token": self.access_token,
        }

    @classmethod
    def deserialize(cls, raw_data: RawCredentials) -> Self:
        return cls(
            access_token=raw_data["access_token"],
        )

    @classmethod
    def empty(cls) -> Self:
        return cls(access_token="")
