from pathlib import Path

from bbd.working_directory import resolve_working_directory_path, set_working_directory


def test_relative_path():
    """Relative path should resolve to absolute path relative to working directory"""
    relative_path = "a/test/path"

    resolved = resolve_working_directory_path(relative_path)

    assert resolved == Path.cwd() / relative_path


def test_absolute_path():
    """Absolute path should remain the same"""
    abs_path = Path.home() / "a/test/path/to/file.txt"

    resolved = resolve_working_directory_path(abs_path)

    assert abs_path == resolved


def test_wd_can_be_set():
    """Working directory should respect being set"""
    set_working_directory(Path.home() / "working_dir")

    resolved = resolve_working_directory_path("a/test/path")

    assert resolved == Path.home() / "working_dir" / "a/test/path"


def _test_wd_can_be_set_and_reset():
    """Working directory should respect being set and re-set"""
    assert resolve_working_directory_path("a/test") == Path.cwd() / "a/test"

    set_working_directory(Path.home())
    assert resolve_working_directory_path("a/test") == Path.home() / "a/test"

    set_working_directory(Path.cwd() / "extra")
    assert resolve_working_directory_path("a/test") == Path.cwd() / "extra/a/test"
