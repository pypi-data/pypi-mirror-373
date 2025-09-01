# Copyright (c) 2009, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Willow Garage, Inc. nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Author Tully Foote/tfoote@willowgarage.com

import os
import subprocess
import sys
import re

from configparser import ConfigParser
from pathlib import Path

try:
    import importlib.metadata as importlib_metadata
except ImportError:
    import importlib_metadata

from packaging.requirements import Requirement
from packaging.version import InvalidVersion, parse
from ..core import InstallFailed
from ..installers import PackageManagerInstaller
from ..shell_utils import read_stdout

# pip package manager key
PIP_INSTALLER = 'pip'

EXTERNALLY_MANAGED_EXPLAINER = """
rosdep installation of pip packages requires installing packages globally as root.
When using Python >= 3.11, PEP 668 compliance requires you to allow pip to install alongside
externally managed packages using the 'break-system-packages' option.
The recommeded way to set this option when using rosdep is to set the environment variable
PIP_BREAK_SYSTEM_PACKAGES=1
in your environment.

For more information refer to http://docs.ros.org/en/independent/api/rosdep/html/pip_and_pep_668.html
"""


def register_installers(context):
    context.set_installer(PIP_INSTALLER, PipInstaller())


def get_pip_command():
    # First try user specified pip cmd
    if 'ROSDEP_PIP_CMD' in os.environ:
        cmd = os.environ['ROSDEP_PIP_CMD'].split()
        if is_cmd_available(cmd + ['--help']):
            return cmd
        return None

    # next try pip2 or pip3
    cmd = ['pip' + os.environ['ROS_PYTHON_VERSION']]
    if is_cmd_available(cmd):
        return cmd

    # Second, try using the same python executable since we know that exists
    if os.environ['ROS_PYTHON_VERSION'] == sys.version[0]:
        try:
            import pip
        except ImportError:
            pass
        else:
            return [sys.executable, '-m', 'pip']

    # Finally, try python2 or python3 commands
    cmd = ['python' + os.environ['ROS_PYTHON_VERSION'], '-m', 'pip']
    if is_cmd_available(cmd):
        return cmd
    return None


def in_virtual_environment():
    return sys.prefix != sys.base_prefix


def externally_managed_installable():
    """
    PEP 668 enacted in Python 3.11 blocks pip from working in "externally
    managed" environments such as operating systems with included package
    managers. If we're on Python 3.11 or greater, we need to check that pip
    is configured to allow installing system-wide packages with the
    flagrantly named "break system packages" config option or environment
    variable.
    """

    # This doesn't affect Python versions before 3.11
    if sys.version_info < (3, 11):
        return True

    # This doesn't affect Python virtual environments
    if in_virtual_environment():
        return True

    if (
            'PIP_BREAK_SYSTEM_PACKAGES' in os.environ and
            os.environ['PIP_BREAK_SYSTEM_PACKAGES'].lower() in ('yes', '1', 'true')
    ):
        return True

    # Check the same configuration directories as pip does per
    # https://pip.pypa.io/en/stable/topics/configuration/
    pip_config = ConfigParser()
    if 'XDG_CONFIG_DIRS' in os.environ:
        for xdg_dir in os.environ['XDG_CONFIG_DIRS'].split(':'):
            pip_config_file = Path(xdg_dir) / 'pip' / 'pip.conf'
            pip_config.read(pip_config_file)
            if pip_config.getboolean('install', 'break-system-packages', fallback=False):
                return True

    fallback_config = Path('/etc/pip.conf')
    pip_config.read(fallback_config)
    if pip_config.getboolean('install', 'break-system-packages', fallback=False):
        return True
    # On Python 3.11 and later, when no explicit configuration is present,
    # global pip installation will not work.
    return False


def is_cmd_available(cmd):
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _ = proc.communicate()
        return 0 == proc.returncode
    except OSError:
        return False


def parse_version(version_str):
    """
    Given a textual representation of a Python package version, return its parsed representation.

    :param version_str: The textual representation of the version.
    :return: The parsed representation of None if the version cannot be parsed.
    :rtype: packaging.version.Version or packaging.version.LegacyVersion or None
    """
    try:
        return parse(version_str)
    except InvalidVersion:
        return None


def pip_detect(pkgs, exec_fn=None):
    """
    Given a list of package specifications, return the list of installed
    packages which meet the specifications.

    :param exec_fn: function to execute Popen and read stdout (for testing)
    """
    pip_cmd = get_pip_command()
    if not pip_cmd:
        return []

    if exec_fn is None:
        exec_fn = read_stdout
    pkg_list = exec_fn(pip_cmd + ['freeze']).split('\n')
    pkg_list = [p for p in pkg_list if len(p) > 0]

    ret_list = []
    version_list = []
    req_list = []

    for pkg in pkg_list:
        pkg_row = pkg.split('==')

        # skip over locally editable packages
        line = pkg_row[0].strip()
        if line.startswith("#") or line.startswith('-e'):
            continue

        # skip over other errors
        if len(pkg_row) != 2:
            print(f"Incomprehensibled package line: {pkg}")
            continue

        # Account for some unusual instances of === instead of ==
        pkg_row[1] = pkg_row[1].strip('=')

        version_list.append((pkg_row[0], parse_version(pkg_row[1])))

    for pkg in pkgs:
        req_list.append(Requirement(pkg))

    def canonicalize_name(name):
        return re.sub(r"[-_.]+", "-", name).lower()

    if (os.environ.get('ROSDEP_DEBUG') or '').lower() in ('yes', '1', 'true'):
        print("REQ:", req_list)
        print("PKG:", pkgs)
        print("VER:", version_list)
        print("PKGLST:", pkg_list)

    for req in req_list:
        for pkg in [ver for ver in version_list if canonicalize_name(ver[0]) == canonicalize_name(req.name)]:
            if pkg[1] is None or pkg[1] in req.specifier:
                ret_list.append(req.name)

    return ret_list


class PipInstaller(PackageManagerInstaller):
    """
    :class:`Installer` support for pip.
    """

    def __init__(self):
        super(PipInstaller, self).__init__(pip_detect, supports_depends=True)

        # Pass necessary environment for pip functionality via sudo
        if self.as_root and self.sudo_command != '':
            self.sudo_command += ' --preserve-env=PIP_BREAK_SYSTEM_PACKAGES'

    def get_version_strings(self):
        pip_version = importlib_metadata.version('pip')
        # keeping the name "setuptools" for backward compatibility
        setuptools_version = importlib_metadata.version('setuptools')
        version_strings = [
            'pip {}'.format(pip_version),
            'setuptools {}'.format(setuptools_version),
        ]
        return version_strings

    def get_packages_to_install(self, resolved, reinstall=False):
        if reinstall:
            return resolved
        if not resolved:
            return []
        else:
            detected = self.detect_fn(resolved)
            return [x for x in resolved if Requirement(x).name not in detected]

    def get_install_command(self, packages, interactive=True, reinstall=False, quiet=False, oneshot=[]):
        pip_cmd = get_pip_command()
        if not pip_cmd:
            raise InstallFailed((PIP_INSTALLER, 'pip is not installed'))
        if not externally_managed_installable():
            raise InstallFailed((PIP_INSTALLER, EXTERNALLY_MANAGED_EXPLAINER))
        if not packages:
            return []
        cmd = pip_cmd + ['install', '-U']
        if quiet:
            cmd.append('-q')
        if reinstall:
            cmd.append('-I')
        if 'pip' in oneshot:
            return [self.elevate_priv(cmd + sorted(packages))]
        return [self.elevate_priv(cmd + [p]) for p in packages]
