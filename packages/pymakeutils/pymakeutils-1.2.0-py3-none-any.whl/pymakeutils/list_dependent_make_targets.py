#!/usr/bin/env python3
#
# Author: Luca Colagrande

import argparse
from pymakeutils.common import list_dependents


def parse_args():
    parser = argparse.ArgumentParser(
        description="List all targets that depend on one or more prerequisites.")
    parser.add_argument(
        'prerequisites',
        nargs='+',
        help="One or more files/targets whose dependents you want to list")
    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help="Recursively include transitive dependents")
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output to show intermediate steps")
    return parser.parse_args()


def main():
    args = parse_args()

    # Take the union of all dependent targets for the given prerequisites
    all_deps = set()
    for p in args.prerequisites:
        all_deps.update(
            list_dependents(p, recursive=args.recursive, debug=args.debug)
        )
    dependents = sorted(all_deps)

    # Print the list of dependent targets
    print('\n'.join(dependents))


if __name__ == "__main__":
    main()
