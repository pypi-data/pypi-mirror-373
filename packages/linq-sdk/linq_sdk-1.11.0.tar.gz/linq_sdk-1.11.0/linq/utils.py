import os
import re
from pathlib import Path
from typing import Generator

import requests
import urllib3.util

from linq.client import Linq


def get_latest_scheduler_version() -> str:
    """Gets the latest supported scheduler version.

    This can be used to automatically make a workflow use the latest support version (at time of saving the workflow).
    """
    client = Linq()
    return client.get_supported_scheduler_versions()["maestro"][0]


class Download:
    def __init__(
        self,
        url: str,
        output_dir: str | Path,
        *,
        chunk_size: int = 8192,
    ):
        self.url = url

        self.output_dir = output_dir if isinstance(output_dir, Path) else Path(output_dir)
        self._check_output_dir()

        self._chunk_size = chunk_size

        self._response = requests.get(self.url, stream=True)
        self._response.raise_for_status()

        self.filename = self._get_download_filename()
        self.full_path = self.output_dir / self.filename

        self._file = open(self.full_path, "wb")

        self.total_size = int(self._response.headers.get("Content-Length", 0))
        self.written = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._response.close()
        self._file.close()

    def transfer(self) -> None:
        for _ in self.transfer_with_progress():
            pass

    def transfer_with_progress(self) -> Generator[float, None, None]:
        for chunk in self._response.iter_content(chunk_size=self._chunk_size):
            self._file.write(chunk)
            self.written += len(chunk)
            yield self.progress

    @property
    def progress(self):
        return self.written / self.total_size

    def _check_output_dir(self):
        assert self.output_dir.is_dir(), f'output_dir "{self.output_dir}" must be a directory'
        assert os.access(
            self.output_dir, os.W_OK
        ), f'insufficient permissions to write to output_dir "{self.output_dir}"'

    def _get_download_filename(self) -> str:
        if "Content-Disposition" in self._response.headers:
            disposition = self._response.headers["Content-Disposition"]
            if match := re.search(r'filename="?([^\s"]+)"?', disposition):  # pragma: no branch
                return match.group(1)
        parsed_url = urllib3.util.parse_url(self.url)
        assert parsed_url.path is not None
        return Path(parsed_url.path).name
