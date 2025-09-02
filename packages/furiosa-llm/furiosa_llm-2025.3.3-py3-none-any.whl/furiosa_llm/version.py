# Borrowed from: https://github.com/furiosa-ai/furiosa-sdk-private/blob/main/python/furiosa-common/furiosa/common/utils.py
import logging
import pkgutil

from packaging.version import Version


class FuriosaVersionInfo:
    def __init__(self, version: Version):
        self.version = version.base_version
        self.stage = "dev" if version.is_devrelease else "release"
        assert version.local is not None
        self.hash = version.local.split(".")[0][1:]

    def __str__(self):
        return f"{self.version}-{self.stage} (rev: {self.hash[0:9]})"

    def __repr__(self):
        return f"FuriosaVersionInfo(({self.stage}, {self.version}, {self.hash}))"


def get_sdk_version(module) -> FuriosaVersionInfo:
    """Returns the git commit hash representing the current version of the application."""
    sdk_version = FuriosaVersionInfo(Version("0.0.1dev0+unknown"))
    try:
        git_version = pkgutil.get_data(module, 'git_version.txt')
    except FileNotFoundError:
        logging.debug(
            "git_version.txt is missing. This warning is not expected unless "
            "you're using this package directly"
        )
        return sdk_version

    try:
        assert git_version is not None
        version_string = str(git_version, encoding="UTF-8")
        sdk_version = FuriosaVersionInfo(Version(version_string))
    except Exception as e:  # pylint: disable=broad-except
        logging.warning(e)

    return sdk_version


FURIOSA_LLM_VERSION = get_sdk_version("furiosa_llm")
