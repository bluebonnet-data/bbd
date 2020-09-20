from pathlib import Path


_working_directory = Path.home()


def resolve_working_directory_path(path) -> Path:
    """If `path` is relative, this method returns it relative to the
    `working_directory`.

    If `path` is already absolute, it will simply be returned.
    """
    p = Path(path)
    if p.is_absolute():
        return p
    else:
        return _working_directory / path


def set_working_directory(path) -> None:
    """Sets the working directory. This is the directory used to cache
    datasets and shapefiles. If a file is passed in, the parent directory
    will be used.
    """
    input_path = Path(path)

    if input_path.is_file():
        p = input_path.parent
    else:
        p = input_path

    p.mkdir(parents=True, exist_ok=True)
    _working_directory = p
