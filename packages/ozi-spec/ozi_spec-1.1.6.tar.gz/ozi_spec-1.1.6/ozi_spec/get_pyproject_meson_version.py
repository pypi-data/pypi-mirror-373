# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: MIT-0
"""Get the OZI.build version currently in use."""
import os
import pathlib
import sys
from configparser import ConfigParser

if sys.version_info >= (3, 11):  # pragma: no cover
    import tomllib as toml
elif sys.version_info < (3, 11):  # pragma: no cover
    import tomli as toml

if __name__ == '__main__':
    with open(
        pathlib.Path(os.environ.get('MESON_SOURCE_ROOT', '.')) / 'pyproject.toml',
        'rb',
    ) as fh:
        pyproject = toml.load(fh)
    config = ConfigParser()
    config.read_string(pyproject['tool']['tox']['legacy_tox_ini'])
    print(config['testenv']['commands_pre'].strip().split('\n')[1].split()[-1].strip('"'))
