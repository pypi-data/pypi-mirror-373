from pathlib import Path
from typing import Optional

import semver
import typer
from typer import Typer

from vrz.core import VersionSubstitution, Vrz
from vrz.git_utils import Git
from vrz.poetry_utils import Poetry


def _bump_minor(version: str) -> str:
    """Return a version string with the minor part incremented."""
    return str(semver.VersionInfo.parse(version).bump_minor())

def main():
    poetry = Poetry()
    git = Git()
    version_substitution = VersionSubstitution()
    vrz = Vrz(Path.cwd())
    
    app = Typer(
        no_args_is_help=True, 
        help="vrz simplifies versioning and releases of software packages. Created primarily for Python, but can be used with other language platforms as well."
        )

    @app.command()
    def minor(update_file: Optional[list[str]] = typer.Option(default=None)):
        is_poetry_project = poetry.is_poetry_project(Path.cwd())

        if not git.is_git_repo():
            typer.echo("Not a git repository.")
            raise typer.Exit(code=1)

        if is_poetry_project:
            old_version = poetry.version_read()
            poetry.version_bump_minor()
            new_version = poetry.version_read()
            typer.echo(f"Version bumped to {new_version}.")
        else:
            tags = git.list_tags()
            old_version = tags[-1].lstrip("v") if tags else "0.0.0"
            new_version = _bump_minor(old_version)
            typer.echo(f"Version bumped to {new_version}.")

        tag_name = f"v{new_version}"

        if is_poetry_project:
            git.add("pyproject.toml")
            git.commit(f"Released {tag_name}.")
            git.push()
            typer.echo("Pushed updated pyproject.toml.")

        git.create_tag(tag_name)
        git.push_tag(tag_name)
        typer.echo(f"Git tag {tag_name} created and pushed.")

        if update_file:
            for file in update_file:
                typer.echo(f"Updating version in file: {file}")
                version_substitution.replace_version(file, old_version, new_version)
                git.add(file)
            git.commit(f"Updated version to {new_version}.")
            git.push()
            typer.echo("Pushed updated files.")

        if is_poetry_project and poetry.is_current_project_published():
            typer.echo("Publishing package to PyPI.")
            poetry.publish()
            typer.echo("Publishing to PyPI done.")

    @app.command()
    def latest():
        """Get the latest version of the project."""
        typer.echo(vrz.latest())

    app()

if __name__ == "__main__":
    main()
