{project_name} documentation
################################

welcome to the documentation of the {project_name} project.


.. include:: features_and_examples.rst


code maintenance guidelines
***************************


portions code requirements
==========================

    * pure python
    * fully typed (:pep:`526`)
    * fully :ref:`documented <{namespace_name}-portions>`
    * 100 % test coverage
    * multi thread save
    * code checks (using pylint and flake8)


design pattern and software principles
======================================

    * `DRY <http://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_
    * `KISS <http://en.wikipedia.org/wiki/Keep_it_simple_stupid>`_


.. include:: ../CONTRIBUTING.rst


main module
***********

.. autosummary::
    :toctree: _autosummary
    :nosignatures:

    {import_name}



indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* `portion repositories at {repo_domain} <{repo_root}>`_
