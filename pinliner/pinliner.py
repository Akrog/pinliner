#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

import argparse
import json
import os
from pinliner import __version__
import sys


TEMPLATE_FILE = 'importer.template'
TEMPLATE_PATTERN = '${CONTENTS}'


def output(cfg, what, newline=True):
    # We need indentation for PEP8
    cfg.outfile.write(what)
    if newline:
        cfg.outfile.write(os.linesep)


def process_file(cfg, base_dir, package_path):
    if cfg.tagging:
        output(cfg, '<tag:' + package_path + '>')
    path = os.path.splitext(package_path)[0].replace(os.path.sep, '.')
    package_start = cfg.outfile.tell()
    full_path = os.path.join(base_dir, package_path)
    with open(full_path, 'r') as f:
        # Read the whole file
        code = f.read()

        # Insert escape character before ''' since we'll be using ''' to insert
        # the code as a string
        output(cfg, code.replace("'''", r"\'''"), newline=cfg.tagging)
    package_end = cfg.outfile.tell()
    is_package = 1 if path.endswith('__init__') else 0
    if is_package:
        path = path[:-9]

    # Get file timestamp
    timestamp = long(os.path.getmtime(full_path))
    return path, is_package, package_start, package_end, timestamp


def template(cfg):
    template_path = os.path.join(os.path.dirname(__file__), TEMPLATE_FILE)
    with open(template_path) as f:
        template = f.read()
    prefix_end = template.index(TEMPLATE_PATTERN)
    prefix_data = template[:prefix_end].replace('%{FORCE_EXC_HOOK}',
                                                str(cfg.set_hook))
    prefix_data = prefix_data.replace('%{DEFAULT_PACKAGE}', cfg.default_module)
    cfg.outfile.write(prefix_data)
    postfix_begin = prefix_end + len(TEMPLATE_PATTERN)
    return template[postfix_begin:]


def process_directory(cfg, base_dir, package_path):
    files = []
    contents = os.listdir(os.path.join(base_dir, package_path))
    for content in contents:
        next_path = os.path.join(package_path, content)
        path = os.path.join(base_dir, next_path)
        if is_module(path):
            files.append(process_file(cfg, base_dir, next_path))
        elif is_package(path):
            files.extend(process_directory(cfg, base_dir, next_path))
    return files


def process_files(cfg):
    cfg.default_module = os.path.split(cfg.packages[0])[1]
    # template would look better as a context manager
    postfix = template(cfg)
    files = []
    output(cfg, "'''")
    for package_path in cfg.packages:
        base_dir, module_name = os.path.split(package_path)
        files.extend(process_directory(cfg, base_dir, module_name))
    output(cfg, "'''")

    # Transform the list into a dictionary
    inliner_packages = {data[0]: data[1:] for data in files}

    # Generate the references to the positions of the different packages and
    # modules inside the main file.
    # We don't use indent to decrease the number of bytes in the file
    data = json.dumps(inliner_packages)
    output(cfg, 2 * os.linesep + 'inliner_packages = ', newline=False)
    data = data.replace('],', '],' + os.linesep + '   ')
    data = data.replace('[', '[' + os.linesep + 8 * ' ')
    data = '%s%s    %s%s%s' % (data[0], os.linesep, data[1:-1], os.linesep,
                               data[-1])

    output(cfg, data)
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
        $ pinliner my_package test/my_package.py
        $ cd test
        $ python

    You'll be able to use this file as if it were the real package:
        >>> import my_package
        >>> from my_package import file_a as a_file
        >>> from my_package.sub_package import file_b

    And __init__.py contents will be executed as expected when importing
my_package and you'll be able to access its contents like you would with your
normal package.  Modules will also behave as usual.

    By default there is no visible separation between the different modules'
source code, but one can be enabled for clarity with option --tag, which will
include a newline and a <tag:file_path> tag before each of the source files.
""" % __version__
    general_epilog = None

    parser = MyParser(description=general_description, version=__version__,
                      epilog=general_epilog, argument_default='',
                      formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('package', help='Package to inline.')
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout, help='Output file.')
    parser.add_argument('--set-except', default=None, dest='set_hook',
                        action='store_true',
                        help='Force setting handler for uncaught exceptions.')
    parser.add_argument('--no-except', default=None, dest='set_hook',
                        action='store_false',
                        help="Don't set handler for uncaught exceptions.")
    parser.add_argument('--tag', default=False, dest='tagging',
                        action='store_true',
                        help="Mark with <tag:file_path> each added file.")
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
