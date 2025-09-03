"""
    Simple and generic functions to handle inputs, files and strings for CWL interface
"""

__RCSID__ = "$Id$"

import os
import shellescape
import re


def check_if_file_input(entry):
    if isinstance(entry, dict):
        if "class" in entry:
            if entry["class"] == "File":
                return True
    else:
        return False


def add_fake_file(location):
    dir = os.path.dirname(location)
    if dir != "":
        if not os.path.exists(dir):
            os.makedirs(dir)
    open(location, "a").close()
    return


def remove_fake_file(location):
    os.remove(location)
    return


def maybe_quote(arg):
    needs_shell_quoting = re.compile(r"""(^$|[\s|&;()<>\'"$@])""").search
    return shellescape.quote(arg) if needs_shell_quoting(arg) else arg


def get_source_name(source):
    return source.rsplit("/", 1)[0]


def topological_sort(source):
    """from https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list
    perform topo sort on elements.

    :arg source: list of ``(steps, [list of dependencies])`` pairs
    :returns: list of steps, with dependencies listed first
    """
    pending = [
        (step, set(deps)) for step, deps in source
    ]  # copy deps so we can modify set in-place
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            step, deps = entry
            deps.difference_update(emitted)  # remove deps we emitted last pass
            if deps:  # still has deps? recheck during next pass
                next_pending.append(entry)
            else:  # no more deps? time to emit
                yield step
                emitted.append(
                    step
                )  # <-- not required, but helps preserve original ordering
                next_emitted.append(
                    step
                )  # remember what we emitted for difference_update() in next pass
        if (
            not next_emitted
        ):  # all entries have unmet deps, one of two things is wrong...
            raise ValueError(f"cyclic or missing dependency detected: {next_pending!r}")
        pending = next_pending
        emitted = next_emitted
    return emitted
