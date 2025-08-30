# ozi_spec/get_github_publish_version.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Get the workflow version currently in use."""
import os
import pathlib

import yaml

if __name__ == '__main__':
    with open(
        pathlib.Path(os.environ.get('MESON_SOURCE_ROOT', '.')) / '.github/workflows/ozi.yml',
        'r',
    ) as fh:
        workflow = yaml.safe_load(fh)
    print(workflow['jobs']['publish']['steps'][1]['uses'].split('@')[1])
