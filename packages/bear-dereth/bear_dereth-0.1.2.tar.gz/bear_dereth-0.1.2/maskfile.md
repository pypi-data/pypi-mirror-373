# Python Project Mask File

## clean

> This command cleans the build artifacts

```bash
rm -rf dist/
rm -rf .nox/
rm -rf htmlcov/
rm -rf .coverage*
```

## lint

> Run linting checks with ruff

```bash
nox -s ruff_check
```

## fix

> Fix linting issues with ruff

```bash
nox -s ruff_fix
```

## typecheck

> Run type checking with pyright

```bash
nox -s pyright
```

## test

> This command runs the tests using nox

```bash
nox -s tests
```

## check

> Run all quality checks (lint + typecheck + test)

```bash
$MASK lint
$MASK typecheck
$MASK test
```

## bump (patch_version)

> Bump the version of the local project specifying the patch level: `minor`, `major`, `patch`

```bash
uv sync
path_to_script=bear-dereth
current_version=$(${path_to_script} version)
echo "Current version: ${current_version}"
if [ -z "${patch_version}" ]; then
    echo "Please specify a patch version: minor, major, or patch"
    exit 1
fi
if [ "${patch_version}" != "minor" ] && [ "${patch_version}" != "major" ] && [ "${patch_version}" != "patch" ]; then
    echo "Invalid patch version specified. Use minor, major, or patch."
    exit 1
fi
if [ -z "${current_version}" ]; then
    echo "Current version is not set. Please run '${path_to_script} version' first."
    exit 1
fi
new_version=$(${path_to_script} bump "${patch_version}")
if [ $? -ne 0 ]; then
    echo "Failed to bump version. Please check the current version and try again."
    exit 1
fi
if [ -z "${new_version}" ]; then
    echo "Failed to bump version. Please check the current version and try again."
    exit 1
fi
echo "New version: ${new_version}"  
git tag -a "v${new_version}" -m "Bump version to v${new_version}"
git push origin "v${new_version}"
```

## build

> This command builds the project via uv

```bash
uv build
```

## publish (publish_location)

> This command publishes the package to PyPI or a local repository! Isn't that great?

```bash
if [ "${publish_location}" = "twine" ]; then
    twine upload -r local dist/* # uploads to a local repository
else
    export UV_PUBLISH_TOKEN=$(op read "op://Private/PyPI Prod/api_key")
    uv publish --index pypi dist/* --token $UV_PUBLISH_TOKEN
fi
```

## full (patch_version) (publish_location)

> This command runs the full build and publish process

```bash
$MASK clean
$MASK bump ${patch_version}
$MASK build
$MASK publish ${publish_location}
```
