from pathlib import Path

# TODO decide whether or not this paradime is useful


class Cache:
    _working_directory = Path.home()

    def make_path(self, relative_path) -> Path:
        """Constructs an absolute path to a place in the filesystem relative
        to the cache directory.
        """
        return self._working_directory / relative_path

    def has_file(self, relative_path) -> bool:
        """Returns true if file exists relative to the working directory,
        else false.
        """
        p = self.make_path(relative_path)
        return p.exists() and p.is_file()

    def has_dir(self, relative_path) -> bool:
        """Returns true if directory exists relative to in working directory,
        else false.
        """
        p = self.make_path(relative_path)
        return p.exists() and p.is_dir()

    def set_working_directory(self, path):
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
        self._working_directory = p


cache_ = Cache()


def set_working_directory(path):
    """Sets the working directory. This is the directory used to cache
    datasets and shapefiles. If a file is passed in, the parent directory
    will be used.
    """
    cache_.set_working_directory(path)
