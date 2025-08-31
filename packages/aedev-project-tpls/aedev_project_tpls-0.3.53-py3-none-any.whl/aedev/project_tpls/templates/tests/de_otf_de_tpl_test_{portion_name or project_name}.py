# pylint: disable=invalid-name
""" default integration and unit tests for new app/namespace-root/aedev-template/... projects.

remove the outsourced marker in the first line of this test module if you want to add more specialized tests. you then
want also to remove ``main_imp_name`` and to replace importlib.import_module (only there to prevent syntax errors in
this template) with an import statement.
"""
import importlib
import os

from ae.base import TESTS_FOLDER, module_attr                               # type: ignore


main_imp_name = "{'main' if os.path.isfile(os.path.join(project_path, 'main' + PY_EXT)) else import_name}"
main_module = importlib.import_module(main_imp_name)


def test_version():
    """ test existence of project package version. """
    # noinspection PyUnresolvedReferences
    pkg_version = main_module.__version__
    assert pkg_version
    assert isinstance(pkg_version, str)
    assert pkg_version.count(".") == 2
    assert pkg_version == module_attr(main_imp_name, '__version__')


def test_docstring():
    """ test existence of project package docstring. """
    pkg_docstring = main_module.__doc__
    assert pkg_docstring
    assert isinstance(pkg_docstring, str)
    assert pkg_docstring == module_attr(main_imp_name, '__doc__')


def test_tests_folder_exists():
    """ test existence of tests folder. """
    assert os.path.isdir(TESTS_FOLDER)
