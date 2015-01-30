# coding: utf-8
from __future__ import absolute_import
from aoiktopdownparser.gen.opts_const import GS_TPLT
from aoiktopdownparser.gen.opts_const import GS_VER
from aoiktopdownparser.gen.opts_const import SS_CTX_K_NAME
from aoiktopdownparser.gen.opts_const import SS_CTX_K_PAR
from aoiktopdownparser.gen.opts_const import SS_CTX_K_REM
from aoiktopdownparser.gen.opts_const import SS_FILE_POF
from aoiktopdownparser.gen.opts_const import SS_FILE_PRF
from aoiktopdownparser.gen.opts_const import SS_IMPORTS_POF
from aoiktopdownparser.gen.opts_const import SS_IMPORTS_PRF
from aoiktopdownparser.gen.opts_const import SS_INIT_CALL_KARGS_POF
from aoiktopdownparser.gen.opts_const import SS_INIT_CALL_KARGS_PRF
from aoiktopdownparser.gen.opts_const import SS_INIT_CALL_PARGS_POF
from aoiktopdownparser.gen.opts_const import SS_INIT_CALL_PARGS_PRF
from aoiktopdownparser.gen.opts_const import SS_INIT_FUNC_END
from aoiktopdownparser.gen.opts_const import SS_INIT_FUNC_KARGS_POF
from aoiktopdownparser.gen.opts_const import SS_INIT_FUNC_KARGS_PRF
from aoiktopdownparser.gen.opts_const import SS_INIT_FUNC_PARGS_POF
from aoiktopdownparser.gen.opts_const import SS_INIT_FUNC_PARGS_PRF
from aoiktopdownparser.gen.opts_const import SS_PARSE_FUNC_END
from aoiktopdownparser.gen.opts_const import SS_PSR_CLS_NAME
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNCS_POF
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNCS_PRF
from aoiktopdownparser.gen.opts_const import SS_WS_REP
from aoiktopdownparser.gen.opts_util import rr
from aoiktopdownparser.version import __version__

#/
OPTS = {
    GS_VER: __version__,
    GS_TPLT: rr('gen/parser_tplt.py'),
    SS_CTX_K_NAME: 'name',
    SS_CTX_K_PAR: 'par',
    SS_CTX_K_REM: 'rem',
    SS_PSR_CLS_NAME: 'Parser',
    SS_WS_REP: r"r'\s*'",
    SS_FILE_PRF: '',
    SS_FILE_POF: '',
    SS_IMPORTS_PRF: '',
    SS_IMPORTS_POF: '',
    SS_RULE_FUNCS_PRF: '',
    SS_RULE_FUNCS_POF: '',
    SS_INIT_FUNC_PARGS_PRF: '',
    SS_INIT_FUNC_PARGS_POF: '',
    SS_INIT_FUNC_KARGS_PRF: '',
    SS_INIT_FUNC_KARGS_POF: '',
    SS_INIT_FUNC_END: '',
    SS_INIT_CALL_PARGS_PRF: '',
    SS_INIT_CALL_PARGS_POF: '',
    SS_INIT_CALL_KARGS_PRF: '',
    SS_INIT_CALL_KARGS_POF: '',
    SS_PARSE_FUNC_END: '',
}
