# coding: utf-8
from __future__ import absolute_import

import sys


IS_PY2 = sys.version_info[0] == 2


def to_ustr(text):
    if IS_PY2:
        return text.decode('utf-8')
    else:
        return text


EMPTY_USTR = to_ustr('')

SPACE_USTR = to_ustr(' ')

NEWLINE_USTR = to_ustr('\n')
