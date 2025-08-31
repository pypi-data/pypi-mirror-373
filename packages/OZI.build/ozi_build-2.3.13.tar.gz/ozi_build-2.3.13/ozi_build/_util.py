import contextlib
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
from email.message import EmailMessage
from hashlib import sha256
from pathlib import Path
from typing import Optional

from .config import Config
from .config import get_python_bin
from .jwt import encode as jws_encode
from .pyc_wheel import _b64encode
from .pyc_wheel import convert_wheel
from .pyc_wheel import extract_wheel
from .pyc_wheel import zip_wheel
from .wheel.pep425tags import get_abbr_impl
from .wheel.pep425tags import get_abi_tag
from .wheel.pep425tags import get_impl_ver
from .wheel.pep425tags import get_platform_tag
from .wheel.wheelfile import WheelFile

log = logging.getLogger(__name__)

GET_CHECK = """
from ozi_build.wheel import pep425tags
tag = pep425tags.get_abbr_impl() + pep425tags.get_impl_ver()
if tag != pep425tags.get_abi_tag():
    print("{0}-{1}".format(tag, pep425tags.get_abi_tag()))
else:
    print("{0}-none".format(tag))
"""


def sign_record_file(whl_file):
    if not os.environ.get('WHEEL_SIGN_TOKEN'):
        log.warning(
            'pyproject.toml:tool.ozi-build.sign-wheel-files set to True '
            'but WHEEL_SIGN_TOKEN environment variable was not set.'
        )
        return
    dist_info = "-".join(whl_file.stem.split("-")[:-3])
    whl_dir = tempfile.mkdtemp()
    whl_path = Path(whl_dir)
    try:
        members, _ = extract_wheel(whl_file, whl_dir)
        dist_info_path = whl_path.joinpath("{}.dist-info".format(dist_info))
        record_path = dist_info_path / "RECORD"
        record_path.chmod(stat.S_IWUSR | stat.S_IRUSR)
        record_hash = sha256()
        with open(record_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                record_hash.update(data)
        record_path.with_suffix('.jws').write_text(
            jws_encode(
                {'hash': "sha256={}".format(_b64encode(record_hash.digest()))},
                key=os.environ['WHEEL_SIGN_TOKEN'].encode(),
                algorithm='RS256',
            )
        )
        zip_wheel(whl_file, whl_dir, False)
    finally:
        # Clean up original directory
        shutil.rmtree(whl_dir, ignore_errors=True)


@contextlib.contextmanager
def cd(path):
    CWD = os.getcwd()

    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(CWD)


def get_wheel_file(
    is_pure: bool,
    install_paths_to: Optional[list] = None,
    build_number: Optional[list] = None,
):
    msg = EmailMessage()
    msg.add_header('Wheel-Version', '1.9')
    msg.add_header('Generator', 'OZI.build @VERSION@')
    msg.add_header('Root-Is-Purelib', str(is_pure).lower())
    msg.add_header(
        'Tag',
        (
            'py3-none-any'
            if is_pure
            else '{0}{1}-{2}-{3}\n'.format(
                get_abbr_impl(),
                get_impl_ver(),
                get_abi_tag(),
                get_platform_tag(),
            )
        ),
    )
    if install_paths_to:
        for i in install_paths_to:
            msg.add_header('Install-Paths-To', i)
    if build_number:
        msg.add_header('Build', build_number)
    return str(msg).strip()


def install_files_path(installpath, target):
    while os.path.basename(installpath) != target:
        installpath = os.path.dirname(installpath)
    return installpath


def meson(*args, builddir=''):
    try:
        return subprocess.check_output(['meson'] + list(args))
    except subprocess.CalledProcessError as e:
        stdout = ''
        stderr = ''
        if e.stdout:
            stdout = e.stdout.decode().strip()
        if e.stderr:
            stderr = e.stderr.decode().strip()
        print("Could not run meson: %s\n%s" % (stdout, stderr), file=sys.stderr)
        try:
            fulllog = os.path.join(builddir, 'meson-logs', 'meson-log.txt')
            with open(fulllog) as f:
                print("Full log: %s" % f.read())
        except IOError:
            print("Could not open %s" % fulllog)  # type: ignore
        raise SystemExit(e)


def meson_configure(*args):
    args = list(args)
    args.append('-Dlibdir=lib')
    meson(*args, builddir=args[0])


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def check_is_pure(installed):
    variables = sysconfig.get_config_vars()
    suffix = variables.get('EXT_SUFFIX') or variables.get('SO') or variables.get('.so')
    # msys2's python3 has "-cpython-36m.dll", we have to be clever
    split = suffix.rsplit('.', 1)
    suffix = split.pop(-1)

    for installpath in installed.values():
        if "site-packages" in installpath or "dist-packages" in installpath:
            if installpath.split('.')[-1] == suffix:
                return False

    return True


def get_abi(python):
    return subprocess.check_output([python, '-c', GET_CHECK]).decode('utf-8').strip('\n')


class WheelBuilder:
    def __init__(self):
        self.wheel_zip = None  # type: ignore
        self.builddir = tempfile.TemporaryDirectory()
        self.installdir = tempfile.TemporaryDirectory()
        self.metadata_dir = None

    def build(self, wheel_directory, config_settings, metadata_dir):
        config = Config()
        argv_meson_options = (
            config_settings.get('meson-options', '').split(' ')
            if config_settings is not None
            else ''
        )
        meson_options = (
            argv_meson_options if not config.meson_options else config.meson_options
        )
        args = [
            self.builddir.name,
            '--prefix',
            self.installdir.name,
        ] + list(filter(None, meson_options))
        meson_configure(*args)
        config.builddir = self.builddir.name
        if config['version'] == '%OZIBUILDVERSION%':
            config['version'] = Path(os.getcwd()).name.split('-')[1]
        self.metadata_dir = create_dist_info(
            wheel_directory, builddir=self.builddir.name, config=config
        )

        is_pure = check_is_pure(config.installed)
        platform_tag = config.platforms or 'any' if is_pure else get_platform_tag()
        python = get_python_bin(config)
        if not is_pure:
            abi = get_abi(python)
        else:
            abi = config.pure_python_abi or get_abi(python)
        target_fp = wheel_directory / '{}-{}-{}-{}.whl'.format(
            normalize(config['name']).replace('-', '_'),
            config['version'],
            abi,
            platform_tag,
        )

        self.wheel_zip: WheelFile = WheelFile(str(target_fp), 'w')
        for f in os.listdir(str(wheel_directory / self.metadata_dir)):
            self.wheel_zip.write(
                str(wheel_directory / self.metadata_dir / f),
                arcname=str(Path(self.metadata_dir) / f),
            )
        shutil.rmtree(Path(wheel_directory) / self.metadata_dir)

        # Make sure everything is built
        meson('install', '-C', self.builddir.name)
        self.pack_files(config)
        self.wheel_zip.close()
        optimize, *_ = [
            i.get('value', -1)
            for i in config.options
            if i.get('name', '') == 'python.bytecompile'
        ]
        convert_wheel(Path(target_fp), optimize=optimize, **config.pyc_wheel)
        if config.sign_wheel_files:
            sign_record_file(Path(target_fp))
        return target_fp.name

    def pack_files(self, config):
        for _, installpath in config.installed.items():
            if "site-packages" in installpath:
                installpath = install_files_path(installpath, 'site-packages')
                self.wheel_zip.write_files(installpath)
                break
            elif "dist-packages" in installpath:
                installpath = install_files_path(installpath, 'dist-packages')
                self.wheel_zip.write_files(installpath)
                break


def adjust_name(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.name = normalize(info.name).replace('-', '_')
    return info


def maybe_add_key_to_project(config, pyproject, key):
    text = pyproject.read_text()
    maybe_comment = re.search(r'\[project\](.*)\n', text)
    maybe_comment = maybe_comment.group(1) if maybe_comment else ""
    maybe_key = re.search(r'\[project\](?:(?:.*)\n)*(\s*{}\s*=.*)'.format(key), text)
    if maybe_key:
        pyproject.write_text(
            text.replace('[project]\n', '[project]{}\n'.format(maybe_comment)).replace(
                maybe_key.group(1), '{} = "{}"'.format(key, config[key])
            )
        )
    else:
        pyproject.write_text(
            text.replace(
                '[project]\n',
                '[project]{}\n{} = "{}"\n'.format(
                    maybe_comment,
                    key,
                    config[key],
                ),
            )
        )


def create_dist_info(metadata_directory, config_settings=None, builddir=None, config=None):
    """Creates {metadata_directory}/foo-1.2.dist-info"""
    if not builddir:
        builddir = tempfile.TemporaryDirectory().name
        meson_configure(builddir)
    if not config:
        config = Config(builddir)

    dist_info = Path(
        metadata_directory,
        '{}-{}.dist-info'.format(
            normalize(config['name']).replace('-', '_'), config['version']
        ),
    )
    dist_info.mkdir(exist_ok=True)

    with (dist_info / 'WHEEL').open('w') as f:
        f.write(get_wheel_file(check_is_pure(config.installed)))

    with (dist_info / 'METADATA').open('w') as f:
        f.write(config.get_metadata())

    for i in config.get('license-files'):
        with (dist_info / i).open('w') as fw:
            with Path(i).open('r') as fr:
                fw.write(fr.read())

    if config.get('entry-points') or config.get('scripts') or config.get('gui-scripts'):
        res = ''
        console_scripts = {'console_scripts': config.get('scripts', {})}
        gui_scripts = {'gui_scripts': config.get('gui-scripts', {})}
        entry_points = config.get('entry-points', {})
        entry_points.update(console_scripts)
        entry_points.update(gui_scripts)
        for group_name in sorted(entry_points):
            group = entry_points[group_name]
            if len(group) != 0:
                res += '[{}]\n'.format(group_name)
                for entrypoint, module in group.items():
                    res += '{} = {}\n'.format(entrypoint, module)
                res += '\n'
        with (dist_info / 'entry_points.txt').open('w') as f:
            f.write(res)

    return dist_info.name
