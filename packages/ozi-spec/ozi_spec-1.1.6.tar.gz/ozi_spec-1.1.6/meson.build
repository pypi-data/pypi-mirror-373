# OZI 0.4 meson.build:root_files,root_children
# Part of OZI.spec.
# See LICENSE.txt in the project root for details.
# DO NOT EDIT BY HAND - This file was generated for use with OZI tools.
# ozi-fix -> meson rewrite is the standard editing pipeline.
project(
    'ozi-spec',
    default_options: ['warning_level=3'],
    license: 'MIT-0',
    license_files: ['LICENSE.txt'],
    meson_version: '>=1.1.0',
    version: run_command(
        'python3',
        [
            '-c',
            'from setuptools_scm import get_version;print(get_version(normalize=False, fallback_version="%OZIBUILDVERSION%"))',
        ],
        check: true,
    ).stdout().strip(),
)
fs = import('fs')
pymod = import('python')
python_dependencies = get_option('python-dependencies')
python = pymod.find_installation()
project_name = meson.project_name()
root_files = [
    'README',
    'CHANGELOG.md',
    'LICENSE.txt',
    'pyproject.toml',
    '.gitignore',
]
pyproject_config = configuration_data()
pyproject_config.set(
    'PYTHON_VERSION_DIST',
    'py'+''.join(python.language_version().split('.'))
)
pyproject_config.set('VCS_TAG', '@VCS_TAG@')
configure_file(
    input: 'pyproject.toml',
    output: 'pyproject.toml',
    configuration: pyproject_config
)
vcs_tag(input: 'pyproject.toml', output: 'pyproject.orig.toml')

foreach source : root_files
    if source not in ['pyproject.toml', 'requirements.in', '.gitignore', 'README']
        fs.copyfile(source)
    elif source == 'README'
        fs.copyfile(source, 'README.rst')
    endif
endforeach
root_children = ['ozi_spec', 'tests']
foreach child: root_children
    subdir(child)
endforeach
if false
    executable('root_files', root_files)
    executable('root_children', root_children)
endif
if not meson.is_subproject()
    dev = subproject('ozi')
    foreach var : get_option('variables')
        name = var.replace('-', '_')
        set_variable(name, dev.get_variable(name))
    endforeach
    deps = run_command(python, '-c', dev.get_variable('install_dependencies'), check: true).stdout().strip().split('$$')
    if deps[0] != ''
        if find_program('uv', disabler: true).found()
            meson.add_postconf_script('uv', 'venv', 'venv')
        else
            meson.add_postconf_script(dev.get_variable('pip'), 'install', 'virtualenv')
            meson.add_postconf_script('virtualenv', 'venv')
        endif
        meson.add_postconf_script(dev.get_variable('pip'), 'install', deps)
    endif
endif
