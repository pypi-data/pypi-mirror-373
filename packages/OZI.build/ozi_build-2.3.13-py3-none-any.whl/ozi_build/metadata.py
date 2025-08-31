import logging
import string
import subprocess
from pathlib import Path

from packaging.version import Version

log = logging.getLogger(__name__)

PKG_INFO = """\
Metadata-Version: 2.3
Requires-Python: >={min_python}, <{max_python}
Name: {name}
Version: {version}
"""

PKG_INFO_CONFIG_REQUIRES_PYTHON = """\
Metadata-Version: 2.3
Requires-Python: {requires_python}
Name: {name}
Version: {version}
"""

PKG_INFO_NO_REQUIRES_PYTHON = """\
Metadata-Version: 2.3
Name: {name}
Version: {version}
"""

readme_ext_to_content_type = {
    '.rst': 'text/x-rst',
    '.md': 'text/markdown',
    '.txt': 'text/plain',
    '': 'text/plain',
}

GET_PYTHON_VERSION = 'import sys;print("{}.{}".format(*sys.version_info[:2]))'


def auto_python_version(config, python_bin: str, meta):
    python_version = Version(
        subprocess.check_output([python_bin, '-c', GET_PYTHON_VERSION])
        .decode('utf-8')
        .strip('\n')
    )
    if python_version < Version(config.min_python):
        meta.update(
            {
                'min_python': str(python_version),
                'max_python': config.max_python,
            }
        )
    elif python_version >= Version(config.max_python):
        meta.update(
            {
                'min_python': config.min_python,
                'max_python': '{}.{}'.format(
                    python_version.major, str(python_version.minor + 1)
                ),
            }
        )
    else:
        meta.update(
            {
                'min_python': config.min_python,
                'max_python': config.max_python,
            }
        )
    return meta


def check_requires_python(config, meta):
    if config.pure_python_abi is not None:
        meta.pop('min_python')
        meta.pop('max_python')
        res = PKG_INFO_NO_REQUIRES_PYTHON.format(**meta)
    elif config.get('requires-python'):
        meta.pop('min_python')
        meta.pop('max_python')
        meta.update({'requires_python': config.get('requires-python')})
        res = PKG_INFO_CONFIG_REQUIRES_PYTHON.format(**meta)
    else:
        res = PKG_INFO.format(**meta)
    return res


def get_python_bin(config):
    option_build = config.meson_python_option_name
    python = 'python3'
    if option_build:
        for opt in config.options:
            if opt['name'] == option_build:
                python = opt['value']
                break
    return python


def _parse_project_optional_dependencies(config, k: str, v: str):
    metadata = ''
    if any(
        i not in string.ascii_uppercase + string.ascii_lowercase + '-[],0123456789'
        for i in v
    ):
        raise ValueError(
            'pyproject.toml:project.optional-dependencies has invalid character in nested key "{}"'.format(
                k
            )
        )
    for j in (name for name in v.strip('[]').rstrip(',').split(',')):
        if len(j) > 0 and j[0] in string.ascii_uppercase + string.ascii_lowercase:
            for package in config.get('optional-dependencies', {}).get(j, []):
                metadata += 'Requires-Dist: {}; extra=="{}"\n'.format(package, k)
        else:
            raise ValueError(
                'pyproject.toml:project.optional-dependencies nested key target value "{}" invalid'.format(
                    j
                )
            )
    return metadata


def get_optional_dependencies(config):
    res = ''
    for k, v in config.get('optional-dependencies', {}).items():
        res += "Provides-Extra: {}\n".format(k)
        if isinstance(v, list):
            for i in v:
                if i.startswith('['):
                    res += _parse_project_optional_dependencies(config, k, i)
                else:
                    res += 'Requires-Dist: {}; extra=="{}"\n'.format(i, k)
        elif isinstance(v, str):
            res += _parse_project_optional_dependencies(config, k, v)
            log.warning(
                'pyproject.toml:project.optional-dependencies nested key type should be a toml array, like a=["[b,c]", "[d,e]", "foo"], parsed string "{}"'.format(
                    v
                )
            )
    return res


def get_simple_headers(config):  # noqa: C901
    res = ''
    for key, name_header, email_header in [
        ('authors', 'Author', 'Author-email'),
        ('maintainers', 'Maintainer', 'Maintainer-email'),
    ]:
        tables = config.get(key, [])
        names = []
        emails = []
        for table in tables:
            if table.get('name'):
                names += [table['name']]
            if table.get('email'):
                emails += [table['email']]
        if names:
            res += '{}: {}\n'.format(name_header, ', '.join(names))
        if emails:
            res += '{}: {}\n'.format(email_header, ', '.join(emails))
    for key, mdata_key in [
        ('classifiers', 'Classifier'),
        ('urls', 'Project-URL'),
        ('dynamic', 'Dynamic'),
        ('license-files', 'License-File'),
        ('license', 'License'),
        ('description', 'Summary'),
    ]:
        vals = config.get(key, [])
        if key == 'dynamic':
            for i in vals:
                if i in {'Name', 'Version', 'Metadata-Version'}:
                    raise ValueError('{} is not a valid value for dynamic'.format(key))
        if isinstance(vals, str):
            res += '{}: {}\n'.format(mdata_key, vals)
        elif isinstance(vals, dict):
            for k, v in vals.items():
                res += '{}: {}, {}\n'.format(mdata_key, k, v)
        else:
            for val in vals:
                res += '{}: {}\n'.format(mdata_key, val)
    for key, mdata_key in [
        ('provides', 'Provides-Dist'),
        ('obsoletes', 'Obsoletes-Dist'),
        ('requires-external', 'Requires-External'),
    ]:
        vals = config.other_metadata.get(key, [])
        for val in vals:
            res += '{}: {}\n'.format(mdata_key, val)
    return res


def get_requirements_headers(config):
    res = ''
    deps = config.get('dependencies', [])
    if deps:
        for package in deps:
            res += 'Requires-Dist: {}\n'.format(package)
    if config.get('requires', None):
        raise ValueError(
            'pyproject.toml:tools.ozi-build.metadata.requires is deprecated as of OZI.build 1.3'
        )
    return res


def get_description_headers(config):
    res = ''
    description = ''
    description_content_type = 'text/plain'
    if 'readme' in config and isinstance(config['readme'], str):
        description_file = Path(config['readme'])
        with open(description_file, 'r') as f:
            description = f.read()
        description_content_type = readme_ext_to_content_type.get(
            description_file.suffix.lower(), description_content_type
        )
    elif 'readme' in config and isinstance(config['readme'], dict):
        description_file = Path(config['readme']['file'])
        with open(description_file, 'r') as f:
            description = f.read()
        if 'content-type' in config['readme']:
            description_content_type = config['readme']['content-type']
        else:
            raise ValueError('project.readme must specify content-type')

    if description:
        res += 'Description-Content-Type: {}\n'.format(description_content_type)
        res += '\n\n' + description
    return res
