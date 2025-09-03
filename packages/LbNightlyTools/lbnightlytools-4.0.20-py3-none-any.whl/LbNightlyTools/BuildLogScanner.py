###############################################################################
# (c) Copyright 2018 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Collect the build logs produced by lbn-wrapcmd and write the content grouped by
subdir and target.
"""

__author__ = "Marco Clemencic <marco.clemencic@cern.ch>"

import re

_ESCAPE_SEQ = re.compile("\x1b\\[([0-9;]*m|[012]?K)")


def remove_colors(text):
    """
    Strip ANSI color codes from a text.

    >>> remove_colors('\\x1b[34;42mHello\\x1b[2m!\\x1b[m')
    'Hello!'
    """
    return _ESCAPE_SEQ.sub("", text)


_LOG_SCANNERS = []


def log_scanner(func):
    """
    Decorator to declare a function as log scanner.
    """
    global _LOG_SCANNERS
    _LOG_SCANNERS.append(func)
    return func


class IssueSource:
    def __init__(self, name, line=None, pos=None):
        self.name = name
        self.line = line
        self.pos = pos

    def __str__(self):
        return ":".join(str(s) for s in [self.name, self.line, self.pos] if s)

    def __repr__(self):
        return f"IssueSource{tuple(s for s in [self.name, self.line, self.pos] if s)!r}"


class Issue:
    """
    Base class for issues found in logs.
    """

    SEVERITIES = ("error", "warning", "coverity")

    def __init__(self, severity, source, msg, log_range):
        if severity not in self.SEVERITIES:
            raise ValueError("invalid severity value %r", severity)
        self.severity = severity
        if isinstance(source, tuple):
            source = IssueSource(*source)
        self.source = source
        self.msg = msg
        self.log_range = log_range

    def linkText(self):
        return f"{self.source.name}:{self.source.line}"

    def __str__(self):
        return ": ".join(str(s) for s in [self.source, self.severity, self.msg])

    def __repr__(self):
        return f"{self.__class__.__name__}{(self.severity, self.source, self.msg, self.log_range)!r}"


def strip_build_root(path, iterable):
    """
    Helper to strip the build root string from a
    """
    from LbNightlyTools.Scripts.Checkout import PathPrefixRemover

    strip = PathPrefixRemover(path)
    for line in iterable:
        yield strip(line)


def split_build_log(iterable):
    """
    Split a build.log file in chunks.

    @return a list of pairs [(chunk_id, lines)]
    """
    chunks = []
    lines = []
    chunks.append(("None", lines))
    for line in iterable:
        if line.startswith("# Building package"):
            lines = [line]
            chunk_id = line.split()[3]
            chunks.append((chunk_id, lines))
        elif line.startswith("#### CMake"):
            lines = []
            chunk_id = line.split()[-2]
            chunks.append((chunk_id, lines))
        else:
            lines.append(line)
    if chunks[0] == ("None", []):
        chunks.pop(0)
    return chunks


def reports2exclusions(reports=None):
    """
    Translate a list of Issue instances to a list of lines to exclude in an
    enumeration.

    >>> reports2exclusions([Issue('warning', ('f1',), 'm1', (10, 15)),
    ...                     Issue('warning', ('f2',), 'm2', (23, 27)),
    ...                     Issue('error', ('f3',), 'm3', (18, 19))])
    [(10, 15), (18, 19), (23, 27)]
    """
    if not reports:
        return None
    exclusions = [issue.log_range for issue in reports]
    exclusions.sort()
    return exclusions


def enumerate_x(items, exclusions=None):
    """
    Same as builtin enumerate function, but skip items with id in the ranges
    defined by exclusions.

    >>> list(enumerate_x('abcdefghij', [(2, 5), (8, 9)]))
    [(0, 'a'), (1, 'b'), (5, 'f'), (6, 'g'), (7, 'h'), (9, 'j')]

    Exclusions may be overlapping:

    >>> list(enumerate_x('abcdefghij', [(1, 4), (2, 5), (6, 9), (7, 8)]))
    [(0, 'a'), (5, 'f'), (9, 'j')]
    """
    if not exclusions:
        return enumerate(items)
    from itertools import chain

    # invert the exclusions to list of partial enumerations
    ranges = []
    start = 0
    for stop, next_start in exclusions:
        # if there is an overlap in the exclusion we need to skip to the next
        if stop >= start:
            ranges.append(enumerate(items[start:stop], start))
        # max here covers the case of full enclosed exclusions ([(2,10), (3,5)])
        start = max(start, next_start)
    ranges.append(enumerate(items[start:], start))
    # return the joined partial enumerations
    return chain(*ranges)


class GCCIssue(Issue):
    pass


@log_scanner
def gcc_output_scanner(lines, reports=None):
    if reports is None:
        reports = []
    diag_rexp = re.compile(r"^(\S+):([0-9]+):([0-9]+): (warning|error): (.*)")
    try:
        ln_iter = enumerate_x(lines, reports2exclusions(reports))
        ln, line = next(ln_iter)
        while True:
            line = remove_colors(line.rstrip())
            m = diag_rexp.match(line)
            if m:
                startln = ln
                ln, line = next(ln_iter)
                try:
                    while line.startswith(" "):
                        ln, line = next(ln_iter)
                except StopIteration:
                    pass
                reports.append(
                    GCCIssue(
                        m.group(4),
                        (m.group(1), int(m.group(2)), int(m.group(3))),
                        m.group(5),
                        (startln, ln),
                    )
                )
            else:
                ln, line = next(ln_iter)
    except StopIteration:
        pass
    return reports


class CMakeIssue(Issue):
    pass


@log_scanner
def cmake_output_scanner(lines, reports=None):
    if reports is None:
        reports = []
    diag_rexp = re.compile(
        r"^CMake (?:Deprecation )?(Warning|Error) (?:\(dev\) )?at (\S+):([0-9]+) \(message\):"
    )
    try:
        ln_iter = enumerate_x(lines, reports2exclusions(reports))
        ln, line = next(ln_iter)
        while True:
            line = line.rstrip()
            m = diag_rexp.match(line)
            if m:
                startln = ln
                ln, line = next(ln_iter)
                try:
                    while line.startswith(" "):
                        ln, line = next(ln_iter)
                except StopIteration:
                    pass
                msg = " ".join(l.strip() for l in lines[startln + 1 : ln]).strip()
                if len(msg) > 120:
                    msg = msg[:80] + "[...]" + msg[-35:]
                reports.append(
                    CMakeIssue(
                        m.group(1).lower(),
                        (m.group(2), int(m.group(3))),
                        msg,
                        (startln, ln),
                    )
                )
            else:
                ln, line = next(ln_iter)
    except StopIteration:
        pass
    return reports


class GaudiIssue(Issue):
    pass


@log_scanner
def gaudi_output_scanner(lines, reports=None):
    if reports is None:
        reports = []
    diag_rexp = re.compile(r".*?(\S+) *(WARNING|ERROR|FATAL) +(.*)")
    try:
        ln_iter = enumerate_x(lines, reports2exclusions(reports))
        ln, line = next(ln_iter)
        while True:
            line = line.rstrip()
            m = diag_rexp.match(line)
            if m:
                diag_type = m.group(2).lower()
                if diag_type == "fatal":
                    diag_type = "error"
                reports.append(
                    GaudiIssue(diag_type, (m.group(1),), m.group(3), (ln, ln + 1))
                )
            ln, line = next(ln_iter)
    except StopIteration:
        pass
    return reports


class PythonIssue(Issue):
    def linkText(self):
        return f'File "{self.source.name}", line {self.source.line}'


@log_scanner
def python_output_scanner(lines, reports=None):
    if reports is None:
        reports = []
    warn_rexp = re.compile(r"(\S+):([0-9]+): \S*(Warning): (.*)")
    tbinfo_rexp = re.compile(r'\s+File "(.+)", line ([0-9]+)')
    try:
        ln_iter = enumerate_x(lines, reports2exclusions(reports))
        ln, line = next(ln_iter)
        while True:
            line = line.rstrip()
            m = warn_rexp.match(line)
            if m:
                startln = ln
                ln, line = next(ln_iter)
                reports.append(
                    PythonIssue(
                        "warning",
                        (m.group(1), int(m.group(2))),
                        m.group(4),
                        (startln, ln),
                    )
                )
            elif line.strip() == "Traceback (most recent call last):":
                startln = ln
                ln, line = next(ln_iter)
                filename, fileln, msg = "<unkown>", None, "Python traceback"
                try:
                    while line.startswith(" "):
                        ln, line = next(ln_iter)
                        m = tbinfo_rexp.match(line)
                        if m:
                            filename = m.group(1)
                            fileln = int(m.group(2))
                    # the actual exception message is after of the dump
                    msg = line.strip()
                    ln, line = next(ln_iter)
                except StopIteration:
                    pass
                reports.append(
                    PythonIssue("error", (filename, fileln), msg, (startln, ln))
                )
            else:
                ln, line = next(ln_iter)
    except StopIteration:
        pass
    return reports


class ROOTBreakIssue(Issue):
    pass


@log_scanner
def root_stack_trace_output_scanner(lines, reports=None):
    if reports is None:
        reports = []
    MARKER = "*** Break ***"
    try:
        ln_iter = enumerate_x(lines, reports2exclusions(reports))
        ln, line = next(ln_iter)
        while True:
            line = line.strip()
            if line.startswith(MARKER):
                msg = line[len(MARKER) :].strip()
                reports.append(
                    ROOTBreakIssue("error", ("<unknown>",), msg, (ln, ln + 1))
                )
            ln, line = next(ln_iter)
    except StopIteration:
        pass
    return reports


class GenericIssue(Issue):
    def __str__(self):
        return self.msg


@log_scanner
def generic_scanner(lines, reports=None):
    if reports is None:
        reports = []
    WARNING_RE = re.compile(
        "|".join([r"\bwarning\b", r"\bSyntaxWarning:"]), re.IGNORECASE
    )
    ERROR_RE = re.compile(
        "|".join(
            [
                r"\berror\b",
                r"\*\*\* Break \*\*\*",
                r"^Traceback \(most recent call last\):",
                r"^make: \*\*\* No rule to make target",
                r"Assertion.*failed",
            ]
        ),
        re.IGNORECASE,
    )
    try:
        ln_iter = enumerate_x(lines, reports2exclusions(reports))
        ln, line = next(ln_iter)
        while True:
            line = remove_colors(line.strip())
            diag_type = (WARNING_RE.search(line) and "warning") or (
                ERROR_RE.search(line) and "error"
            )
            if diag_type:
                reports.append(
                    GenericIssue(diag_type, ("<unknown>",), line, (ln, ln + 1))
                )
            ln, line = next(ln_iter)
    except StopIteration:
        pass
    return reports


def scan_build_log(lines):
    reports = None
    for scanner in _LOG_SCANNERS:
        reports = scanner(lines, reports)
    return reports
