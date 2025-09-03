import importlib.metadata

try:
    __version__ = importlib.metadata.version("datatailr")
except importlib.metadata.PackageNotFoundError:
    import toml  # type: ignore

    try:
        # load the version from pyproject.toml which is located two levels up relative to this file
        this_file_path = __file__
        pyproject_path = this_file_path.rsplit("/", 3)[0] + "/pyproject.toml"
        __version__ = toml.load(pyproject_path)["project"]["version"]
    except (FileNotFoundError, KeyError):
        __version__ = "unknown"
