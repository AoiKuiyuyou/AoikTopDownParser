# coding: utf-8
from __future__ import absolute_import

import os.path

from ..util.path_util import join_file_paths


class Value(object):

    def __init__(self, val):
        self.val = val


class Path(object):

    def __init__(self, path):
        self.path = path


def get_repo_file_path(path):
    import aoiktopdownparser

    res_path = join_file_paths(aoiktopdownparser.__file__, path)

    return res_path


def path_to_abs(path, find_odf, opt_key):
    if os.path.isabs(path):
        return path

    odf_path = find_odf(opt_key)

    if odf_path is None:
        return None

    abs_path = join_file_paths(odf_path, path)

    return abs_path


def read_path(path, find_odf, opt_key):
    abs_path = path_to_abs(
        path=path,
        find_odf=find_odf,
        opt_key=opt_key,
    )

    res = open(abs_path).read()

    return res
