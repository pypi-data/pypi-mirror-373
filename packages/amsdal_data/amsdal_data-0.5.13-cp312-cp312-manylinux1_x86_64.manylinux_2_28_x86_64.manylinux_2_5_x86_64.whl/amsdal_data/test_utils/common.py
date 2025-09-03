import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def temp_dir(*, use_temp_dir: bool = True) -> Iterator[str]:
    tmp_dir = None

    if use_temp_dir:
        tmp_dir = '.tmp'
        Path(tmp_dir).mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(dir=tmp_dir) as directory:
        yield directory
