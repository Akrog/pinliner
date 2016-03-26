===========================
pinliner - Python Inliner
===========================

.. image:: https://img.shields.io/:license-apache-blue.svg
         :target: http://www.apache.org/licenses/LICENSE-2.0

.. image:: https://img.shields.io/pypi/v/pinliner.svg
        :target: https://pypi.python.org/pypi/pinliner


This tool allows you to merge all files that comprise a Python package into
a single file and be able to use this single file as if it were a package.

Imports will work as usual so if you have a package structure like:

::

    .
    └── [my_package]
         ├── file_a.py
         ├── [sub_package]
         │    ├── file_b.py
         │    └── __init__.py
         ├── __init__.py

And you execute:

.. code:: bash

    $ mkdir test
    $ ./pinliner.py my_package test/my_package.py
    $ cd test
    $ python

You'll be able to use generated `my_package.py` file as if it were the real
package:

.. code:: python

    >>> import my_package
    >>> from my_package import file_a as a_file
    >>> from my_package.sub_package import file_b

And `__init__.py` contents will be executed as expected when importing
`my_package` package and you'll be able to access its contents like you would
with your normal package.

Modules will also behave as usual.
