# charmcraftlocal
Pack charms with local Python package dependencies

## Installation
Install `pipx`: https://pipx.pypa.io/stable/installation/
```
pipx install charmcraftlocal
```

## Usage
At the moment, only charms that manage Python dependencies with Poetry are supported.

### Example directory layout
```
common/
    # Local Python package with shared code
    pyproject.toml
    common/
        __init__.py
kubernetes/
    charmcraft.yaml
    pyproject.toml
    poetry.lock
    # [...]
machines/
    charmcraft.yaml
    pyproject.toml
    poetry.lock
    # [...]
```

<details>
<summary>Example common/pyproject.toml</summary>

```toml
[project]
name = "common"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
]

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```
</details>


### Step 1: Add local package to charm dependencies

Repeat this step for each charm that depends on the local package.

```
poetry add ../common --editable
```

Example pyproject.toml
```toml
[tool.poetry.dependencies]
common = {path = "../common", develop = true}
```

### Step 2: Install charmcraftlocal in charmcraft.yaml
Install charmcraftlocal in the `poetry-deps` charmcraft.yaml part.

Example charmcraft.yaml
```yaml
parts:
  poetry-deps:
    plugin: nil
    override-build: |
      # [...]
      "$HOME/.local/bin/uv" tool install --no-python-downloads charmcraftlocal
```

To install with pipx instead of uv, use `pipx install charmcraftlocal`

### Step 3: Call charmcraftlocal in charmcraft.yaml
Run `charmcraftlocal update-lock` before `poetry export` runs in the charmcraft.yaml part with `plugin: poetry`

Example charmcraft.yaml
```yaml
parts:
  # [...]
  charm-poetry:
    plugin: poetry
    after:
      - poetry-deps
    override-build: |
      # [...]
      "$HOME/.local/bin/charmcraftlocal" update-lock -v

      craftctl default
      # [...]
```


### Step 4: Pack charm
```
ccl pack
```

## How it works
Currently, during `charmcraft pack`, charmcraft can only access files in the directory that contains charmcraft.yaml.

`charmcraftlocal pack`
- searches (the charm's) pyproject.toml for local Python dependencies,
- copies them to the charm directory,
- and calls `charmcraft pack`

`charmcraftlocal update-lock` (called by `charmcraft pack`)
- searches (the charm's) pyproject.toml for local Python dependencies
- and calls Poetry to update pyproject.toml and poetry.lock to reference the copied package(s)

### Why does charmcraftlocal need to be called in charmcraft.yaml?
In the first prototype of charmcraftlocal
- only `ccl pack` needed to be called,
- `ccl pack` called Poetry to update pyproject.toml and poetry.lock,
- and `ccl update-lock` did not exist

The design was changed to maintain compatibility with tooling that expects
- one charm per git repository,
- charmcraft.yaml located at the root of the git repository,
- and `charmcraft pack` to successfully build the charm

To maintain compatibility with that tooling, the `ccl mirror` command automates the creation and updates of "mirror" git repositories that meet the above requirements.

For example, for a git repository with this directory layout
```
common/
    # Local Python package with shared code
    pyproject.toml
    common/
        __init__.py
kubernetes/
    charmcraft.yaml
    pyproject.toml
    poetry.lock
    # [...]
machines/
    charmcraft.yaml
    pyproject.toml
    poetry.lock
    # [...]
```

`ccl mirror` can be used to create two "mirror" repositories—

one for `kubernetes`
```
common/
    # Local Python package with shared code
    pyproject.toml
    common/
        __init__.py
charmcraft.yaml
pyproject.toml
poetry.lock
# [...]
```

and one for `machines`
```
common/
    # Local Python package with shared code
    pyproject.toml
    common/
        __init__.py
charmcraft.yaml
pyproject.toml
poetry.lock
# [...]
```

[git-filter-repo](https://github.com/newren/git-filter-repo) is used to create these "mirror" repositories. In order to preserve commit history while avoiding merge conflicts, `pyproject.toml` and `poetry.lock` must not be modified between the source repository and the "mirror" repositories.

Therefore, `pyproject.toml` and `poetry.lock` are modified at build time by calling `ccl update-lock` in charmcraft.yaml. (This approach enables the "mirror" repositories to be successfully built with `charmcraft pack`.)
