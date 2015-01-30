# coding: utf-8
from __future__ import absolute_import
from path_util import file_path_join
import os.path

#/
def quote_add(txt):
    if not isinstance(txt, str):
        return repr(txt)
    if txt.endswith("'") or txt.endswith('"'):
        return txt
    else:
        return repr(txt)

q = quote_add

#/
class Value(object):

    def __init__(self, val):
        self.val = val

v = Value

#/
class Path(object):

    def __init__(self, path):
        self.path = path

#/
p = Path

#/
def path_to_asb(path, odf_find, opt_key):
    #/
    if os.path.isabs(path):
        return path

    #/
    odf_path = odf_find(opt_key)

    #/
    if odf_path is None:
        return None

    #/
    abs_path = file_path_join(odf_path, path)

    #/
    return abs_path

#/
def path_read(path, odf_find, opt_key):
    #/
    abs_path = path_to_asb(
        path=path,
        odf_find=odf_find,
        opt_key=opt_key,
    )

    #/
    res = open(abs_path).read()

    #/
    return res

#/
def read_repo(path):
    """ Read this repo's file specified by param "path".
    @param path: a path relative to this repo's "src/aoiktopdownparser" dir.
    """
    #/
    import aoiktopdownparser

    #/
    res_path = file_path_join(aoiktopdownparser.__file__, path)

    #/
    res = Path(res_path)

    #/
    return res

rr = read_repo
