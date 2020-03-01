# coding: utf-8
from __future__ import absolute_import

from .str_util import NEWLINE_USTR
from .str_util import SPACE_USTR


def add_indent(txt, step=1, indent=SPACE_USTR * 4):
    lines = txt.splitlines()

    spaces_count = 0
    for line in lines:
        spaces_count = 0
        found = False
        for char in line:
            if char != SPACE_USTR:
                found = True
                break
            spaces_count += 1
        else:
            continue
        if found:
            break

    if spaces_count:
        new_lines = []
        for line in lines:
            new_line = line[spaces_count:]
            new_lines.append(new_line)
        lines = new_lines

    prefix = indent * step

    return NEWLINE_USTR.join(prefix + x for x in lines)
