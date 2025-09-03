#!/usr/bin/env python3
#
# Author: Luca Colagrande

from anytree import Node, RenderTree
from functools import lru_cache
from pathlib import Path
import hashlib
import re
import subprocess
import sys


# Function to parse all rules from 'make -pq' output
@lru_cache(maxsize=4)
def _parse_makefile():
    # Run 'make -pq' and capture its output
    result = subprocess.run(
        ['make', '-pq'],
        capture_output=True,
        text=True)

    # Initialize an empty dictionary to store the targets and their prerequisites
    targets = {}

    # Split the output by lines
    make_output = result.stdout.splitlines()

    # Regex to capture target and its prerequisites
    target_pattern = re.compile(r'^([^\s]+)\s*:\s*([^\|]*)')

    # Parse the make output
    for line in make_output:
        match = target_pattern.match(line)
        if match:
            target = match.group(1)
            prerequisites = match.group(2).split()
            targets[target] = prerequisites

    return targets


# Internal function used for building a dependency tree with recursion.
def _get_prerequisites_recursive(target, targets, recursive=False):

    # Get the prerequisites for the target and attach them to the tree
    prerequisites = targets.get(target.name, [])
    nodes = [Node(prereq, parent=target) for prereq in prerequisites]

    # Recursively travel through prerequisites, to attach their prerequisites to the tree.
    if recursive and nodes:
        for node in nodes:
            _get_prerequisites_recursive(node, targets, recursive=True)


# Function to list prerequisites, optionally recursively
def list_prerequisites(target, recursive=False, debug=False):

    # Parse the makefile
    targets = _parse_makefile()

    # Handle non-existing target
    if target not in targets:
        raise Exception(f"Target '{target}' not found in the Makefile.")

    # Build the dependency tree for the specified target
    root = Node(target)
    _get_prerequisites_recursive(root, targets, recursive=recursive)

    # Print tree structure for debugging
    if debug:
        for pre, _, node in RenderTree(root):
            print(f"{pre}{node.name}")

        # Print a newline to separate debugging output from regular output
        print("")

    # Find all leaf prerequisites, uniquify and sort
    leaf_prereqs = [n.name for n in root.descendants if n.is_leaf]
    return sorted(set(leaf_prereqs))


# Takes in a structure like that returned by _parse_makefile,
# i.e. {target: [prereq1, prereq2, ...], ...}, and reverses it to a structure like
# i.e. {prereq: [target1, target2, ...], ...} listing targets directly depending
# on each prerequisite.
def _build_reverse_dict(targets):
    reverse_dict = {}
    for target, prerequisites in targets.items():
        for prerequisite in prerequisites:
            reverse_dict.setdefault(prerequisite, set()).add(target)
    return reverse_dict


# Internal function used for building a dependency tree with recursion.
def _get_dependents_recursive(prerequisite, prerequisites, recursive=False):

    # Get the targets directly depending on the prerequisite and attach them to the tree
    targets = prerequisites.get(prerequisite.name, [])
    nodes = [Node(target, parent=prerequisite) for target in targets]

    # Recursively travel through the direct targets, to attach the targets which in turn directly
    # depend on them to tree.
    if recursive and nodes:
        for node in nodes:
            _get_dependents_recursive(node, prerequisites, recursive=True)


# Return a sorted list of targets that depend on `prerequisite`.
# If `recursive` is False, only direct dependents are returned.
def list_dependents(prerequisite, recursive=False, debug=False):

    # Parse the makefile
    targets = _parse_makefile()
    prerequisites = _build_reverse_dict(targets)

    # Handle non-existing prerequisite
    if prerequisite not in prerequisites:
        raise Exception(f"Prerequisite '{prerequisite}' not found in the Makefile.")

    # Build the dependency tree from the specified prerequisite
    root = Node(prerequisite)
    _get_dependents_recursive(root, prerequisites, recursive=recursive)

    # Print tree structure for debugging
    if debug:
        for pre, _, node in RenderTree(root):
            print(f"{pre}{node.name}")

        # Print a newline to separate debugging output from regular output
        print("")

    # Find all targets, uniquify and sort
    dependents = [n.name for n in root.descendants]
    return sorted(set(dependents))


# Calculate a SHA-256 hash from the contents of a list of files, expanding directories recursively
def hash_files(file_list):
    # Create a new SHA-256 hash object
    hasher = hashlib.sha256()

    # If any prerequisite is a directory, replace it with its (recursive) contents
    expanded_file_list = []
    for file_name in file_list:
        file = Path(file_name)
        if file.is_dir():
            expanded_file_list.extend([str(f) for f in file.rglob('*') if f.is_file()])
        else:
            expanded_file_list.append(file_name)

    # Hash file contents
    for file_name in expanded_file_list:
        try:
            with open(file_name, 'rb') as f:
                # Read the file content in chunks to avoid memory issues with large files
                while chunk := f.read(8192):  # 8192 bytes per chunk
                    hasher.update(chunk)  # Update the hash with each chunk
        except FileNotFoundError:
            print(f"File '{file_name}' not found.", file=sys.stderr)

    # Return the final hexadecimal hash value
    return hasher.hexdigest()
