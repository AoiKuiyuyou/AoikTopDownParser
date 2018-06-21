# coding: utf-8
from __future__ import absolute_import

import os.path


def join_file_paths(path1, path2):
    path1_abs = os.path.abspath(path1)

    path1_dir = os.path.dirname(path1_abs)

    path = os.path.join(path1_dir, path2)

    path = os.path.normpath(path)

    return path
