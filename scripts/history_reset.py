#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Reset the <History> of every pspec.xml under a directory to a single entry.

Used when a new repository generation starts from the existing recipes: the
accumulated update history is replaced by one "First release" entry with
release 1 (the newest entry's Version, Name and Email are kept, so the
package keeps its current version). Every file
that is rewritten is first copied into a backup directory that mirrors the
tree, so the operation can be undone with a plain copy back.

The script only uses the standard library and runs on Python 2.7 and 3.

Usage:
    history_reset.py [--root DIR] [--backup-dir DIR] [--comment TEXT] [--release N]
"""

from __future__ import print_function

import argparse
import os
import re
import sys

SPEC_FILE_NAME = "pspec.xml"
RELEASE_ATTRIBUTE = re.compile(r'(.*?release\s*=\s*)["\']\d+["\'](.*?)')


def read_file(path):
    with open(path) as handle:
        return handle.read().strip()


def write_file(path, content):
    with open(path, "w") as handle:
        handle.write(content)
        handle.write("\n")


def reset_history(spec_text, comment, release):
    """Return ``spec_text`` with its <History> reduced to the newest <Update>.

    The file is processed line by line on purpose: an XML round-trip would
    reorder attributes and lose the hand-written formatting of the recipes.
    The <History> block lists updates newest first, so the first <Update>
    carries the current version; it is kept with its release number and
    comment replaced, every older update is dropped.
    """
    updates = []          # (start, end) line indexes of every <Update> block
    lines = spec_text.split("\n")
    in_history = False
    for index, line in enumerate(lines):
        if "<History>" in line:
            in_history = True
        elif "</History>" in line:
            in_history = False
        elif in_history and "<Update" in line:
            updates.append([index, None])
        elif in_history and "</Update>" in line:
            updates[-1][1] = index
    if not updates:
        return spec_text

    keep_start, keep_end = updates[0]
    kept = []
    skipping_comment = False
    for line in lines[keep_start:keep_end + 1]:
        if "<Update" in line:
            line = RELEASE_ATTRIBUTE.sub(r'\1"%s"\2' % release, line)
        if "<Comment" in line and "</Comment" not in line:
            skipping_comment = True          # multi-line comment starts
        if "</Comment" in line:
            skipping_comment = False
            line = " " * 12 + "<Comment>%s</Comment>" % comment
        if not skipping_comment:
            kept.append(line)

    last_end = updates[-1][1]
    return "\n".join(lines[:keep_start] + kept + lines[last_end + 1:])


def prepare_backup_directory(backup_path):
    """Create ``backup_path``; an existing one is renamed with a numeric suffix."""
    if os.path.isdir(backup_path):
        suffix = 1
        while os.path.isdir("%s%02d" % (backup_path, suffix)):
            suffix += 1
        os.rename(backup_path, "%s%02d" % (backup_path, suffix))
    os.makedirs(backup_path)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Reset the History of every pspec.xml to a single release.")
    parser.add_argument("--root", default=".",
                        help="directory to walk for pspec.xml files (default: .)")
    parser.add_argument("--backup-dir", default="../backup",
                        help="where original files are copied before rewriting "
                             "(default: ../backup, relative to --root)")
    parser.add_argument("--comment", default="First release",
                        help="comment of the remaining history entry")
    parser.add_argument("--release", default="1",
                        help="release number of the remaining history entry")
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    root = os.path.normpath(arguments.root)
    backup_root = os.path.normpath(os.path.join(root, arguments.backup_dir))
    prepare_backup_directory(backup_root)

    for directory, _, files in os.walk(root):
        if SPEC_FILE_NAME not in files:
            continue
        spec_path = os.path.join(directory, SPEC_FILE_NAME)
        backup_path = os.path.join(backup_root, os.path.relpath(spec_path, root))
        print(spec_path)
        spec_text = read_file(spec_path)
        if not os.path.isdir(os.path.dirname(backup_path)):
            os.makedirs(os.path.dirname(backup_path))
        write_file(backup_path, spec_text)
        write_file(spec_path, reset_history(spec_text, arguments.comment,
                                            arguments.release))
    return 0


if __name__ == "__main__":
    sys.exit(main())
