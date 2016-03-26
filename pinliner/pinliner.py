#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import os
from pinliner import __version__
import sys


TEMPLATE_FILE = 'importer.template'
TEMPLATE_PATTERN = '${CONTENTS}'


def output(cfg, what, newline=True):
    # We need indentation for PEP8
    cfg.outfile.write('    ' * cfg.depth)
    cfg.outfile.write(what)
    if newline:
        cfg.outfile.write('\n')


def nested(f):
    def wrapper(cfg, *args, **kwargs):
        cfg.depth += 1
        result = f(cfg, *args, **kwargs)
        cfg.depth -= 1
        return result
    return wrapper


@nested
def process_file(cfg, path):
    # Get the filename from the path and remove the extension (.py)
    filename = os.path.split(path)[1]
    module_name = os.path.splitext(filename)[0]
    with open(path, 'r') as f:
        # Read the whole file
        code = f.read()

        # Insert escape character before ''' since we'll be using ''' to insert
        # the code as a string
        code = code.replace("'''", "\'''")
        # Output the file as a dictionary entry
        output(cfg, "'%s': '''\n%s\n'''," % (module_name, code))


def template(cfg):
    template_path = os.path.join(os.path.dirname(__file__), TEMPLATE_FILE)
    with open(template_path) as f:
        template = f.read()
    prefix_end = template.index(TEMPLATE_PATTERN)
    cfg.outfile.write(template[:prefix_end])
    postfix_begin = prefix_end + len(TEMPLATE_PATTERN)
    return template[postfix_begin:]


@nested
def process_directory(cfg, dirname):
    package_name = os.path.split(dirname)[1]
    output(cfg, "'%s': {" % package_name)
    contents = os.listdir(dirname)
    for content in contents:
        path = os.path.join(dirname, content)
        if is_module(path):
            process_file(cfg, path)
        elif is_package(path):
            process_directory(cfg, path)
    output(cfg, "},")


def process_files(cfg):
    cfg.depth = 0
    # template would look better as a context manager
    postfix = template(cfg)
    for package_path in cfg.packages:
        process_directory(cfg, package_path)
    # No newline on last line, as we want output file to be PEP8 compliant.
    output(cfg, postfix, newline=False)
    cfg.outfile.close()


def parse_args():
    class MyParser(argparse.ArgumentParser):
        """Class to print verbose help on error."""
        def error(self, message):
            self.print_help()
            sys.stderr.write('\nERROR: %s\n' % message)
            sys.exit(2)

    general_description = """Pinliner - Python Inliner (Version %s)

    This tool allows you to merge all files that comprise a Python package into
a single file and be able to use this single file as if it were a package.

    Imports will work as usual so if you have a package structure like:
        .
        └── [my_package]
             ├── file_a.py
             ├── [sub_package]
             │    ├── file_b.py
             │    └── __init__.py
             ├── __init__.py

    And you execute:
        $ mkdir test
        $ ./pinliner.py my_package test/my_package.py
        $ cd test
        $ python

    You'll be able to use this file as if it were the real package:
        >>> import my_package
        >>> from my_package import file_a as a_file
        >>> from my_package.sub_package import file_b

    And __init__.py contents will be executed as expected when importing
my_package and you'll be able to access its contents like you would with your
normal package.  Modules will also behave as usual.
""" % __version__
    general_epilog = None

    parser = MyParser(description=general_description, version=__version__,
                      epilog=general_epilog, argument_default='',
                      formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('package', help='Package to inline.')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help='Output file.')
    return parser.parse_args()


def is_module(module):
    # This validation is poor, but good enough for now
    return os.path.isfile(module) and module.endswith('.py')


def is_package(package):
    init_file = os.path.join(package, '__init__.py')
    return os.path.isdir(package) and os.path.isfile(init_file)


def validate_args(cfg):
    missing = False
    # This is weird now, but in the future we'll allow to inline multiple
    # packages
    cfg.packages = [cfg.package]
    for package in cfg.packages:
        if not is_package(package):
            sys.stderr.write('ERROR: %s is not a python package' % package)
            missing = True
    if missing:
        sys.exit(1)


def main():
    cfg = parse_args()
    validate_args(cfg)
    process_files(cfg)


if __name__ == '__main__':
    main()
