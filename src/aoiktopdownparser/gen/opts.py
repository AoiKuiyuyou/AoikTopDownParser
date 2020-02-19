# coding: utf-8
from __future__ import absolute_import

from aoiktopdownparser.gen.opts_const import GS_BACKTRACKING_ON
from aoiktopdownparser.gen.opts_const import GS_CODE_POF
from aoiktopdownparser.gen.opts_const import GS_CODE_POF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_CODE_PRF
from aoiktopdownparser.gen.opts_const import GS_CODE_PRF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_RULE_FUNC_NAME_POF
from aoiktopdownparser.gen.opts_const import GS_RULE_FUNC_NAME_POF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_RULE_FUNC_NAME_PRF
from aoiktopdownparser.gen.opts_const import GS_RULE_FUNC_NAME_PRF_V_DFT


OPTS = {
    GS_BACKTRACKING_ON: 0,
    GS_CODE_PRF: GS_CODE_PRF_V_DFT,
    GS_CODE_POF: GS_CODE_POF_V_DFT,
    GS_RULE_FUNC_NAME_PRF: GS_RULE_FUNC_NAME_PRF_V_DFT,
    GS_RULE_FUNC_NAME_POF: GS_RULE_FUNC_NAME_POF_V_DFT,
}
