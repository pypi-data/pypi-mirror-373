from __future__ import annotations

from io import BytesIO

import pytest

from dissect.qnxfs.qnx4 import QNX4
from dissect.qnxfs.qnx6 import QNX6
from dissect.qnxfs.qnxfs import is_qnxfs


@pytest.mark.parametrize(
    ("name", "FS"),
    [
        ("qnx6_le", QNX6),
        ("qnx6_be", QNX6),
        ("qnx4", QNX4),
    ],
)
def test_qnx(name: str, FS: type[QNX4 | QNX6], request: pytest.FixtureRequest) -> None:
    fh = request.getfixturevalue(name)

    assert is_qnxfs(fh)

    fs = FS(fh)

    assert sorted(fs.get("/").listdir().keys()) == sorted(
        [
            ".",
            "..",
            ".boot",
            "another_very_long_file_name_to_find_out_how_the_long_entries_work.txt",
            "dir",
            "directory",
            "file.txt",
            "symlink.txt",
            "very_long_file_name_that_will_never_fit_in_a_regular_directory_entry.txt",
        ]
        + ([".altboot", ".bitmap", ".inodes", ".longfilenames"] if FS is QNX4 else [])
    )

    entry = fs.get("file.txt")
    assert entry.is_file()
    assert entry.open().read() == b"wow much qnx\n"
    assert fs.get(entry.inum) is entry

    entry = fs.get("directory")
    assert entry.is_dir()
    assert list(entry.listdir().keys()) == [".", "..", "another.txt"]
    assert fs.get(entry.inum) is entry

    entry = fs.get("dir")
    assert entry.is_symlink()
    assert entry.link == "directory"

    entry = fs.get("symlink.txt")
    assert entry.is_symlink()
    assert entry.link == "directory/another.txt"

    entry = fs.get("very_long_file_name_that_will_never_fit_in_a_regular_directory_entry.txt")
    assert entry.is_file()
    assert entry.open().read() == b"very long file indeed\n"

    entry = fs.get("another_very_long_file_name_to_find_out_how_the_long_entries_work.txt")
    assert entry.is_file()
    assert entry.open().read() == b"how long?\n"

    entry = fs.get("dir/another.txt")
    assert entry.is_file()
    assert entry.open().read() == b"very realtime\n"


def test_qnx_invalid() -> None:
    assert not is_qnxfs(BytesIO(b""))
