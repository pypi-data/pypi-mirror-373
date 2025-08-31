#!/usr/bin/env python3

"""Shared utility functions"""

from importlib import resources

import yaml


def load_yaml(args_file, package, filename):
    """Load YAML from user-provided file or package resource."""
    if args_file:
        with open(args_file, "rb") as f:
            return yaml.safe_load(f)
    with resources.files(package).joinpath(filename).open("rb") as f:
        return yaml.safe_load(f)
