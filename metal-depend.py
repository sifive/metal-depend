#!/usr/bin/env python3
# Copyright (c) 2020 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

"""Generate list of freedom-metal drivers from devicetree source files"""

import argparse
import sys
import os

import jinja2
import pydevicetree

from sources import get_sources, find_source

TEMPLATES_PATH = "templates"

def missingvalue(message):
    """
    Raise an UndefinedError
    This function is made available to the template so that it can report
    when required values are not present and cause template rendering to
    fail.
    """
    raise jinja2.UndefinedError(message)


def parse_arguments(argv):
    """Parse the arguments into a dictionary with argparse"""
    arg_parser = argparse.ArgumentParser(
        description="Generate linker scripts from Devicetrees")

    arg_parser.add_argument("-d", "--dts", required=True,
                            help="The path to the Devicetree for the target")
    arg_parser.add_argument("-m", "--metal", required=True,
                            help="The path to the freedom-metal source tree")
    arg_parser.add_argument("-f", "--feature", action="append")
    arg_parser.add_argument("-o", "--output",
                            type=argparse.FileType('w'),
                            help="The path of the source list file to output")
    group = arg_parser.add_mutually_exclusive_group()
    group.add_argument("--make", action="store_true",
                       help="Emits a source list in make format")
    group.add_argument("--meson", action="store_true",
                       help="Emits a source list in meson format")

    return arg_parser.parse_args(argv)


def get_template(parsed_args):
    """Initialize jinja2 and return the right template"""
    env = jinja2.Environment(
        loader=jinja2.PackageLoader(__name__, TEMPLATES_PATH),
        trim_blocks=True, lstrip_blocks=True,
    )
    # Make the missingvalue() function available in the template so that the
    # template fails to render if we don't provide the values it needs.
    env.globals["missingvalue"] = missingvalue

    if parsed_args.make:
        layout = "make"
    elif parsed_args.meson:
        layout = "meson"
    else:
        layout = "make"

    template = env.get_template("%s.mk" % layout)
    print("Generating source list with %s layout" % layout, file=sys.stderr)

    return template


def print_sources(sources):
    """Report sources to stderr"""
    print("Using layout:", file=sys.stderr)
    for _, source in sources.items():
        end = memory["base"] + memory["length"] - 1
        print("\t%4s: (%s)" %
              (memory["name"], memory["dir"]), file=sys.stderr)


metal_dirs = ('src', 'src/drivers')

helpers = (
    ("uart", "uart.c"),
    )
    

def main(argv):
    """Parse arguments, extract data, and render the linker script to file"""
    parsed_args = parse_arguments(argv)

    template = get_template(parsed_args)

    dts = pydevicetree.Devicetree.parseFile(
        parsed_args.dts, followIncludes=True)

    metal = parsed_args.metal

    dirs = [os.path.join(metal, sub) for sub in metal_dirs]

    (target_c, target_s) = get_sources(dts, dirs)

    for t in target_c:
        print(t)

    # Pass sorted sources to the template generator so that the generated
    # file is reproducible.

    target_c.sort()
    target_s.sort()

    values = {
        "target_c": target_c,
        "target_s": target_s,
    }

    if parsed_args.output:
        parsed_args.output.write(template.render(values))
        parsed_args.output.close()
    else:
        print(template.render(values))


if __name__ == "__main__":
    main(sys.argv[1:])
