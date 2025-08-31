# OZI.build

This is a python module that implements [pep517] for the [meson] build system.

This implies that any project that deals with python code can easily distributed
to [the Python Package Index (PyPI)](https://pypi.org/) by just setting the right
metadatas in its [`pyproject.toml`] config file

[meson]: https://mesonbuild.com
[pep517]: https://www.python.org/dev/peps/pep-0517/
[`pyproject.toml`]: https://www.python.org/dev/peps/pep-0518/#file-format

## Usage

`OZI.build` doesn't provide any command line tools and should be used
though other standard tools like [pip](https://pip.pypa.io/en/stable/),
 [twine](https://pypi.org/project/twine/) or [build](https://pypi.org/project/build/)

```{toctree}
:maxdepth: 2
OZIproject.dev Homepage <https://oziproject.dev>
changes.OZIproject.dev Changelog <https://changes.oziproject.dev/>
docs.OZIproject.dev Documentation <https://docs.oziproject.dev>
pyproject.md
license.md
```

### Workflow to upload a release to pypi

1. Add a [pyproject.toml](pyproject.md) to your project
2. Install build: `pip3 install build`
3. Build packages: `python3 -m build` (which adds the sdist and wheel to
   the `dist/` folder)
4. Publish the package `twine upload dist/*`

In short for the next release: `rm dist/* && python3 -m build && twine upload dist/*`
