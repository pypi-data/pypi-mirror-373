# THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.project_tpls v0.3.53
""" setup of ae namespace module portion base: basic constants, helper functions and context managers. """
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
    'description': 'ae namespace module portion base: basic constants, helper functions and context managers',
    'extras_require': {       'dev': [       'aedev_project_tpls', 'ae_ae', 'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8',
                       'mypy', 'pylint', 'pytest', 'pytest-cov', 'pytest-django', 'typing', 'types-setuptools'],
        'docs': [],
        'tests': [       'anybadge', 'coverage-badge', 'aedev_git_repo_manager', 'flake8', 'mypy', 'pylint', 'pytest',
                         'pytest-cov', 'pytest-django', 'typing', 'types-setuptools']},
    'install_requires': [],
    'keywords': ['configuration', 'development', 'environment', 'productivity'],
    'license': 'GPL-3.0-or-later',
    'long_description': ('<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project ae.ae v0.3.96 -->\n'
 '<!-- THIS FILE IS EXCLUSIVELY MAINTAINED by the project aedev.tpl_namespace_root V0.3.14 -->\n'
 '# base 0.3.67\n'
 '\n'
 '[![GitLab develop](https://img.shields.io/gitlab/pipeline/ae-group/ae_base/develop?logo=python)](\n'
 '    https://gitlab.com/ae-group/ae_base)\n'
 '[![LatestPyPIrelease](\n'
 '    https://img.shields.io/gitlab/pipeline/ae-group/ae_base/release0.3.66?logo=python)](\n'
 '    https://gitlab.com/ae-group/ae_base/-/tree/release0.3.66)\n'
 '[![PyPIVersions](https://img.shields.io/pypi/v/ae_base)](\n'
 '    https://pypi.org/project/ae-base/#history)\n'
 '\n'
 '>ae namespace module portion base: basic constants, helper functions and context managers.\n'
 '\n'
 '[![Coverage](https://ae-group.gitlab.io/ae_base/coverage.svg)](\n'
 '    https://ae-group.gitlab.io/ae_base/coverage/index.html)\n'
 '[![MyPyPrecision](https://ae-group.gitlab.io/ae_base/mypy.svg)](\n'
 '    https://ae-group.gitlab.io/ae_base/lineprecision.txt)\n'
 '[![PyLintScore](https://ae-group.gitlab.io/ae_base/pylint.svg)](\n'
 '    https://ae-group.gitlab.io/ae_base/pylint.log)\n'
 '\n'
 '[![PyPIImplementation](https://img.shields.io/pypi/implementation/ae_base)](\n'
 '    https://gitlab.com/ae-group/ae_base/)\n'
 '[![PyPIPyVersions](https://img.shields.io/pypi/pyversions/ae_base)](\n'
 '    https://gitlab.com/ae-group/ae_base/)\n'
 '[![PyPIWheel](https://img.shields.io/pypi/wheel/ae_base)](\n'
 '    https://gitlab.com/ae-group/ae_base/)\n'
 '[![PyPIFormat](https://img.shields.io/pypi/format/ae_base)](\n'
 '    https://pypi.org/project/ae-base/)\n'
 '[![PyPILicense](https://img.shields.io/pypi/l/ae_base)](\n'
 '    https://gitlab.com/ae-group/ae_base/-/blob/develop/LICENSE.md)\n'
 '[![PyPIStatus](https://img.shields.io/pypi/status/ae_base)](\n'
 '    https://libraries.io/pypi/ae-base)\n'
 '[![PyPIDownloads](https://img.shields.io/pypi/dm/ae_base)](\n'
 '    https://pypi.org/project/ae-base/#files)\n'
 '\n'
 '\n'
 '## installation\n'
 '\n'
 '\n'
 'execute the following command to install the\n'
 'ae.base module\n'
 'in the currently active virtual environment:\n'
 ' \n'
 '```shell script\n'
 'pip install ae-base\n'
 '```\n'
 '\n'
 'if you want to contribute to this portion then first fork\n'
 '[the ae_base repository at GitLab](\n'
 'https://gitlab.com/ae-group/ae_base "ae.base code repository").\n'
 'after that pull it to your machine and finally execute the\n'
 'following command in the root folder of this repository\n'
 '(ae_base):\n'
 '\n'
 '```shell script\n'
 'pip install -e .[dev]\n'
 '```\n'
 '\n'
 'the last command will install this module portion, along with the tools you need\n'
 'to develop and run tests or to extend the portion documentation. to contribute only to the unit tests or to the\n'
 'documentation of this portion, replace the setup extras key `dev` in the above command with `tests` or `docs`\n'
 'respectively.\n'
 '\n'
 'more detailed explanations on how to contribute to this project\n'
 '[are available here](\n'
 'https://gitlab.com/ae-group/ae_base/-/blob/develop/CONTRIBUTING.rst)\n'
 '\n'
 '\n'
 '## namespace portion documentation\n'
 '\n'
 'information on the features and usage of this portion are available at\n'
 '[ReadTheDocs](\n'
 'https://ae.readthedocs.io/en/latest/_autosummary/ae.base.html\n'
 '"ae_base documentation").\n'),
    'long_description_content_type': 'text/markdown',
    'name': 'ae_base',
    'package_data': {'': []},
    'packages': ['ae'],
    'project_urls': {       'Bug Tracker': 'https://gitlab.com/ae-group/ae_base/-/issues',
        'Documentation': 'https://ae.readthedocs.io/en/latest/_autosummary/ae.base.html',
        'Repository': 'https://gitlab.com/ae-group/ae_base',
        'Source': 'https://ae.readthedocs.io/en/latest/_modules/ae/base.html'},
    'python_requires': '>=3.9',
    'url': 'https://gitlab.com/ae-group/ae_base',
    'version': '0.3.67',
    'zip_safe': True,
}

if __name__ == "__main__":
    setuptools.setup(**setup_kwargs)
    pass
