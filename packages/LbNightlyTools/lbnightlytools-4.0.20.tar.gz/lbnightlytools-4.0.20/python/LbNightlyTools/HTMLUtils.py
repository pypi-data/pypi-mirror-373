###############################################################################
# (c) Copyright 2013 CERN                                                     #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
Common utility functions.

@author Marco Clemencic <marco.clemencic@cern.ch>
"""

import logging
import re
import sys
from html import escape

HTML_STYLE = """
.xterm-style-0 {}
.xterm-style-1 {font-weight: bold}
.xterm-style-4 {text-decoration: underline}
.xterm-style-5 {font-weight: blink}
.xterm-style-7 {} # reverse
.xterm-color-0 {color: black;}
.xterm-color-1 {color: red;}
.xterm-color-2 {color: green;}
.xterm-color-3 {color: yellow;}
.xterm-color-4 {color: blue;}
.xterm-color-5 {color: magenta;}
.xterm-color-6 {color: cyan;}
.xterm-color-7 {color: white;}
.xterm-bgcolor-0 {/*background-color: black;*/}
.xterm-bgcolor-1 {background-color: red;}
.xterm-bgcolor-2 {background-color: green;}
.xterm-bgcolor-3 {background-color: yellow;}
.xterm-bgcolor-4 {background-color: blue;}
.xterm-bgcolor-5 {background-color: magenta;}
.xterm-bgcolor-6 {background-color: cyan;}
.xterm-bgcolor-7 {background-color: white;}
.even {font-family: monospace; white-space: pre-wrap;
       border: 1px solid WhiteSmoke;
       background-color: WhiteSmoke;}
.odd {font-family: monospace; white-space: pre-wrap;
      border: 1px solid white;
      background-color: white;}
a.lineno {width: 5ch;
          display: inline-block;
          text-align: right;
          padding-right: 0.5em;
          margin-right: 0.5em;
          /*border-right: thin solid black;*/
          /*background-color: lightcyan;*/}
.stderr {background-color: PapayaWhip; font-style: italic;}
.stderr .even {font-family: monospace; white-space: pre-wrap;
               border-color: Bisque;
               background-color: Bisque;}
.stderr .odd {font-family: monospace; white-space: pre-wrap;
              border-color: PapayaWhip;
              background-color: PapayaWhip;}
:target {border-color: black;}
.stderr :target {border-color: red;}
.table-striped > tbody > tr:nth-of-type(2n+1):target,
.table-striped > tbody > tr:nth-of-type(2n):target{
    background-color: #DDD;
}
.table > tbody > tr > td{
    padding:2px;
}
pre {
    white-space: pre-wrap;
    background-color: inherit;
    color: inherit;
    padding: 0;
    margin: 0;
    border: none;
}
"""

# cached regular expression to find ANSI color codes
COLCODE_RE = re.compile("\x1b\\[([0-9;]*m|[012]?K)")


class ANSIStyle:
    __slots__ = ("style", "color", "bgcolor")

    def __init__(self, style=0, color=0, bgcolor=0):
        self.style = style
        self.color = color
        self.bgcolor = bgcolor
        if isinstance(style, str):
            self.style = 0
            self.apply_code(style)

    def apply_code(self, code):
        """
        >>> ANSIStyle(1, 2, 3).apply_code('0')
        ANSIStyle(style=0, color=0, bgcolor=0)
        >>> ANSIStyle().apply_code('1;34')
        ANSIStyle(style=1, color=4, bgcolor=0)
        >>> ANSIStyle().apply_code('45')
        ANSIStyle(style=0, color=0, bgcolor=5)
        """
        if not code or code == "0":
            self.style = self.color = self.bgcolor = 0
        else:
            for subcode in [int(x, 10) for x in code.split(";")]:
                if subcode >= 40:
                    self.bgcolor = subcode - 40
                elif subcode >= 30:
                    self.color = subcode - 30
                else:
                    self.style = subcode
        return self

    def copy(self):
        return ANSIStyle(self.style, self.color, self.bgcolor)

    def code(self, base=None):
        if (self.style, self.color, self.bgcolor) == (0, 0, 0):
            return ""
        if not base:
            base = ANSIStyle()
        if self == base:
            return self.code()  # prevent a no change to become a reset
        codes = []
        if self.style != base.style:
            codes.append(str(self.style))
        if self.color != base.color:
            codes.append(str(30 + self.color))
        if self.bgcolor != base.bgcolor:
            codes.append(str(40 + self.bgcolor))
        return ";".join(codes)

    def css(self, base=None):
        """
        CSS class(es) for the current text style.

        >>> ANSIStyle().css()
        ''
        >>> ANSIStyle('1;32;43').css()
        'xterm-style-1 xterm-color-2 xterm-bgcolor-3'
        """
        if (self.style, self.color, self.bgcolor) == (0, 0, 0):
            return ""
        if not base:
            base = ANSIStyle()
        codes = []
        for key in self.__slots__:
            if getattr(self, key) != getattr(base, key):
                codes.append(f"xterm-{key}-{getattr(self, key)}")
        return " ".join(codes)

    def __repr__(self):
        return "ANSIStyle({})".format(
            ", ".join(f"{key}={getattr(self, key)!r}" for key in self.__slots__)
        )

    def __eq__(self, other):
        return isinstance(other, ANSIStyle) and (
            self.style,
            self.color,
            self.bgcolor,
        ) == (other.style, other.color, other.bgcolor)


class ANSI2HTML:
    """
    Class to convert ANSI codes into HTML classes.
    """

    def __init__(self, start_style=""):
        self.current_style = (
            start_style
            if isinstance(start_style, ANSIStyle)
            else ANSIStyle(start_style)
        )

    def _process(self, line):
        # we record and strip the newline format at end of line not to include
        # it in the formatting
        if line.endswith("\n"):
            newline = "\n"
            line = line[:-1]
        elif line.endswith("\r\n"):
            newline = "\r\n"
            line = line[:-2]
        else:
            newline = ""

        # special handling of styles at beginning of line
        m = COLCODE_RE.match(line)
        while m:
            line = line[m.end() :]
            if m.group(1).endswith("m"):
                self.current_style.apply_code(m.group(1)[:-1])
            m = COLCODE_RE.match(line)

        current_class = self.current_style.css()
        if current_class:
            yield f'<span class="{current_class}">'
        else:
            yield "<span>"

        pos = 0
        while True:
            # look for a control sequence
            m = COLCODE_RE.search(line, pos)
            if not m:
                # no more codes to convert
                break
            # pass the chars so far
            if m.start() != pos:
                yield line[pos : m.start()]
            # parse the new code
            if m.group(1).endswith("m"):
                self.current_style.apply_code(m.group(1)[:-1])
                next_class = self.current_style.css()
            else:
                next_class = current_class

            if next_class != current_class:
                # we have a change, close previous span, open the new one
                yield f'</span><span class="{next_class}">'
                current_class = next_class
            pos = m.end()  # update offset to end of control code

        if pos < len(line):  # flush what remains of the line
            yield line[pos:]
        yield "</span>" + newline  # close the global <span>

    def __call__(self, line):
        """
        Add HTML span tags for ansi colors.
        """
        return "".join(self._process(line))


class TableizeLine:
    """
    Add table row tags and optionally line numbers to lines.
    """

    def __init__(
        self, first_line_no=1, line_id_prefix="L", add_line_nos=False, row_class=None
    ):
        self.line_no = first_line_no

        line_format = '<tr id="{prefix}{{n}}"{{class_desc}}><td>'
        if add_line_nos:
            line_format += '<a href="#{prefix}{{n}}">{{n}}</a></td><td>'
        line_format += "{{text}}</td></tr>"

        if row_class is None or isinstance(row_class, str):
            self.row_class = lambda n: row_class
        else:
            self.row_class = row_class

        self._line_format = line_format.format(prefix=line_id_prefix)

    def __call__(self, line):
        """
        Add HTML tags.
        """
        # we record and strip the newline format at end of line not to include
        # it in the formatting
        if line.endswith("\n"):
            newline = "\n"
            line = line[:-1]
        elif line.endswith("\r\n"):
            newline = "\r\n"
            line = line[:-2]
        else:
            newline = ""

        css = self.row_class(self.line_no)
        class_desc = f' class="{css}"' if css else ""

        out = (
            self._line_format.format(n=self.line_no, class_desc=class_desc, text=line)
            + newline
        )
        self.line_no += 1
        return out


class WrapLine:
    """
    Wrap a line in HTML tags.
    """

    def __init__(self, tag, attrs={}):
        self._line_format = "<{tag}{attrs}>{{text}}</{tag}>".format(
            tag=tag,
            attrs=""
            if not attrs
            else " " + " ".join('{}="{}"'.format(item) for item in list(attrs.items())),
        )

    def __call__(self, line):
        """
        Add HTML tags.
        """
        # we record and strip the newline format at end of line not to include
        # it in the formatting
        if line.endswith("\n"):
            newline = "\n"
            line = line[:-1]
        elif line.endswith("\r\n"):
            newline = "\r\n"
            line = line[:-2]
        else:
            newline = ""
        return self._line_format.format(text=line) + newline


class ClassifyByLineNo:
    """
    Helper to set specific class for groups of lines in TableizeLine.
    """

    def __init__(self, range_classes):
        self.range_classes = list(range_classes)

    def __call__(self, line_no):
        for (begin, end), css in self.range_classes:
            if line_no >= begin and line_no < end:
                return css
        return None


class XTerm2HTML:
    """
    Class to translate an ASCII string (containing ANSI color codes), into an
    HTML page.

    Usage:

    >>> input = '\\x1b[31mHello \\x1b[34mcolored \\x1b[32mworld\\x1b[0m!'
    >>> conv = XTerm2HTML()
    >>> html = ''.join([conv.head(title='Hi!'), conv.process(input),
    ...                 conv.tail()])
    """

    def __init__(
        self,
        first_line=1,
        show_line_no=False,
        line_prefix="L",
        is_escaped=False,
        plugins_function=None,
    ):
        """
        Initialize the conversion instance.
        An optional first_line can be provided if the output of the processing
        is meant to be concatenated with the output of another call to this
        class.
        """
        self.actions = [] if is_escaped else [lambda line: escape(line, quote=True)]
        self.actions.extend(plugins_function or [])
        self.actions.extend(
            [
                ANSI2HTML(),
                WrapLine("pre"),
                TableizeLine(
                    first_line_no=first_line,
                    line_id_prefix=line_prefix,
                    add_line_nos=show_line_no,
                ),
            ]
        )
        self.log = logging.getLogger(self.__class__.__name__)
        self.is_escaped = is_escaped

    def head(self, title=""):
        """
        Return a string containing the head of the HTML page.
        """
        return (
            '<!DOCTYPE html><html><head><meta charset="utf-8">'
            '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn'
            '.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="'
            "sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmS"
            'Tsz/K68vbdEjh4u" crossorigin="anonymous">'
            '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn'
            '.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" '
            'integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SV'
            'rLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">'
            f"<style>{HTML_STYLE}</style><title>{title}</title></head><body>\n"
        )

    def tail(self):
        """
        Return a string containing the tail of the HTML page.
        """
        return (
            "</body>"
            '<script src="https://ajax.googleapis.com/ajax/libs/jquery'
            '/1.12.4/jquery.min.js"></script>'
            '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/'
            '3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027q'
            'vyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" '
            'crossorigin="anonymous"></script>'
            "</html>\n"
        )

    def process(self, lines):
        """
        Choose the correct function to process the data
        """
        return "".join(self._process(lines))

    def _process(self, lines):
        """
        Process a chunk of text and return the corresponding HTML code.
        """
        yield '<table class="table table-striped" style="text-align:left">'

        if isinstance(lines, str):
            lines = lines.splitlines(True)

        for line in lines:
            for action in self.actions:
                line = action(line)
            yield line

        yield "</table>"


def convertFile(src, dst, show_line_no=False, line_prefix="L", plugins_function=[]):
    """
    Small helper to convert a text (ANSI) file to HTML.
    """
    import codecs
    from os.path import basename

    conv = XTerm2HTML(
        show_line_no=show_line_no,
        line_prefix=line_prefix,
        plugins_function=plugins_function,
    )
    with codecs.open(dst, "w", "utf-8") as dst_file, codecs.open(
        src, "r", "utf-8", "ignore"
    ) as src_file:
        dst_file.write(conv.head(title=basename(src)))
        dst_file.write(conv.process(src_file))
        dst_file.write(conv.tail())


class AddGitlabLinks:
    """
    Inject links to gitlab in a string.
    """

    def __init__(self):
        self.proj = None
        self._proj_sig = re.compile(
            r"checking out .* from "
            r"(?:https|ssh)://(?::@|git@)?gitlab.cern.ch(?::7999|:8443)?"
            r"/([a-zA-Z0-9-_.]+/[a-zA-Z0-9-_./]+).git",
        )
        self._mr_link = re.compile(r"([a-zA-Z0-9-_.]+/[a-zA-Z0-9-_./]+)!(\d+)")

        def mr_link_repl(matchobj):
            """
            re.sub function to add links to MRs
            """
            from gitlab import GitlabGetError

            from LbNightlyTools.Utils import getMRTitle

            try:
                title = getMRTitle(matchobj.group(1), int(matchobj.group(2)))
                if title:
                    title = escape(title, quote=True)
                    if not isinstance(title, str):
                        title = title.decode("utf-8", errors="replace")
                    return (
                        '<a href="https://gitlab.cern.ch/{0}/'
                        'merge_requests/{1}" data-toggle="tooltip" '
                        'title="{title}" target="_blank">{0}!{1}</a>'
                    ).format(*matchobj.groups(), title=title)
                else:
                    return (
                        '<a href="https://gitlab.cern.ch/{0}/'
                        'merge_requests/{1}" target="_blank">{0}!{1}</a>'
                    ).format(*matchobj.groups())
            except GitlabGetError:
                # the group/project!id match is invalid (e.g. no project found)
                # do not replace
                return matchobj.group(0)

        self._mr_link_repl = mr_link_repl

        self._commit_link = re.compile(r"\b([a-f0-9]{7,40})\b")
        self._commit_link_repl = r"\1"  # temporary value

    def __call__(self, line):
        if not self.proj:
            m = self._proj_sig.search(line)
            if m:
                self.proj = m.group(1)
                self._commit_link_repl = (
                    rf'<a href="https://gitlab.cern.ch/{self.proj}/commit/'
                    r'\1" target="_blank">\1</a>'
                )
        else:
            # replace group/Project!123 with link to merge request
            line = self._mr_link.sub(self._mr_link_repl, line)
            # replace commit ids with links to gitlab
            line = self._commit_link.sub(self._commit_link_repl, line)
        return line


# tests for special cases
def test_special_cases():
    """Test for Special Cases"""
    assert ANSIStyle("") == ANSIStyle(0, 0, 0)
    expected = (
        '<table class="table table-striped" style="text-align:left">'
        '<tr id="L1"><td><pre><span class="xterm-color-4">test</span>'
        # FIXME: it would be nice to avoid emitting empty tags
        '<span class="xterm-color-4 xterm-bgcolor-3"></span>'
        '<span class="xterm-color-2 xterm-bgcolor-3">blah</span>'
        '<span class="">blah</span></pre></td></tr></table>'
    )
    actual = XTerm2HTML().process(
        "\x1b[31m\x1b[34mtest" "\x1b[34;43m\x1b[32mblah\x1b[0mblah"
    )
    print("actual   ->", repr(actual))
    print("expected ->", repr(expected))
    assert actual == expected


if __name__ == "__main__":
    if "--convertFile" in sys.argv:
        src = sys.argv[sys.argv.index("--convertFile") + 1]
        plugin = []
        dest = src + ".html"
        convertFile(src, dest, show_line_no="--show-line-no" in sys.argv)
    else:
        conv = XTerm2HTML(
            show_line_no="--show-line-no" in sys.argv,
            plugins_function=[lambda line: str(line, "utf-8", "ignore")],
        )
        sys.stdout.write(conv.head(title="stdin"))
        sys.stdout.write(conv.process(sys.stdin).encode("utf8"))
        sys.stdout.write(conv.tail())
