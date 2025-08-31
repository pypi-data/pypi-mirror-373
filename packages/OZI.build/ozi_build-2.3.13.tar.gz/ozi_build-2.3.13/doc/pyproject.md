# Configuration

OZI.build only supports reading configuration from `pyproject.toml`.
This file lives at the root of the module/package, at the same place
as the toplevel `meson.build` file.

## Build system table

This tells tools like pip to build your project with flit. It's a standard
defined by PEP 517. For any project using OZI.build, it will look something like this:

``` toml
    [build-system]
    requires = ["OZI.build[core]~=1.9"]
    build-backend = "ozi_build.buildapi"
```

## Project table

This holds the essential project metadata that is outside of the ``meson.build`` file.
Some keys remain in the project table for improved cross-compatibility.
It should look similar to this in an OZI.build project:

``` toml
    [project]
    name = "project_name"
    dynamic = ["version"]
    dependencies = [
    'TAP-Producer~=1.0.4',
    ]

    [project.license]
    file = "LICENSE.txt"

    [project.optional-dependencies]
    ...
```

> NOTE: The project version and name are extracted from the `meson.build`
> [`project()`](http://mesonbuild.com/Reference-manual.html#project) table.

### `authors`

A list of mappings with keys 'name' and 'email'.

### `classifiers`

A list of [classifiers](https://pypi.python.org/pypi?%3Aaction=list_classifiers).

### `dependencies`

A list of requirements.

### `description`

A short project summary.

### `dynamic`

A list of other headers to be treated as dynamic fields.

### `entry-points`

A collection of tables. Each sub-table name is an entry point group.
For example:

``` toml
[project.entry-points."otio"]
view = "opentimelineview.console:main"
cat = "opentimelineio.console.otiocat:main"
convert = "opentimelineio.console.otioconvert:main"
stat = "opentimelineio.console.otiostat:main"
autogen_serialized_schema_docs = "opentimelineio.console.autogen_serialized_datamodel:main"
```

### `gui-scripts`

A table of entry point names mapped to modules.
For example:

``` toml
[project.gui-scripts]
otioview = "opentimelineview.console:main"
otiocat = "opentimelineio.console.otiocat:main"
otioconvert = "opentimelineio.console.otioconvert:main"
otiostat = "opentimelineio.console.otiostat:main"
otioautogen_serialized_schema_docs = "opentimelineio.console.autogen_serialized_datamodel:main"
```

### `keywords`

Comma-separated keywords as a string.

### `license`

Text indicating the license covering the distribution.
This text can be either a valid license expression as defined in [pep639](https://www.python.org/dev/peps/pep-0639/#id88) or any free text.


### `license-files`

An array of license filenames.

### `maintainers`

A collection of tables with keys 'name' and 'email'.

### `name`

The non-normalized package name.

### `optional-dependencies`

A mapping of optional dependency group names to lists of requirements.

### `readme`

A string of the readme filename or a table with keys ``file`` and ``content-type``.

### `requires-python`

A version specifier for the versions of Python this requires, e.g. ``~=3.3`` or
``>=3.3,<4`` which are equivalents.

### `scripts`

A table of entry point names mapped to modules.

For example:

``` toml
[project.scripts]
otioview = "opentimelineview.console:main"
otiocat = "opentimelineio.console.otiocat:main"
otioconvert = "opentimelineio.console.otioconvert:main"
otiostat = "opentimelineio.console.otiostat:main"
otioautogen_serialized_schema_docs = "opentimelineio.console.autogen_serialized_datamodel:main"
```


### `urls`

A table of labels mapped to urls.
For example:

``` toml
[project.urls]
Source = "https://github.com/OZI-Project/OZI.build"
```


### `version`

The current package version.


## OZI.build configuration

This table is called `[tool.ozi-build]` in the file.

### `meson-options`

A list of default meson options to set, can be overridden and expanded through the `MESON_ARGS`
environment variable at build time.

### `meson-dist-options`

A list of default ``meson dist`` options to set at build time.

### `meson-python-option-name`

The name of the meson options that is used in the meson build definition
to set the python installation when using
[`python.find_installation()`](http://mesonbuild.com/Python-module.html#find_installation).

### `sign-wheel-files`

:::{versionadded} 2.2
Sign wheel RECORD files with JWS (JSON Web Signature).
:::

> ! NOTE: Requires WHEEL_SIGN_TOKEN environment variable to be set.

### `metadata`

Table of additional, rarely used packaging metadata.

### `platforms`

Supported Python platforms, can be 'any', py3, etc...

### `pure-python-abi`

An override of the pure python abi build target e.g. ``py3-none``.

### `pyc_wheel`

Table of options for pyc_wheel.


## Metadata table

This table is called `[tool.ozi-build.metadata]` in the file.

### `obsoletes`


A list of PyPI packages that this project should not be installed concurrently with.

``` toml
      obsoletes = [
        "OtherProject",
        "AnotherProject==3.4",
        'virtual_package; python_version >= "3.4"',
      ]
```


### `provides`

A list of PyPI packages that this project provides its own version of.

``` toml
      provides = [
        "OtherProject",
        "AnotherProject==3.4",
        'virtual_package; python_version >= "3.4"',
      ]
```

### `requires-external`

A list of non-PyPI dependency packages. For example:

``` toml
      requires-external = [
          "git",
          "node",
      ]
```


## ``pyc_wheel`` configuration

This table is called `[tool.ozi-build.pyc_wheel]` in the file.

### `exclude`

A regular expression of files for pyc_wheel to ignore.

### `quiet`

Quiet non-error output of pyc_wheel.


