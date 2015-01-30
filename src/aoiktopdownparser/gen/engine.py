# coding: utf-8
from __future__ import absolute_import
from aoikexcutil import raise_
from aoikindentutil import indent_add
from aoiktopdownparser.gen.ast import Code
from aoiktopdownparser.gen.ast import ExprSeq
from aoiktopdownparser.gen.ast import Pattern
from aoiktopdownparser.gen.opts_const import GS_ENTRY
from aoiktopdownparser.gen.opts_const import GS_ENTRY_V_DFT
from aoiktopdownparser.gen.opts_const import GS_FUNC_POF
from aoiktopdownparser.gen.opts_const import GS_FUNC_POF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_FUNC_PRF
from aoiktopdownparser.gen.opts_const import GS_FUNC_PRF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_TPLT
from aoiktopdownparser.gen.opts_const import GS_TPLT_V_DFT
from aoiktopdownparser.gen.opts_const import SS_ENTRY_RULE
from aoiktopdownparser.gen.opts_const import SS_PRF
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNCS
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNC_POF
from aoiktopdownparser.gen.opts_const import SS_RULE_FUNC_PRF
from aoiktopdownparser.gen.opts_util import Path
from aoiktopdownparser.gen.opts_util import Value
from aoiktopdownparser.gen.opts_util import path_read
from aoiktopdownparser.gen.opts_util import path_to_asb
from aoiktopdownparser.gen.opts_util import quote_add
from path_util import file_path_me_join
import os.path
import sys

#/
def sub(txt, spec, odf_find):
    #/
    for key, val in spec.items():
        #/
        if isinstance(val, Path):
            #/
            val = path_read(
                path=val.path,
                odf_find=odf_find,
                opt_key=key,
            )

        #/
        txt = txt.replace('{%s}'%key, val)

    #/
    return txt

#/
def expr_is_pattern(expr):
    #/
    if isinstance(expr, Pattern):
        return True

    #/
    if not isinstance(expr, ExprSeq):
        return False

    #/ find if there is one and only one Pattern item in this seq
    ##  with optional Code items
    patt_item = None

    for item in expr.items:
        #/
        if isinstance(item, Pattern):
            #/ if met the first pattern in this seq
            if patt_item is None:
                patt_item = item
            #/ if met the second pattern in this seq
            else:
                patt_item = None
                break
        else:
            #/ if met a non-Code item
            if not isinstance(item, Code):
                patt_item = None
                break

    #/
    return patt_item is not None

#/
def gen(rules, opts, odf_find):
    """
    @odf_find: "odf" find function.
    "odf" means the option-defining file's path.
    If the option value is a relative path, the path found is used as base path.
    """
    #/
    gs_tplt_odf = None

    #/
    gs_tplt = opts.get(GS_TPLT, GS_TPLT_V_DFT)

    tplt_data = None

    tplt_path = None

    #/ if it is not specified
    if gs_tplt is GS_TPLT_V_DFT:
        #/
        tplt_path = file_path_me_join('parser_tplt.py')
    #/ if it is specified as data
    elif isinstance(gs_tplt, Value):
        #/
        tplt_data = gs_tplt.val

    #/ if it is specified as path
    ## We consider str type as path, not data.
    elif isinstance(gs_tplt, (str, Path)):
        #/
        if isinstance(gs_tplt, str):
            #/
            tplt_path = gs_tplt
        elif isinstance(gs_tplt, Path):
            #/
            tplt_path = gs_tplt.path
        else:
            assert 0

        #/
        if os.path.isabs(tplt_path):
            pass
            #tplt_path = tplt_path
        else:
            #/
            rel_path = tplt_path

            tplt_path = None

            #/
            gs_tplt_odf = odf_find(GS_TPLT)

            #/
            if gs_tplt_odf is None:
                #/
                msg = (
                    'Unable to resolve relative template file path'
                    ' into absolute one.\n'
                    'Template file path is: |{}|'
                ).format(rel_path)

                raise ValueError(msg)

            #/
            tplt_path = path_to_asb(
                path=rel_path,
                odf_find=odf_find,
                opt_key=GS_TPLT,
            )

            assert tplt_path is not None
    #/
    else:
        assert 0, gs_tplt

    #/
    if tplt_data is None:
        #/
        assert tplt_path is not None

        #/
        try:
            #/
            tplt_data = open(tplt_path).read()
        #/
        except Exception:
            #/
            msg = 'Failed reading template file: |{}|'.format(tplt_path)

            #/
            if gs_tplt_odf is not None:
                msg += (
                    '\nThe template file is specified by option {GS_TPLT}'
                    ' in file: |{gs_tplt_odf}|'
                ).format(
                     GS_TPLT=GS_TPLT,
                     gs_tplt_odf=os.path.abspath(gs_tplt_odf),
                )

            #/
            raise_(ValueError(msg), tb=sys.exc_info()[2])

    #/
    ss_d = dict(x for x in opts.items() if x[0].startswith(SS_PRF))

    #/
    txt_s = []

    #/ 4r6wOwv
    entry_rule_name = opts.get(GS_ENTRY, GS_ENTRY_V_DFT)

    entry_rule = None
    for rule in rules:
        if entry_rule is None:
            if entry_rule_name:
                if entry_rule_name == rule.name:
                    entry_rule = rule
            else:
                if not expr_is_pattern(rule.expr):
                    entry_rule = rule
        txt = rule.gen(opts=opts)
        txt_s.append(txt)

    #/
    if entry_rule_name:
        if entry_rule is None:
            raise ValueError('Entry rule not found.\nRule name is |{}|.'.format(entry_rule_name))

    #/ this happens if no non-term rules.
    ## use the first term rule instead.
    if entry_rule is None:
        entry_rule = rules[0]

    #/
    ss_d[SS_ENTRY_RULE] = entry_rule.name

    #/
    rule_funcs_txt = '\n\n'.join(txt_s)

    rule_funcs_txt = indent_add(rule_funcs_txt)

    ss_d[SS_RULE_FUNCS] = rule_funcs_txt

    #/
    func_prf = opts.get(GS_FUNC_PRF, GS_FUNC_PRF_V_DFT)

    func_pof = opts.get(GS_FUNC_POF, GS_FUNC_POF_V_DFT)

    ss_d[SS_RULE_FUNC_PRF] = quote_add(func_prf)

    ss_d[SS_RULE_FUNC_POF] = quote_add(func_pof)

    #/
    res = sub(tplt_data, ss_d, odf_find=odf_find)

    #/ substitute the second time because included sub templates have variables
    res = sub(res, ss_d, odf_find=odf_find)

    #/
    return res
