# coding: utf-8
from aoikdyndocdsl.ext.all import nto as nto_dft
from aoikdyndocdsl.ext.var import var
from aoikdyndocdsl.ext.var import var_set
from aoikdyndocdsl.ext.var import var_set_v2
from aoikdyndocdsl.parser.ext import iarg_psr
from functools import partial
import os.path


#
_FILE_READER_CACHE = {}

def file_reader(key, val, file_path=None, line_num=None):
    #
    if file_path is not None:
        file_path_2 = file_path
    else:
        prefix_1 = '/'
        prefix_1_len = len(prefix_1)

        prefix_2 = 'https://github.com/AoiKuiyuyou/AoikTopDownParserDemo/blob/0.1/'
        prefix_2_len = len(prefix_2)

        #
        if val.startswith(prefix_1):
            file_path_2 = val[prefix_1_len:]
        elif val.startswith(prefix_2):
            file_path_2 = val[prefix_2_len:]
            file_path_2 = '../AoikTopDownParserDemo/' + file_path_2
        else:
            assert 0, (key, val, file_path_2)

        assert file_path_2
    assert file_path_2

    #
    if line_num is None:
        file_path_2, sep, line_num = file_path_2.rpartition('#L')
        assert sep == '#L'
        line_num = int(line_num)

    assert file_path_2
    assert line_num is not None

    #
    file_path_2 = os.path.normpath(file_path_2)

    #
    txt = _FILE_READER_CACHE.get(file_path_2, None)

    if txt is None:
        file_obj = open(file_path_2)

        txt = file_obj.read()

        _FILE_READER_CACHE[file_path_2] = txt

    #
    return txt, line_num

#
v = var

vs = var_set

vs2 = iarg_psr(partial(var_set_v2, file_reader=file_reader))

#
def nto(name):
    obj = globals().get(name, None)

    if obj is None:
        obj = nto_dft(name)

    return obj
