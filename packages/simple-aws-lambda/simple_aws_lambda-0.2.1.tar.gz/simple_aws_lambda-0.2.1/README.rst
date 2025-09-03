
.. image:: https://readthedocs.org/projects/simple-aws-lambda/badge/?version=latest
    :target: https://simple-aws-lambda.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/simple_aws_lambda-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/simple_aws_lambda-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/simple_aws_lambda-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/simple_aws_lambda-project

.. image:: https://img.shields.io/pypi/v/simple-aws-lambda.svg
    :target: https://pypi.python.org/pypi/simple-aws-lambda

.. image:: https://img.shields.io/pypi/l/simple-aws-lambda.svg
    :target: https://pypi.python.org/pypi/simple-aws-lambda

.. image:: https://img.shields.io/pypi/pyversions/simple-aws-lambda.svg
    :target: https://pypi.python.org/pypi/simple-aws-lambda

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/simple_aws_lambda-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/simple_aws_lambda-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://simple-aws-lambda.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_lambda-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_lambda-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_lambda-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/simple-aws-lambda#files


Welcome to ``simple_aws_lambda`` Documentation
==============================================================================
.. image:: https://simple-aws-lambda.readthedocs.io/en/latest/_static/simple_aws_lambda-logo.png
    :target: https://simple-aws-lambda.readthedocs.io/en/latest/

simple_aws_lambda is a Pythonic library that provides a simplified, high-level interface for AWS Lambda operations. Built on top of boto3, it offers intuitive data models, property-based access patterns, and comprehensive type hints to make working with AWS Lambda resources more developer-friendly and maintainable.

**Key Features:**

**Data Models** - Transform raw boto3 responses into Pythonic objects with property-based access, following the Raw Data Storage, Property-Based Access, and Core Data Extraction patterns to ensure API resilience and clean interfaces.

**Better Client** - Enhance the standard boto3 Lambda client with idempotent operations, automatic pagination, better error handling, and direct return of data model objects instead of raw dictionaries.

**Recipes** - Provide high-level functions for common Lambda layer management tasks such as version cleanup, cross-account access management, and intelligent layer discovery that combine multiple API calls with best practices.


.. _install:

Install
------------------------------------------------------------------------------

``simple_aws_lambda`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install simple-aws-lambda

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade simple-aws-lambda
