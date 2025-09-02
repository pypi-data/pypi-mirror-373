========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |github-actions| |coveralls| |codecov| |scrutinizer| |codacy|
    * - package
      - |version| |wheel| |supported-versions| |supported-implementations| |commits-since|

.. |github-actions| image:: https://github.com/ionelmc/python-csu/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/ionelmc/python-csu/actions

.. |coveralls| image:: https://coveralls.io/repos/github/ionelmc/python-csu/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://coveralls.io/github/ionelmc/python-csu?branch=main

.. |codecov| image:: https://codecov.io/gh/ionelmc/python-csu/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/ionelmc/python-csu

.. |codacy| image:: https://img.shields.io/codacy/grade/[Get ID from https://app.codacy.com/gh/ionelmc/python-csu/settings].svg
    :target: https://www.codacy.com/app/ionelmc/python-csu
    :alt: Codacy Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/csu.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/csu

.. |wheel| image:: https://img.shields.io/pypi/wheel/csu.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/csu

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/csu.svg
    :alt: Supported versions
    :target: https://pypi.org/project/csu

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/csu.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/csu

.. |commits-since| image:: https://img.shields.io/github/commits-since/ionelmc/python-csu/v1.17.0.svg
    :alt: Commits since latest release
    :target: https://github.com/ionelmc/python-csu/compare/v1.17.0...main

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/quality/g/ionelmc/python-csu/main.svg
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/ionelmc/python-csu/


.. end-badges

Clean Slate Utils - bunch of utility code, mostly Django/DRF specific.

* Free software: BSD 2-Clause License

Installation
============

::

    pip install csu

You can also install the in-development version with::

    pip install https://github.com/ionelmc/python-csu/archive/main.zip


Documentation
=============

None.

Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
