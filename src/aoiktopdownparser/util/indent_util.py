# coding: utf-8
from __future__ import absolute_import


def add_indent(txt, step=1, indent=' ' * 4):
    prefix = indent * step
    return '\n'.join(prefix + x for x in txt.splitlines())
