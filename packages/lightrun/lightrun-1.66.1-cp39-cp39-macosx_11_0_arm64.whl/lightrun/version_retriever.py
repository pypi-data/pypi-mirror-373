from pkgutil import get_data


def get_version_full():
    return get_data(__name__, "version.txt").decode("ascii").strip()
