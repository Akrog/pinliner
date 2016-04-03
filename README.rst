===========================
pinliner - Python Inliner
===========================

.. image:: https://img.shields.io/:license-apache-blue.svg
         :target: http://www.apache.org/licenses/LICENSE-2.0

.. image:: https://img.shields.io/pypi/v/pinliner.svg
        :target: https://pypi.python.org/pypi/pinliner


This tool allows you to merge all files that comprise a Python package into
a single file and be able to use this single file as if it were a package.

Not only will it behave as if it were the original package, but it will also
show code in exceptions and debug sessions, and will display the right line
number and file when logging.

Imports will work as usual so if you have a package structure like:

::

    .
    └── [my_package]
         ├── file_a.py
         ├── [sub_package]
         │    ├── file_b.py
         │    └── __init__.py
         ├── __init__.py

And with pinliner installed you execute:

.. code:: bash

    $ mkdir test
    $ pinliner my_package test/my_package.py
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

If your package is checking `__name__` for `__main__` it will also work as
usual.  Although given the fact that we only have 1 file we will no longer be
able to call other packages/modules directly from the command line to trigger
code conditioned to `__name__` having `__main__` as its value.

Loader code will automatically compile packages and modules to byte code,
before running it.  When a module is imported for the first time, or when the
specific's package/module source (not the whole inlined file) is more recent
than the current compiled file, a .pyc file containing the compiled code will
be created in the same directory as the pinlined .py file.

If the byte code is up to date then it will be used instead, thus avoiding a
recompilation, exactly the same as python normally does, with the only
exception that all .pyc files will be in the same directory and the filenames
will include the full path to the original file.

Installation
------------

You can install pinliner globally in your system or use a virtual environment,
this is how it could be done using a virtual environment:

.. code:: bash

    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install pinliner

After that you can run the tool with `pinliner`.
