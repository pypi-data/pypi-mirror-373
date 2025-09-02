from importlib.metadata import PackageNotFoundError, version
from platform import platform


def get_user_agent(package_name: str) -> str:
    """
    Generates a user agent string for the bigdata-client package
    based on the package version and the platform.
    """
    try:
        package_version = version(package_name)
    except PackageNotFoundError:
        package_version = "dev"
    return f"{package_name}/{package_version} (platform; {platform()})"
