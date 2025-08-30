# ozi_spec/meson.build
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
foreach file : ['github_ci.py', 'github_ci.pyi']
    configure_file(
        input: file,
        output: file,
        configuration: configuration_data({
            'github_checkpoint_version': run_command(python, ['get_github_checkpoint_version.py'], check: true).stdout().strip(),
            'github_draft_version': run_command(python, ['get_github_draft_version.py'], check: true).stdout().strip(),
            'github_publish_version': run_command(python, ['get_github_publish_version.py'], check: true).stdout().strip(),
            'github_provenance_version': run_command(python, ['get_github_provenance_version.py'], check: true).stdout().strip(),
            'github_release_version': run_command(python, ['get_github_release_version.py'], check: true).stdout().strip(),
            'github_slsa_version': run_command(python, ['get_github_slsa_version.py'], check: true).stdout().strip(),
            'github_harden_runner_version': run_command(python, ['get_github_harden_runner_version.py'], check: true).stdout().strip(),
            'github_action_pypi_publish_version': run_command(python, ['get_github_action_pypi_publish_version.py'], check: true).stdout().strip(),
            'github_checkpoint_endpoints': run_command(python, ['get_github_checkpoint_endpoints.py'], check: true).stdout().strip(),
            'github_draft_endpoints': run_command(python, ['get_github_draft_endpoints.py'], check: true).stdout().strip(),
            'github_release_endpoints': run_command(python, ['get_github_release_endpoints.py'], check: true).stdout().strip(),
            'github_publish_endpoints': run_command(python, ['get_github_publish_endpoints.py'], check: true).stdout().strip(),
            'github_provenance_endpoints': run_command(python, ['get_github_provenance_endpoints.py'], check: true).stdout().strip(),
        }),
        install: true,
        install_dir: python.get_install_dir() / 'ozi_spec',
        install_tag: 'python-runtime',
    )
endforeach
foreach file : ['ci.py', 'ci.pyi']
    configure_file(
        input: file,
        output: file,
        configuration: configuration_data({
            'pyproject_ozi_build_version': run_command(python, ['get_pyproject_ozi_build_version.py'], check: true).stdout().strip(),
            'pyproject_meson_version': run_command(python, ['get_pyproject_meson_version.py'], check: true).stdout().strip(),
        }),
        install: true,
        install_dir: python.get_install_dir() / 'ozi_spec',
        install_tag: 'python-runtime',
    )
endforeach
source_files = [
    '__init__.py',
    '__init__.pyi',
    '_license.py',
    '_license.pyi',
    '_spec.py',
    '_spec.pyi',
    'base.py',
    'base.pyi',
    'pkg.py',
    'pkg.pyi',
    'project.py',
    'project.pyi',
    'python.py',
    'python.pyi',
    'src.py',
    'src.pyi',
    'py.typed',
]
foreach file: source_files
    if not meson.is_subproject() or get_option('install-subprojects').enabled()
        python.install_sources(file, subdir: 'ozi_spec')
    endif
    fs.copyfile(file)
endforeach
if false
    executable('source_files', source_files)
endif
