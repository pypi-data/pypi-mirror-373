# vrz: Easy versioning and releases

`vrz` simplifies versioning and releases of software packages. Created primarily for Python, but can be used with other language platforms as well.

## Installation

In order to add `vrz` into your Poetry project, execute the following command:

```bash
poetry add --group=dev vrz
```

You can also install `vrz` globally using pipx:

```bash
pipx install vrz
```

## Usage

In order to release new minor version of your application, execute the `vrz minor` command:

```
$ vrz minor
Version bumped to 0.31.0.
Pushed updated pyproject.toml.
Git tag v0.31.0 created and pushed.
Publishing package to PyPI.
Publishing to PyPI done.
```

`vrz` will:
- bump your `pyproject.toml` project version (if Poetry project is detected)
- commit and push `pyproject.toml` (if Poetry project is detected)
- create and push Git tag
- publish package to PyPI (if current project is already present in PyPI index)

## Release GitHub workflow

[Release workflow](.github/workflows/release.yml) from this project can be used as a copy-paste ready template for your project:

```bash
cd myproject
mkdir -p .github/workflows
curl -fsSL "https://raw.githubusercontent.com/hekonsek/vrz/refs/heads/main/.github/workflows/release.yml" \
  -o .github/workflows/release.yml
```

With this workflow you can just go straight to "Release" workflow in your "Action" and trigger workflow manually using "Run workflow" to release new minor version of your project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.