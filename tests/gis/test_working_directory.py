from pathlib import Path

from bbd.working_directory import working_directory


def test_relative_path():
    """Relative path should resolve to absolute path relative to working directory"""
    relative_path = "a/test/path"

    resolved = working_directory.resolve(relative_path)

    assert resolved == Path.cwd() / relative_path


def test_absolute_path():
    """Absolute path should remain the same"""
    abs_path = Path.home() / "a/test/path/to/file.txt"

    resolved = working_directory.resolve(abs_path)

    assert abs_path == resolved


def test_wd_can_be_set():
    """Working directory should respect being set"""
    working_directory.path = Path.home() / "working_dir"

    resolved = working_directory.resolve("a/test/path")

    assert resolved == Path.home() / "working_dir" / "a/test/path"


def _test_wd_can_be_set_and_reset():
    """Working directory should respect being set and re-set"""
    assert working_directory.resolve("a/test") == Path.cwd() / "a/test"

    working_directory.path = Path.home()
    assert working_directory.resolve("a/test") == Path.home() / "a/test"

    working_directory.paht = Path.cwd() / "extra"
    assert working_directory.resolve("a/test") == Path.cwd() / "extra/a/test"
