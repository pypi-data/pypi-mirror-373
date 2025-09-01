import gzip
from collections.abc import Iterator
from pathlib import Path
from typing import IO, BinaryIO

import pytest


def absolute_path(filename: str) -> Path:
    return Path(__file__).parent / filename


def open_file(name: str, mode: str = "rb") -> Iterator[IO]:
    with absolute_path(name).open(mode) as fh:
        yield fh


def open_file_gz(name: str, mode: str = "rb") -> Iterator[IO]:
    with gzip.GzipFile(absolute_path(name), mode) as fh:
        yield fh


@pytest.fixture
def qnx6_le() -> Iterator[BinaryIO]:
    yield from open_file_gz("_data/qnx6-le.bin.gz")


@pytest.fixture
def qnx6_be() -> Iterator[BinaryIO]:
    yield from open_file_gz("_data/qnx6-be.bin.gz")


@pytest.fixture
def qnx4() -> Iterator[BinaryIO]:
    yield from open_file_gz("_data/qnx4.bin.gz")
