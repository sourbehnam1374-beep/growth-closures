#!/usr/bin/env python3
"""Reject trust-expanding Lean tokens outside comments and strings.

Lean accepts ``sorry`` with a diagnostic, so compilation alone is not a
sufficient CI gate. This scanner understands nested block comments, line
comments and escaped string literals before looking for forbidden tokens.
"""

from __future__ import annotations

import pathlib
import re
import sys

FORBIDDEN = re.compile(r"\b(?:sorry|admit)\b|\bClassical\.choice\b")


def executable_text(source: str) -> str:
    out: list[str] = []
    index = 0
    block_depth = 0
    in_line_comment = False
    in_string = False
    escaped = False
    while index < len(source):
        pair = source[index : index + 2]
        char = source[index]
        if in_line_comment:
            if char == "\n":
                in_line_comment = False
                out.append("\n")
            else:
                out.append(" ")
            index += 1
            continue
        if block_depth:
            if pair == "/-":
                block_depth += 1
                out.extend("  ")
                index += 2
            elif pair == "-/":
                block_depth -= 1
                out.extend("  ")
                index += 2
            else:
                out.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if in_string:
            out.append("\n" if char == "\n" else " ")
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if pair == "--":
            in_line_comment = True
            out.extend("  ")
            index += 2
        elif pair == "/-":
            block_depth = 1
            out.extend("  ")
            index += 2
        elif char == '"':
            in_string = True
            out.append(" ")
            index += 1
        else:
            out.append(char)
            index += 1
    if block_depth:
        raise ValueError("unclosed Lean block comment")
    if in_string:
        raise ValueError("unclosed Lean string literal")
    return "".join(out)


def verify(path: pathlib.Path) -> list[str]:
    code = executable_text(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for match in FORBIDDEN.finditer(code):
        line = code.count("\n", 0, match.start()) + 1
        failures.append(f"{path}:{line}: forbidden token {match.group(0)!r}")
    return failures


def main() -> int:
    paths = sorted(pathlib.Path("lean").rglob("*.lean"))
    if not paths:
        print("LEAN SOURCE HYGIENE: FAIL (no Lean sources found)")
        return 1
    failures = [failure for path in paths for failure in verify(path)]
    if failures:
        print("\n".join(failures))
        print(f"LEAN SOURCE HYGIENE: FAIL ({len(failures)} finding(s))")
        return 1
    print(f"LEAN SOURCE HYGIENE: PASS ({len(paths)} source file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
