#!/usr/bin/env python3
#
# Author: Luca Colagrande

import argparse
from pymakeutils.common import list_prerequisites, hash_files


def parse_args():
    parser = argparse.ArgumentParser(
        description="List prerequisites for a specified Makefile target.")
    parser.add_argument(
        'target',
        help="The make target whose prerequisites you want to list")
    parser.add_argument(
        '-r',
        '--recursive',
        action='store_true',
        help="Recursively list all prerequisites")
    parser.add_argument(
        '--hash',
        action='store_true',
        help="Generate a hash from the contents of all prerequisites")
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output to show intermediate steps")

    return parser.parse_args()


def main():
    args = parse_args()

    prerequisites = list_prerequisites(args.target, recursive=args.recursive, debug=args.debug)

    if args.hash:
        # Print a hash of the prerequisites' contents
        hash_value = hash_files(prerequisites)
        print(hash_value)
    else:
        # Print the list of prerequisites
        print('\n'.join(prerequisites))


if __name__ == "__main__":
    main()
