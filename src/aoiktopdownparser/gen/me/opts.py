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
    SS_IMPORTS: """
from aoiktopdownparser.gen.ast import Code
from aoiktopdownparser.gen.ast import ExprOcc01
from aoiktopdownparser.gen.ast import ExprOcc0m
from aoiktopdownparser.gen.ast import ExprOcc1m
from aoiktopdownparser.gen.ast import ExprOr
from aoiktopdownparser.gen.ast import ExprSeq
from aoiktopdownparser.gen.ast import Pattern
from aoiktopdownparser.gen.ast import RuleDef
from aoiktopdownparser.gen.ast import RuleRef""",
    SS_WS_REP: r"r'([\s]*(#[^\n]*)?)*'",
}
