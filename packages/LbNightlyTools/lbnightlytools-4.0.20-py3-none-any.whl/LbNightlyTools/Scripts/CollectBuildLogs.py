###############################################################################
# (c) Copyright 2015 CERN                                                     #
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

import html
import logging
import os

from LbNightlyTools.Scripts.Common import PlainScript


def collect_cmake_logs(path):
    """
    Looks for files ending in '-build.log' in all the subdirs.

    @param path: directory where to start the search from
    @return: dictionary with the subdir as key (relative path) and the list of
             files (full path) as values.
    """
    log = logging.getLogger("collect_cmake_logs")
    log.info("searching for log files")
    logs = {}
    for subdir, _dirs, files in os.walk(path):
        files = [os.path.join(subdir, f) for f in files if f.endswith("-build.log")]
        if files:
            log.debug("found %d files in %s", len(files), subdir)
            files.sort()
            logs[os.path.relpath(subdir, path)] = files
    return logs


def collect_cmt_logs(path, platform):
    """
    Looks for files ending in '-build.log' in all the subdirs.

    @param path: directory where to start the search from
    @return: dictionary with the subdir as key (relative path) and the list of
             files (full path) as values.
    """
    logging.getLogger("collect_cmt_logs").info("searching for log files")
    logs = {}
    filename = f"build.{platform}.log"
    for subdir, _dirs, files in os.walk(path):
        if filename in files:
            logs[os.path.relpath(subdir, path)] = [os.path.join(subdir, filename)]
    return logs


class CollectLogsError(RuntimeError):
    """
    Exception raised when there are problems collecting the build logs.
    """

    pass


class RegexExcusion:
    """
    Small helper class to filter a list excluding entries matching one of the
    provided regular expressions.
    """

    def __init__(self, exps):
        """
        Initialize the object with a list of regular expression (strings).
        """
        from re import compile

        self.exps = [compile(exp) for exp in exps]

    def __call__(self, s):
        """
        Check if a string is good (no match) or not (match).

        @return: True if there is no match, False if there is a match.
        """
        for x in self.exps:
            if x.match(s):
                return False
        return True

    def filter(self, iterable):
        """
        Generator that returns only the good (not excluded) entries in an
        iterable.
        """
        return (s for s in iterable if self(s))


class Script(PlainScript):
    """
    Collect partial build logs from a directory and group them in a single
    file.
    """

    __usage__ = "%prog [options] directory output_file"

    def defineOpts(self):
        """
        Options specific to this script.
        """
        self.parser.add_option(
            "--append",
            action="store_true",
            help="append to the output file instead of " "overwrite it",
        )
        self.parser.add_option(
            "-x",
            "--exclude",
            action="append",
            help="regular expression to select files that "
            "should not be included in the output",
        )
        self.parser.add_option(
            "--cmt",
            action="store_const",
            dest="build_tool",
            const="cmt",
            help="expect a CMT build directory",
        )
        self.parser.add_option(
            "--cmake",
            action="store_const",
            dest="build_tool",
            const="cmake",
            help="expect a CMake build directory (default)",
        )
        self.parser.add_option(
            "--platform",
            action="store",
            help="platform id (used only with the CMT " "scanner) [default: %default]",
        )
        platform = os.environ.get("BINARY_TAG", os.environ.get("CMTCONFIG", ""))
        self.parser.set_defaults(exclude=[], build_tool="cmake", platform=platform)

    def cmake(self):
        """
        CMake specific logic.
        """
        path, output = self.args
        exclude = RegexExcusion(self.options.exclude)

        logs = collect_cmake_logs(path)
        if not logs:
            raise CollectLogsError(f"lbn-wrapcmd did not produce files in {path}")

        # sort the directories by contained filename, so that even if they
        # are built at the same time, the one that completes first wins
        # (note that the list of files in each subdir is sorted)
        from os.path import basename

        subdirs = sorted(logs, key=lambda s: (basename(logs[s][-1]), s))
        # copy the content of each log file into the output file, prepending
        # the group of files in a subdir with a separator
        with open(output, "a" if self.options.append else "w") as outfile:
            for subdir in subdirs:
                # we want to show only files that are not excluded
                files = exclude.filter(logs[subdir])
                if files:
                    # targets in the '.' directory are "global" targets
                    if subdir == ".":
                        subdir = "ROOT_DIR"
                    outfile.write(f"#### CMake {subdir} ####\n")
                    for fname in files:
                        outfile.writelines(open(fname))

    def cmt(self):
        """
        CMT specific logic.
        """
        path, output = self.args
        exclude = RegexExcusion(self.options.exclude)

        logs = collect_cmt_logs(path, self.options.platform)
        if not logs:
            raise CollectLogsError(f"CMT build did not produce log files in {path}")

        # sort the directories by contained filename, so that even if they
        # are built at the same time, the one that completes first wins
        # (note that the list of files in each subdir is sorted)
        import re

        hdr = re.compile(r"Building package[^[]*\[(\d+)/\d+\]")

        def key(subdir):
            filename = logs[subdir][0]
            # self.log.debug('key for %s', filename)
            with open(filename) as f:
                m = hdr.search(f.read(1024))
            k = int(m.group(1)) if m else None
            # self.log.debug('key found: %s', k)
            return k

        subdirs = sorted(logs, key=key)
        # copy the content of each log file into the output file, prepending
        # the group of files in a subdir with a separator
        with open(output, "a" if self.options.append else "w") as outfile:
            for subdir in subdirs:
                # we want to show only files that are not excluded
                files = exclude.filter(logs[subdir])
                for fname in files:
                    outfile.writelines(open(fname))

    def main(self):
        """
        Script logic.
        """
        try:
            getattr(self, self.options.build_tool)()
            return 0
        except CollectLogsError as x:
            self.log.error(str(x))
            return 1


CHUNK_LOADER = """<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
<link rel="stylesheet" href="ansi.css"></head>
<body>Loading...</body>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
<script>
document.title = location.search.slice(1);
$('body').load(document.title + '.html', function(){
  if (location.hash) location.hash = location.hash;
});
</script>
</html>"""

TABLE_HEAD = '<table class="table table-striped" style="text-align:left">'
TABLE_TAIL = "</table>"


class IssueLinker:
    def __init__(self, issues, url_format):
        self.issues = issues
        self.url_format = url_format
        self._count = 0

    def __call__(self, line):
        n = self._count
        for issue in self.issues:
            l, h = issue.log_range
            if n >= l and n < h:
                txt = html.escape(issue.linkText(), quote=True)
                line = line.replace(
                    txt,
                    f'<a href="{self.url_format(issue.source)}">{txt}</a>',
                )
                break
        self._count += 1
        return line


class GitlabUrlFormat:
    def __init__(self, base_url):
        base_url = base_url.rstrip("/")
        self.format = base_url + "/{name}#L{line}"

    def __call__(self, source):
        return self.format.format(name=source.name, line=source.line)


def report_dict(chunks, reports):
    """
    Convert list of (chunk_id, lines) and a dictionary {chunk_id: issues} into
    a simplified report suitable for conversion to JSON.

    The output format is:

        {'sections': [{'id': 'section_id',
                       'desc': 'html title of the section',
                       'url': 'url of section content (html)'}, ...],
         'issues': {
             'severity': [{
                  'section_id': 'id of section it comes from',
                  'anchor': 'html anchor in section content',
                  'desc': 'one line description of the issue',
                  'text': ['full issue', 'report', ...]
             }, ...],
             ...
        }}
    """
    from LbNightlyTools.BuildLogScanner import Issue, remove_colors

    report = {"sections": [], "issues": {severity: [] for severity in Issue.SEVERITIES}}

    for chunk_id, chunk in chunks:
        report["sections"].append(
            {"id": chunk_id, "desc": chunk_id, "url": f"{chunk_id}.html"}
        )
        for issue in reports[chunk_id]:
            report["issues"][issue.severity].append(
                {
                    "section_id": chunk_id,
                    "anchor": f"{chunk_id}_{issue.log_range[0] + 1}",
                    "desc": html.escape(str(issue), quote=True),
                    "text": [
                        html.escape(remove_colors(line.rstrip()), quote=True)
                        for line in chunk[issue.log_range[0] : issue.log_range[1]]
                    ],
                }
            )
    return report


def write_report_index(report, output_dir):
    """
    Generate index.html (and accessory files) to allow access to report
    sections.
    """
    from LbNightlyTools.BuildLogScanner import Issue
    from LbNightlyTools.HTMLUtils import HTML_STYLE
    from LbNightlyTools.Utils import natsort_key

    with open(os.path.join(output_dir, "index.html"), "w") as h:
        title = "Build Log"
        if "project" in report:
            title += " of " + html.escape(report["project"], quote=True)
            if "version" in report:
                title += "/" + html.escape(report["version"], quote=True)
        h.write(
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            "<style>.issue-error {background-color: pink;}\n"
            ".issue-warning {background-color: lightyellow;}</style>"
            f"<title>{title}</title></head><body><h1>{title}</h1>\n"
        )

        if "ignored_issues" in report:
            ignored = []
            for severity in Issue.SEVERITIES:
                counts = report["ignored_issues"].get(severity, {})
                if sum(counts.values()):
                    ignored.append(f"<li><strong>{severity}</strong>\n<ul>\n")
                    ignored.extend(
                        f"<li>{html.escape(text, quote=True)}: {count}</li>\n"
                        for text, count in counts.items()
                        if count
                    )
                    ignored.append("</ul></li>\n")
            if ignored:
                h.write("<h2>Ignored issues</h2>\n<ul>\n")
                h.writelines(ignored)
                h.write("</ul>\n")

        h.write("<h2>Sections:</h2>\n<ul>\n")
        for section in report["sections"]:
            h.write('<li><a href="load_section.html?{id}">{id}</a>\n'.format(**section))
            # add the list only if we do have any issue
            if sum(len(items) for items in report["issues"].values()):
                h.write("<ul>")
                for severity in Issue.SEVERITIES:
                    issues = [
                        issue
                        for issue in report["issues"][severity]
                        if issue["section_id"] == section["id"]
                    ]
                    if issues:
                        issues.sort(key=lambda issue: natsort_key(issue["desc"]))
                        h.write(
                            f'<li class="issue-{severity}">{severity}s ({len(issues)})<ul>\n'
                        )
                        h.writelines(
                            '<li><a href="load_section.html?'
                            '{section_id}#{anchor}">{desc}</a></li>\n'.format(**issue)
                            for issue in issues
                        )
                        h.write("</ul></li>")
                h.write("</ul>")
            h.write("</li>\n")
        h.write("</ul>\n</body>\n")

    with open(os.path.join(output_dir, "ansi.css"), "w") as h:
        h.write(HTML_STYLE)

    with open(os.path.join(output_dir, "load_section.html"), "w") as h:
        h.write(CHUNK_LOADER)


class LogToHTML(PlainScript):
    """
    Scan a build.log file and produce an HTML report for it.
    """

    __usage__ = "%prog [options] path/to/build.log output_dir"

    def defineOpts(self):
        """
        Options specific to this script.
        """
        self.parser.add_option(
            "--build-root", help="build root of the project (to strip)"
        )
        self.parser.add_option(
            "--slot-build-root", help="build root of the slot (to strip)"
        )
        self.parser.add_option("--base-url", help="base URL to access source files")
        self.parser.set_defaults(strip_string=[])

    def main(self):
        """
        Script logic.
        """
        import json

        from LbNightlyTools.Scripts.Build import genBuildReport

        log_file, output_dir = self.args

        jreport = genBuildReport(
            log_file, output_dir, self.options.build_root, self.options.slot_build_root
        )
        json.dump(
            jreport, open(os.path.join(output_dir, "report.json"), "wb"), indent=2
        )
        write_report_index(jreport, output_dir)
