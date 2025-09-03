from importlib import metadata


def get_package_version(package_name):
    try:
        version = metadata.version(package_name)
        return version
    except metadata.PackageNotFoundError:  # pragma no cover
        return f"{package_name} not found"


version = get_package_version("versionix")


from .logging import Logging

logger = Logging("versionix", "INFO", text_color="green")

from versionix.parser import get_version
