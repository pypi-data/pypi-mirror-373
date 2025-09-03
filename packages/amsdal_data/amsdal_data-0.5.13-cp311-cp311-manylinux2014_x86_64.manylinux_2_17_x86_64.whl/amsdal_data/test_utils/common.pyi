from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def temp_dir(*, use_temp_dir: bool = True) -> Iterator[str]: ...
