"""PEP-517 compliant buildsystem API"""

import logging
import os
import tarfile
import tempfile
from gzip import GzipFile
from pathlib import Path

from ._util import WheelBuilder
from ._util import cd
from ._util import create_dist_info
from ._util import maybe_add_key_to_project
from ._util import meson
from ._util import normalize
from .config import Config

log = logging.getLogger(__name__)


def get_requires_for_build_wheel(config_settings=None):
    """Returns a list of requirements for building, as strings"""
    return Config().get('dependencies', [])


# For now, we require all dependencies to build either a wheel or an sdist.
get_requires_for_build_sdist = get_requires_for_build_wheel
prepare_metadata_for_build_wheel = create_dist_info


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    """Builds a wheel, places it in wheel_directory"""
    return WheelBuilder().build(Path(wheel_directory), config_settings, metadata_directory)


def build_sdist(sdist_directory, config_settings=None):
    """Builds an sdist, places it in sdist_directory"""
    distdir = Path(sdist_directory)
    with tempfile.TemporaryDirectory() as builddir:
        with tempfile.TemporaryDirectory() as installdir:
            config = Config()
            argv_meson_options = list(
                filter(None, config_settings.get('meson-options', '').split(' '))
            )
            meson_options = (
                argv_meson_options if not config.meson_options else config.meson_options
            )
            args = [builddir, '--prefix', installdir] + meson_options
            meson(*args, builddir=builddir)
            config.builddir = builddir
            argv_dist_options = list(
                filter(None, config_settings.get('meson-dist-options', '').split(' '))
            )
            meson_options = (
                argv_dist_options
                if not config.meson_dist_options
                else config.meson_dist_options
            )
            dist_args = ['dist', '--no-tests', '-C', builddir] + meson_options
            meson(*dist_args)
            tf_dir = '{}-{}'.format(config['name'], config['version'])
            mesondistfilename = '%s.tar.xz' % tf_dir
            mesondisttar = tarfile.open(Path(builddir) / 'meson-dist' / mesondistfilename)
            for entry in mesondisttar:
                # GOOD: Check that entry is safe
                if os.path.isabs(entry.name) or ".." in entry.name:
                    raise ValueError("Illegal tar archive entry")
                mesondisttar.extract(entry, installdir)
            # OZI uses setuptools_scm to create PKG-INFO
            pkg_info = config.get_metadata()
            distfilename = '{}-{}.tar.gz'.format(
                normalize(config['name']).replace('-', '_'), config['version']
            )
            target = distdir / distfilename
            source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH', '')
            mtime = int(source_date_epoch) if source_date_epoch else None
            with GzipFile(str(target), mode='wb', mtime=mtime) as gz:
                with cd(installdir):
                    with tarfile.TarFile(
                        str(target),
                        mode='w',
                        fileobj=gz,
                        format=tarfile.PAX_FORMAT,
                    ) as tf:
                        root = Path(installdir) / tf_dir
                        maybe_add_key_to_project(config, root / 'pyproject.toml', 'version')
                        maybe_add_key_to_project(config, root / 'pyproject.toml', 'name')
                        tf.add(
                            tf_dir,
                            arcname='{}-{}'.format(
                                normalize(config['name']).replace('-', '_'),
                                config['version'],
                            ),
                            recursive=True,
                        )
                        pkginfo_path = root / 'PKG-INFO'
                        if not pkginfo_path.exists():
                            with open(pkginfo_path, mode='w') as fpkginfo:
                                fpkginfo.write(pkg_info)
                                fpkginfo.flush()
                                tf.add(
                                    Path(tf_dir) / 'PKG-INFO',
                                    arcname=Path(
                                        '{}-{}'.format(
                                            normalize(config['name']).replace('-', '_'),
                                            config['version'],
                                        )
                                    )
                                    / 'PKG-INFO',
                                )
    return target.name
