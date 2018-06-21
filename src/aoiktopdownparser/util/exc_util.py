# coding: utf-8
from __future__ import absolute_import

import sys


IS_PY2 = sys.version_info[0] == 2


# define `exec_` and `raise_` that are 2*3 compatible.
#
# Modified from |six|:
# https://bitbucket.org/gutworth/six/src/e5218c3f66a2614acb7572204a27e2b508682168/six.py?at=1.10.0#six.py-678
#
# ----- BEG -----
if IS_PY2:
    def exec_(_code_, _globs_=None, _locs_=None):
        """Execute code in a namespace."""
        if _globs_ is None:
            frame = sys._getframe(1)
            _globs_ = frame.f_globals
            if _locs_ is None:
                _locs_ = frame.f_locals
            del frame
        elif _locs_ is None:
            _locs_ = _globs_
        exec("""exec _code_ in _globs_, _locs_""")

    exec_("""def raise_(exc, tb=None):
    raise exc, None, tb
""")
else:
    exec_ = eval('exec')

    def raise_(exc, tb=None):
        if tb is not None and exc.__traceback__ is not tb:
            raise exc.with_traceback(tb)
        else:
            raise exc
# ----- END -----
