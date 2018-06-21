# coding: utf-8
from __future__ import absolute_import

from collections import OrderedDict
import os.path
import sys

from ..util.exc_util import raise_
from ..util.indent_util import add_indent
from ..util.path_util import join_file_paths
from .opts_const import GS_BACKTRACKING_ON
from .opts_const import GS_PARSER_TPLT
from .opts_const import GS_PARSER_TPLT_V_DFT
from .opts_const import GS_RULE_FUNC_NAME_POF
from .opts_const import GS_RULE_FUNC_NAME_POF_V_DFT
from .opts_const import GS_RULE_FUNC_NAME_PRF
from .opts_const import GS_RULE_FUNC_NAME_PRF_V_DFT
from .opts_const import SS_BACKTRACKING_FUNCS
from .opts_const import SS_ENTRY_RULE
from .opts_const import SS_PRF
from .opts_const import SS_RULE_FUNC_NAME_POF
from .opts_const import SS_RULE_FUNC_NAME_PRF
from .opts_const import SS_RULE_FUNCS
from .opts_const import SS_RULE_REOS
from .opts_util import Path
from .opts_util import Value
from .opts_util import path_to_abs
from .opts_util import read_path


def get_parser_txt(rules, opts, find_odf):
    # `odf` means option-defining-file path.
    gs_tplt_odf = None

    gs_tplt = opts.get(GS_PARSER_TPLT, GS_PARSER_TPLT_V_DFT)

    tplt_data = None

    tplt_path = None

    if gs_tplt is GS_PARSER_TPLT_V_DFT:
        tplt_path = join_file_paths(__file__, 'parser_tplt.py')
    elif isinstance(gs_tplt, Value):
        tplt_data = gs_tplt.val
    elif isinstance(gs_tplt, (str, Path)):
        if isinstance(gs_tplt, str):
            tplt_path = gs_tplt
        elif isinstance(gs_tplt, Path):
            tplt_path = gs_tplt.path
        else:
            assert 0

        if os.path.isabs(tplt_path):
            pass
        else:
            rel_path = tplt_path

            tplt_path = None

            gs_tplt_odf = find_odf(GS_PARSER_TPLT)

            if gs_tplt_odf is None:
                msg = (
                    'Unable to find absolute path for relative template file'
                    ' path: `{}`'
                ).format(rel_path)

                raise ValueError(msg)

            tplt_path = path_to_abs(
                path=rel_path,
                find_odf=find_odf,
                opt_key=GS_PARSER_TPLT,
            )

            assert tplt_path is not None
    else:
        assert 0, gs_tplt

    if tplt_data is None:
        assert tplt_path is not None

        try:
            tplt_data = open(tplt_path).read()
        except Exception:
            msg = 'Failed reading template file: `{}`'.format(tplt_path)

            if gs_tplt_odf is not None:
                msg += (
                    '\nThe template file is specified by option `{0}`'
                    ' in file: `{1}`'
                ).format(
                    GS_PARSER_TPLT,
                    os.path.abspath(gs_tplt_odf),
                )

            raise_(ValueError(msg), tb=sys.exc_info()[2])

    #
    pattern_infos = set()

    for rule in rules:
        rule_pattern_infos = rule.get_pattern_infos()

        pattern_infos.update(rule_pattern_infos)

    pattern_infos = sorted(pattern_infos, key=(lambda x: (len(x[0]), x[0])))

    zfill_len = len(str(len(pattern_infos)))

    # Map pattern info to RE object name as parser class attribute
    to_reo_name = OrderedDict()

    for pattern_index, pattern_info in enumerate(pattern_infos):
        to_reo_name[pattern_info] = '_REO_{}'.format(
            str(pattern_index + 1).zfill(zfill_len)
        )

    # Map rule name to referring rules
    to_referring_rules = {}

    # Map rule name to first set of pattern infos
    to_first_set = {}

    # First set changed rule names
    changed_rule_names = set()

    for rule in rules:
        to_first_set[rule.name] = set()

        rule_refs = rule.get_rule_refs()

        for rule_ref in rule_refs:
            referring_rules = to_referring_rules.get(rule_ref)

            if referring_rules is None:
                referring_rules = to_referring_rules[rule_ref] = set()

            referring_rules.add(rule)

    for rule in rules:
        rule_first_set = rule.get_first_set(to_first_set)

        to_first_set[rule.name] = rule_first_set

        changed_rule_names.add(rule.name)

    while changed_rule_names:
        rule_name = changed_rule_names.pop()

        referring_rules = to_referring_rules.get(rule_name, None)

        if not referring_rules:
            continue

        for referring_rule in referring_rules:
            new_first_set = referring_rule.get_first_set(to_first_set)

            old_first_set = to_first_set[referring_rule.name]

            if new_first_set != old_first_set:
                to_first_set[referring_rule.name] = new_first_set

                changed_rule_names.add(referring_rule.name)

    #
    rule_func_txts = []

    # 4R6WO
    entry_rule_name = opts.get(SS_ENTRY_RULE, None)

    entry_rule = None

    for rule in rules:
        if entry_rule is None:
            if entry_rule_name:
                if rule.name == entry_rule_name:
                    entry_rule = rule

        rule_func_txt = rule.gen(to_reo_name, to_first_set, opts=opts)

        rule_func_txts.append(rule_func_txt)

    if entry_rule_name:
        if entry_rule is None:
            msg = 'Entry rule not found: `{}`.'.format(entry_rule_name)

            raise ValueError(msg)

    if entry_rule is None:
        entry_rule = rules[0]

    #
    map_ss_key_to_value = dict(
        x for x in opts.items() if x[0].startswith(SS_PRF)
    )

    #
    map_ss_key_to_value[SS_ENTRY_RULE] = entry_rule.name

    #
    rule_funcs_txt = '\n\n'.join(rule_func_txts)

    rule_funcs_txt = add_indent(rule_funcs_txt)

    map_ss_key_to_value[SS_RULE_FUNCS] = rule_funcs_txt

    #
    func_prf = opts.get(GS_RULE_FUNC_NAME_PRF, GS_RULE_FUNC_NAME_PRF_V_DFT)

    func_pof = opts.get(GS_RULE_FUNC_NAME_POF, GS_RULE_FUNC_NAME_POF_V_DFT)

    map_ss_key_to_value[SS_RULE_FUNC_NAME_PRF] = func_prf

    map_ss_key_to_value[SS_RULE_FUNC_NAME_POF] = func_pof

    #
    reo_txts = []

    for pattern_info, reo_name in to_reo_name.items():
        if pattern_info[1] == '0':
            reo_txt = '{0} = re.compile({1})'.format(
                reo_name,
                pattern_info[0],
            )
        else:
            reo_txt = '{0} = re.compile({1}, {2})'.format(
                reo_name,
                pattern_info[0],
                pattern_info[1],
            )

        reo_txts.append(reo_txt)

    map_ss_key_to_value[SS_RULE_REOS] = add_indent('\n'.join(reo_txts))

    #
    backtracking_on = opts.get(GS_BACKTRACKING_ON, None) == 1

    if backtracking_on:
        methods_file_path = join_file_paths(__file__, 'backtracking_funcs.py')

        methods_txt = open(methods_file_path).read()

        methods_txt = '\n' + add_indent(methods_txt) + '\n'

        map_ss_key_to_value[SS_BACKTRACKING_FUNCS] = methods_txt
    else:
        map_ss_key_to_value[SS_BACKTRACKING_FUNCS] = ''

    #
    parser_txt = replace_ss_keys(
        tplt_data, map_ss_key_to_value, find_odf=find_odf
    )

    return parser_txt


def replace_ss_keys(txt, spec, find_odf):
    for key, value in spec.items():
        if isinstance(value, Path):
            value = read_path(
                path=value.path,
                find_odf=find_odf,
                opt_key=key,
            )

        txt = txt.replace('{%s}' % key, value)

    return txt
