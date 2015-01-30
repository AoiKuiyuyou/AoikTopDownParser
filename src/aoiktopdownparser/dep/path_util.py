# coding: utf-8
from __future__ import absolute_import
import inspect
import os.path

#/
def caller_mod_file_path():
    frame=inspect.currentframe()
    frame=frame.f_back.f_back
    code=frame.f_code
    return code.co_filename

#/
def file_path_join(path1, path2):
    path1_abs = os.path.abspath(path1)

    path1_dir = os.path.dirname(path1_abs)

    path = os.path.join(path1_dir, path2)

    path = os.path.normpath(path)

    return path

#/
def file_path_me_join(path):
    #/
    me_path = caller_mod_file_path()

    #/
    res_path = file_path_join(me_path, path)

    #/
    return res_path
