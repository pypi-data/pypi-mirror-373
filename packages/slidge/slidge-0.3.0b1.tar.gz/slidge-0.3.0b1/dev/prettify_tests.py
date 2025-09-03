"""
Prettify XML in slixmpp tests, using utidylib
"""

import re
from argparse import ArgumentParser
from pathlib import Path
from textwrap import indent

import tidy


def get_parser():
    parser = ArgumentParser()
    parser.add_argument("INPUT", nargs="*", help="Python file or dir to process")
    return parser


def main():
    args = get_parser().parse_args()
    for path in args.INPUT:
        path = Path(path)
        if path.is_file():
            process(path)
        else:
            for file in path.glob("**/*.py"):
                process(file)


def process(path: Path):
    content = path.read_text()
    pretty = re.sub(PATTERN, sub, content)
    new = []
    # remove useless language injection tags and place them at the right place
    for line in pretty.split("\n"):
        stripped = line.strip()
        if stripped in ("self.recv(", "self.send("):
            new.append(line.replace("# language=XML", "").rstrip() + "  # language=XML")
        else:
            new.append(line)
    new = "\n".join(new)
    if new != content:
        print(f"Prettyfying {path}")
        path.write_text(new)


def sub(match: re.Match):
    whole = match.group(0)
    lines = whole.lstrip(" \n").split("\n")
    first = lines[0][0]
    if first == "#" or first != '"':
        return whole
    line = lines[1 if len(lines) > 1 else 0].lstrip(" \n")
    if not line:
        return whole
    first_non_quote = line[0]
    if first_non_quote != "<":
        return whole
    return '"""\n' + indent(prettify(match.group(1)) + '"""', " " * 12)


def prettify(xml: str):
    r = str(
        tidy.parseString(
            xml,
            input_xml=True,
            indent_attributes=True,
            indent="auto",
            indent_spaces=2,
            # we don't want to wrap anything because whitespace
            # in tag text is meaningful
            wrap=10_000,
        )
    )
    lines = r.split("\n")
    return "\n".join(line.rstrip() for line in lines)


def strip_first_line(s: str):
    return "\n".join(s.split("\n")[1:])


PATTERN = re.compile(r'"""(.*?)"""', re.MULTILINE | re.DOTALL)


if __name__ == "__main__":
    main()
