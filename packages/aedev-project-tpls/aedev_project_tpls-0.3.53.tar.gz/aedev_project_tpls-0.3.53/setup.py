# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.52
""" setup of aedev namespace package portion project_tpls: outsourced Python project files templates. """
# noinspection PyUnresolvedReferences
import sys
print(f"SetUp {__name__=} {sys.executable=} {sys.argv=} {sys.path=}")

# noinspection PyUnresolvedReferences
import setuptools

setup_kwargs = {
    'author': 'AndiEcker',
    'author_email': 'aecker2@gmail.com',
    'classifiers': [       'Development Status :: 3 - Alpha', 'Natural Language :: English', 'Operating System :: OS Independent',
        'Programming Language :: Python', 'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9', 'Topic :: Software Development :: Libraries :: Python Modules',
        'Typing :: Typed'],
    'description': 'aedev namespace package portion project_tpls: outsourced Python project files templates',
    'extras_require': {       'dev': [       'aedev_project_tpls', 'aedev_aedev', 'anybadge', 'coverage-badge', 'aedev_git_repo_manager',
                       'flake8', 'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing',
                       'types-setuptools'],
        'docs': [],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools']},
    'install_requires': [],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.aedev v0.3.26 -->\n'
 '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.namespace_root_tpls v0.3.18 -->\n'
 '# project_tpls 0.3.53\n'
 '\n'
 '[![GitLab develop](https://img.shields.io/gitlab/pipeline/aedev-group/aedev_project_tpls/develop?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_project_tpls)\n'
 '[![LatestPyPIrelease](\n'
 '    https://img.shields.io/gitlab/pipeline/aedev-group/aedev_project_tpls/release0.3.53?logo=python)](\n'
 '    https://gitlab.com/aedev-group/aedev_project_tpls/-/tree/release0.3.53)\n'
 '[![PyPIVersions](https://img.shields.io/pypi/v/aedev_project_tpls)](\n'
 '    https://pypi.org/project/aedev-project-tpls/#history)\n'
 '\n'
 '>aedev namespace package portion project_tpls: outsourced Python project files templates.\n'
 '\n'
 '[![Coverage](https://aedev-group.gitlab.io/aedev_project_tpls/coverage.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_project_tpls/coverage/index.html)\n'
 '[![MyPyPrecision](https://aedev-group.gitlab.io/aedev_project_tpls/mypy.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_project_tpls/lineprecision.txt)\n'
 '[![PyLintScore](https://aedev-group.gitlab.io/aedev_project_tpls/pylint.svg)](\n'
 '    https://aedev-group.gitlab.io/aedev_project_tpls/pylint.log)\n'
 '\n'
 '[![PyPIImplementation](https://img.shields.io/pypi/implementation/aedev_project_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_project_tpls/)\n'
 '[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/aedev_project_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_project_tpls/)\n'
 '[![PyPIWheel](https://img.shields.io/pypi/wheel/aedev_project_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_project_tpls/)\n'
 '[![PyPIFormat](https://img.shields.io/pypi/format/aedev_project_tpls)](\n'
 '    https://pypi.org/project/aedev-project-tpls/)\n'
 '[![PyPILicense](https://img.shields.io/pypi/l/aedev_project_tpls)](\n'
 '    https://gitlab.com/aedev-group/aedev_project_tpls/-/blob/develop/LICENSE.md)\n'
 '[![PyPIStatus](https://img.shields.io/pypi/status/aedev_project_tpls)](\n'
 '    https://libraries.io/pypi/aedev-project-tpls)\n'
 '[![PyPIDownloads](https://img.shields.io/pypi/dm/aedev_project_tpls)](\n'
 '    https://pypi.org/project/aedev-project-tpls/#files)\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 '\n'
 'execute the following command to install the\n'
 'aedev.project_tpls package\n'
 'in the currently active virtual environment:\n'
 ' \n'
 '```shell script\n'
 'pip install aedev-project-tpls\n'
 '```\n'
 '\n'
 'if you want to contribute to this portion then first fork\n'
 '[the aedev_project_tpls repository at GitLab](\n'
 'https://gitlab.com/aedev-group/aedev_project_tpls "aedev.project_tpls code repository").\n'
 'after that pull it to your machine and finally execute the\n'
 'following command in the root folder of this repository\n'
 '(aedev_project_tpls):\n'
 '\n'
 '```shell script\n'
 'pip install -e .[dev]\n'
 '```\n'
 '\n'
 'the last command will install this package portion, along with the tools you need\n'
 'to develop and run tests or to extend the portion documentation. to contribute only to the unit tests or to the\n'
 'documentation of this portion, replace the setup extras key `dev` in the above command with `tests` or `docs`\n'
 'respectively.\n'
 '\n'
 'more detailed explanations on how to contribute to this project\n'
 '[are available here](\n'
 'https://gitlab.com/aedev-group/aedev_project_tpls/-/blob/develop/CONTRIBUTING.rst)\n'
 '\n'
 '\n'
 '## namespace portion documentation\n'
 '\n'
 'information on the features and usage of this portion are available at\n'
 '[ReadTheDocs](\n'
 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.project_tpls.html\n'
 '"aedev_project_tpls documentation").\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'aedev_project_tpls',
    'package_data': {       '': [       'templates/de_tpl_README.md', 'templates/de_sfp_de_otf_de_tpl_.readthedocs.yaml',
                    'templates/de_otf_pyproject.toml', 'templates/de_otf_de_tpl_dev_requirements.txt',
                    'templates/de_otf_de_tpl_.gitlab-ci.yml', 'templates/de_otf_de_tpl_.gitignore',
                    'templates/de_spt_app_de_otf_de_tpl_setup.py', 'templates/de_otf_SECURITY.md',
                    'templates/de_otf_LICENSE.md', 'templates/de_otf_de_tpl_CONTRIBUTING.rst',
                    'templates/tests/de_otf_de_tpl_test_{portion_name or project_name}.py',
                    'templates/tests/de_otf_de_tpl_requirements.txt', 'templates/tests/de_otf_conftest.py',
                    'templates/de_sfp_docs/de_otf_Makefile', 'templates/de_sfp_docs/de_otf_de_tpl_requirements.txt',
                    'templates/de_sfp_docs/de_otf_de_tpl_index.rst', 'templates/de_sfp_docs/features_and_examples.rst',
                    'templates/de_sfp_docs/de_otf_de_tpl_conf.py']},
    'packages': [       'aedev.project_tpls', 'aedev.project_tpls.templates', 'aedev.project_tpls.templates.tests',
        'aedev.project_tpls.templates.de_sfp_docs'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/aedev-group/aedev_project_tpls/-/issues',
        'Documentation': 'https://aedev.readthedocs.io/en/latest/_autosummary/aedev.project_tpls.html',
        'Repository': 'https://gitlab.com/aedev-group/aedev_project_tpls',
        'Source': 'https://aedev.readthedocs.io/en/latest/_modules/aedev/project_tpls.html'},
    'python_requires': '>=3.9',
    'url': 'https://gitlab.com/aedev-group/aedev_project_tpls',
    'version': '0.3.53',
    'zip_safe': False,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
