from pathlib import Path

# TODO decide whether or not this paradime is useful


class Cache:
    _working_directory = Path.home()

    def make_path(self, path) -> Path:
        """If `path` is relative, this method returns it relative to the
        `working_directory`.

        If `path` is already absolute, it will simply be returned.
        """
        p = Path(path)
        if p.is_absolute():
            return p
        else:
            return self._working_directory / path

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
    # Simple wrapper for singleton
    __doc__ = cache_.set_working_directory.__doc__  # noqa
    cache_.set_working_directory(path)
