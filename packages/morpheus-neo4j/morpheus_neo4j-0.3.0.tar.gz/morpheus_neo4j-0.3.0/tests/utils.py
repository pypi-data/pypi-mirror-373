"""Test utilities for morpheus tests."""

import tempfile
from collections.abc import Generator
from contextlib import contextmanager, suppress
from pathlib import Path


@contextmanager
def temporary_file(
    mode: str = "w",
    suffix: str | None = None,
    prefix: str | None = None,
    content: str | None = None,
) -> Generator[Path, None, None]:
    """
    Context manager for creating temporary files with guaranteed cleanup.

    This context manager ensures that temporary files are always cleaned up,
    even if an exception occurs during processing.

    Args:
        mode: File mode for opening the temporary file
        suffix: Suffix for the temporary file name
        prefix: Prefix for the temporary file name
        content: Optional content to write to the file

    Yields:
        Path: Path object pointing to the temporary file

    Example:
        with temporary_file(suffix=".py", content="print('hello')") as temp_path:
            # Use temp_path here
            migration = Migration(id="test", file_path=temp_path)
        # File is automatically cleaned up here
    """
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(
            mode=mode, suffix=suffix, prefix=prefix, delete=False
        ) as f:
            if content is not None:
                f.write(content)
                f.flush()
            temp_file = Path(f.name)

        yield temp_file

    finally:
        if temp_file and temp_file.exists():
            with suppress(OSError):
                temp_file.unlink()
