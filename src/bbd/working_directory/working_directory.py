from pathlib import Path


class _WorkingDirectory:
    def __init__(self):
        self._path = Path.cwd()

    @property
    def path(self):
        """BBD working directory"""
        return self._path

    @path.setter
    def path(self, new_working_directory) -> None:
        """Sets the working directory. This is the directory used to cache
        datasets and shapefiles. If a file is passed in, the parent directory
        will be used.
        """
        input_path = Path(new_working_directory)

        if input_path.is_file():
            p = input_path.parent
        else:
            p = input_path

        if not p.is_absolute():
            raise ValueError(
                f"Working directory must be set to an absolute path, not: {p}"
            )

        p.mkdir(parents=True, exist_ok=True)
        self._path = p

    def resolve(self, path) -> Path:
        """If `path` is relative, this method returns it relative to the
        `working_directory`.

        If `path` is already absolute, it will simply be returned.
        """
        p = Path(path)
        if p.is_absolute():
            return p
        else:
            return self.path / path


working_directory = _WorkingDirectory()
