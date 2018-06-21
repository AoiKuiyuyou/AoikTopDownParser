# coding: utf-8
from __future__ import absolute_import

from aoiktopdownparser.gen.opts_const import GS_BACKTRACKING_ON
from aoiktopdownparser.gen.opts_const import GS_PARSER_TPLT
from aoiktopdownparser.gen.opts_const import SS_IMPORTS
from aoiktopdownparser.gen.opts_const import SS_WS_REP
from aoiktopdownparser.gen.opts_util import get_repo_file_path


OPTS = {
    GS_BACKTRACKING_ON: 0,
    GS_PARSER_TPLT: get_repo_file_path('gen/parser_tplt.py'),
    SS_IMPORTS: '',
    SS_WS_REP: r"r'\s*'",
}
