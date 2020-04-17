#!/usr/bin/env python3
# Copyright (c) 2020 SiFive Inc.
# SPDX-License-Identifier: Apache-2.0

"""Functions for finding freedom-metal sources in a Device Tree"""

import sys
import os

def has_compat(node) -> bool:
    return node.get_fields("compatible") is not None

def get_compatibles(tree):
    """Given a Devicetree, get the list of 'compatible' values"""

    compatibles = tree.filter(has_compat)

    return compatibles

extensions = ('.c', '.S')

def make_filename(compatible):
    return compatible.replace(',', '_')

def find_source(basename, dirs):
    for dir in dirs:
        path = os.path.join(dir, basename)
        if os.path.exists(path):
            return path
    return None

def get_sources(tree, dirs):
    """Given a Devicetree, get the list of source files available"""
    
    compatibles = get_compatibles(tree)
    sources_c = []
    sources_s = []
    for compatible in compatibles:
        device_types = compatible.get_fields("device_type")
        if device_types is None:
            device_types = [None]
        else:
            device_types = [None] + [d for d in device_types]
        for compat in compatible.get_fields("compatible"):
            for device_type in device_types:
                c = compat
                if device_type is not None:
                    c += '_' + device_type
                file = make_filename(c)
                for ext in extensions:
                    path = find_source(file + ext, dirs)
                    if path:
                        if path not in sources_c and path not in sources_s:
                            if ext == '.c':
                                sources_c += [path]
                            else:
                                sources_s += [path]

    return (sources_c, sources_s)
