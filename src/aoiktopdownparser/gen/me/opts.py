# coding: utf-8
from __future__ import absolute_import
from aoiktopdownparser.gen.opts_const import GS_CODE_POF
from aoiktopdownparser.gen.opts_const import GS_CODE_PRF
from aoiktopdownparser.gen.opts_const import GS_CTX_VAR
from aoiktopdownparser.gen.opts_const import GS_ENTRY
from aoiktopdownparser.gen.opts_const import GS_FUNC_POF
from aoiktopdownparser.gen.opts_const import GS_FUNC_PRF
from aoiktopdownparser.gen.opts_const import GS_REO_POF
from aoiktopdownparser.gen.opts_const import GS_REO_PRF
from aoiktopdownparser.gen.opts_const import GS_REP_VAR
from aoiktopdownparser.gen.opts_const import GS_RES_VAR
from aoiktopdownparser.gen.opts_const import GS_VER
from aoiktopdownparser.gen.opts_const import SS_CTX_K_NAME
from aoiktopdownparser.gen.opts_const import SS_CTX_K_PAR
from aoiktopdownparser.gen.opts_const import SS_CTX_K_REM
from aoiktopdownparser.gen.opts_const import SS_FILE_POF
from aoiktopdownparser.gen.opts_const import SS_FILE_PRF
from aoiktopdownparser.gen.opts_const import SS_IMPORTS_POF
from aoiktopdownparser.gen.opts_const import SS_IMPORTS_PRF
from aoiktopdownparser.gen.opts_const import SS_PSR_CLS_NAME
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNCS_POF
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNCS_PRF
from aoiktopdownparser.gen.opts_const import SS_WS_REP
from aoiktopdownparser.gen.opts_util import p
from aoiktopdownparser.version import __version__

#/
OPTS = {
    GS_VER: __version__,
    GS_REO_PRF: '',
    GS_REO_POF: '_REO',
    GS_FUNC_PRF: '',
    GS_FUNC_POF: '',
    GS_CTX_VAR: '_ctx',
    GS_RES_VAR: None,
    GS_REP_VAR: '_rep',
    GS_CODE_PRF: '#```\n',
    GS_CODE_POF: '\n#```',
    GS_ENTRY: 'all',
    SS_CTX_K_NAME: 'name',
    SS_CTX_K_PAR: 'par',
    SS_CTX_K_REM: 'rem',
    SS_PSR_CLS_NAME: 'Parser',
    SS_WS_REP: r"r'([\s]*(#[^\n]*)?)*'",
    SS_FILE_PRF: '',
    SS_FILE_POF: '',
    SS_IMPORTS_PRF: '',
    SS_IMPORTS_POF: p('ss_imports_pof.py'),
    SS_RULE_FUNCS_PRF: p('ss_rule_funcs_prf.py'),
    SS_RULE_FUNCS_POF: '',
}
