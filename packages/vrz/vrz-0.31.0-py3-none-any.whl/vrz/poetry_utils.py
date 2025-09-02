"""Utilities for interacting with Poetry projects."""

from __future__ import annotations

from pathlib import Path
import shlex
import subprocess
import tempfile
import tomllib
import requests as request


class Poetry:
    def __init__(self, working_dir: Path | None = None):
        self.working_dir = working_dir

    @classmethod
    def init_project(cls, path: Path | None = None) -> "Poetry":
        """Initialise a new Poetry project in ``path``.

        If ``path`` is ``None`` a temporary directory will be created.  The
        returned :class:`Poetry` instance has its ``working_dir`` set to the
        project directory.
        """

        if path is None:
            temp_dir = tempfile.TemporaryDirectory()
            project_path = Path(temp_dir.name)
            project_path._temp_dir = temp_dir  # type: ignore[attr-defined]
        else:
            project_path = Path(path)
            project_path.mkdir(parents=True, exist_ok=True)

        subprocess.run(
            shlex.split("poetry init -n"),
            check=True,
            capture_output=True,
            text=True,
            cwd=project_path,
        )

        return cls(working_dir=project_path)

    def is_poetry_project(self, directory: Path | None = None) -> bool:
        """Return ``True`` if ``directory`` contains a Poetry project."""

        dir_path = Path(directory) if directory is not None else self.working_dir
        if dir_path is None:
            return False

        pyproject = dir_path / "pyproject.toml"
        if not pyproject.is_file():
            return False

        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return False

        tool = data.get("tool", {})
        if "poetry" in tool:
            return True

        project = data.get("project")
        build_backend = data.get("build-system", {}).get("build-backend")
        if project and build_backend == "poetry.core.masonry.api":
            return True

        return False

    def version_bump_minor(self) -> None:
        subprocess.run(
            shlex.split("poetry version minor"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.working_dir,
        )

    def version_read(self) -> str:
        output = subprocess.run(
            shlex.split("poetry version -s"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.working_dir,
        )
        return output.stdout.strip()

    def is_published(self, package_name: str) -> bool:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = request.get(url)
        return response.status_code != 404

    def is_current_project_published(self) -> bool:
        project_name = self.project_name()
        return self.is_published(project_name)

    def publish(self) -> bool:
        try:
            subprocess.run(
                shlex.split("poetry publish --build"),
                check=True,
                capture_output=True,
                text=True,
                cwd=self.working_dir,
            )
        except subprocess.CalledProcessError as e:
            print("STDOUT:\n", e.stdout)
            print("STDERR:\n", e.stderr)
            raise
        return True

    def project_name(self) -> str:
        output = subprocess.run(
            shlex.split("poetry version"),
            check=True,
            capture_output=True,
            text=True,
            cwd=self.working_dir,
        )
        return output.stdout.split()[0].strip()


__all__ = ["Poetry"]

