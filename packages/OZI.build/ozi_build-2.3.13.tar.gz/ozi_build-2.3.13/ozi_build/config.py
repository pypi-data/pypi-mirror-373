import json
import logging
import os
import re
import sys

from .metadata import auto_python_version
from .metadata import check_requires_python
from .metadata import get_description_headers
from .metadata import get_optional_dependencies
from .metadata import get_python_bin
from .metadata import get_requirements_headers
from .metadata import get_simple_headers
from .regexploit import check_pyproject_regexes
from .schema import VALID_BUILD_OPTIONS
from .schema import VALID_EXTRA_METADATA
from .schema import VALID_PROJECT
from .schema import VALID_PYC_WHEEL_OPTIONS

if sys.version_info >= (3, 11):
    import tomllib as toml
elif sys.version_info < (3, 11):
    import tomli as toml

log = logging.getLogger(__name__)


class Config:
    def __init__(self, builddir=None):
        config = self.__get_config()
        self.__metadata = config.get('tool', {}).get('ozi-build', {}).get('metadata', {})
        self.__build = config.get('tool', {}).get('ozi-build', {})
        self.__project = config['project']
        self.__min_python = '3.10'
        self.__max_python = '3.13'
        self.__pyc_wheel = config.get('tool', {}).get('ozi-build', {}).get('pyc_wheel', {})
        self.installed = []
        self.options = []
        if builddir:
            self.builddir = builddir

    @property
    def other_metadata(self):
        return self.__metadata

    @property
    def min_python(self):
        return self.__min_python

    @property
    def max_python(self):
        return self.__max_python

    @property
    def pyc_wheel(self):
        return self.__pyc_wheel

    @property
    def meson_options(self):
        return self.__build.get('meson-options', [])

    @property
    def sign_wheel_files(self):
        return self.__build.get('sign-wheel-files', False)

    @property
    def meson_dist_options(self):
        return self.__build.get('meson-dist-options', [])

    @property
    def meson_python_option_name(self):
        return self.__build.get('meson-python-option-name', None)

    @property
    def pure_python_abi(self):
        return self.__build.get('pure-python-abi', None)

    @property
    def platforms(self):
        return self.__build.get('platforms', None)

    def __introspect(self, introspect_type):
        with open(
            os.path.join(
                self.__builddir,
                'meson-info',
                'intro-' + introspect_type + '.json',
            )
        ) as f:
            return json.load(f)

    @staticmethod
    def __get_config():
        with open('pyproject.toml', 'rb') as f:
            config = toml.load(f)
        check_pyproject_regexes(config)
        return config

    def __getitem__(self, key):
        return self.__project[key]

    def __setitem__(self, key, value):
        self.__project[key] = value

    def __contains__(self, key):
        return key in self.__project

    @property
    def builddir(self):
        return self.__builddir

    @builddir.setter
    def builddir(self, builddir):
        self.__builddir = builddir
        project = self.__introspect('projectinfo')
        self['name'] = project['descriptive_name']
        self['version'] = project['version']
        if 'license' not in self:
            self['license'] = project.get('license', '')[0]
            if 'license' == '':
                raise RuntimeError(
                    "license metadata not found in pyproject.toml or meson.build"
                )
        build_licenses = project.get('license_files')
        self['license-files'] = (
            build_licenses if build_licenses else self.get('license-files', [])
        )
        if len(self.get('license-files')) == 0:
            raise RuntimeError(
                "license-files metadata not found in pyproject.toml or meson.build"
            )

        self.installed = self.__introspect('installed')
        self.options = self.__introspect('buildoptions')
        self.validate_options()

    def validate_options(self):  # noqa: C901
        project = VALID_PROJECT.copy()
        for field, value in self.__project.items():
            if field not in project:
                raise RuntimeError(
                    "%s is not a valid option in the `[project]` section, "
                    "got value: %s" % (field, value)
                )
            elif '{deprecated}' in project[field]['description']:
                log.warning(
                    "%s is deprecated in the `[project]` section, " "got value: %s",
                    field,
                    value,
                )
            del project[field]
        for field, desc in project.items():
            if desc.get('required'):
                raise RuntimeError(
                    "%s is mandatory in the `[project]` section but was not found" % field
                )
        metadata = VALID_EXTRA_METADATA.copy()
        metadata['version'] = {}
        metadata['module'] = {}
        for field, value in self.__metadata.items():
            if field not in metadata:
                raise RuntimeError(
                    "%s is not a valid option in the `[tool.ozi-build.metadata]` section, "
                    "got value: %s" % (field, value)
                )
            elif '{deprecated}' in metadata[field]['description']:
                log.warning(
                    "%s is deprecated in the `[tool.ozi-build.metadata]` section, "
                    "got value: %s" % (field, value)
                )
            del metadata[field]
        for field, desc in metadata.items():
            if desc.get('required'):
                raise RuntimeError(
                    "%s is mandatory in the `[tool.ozi-build.metadata]` section but was not found"
                    % field
                )
        build = VALID_BUILD_OPTIONS.copy()
        for field, value in self.__build.items():
            if field not in build:
                raise RuntimeError(
                    "%s is not a valid option in the `[tool.ozi-build]` section, "
                    "got value: %s" % (field, value)
                )
            elif '{deprecated}' in build[field]['description']:
                log.warning(
                    "%s is deprecated in the `[tool.ozi-build]` section, "
                    "got value: %s" % (field, value)
                )
            del build[field]
        pyc_whl_options = VALID_PYC_WHEEL_OPTIONS.copy()
        for field, value in self.__pyc_wheel.items():
            if field not in pyc_whl_options:
                raise RuntimeError(
                    "%s is not a valid option in the `[tool.ozi-build.pyc_wheel]` section, "
                    "got value: %s" % (field, value)
                )
            del pyc_whl_options[field]
        for k in self['optional-dependencies']:
            if re.match('^[a-z0-9]+(-[a-z0-9]+)*$', k) is None:
                raise RuntimeError(
                    '[project.optional-dependencies] key "{}" is not valid.'.format(k)
                )

    def get(self, key, default=None):
        return self.__project.get(key, default)

    def get_metadata(self):
        meta = {
            'name': self['name'],
            'version': self['version'],
        }
        res = check_requires_python(
            self, auto_python_version(self, get_python_bin(self), meta)
        )
        res += get_simple_headers(self)
        res += get_requirements_headers(self)
        res += get_optional_dependencies(self)
        res += get_description_headers(self)

        return res
