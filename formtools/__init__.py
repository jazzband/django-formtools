from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-formtools")
except PackageNotFoundError:
    # package is not installed
    __version__ = None
