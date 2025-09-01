
.. image:: https://readthedocs.org/projects/pywf-internal-proprietary/badge/?version=latest
    :target: https://pywf-internal-proprietary.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pywf_internal_proprietary-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/pywf_internal_proprietary-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/pywf_internal_proprietary-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/pywf_internal_proprietary-project

.. image:: https://img.shields.io/pypi/v/pywf-internal-proprietary.svg
    :target: https://pypi.python.org/pypi/pywf-internal-proprietary

.. image:: https://img.shields.io/pypi/l/pywf-internal-proprietary.svg
    :target: https://pypi.python.org/pypi/pywf-internal-proprietary

.. image:: https://img.shields.io/pypi/pyversions/pywf-internal-proprietary.svg
    :target: https://pypi.python.org/pypi/pywf-internal-proprietary

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pywf_internal_proprietary-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pywf_internal_proprietary-project

------

.. image:: https://img.shields.io/badge/Link-Document-blue.svg
    :target: https://pywf-internal-proprietary.readthedocs.io/en/latest/

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://pywf-internal-proprietary.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/pywf_internal_proprietary-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/pywf_internal_proprietary-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/pywf_internal_proprietary-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/pywf-internal-proprietary#files


Welcome to ``pywf_internal_proprietary`` Documentation
==============================================================================
.. image:: https://pywf-internal-proprietary.readthedocs.io/en/latest/_static/pywf_internal_proprietary-logo.png
    :target: https://pywf-internal-proprietary.readthedocs.io/en/latest/

``pywf_internal_proprietary`` streamlines internal proprietary Python project development by providing a unified workflow automation framework. It eliminates the cognitive overhead of switching between projects by normalizing common development tasks through a consistent interface.

The library automates common operations for projects using:

- A public `GitHub repo <https://github.com/>`_ to host your project.
- Use `poetry <https://python-poetry.org/>`_ to manage your project dependencies and build distribution package.
- Use `pytest <https://docs.pytest.org/>`_ unit test framework for testing.
- Use `GitHub Actions <https://github.com/features/actions>`_ to run your test.
- Use `Codecov.io <https://about.codecov.io/>`_ to publish your test coverage result.
- Use `sphinx-doc <https://www.sphinx-doc.org/>`_ to build your documentation website.
- A private `CloudFlare Pages <https://developers.cloudflare.com/pages/>`_ project that requires email login to host your documentation website.
- A private `AWS S3 Bucket <https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html>`_ to store your historical versioned document site as a record.
- Use `twine <https://twine.readthedocs.io/>`_ to publish your package to AWS CodeArtifact.
- Use `AWS CodeArtifact <https://docs.aws.amazon.com/codeartifact/latest/ug/using-python.html>`_ to publish your package.
- Use `GitHub Release <https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases>`_ to track your historical assets.

It assumes the following code folder structure::

    .github/workflows/main.yml # GitHub Actions CI/CD configuration file
    ${package_name}/
    ${package_name}/__init__.py
    ${package_name}/*.py
    docs/
    docs/source # documentation source folder
    docs/source/conf.py # sphinx doc configuration file
    tests/ # unit test folder
    bin/ # development workflow automation scripts
    bin/pywf.py
    bin/g01_....py
    bin/g02_....py
    bin/...
    Makefile # makefile for automation
    .coveragerc # code coverage test configuration file
    codecov.yml # code coverage CI rules configuration file
    pyproject.toml # Python project configuration file, no setup.py


Project Maintainer Note
------------------------------------------------------------------------------
This project follows the best practice mentioned in `THIS DOCUMENT <https://dev-exp-share.readthedocs.io/en/latest/search.html?q=Creating+Reusable+Project+Templates%3A+From+Concept+to+Implementation&check_keywords=yes&area=default>`_.

- **Seed Repository** (Private Git Repo to simulate internal proprietary project): `cookiecutter_pywf_internal_proprietary_demo-project <https://github.com/MacHu-GWU/cookiecutter_pywf_internal_proprietary_demo-project>`_
- **Automation Library**: `pywf_internal_proprietary-project <https://github.com/MacHu-GWU/pywf_internal_proprietary-project>`_
- **Cookiecutter Template**: `cookiecutter-pywf_internal_proprietary <https://github.com/MacHu-GWU/cookiecutter-pywf_internal_proprietary>`_


.. _install:

Install
------------------------------------------------------------------------------

``pywf_internal_proprietary`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install pywf-internal-proprietary

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pywf-internal-proprietary
