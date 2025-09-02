"""Core library for vrz.
"""

from pathlib import Path

from semver import Version
from vrz.git_utils import Git
from vrz.poetry_utils import Poetry


class Vrz:
    def __init__(self, path: Path = Path.cwd()):
        self.path = path
        self.poetry = Poetry(path)
        self.git = Git(path)
        self.version_substitution = VersionSubstitution()

    def latest(self) -> Version:
        if self.poetry.is_poetry_project():
            version_str = self.poetry.version_read()
            return Version.parse(version_str)
        else:
            return self.git.latest_version() or Version.parse("0.0.0")

class VersionSubstitution:
    """Replace occurrences of a version string in a file."""

    def replace_version(self, file_path: str, old_version: str, new_version: str):
        with open(file_path, "r") as file:
            content = file.read()

        new_content = content.replace(old_version, new_version)

        with open(file_path, "w") as file:
            file.write(new_content)


__all__ = ["VersionSubstitution"]

