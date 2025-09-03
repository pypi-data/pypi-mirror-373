#!/usr/bin/env python3
#
# Author: Luca Colagrande

import argparse
from pymakeutils.common import list_dependents
import sys


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
        '-M',
        '--emit-makefrag',
        action='store_true',
        help="Instead of outputting a list of Make targets, emit a Makefile fragment "
             "conditionally including each prerequisite if MAKE_CMD_GOALS includes "
             "any of its dependent targets.")
    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help="Enable debug output to show intermediate steps")
    return parser.parse_args()


def emit_makefrag(prerequisites, recursive, debug):
    s = "-include "
    for p in sorted(set(prerequisites)):
        targets = list_dependents(p, recursive=recursive, debug=debug)

        if not targets:
            print(f'Warning: no targets depend on prerequisite {p}.', file=sys.stderr)
            continue

        target_list = " ".join(sorted(targets))
        s += f"$(if $(filter {target_list},$(MAKECMDGOALS)),{p}) "
    print(s.strip())


def emit_targets(prerequisites, recursive, debug):
    # Take the union of all dependent targets for the given prerequisites
    all_deps = set()
    for p in prerequisites:
        all_deps.update(
            list_dependents(p, recursive=recursive, debug=debug)
        )
    print('\n'.join(sorted(all_deps)))


def main():
    args = parse_args()

    if args.emit_makefrag:
        emit = emit_makefrag
    else:
        emit = emit_targets
    emit(args.prerequisites, args.recursive, args.debug)


if __name__ == "__main__":
    main()
