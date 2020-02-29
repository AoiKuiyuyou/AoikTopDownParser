# coding: utf-8
from __future__ import absolute_import

import json

from ..util.indent_util import add_indent
from ..util.path_util import join_file_paths
from .ast import EMPTY_PATTERN_INFO
from .ast import Code
from .ast import ExprSeq
from .ast import Pattern
from .opts_const import GS_BACKTRACKING_ON
from .opts_const import GS_RULE_FUNC_NAME_POF
from .opts_const import GS_RULE_FUNC_NAME_POF_V_DFT
from .opts_const import GS_RULE_FUNC_NAME_PRF
from .opts_const import GS_RULE_FUNC_NAME_PRF_V_DFT
from .opts_const import SS_BACKTRACKING_FUNCS
from .opts_const import SS_ENTRY_RULE
from .opts_const import SS_PRF
from .opts_const import SS_RULE_FIRST_SET_MAPPING
from .opts_const import SS_RULE_FOLLOW_SET_MAPPING
from .opts_const import SS_RULE_FUNC_NAME_POF
from .opts_const import SS_RULE_FUNC_NAME_PRF
from .opts_const import SS_RULE_FUNCS
from .opts_const import SS_RULE_REOS


def get_parser_txt(rules, tplt_text, opts):
    # A set of tuples.
    # Each tuple has two items.
    # The first item is the match pattern.
    # The second item is the match flag.
    pattern_infos = set()

    token_names = set()

    # Map pattern info to terminal token name
    to_token_name = {}

    for rule in rules:
        # Get pattern infos of the rule.
        # Container rules may have more than one pattern info.
        rule_pattern_infos = rule.get_pattern_infos()

        # Add to the total set.
        pattern_infos.update(rule_pattern_infos)

        # Get the only pattern of the rule.
        signle_pattern_item = get_single_pattern(rule.item)

        # If the rule has only one pattern.
        if signle_pattern_item is not None:
            pattern_info = next(iter(rule_pattern_infos))

            # Store the mapping from pattern info to terminal token name.
            to_token_name[pattern_info] = rule.name

            # Store the terminal token name.
            token_names.add(rule.name)

    # A list of pattern infos that are not the only one for a rule.
    unnamed_pattern_infos = []

    for pattern_info in sorted(
        pattern_infos, key=lambda x: (len(x[0]), x[0])
    ):
        token_name = to_token_name.get(pattern_info, None)

        if token_name is None:
            unnamed_pattern_infos.append(pattern_info)

    zfill_len = 1

    is_zfill_len_found = False

    while True:
        pattern_number = 0

        for pattern_info in unnamed_pattern_infos:
            while True:
                pattern_number += 1

                token_name = '_token_{}'.format(
                    str(pattern_number).zfill(zfill_len)
                )

                if token_name not in token_names:
                    break

            if is_zfill_len_found:
                to_token_name[pattern_info] = token_name

        if is_zfill_len_found:
            break

        new_zfill_len = len(str(pattern_number))

        if new_zfill_len > zfill_len:
            zfill_len = new_zfill_len
        else:
            is_zfill_len_found = True

    # Map rule name to rule def.
    to_rule = {}

    # Map rule name to referring rule def.
    to_referring_rules = {}

    # Map rule name to first set.
    # The set is a set of pattern infos.
    to_first_set = {}

    # A set of rule names whose first set have changed.
    changed_rule_names = set()

    for rule in rules:
        # Store the mapping from rule name to rule def.
        to_rule[rule.name] = rule

        to_first_set[rule.name] = set()

        referred_rule_names = rule.get_rule_refs()

        for referred_rule_name in referred_rule_names:
            referring_rules = to_referring_rules.get(referred_rule_name)

            if referring_rules is None:
                referring_rules = to_referring_rules[referred_rule_name] \
                    = set()

            referring_rules.add(rule)

    # Calculate rules' first set.
    for rule in rules:
        rule_first_set = rule.calc_first_set(to_first_set)

        to_first_set[rule.name] = rule_first_set

        changed_rule_names.add(rule.name)

    while changed_rule_names:
        rule_name = changed_rule_names.pop()

        referring_rules = to_referring_rules.get(rule_name, None)

        if not referring_rules:
            continue

        for referring_rule in referring_rules:
            new_first_set = referring_rule.calc_first_set(to_first_set)

            old_first_set = to_first_set[referring_rule.name]

            if new_first_set != old_first_set:
                to_first_set[referring_rule.name] = new_first_set

                changed_rule_names.add(referring_rule.name)

    # Calculate rules' follow set.
    #
    # A set of rule names whose follow set have changed.
    changed_rule_names = {x.name for x in rules}

    while True:
        while changed_rule_names:
            rule_name = changed_rule_names.pop()

            rule = to_rule[rule_name]

            rule.calc_follow_set(set(), to_first_set, to_rule)

        for rule in rules:
            if rule.is_follow_set_changed:
                rule.is_follow_set_changed = False

                changed_rule_names.add(rule.name)

        if not changed_rule_names:
            break

    to_first_set_token_names = {}

    to_follow_set_token_names = {}

    for rule in rules:
        rule_first_set = to_first_set[rule.name]

        first_set_token_names = [to_token_name[x] for x in rule_first_set if x != EMPTY_PATTERN_INFO]

        first_set_token_names.sort()

        to_first_set_token_names[rule.name] = first_set_token_names

        follow_set_token_names = [to_token_name[x] for x in rule.get_follow_set()]
        follow_set_token_names.sort()

        to_follow_set_token_names[rule.name] = follow_set_token_names

    #
    rule_func_txts = []

    entry_rule_name = opts.get(SS_ENTRY_RULE, None)

    entry_rule = None

    for rule in rules:
        if entry_rule is None:
            if entry_rule_name:
                if rule.name == entry_rule_name:
                    entry_rule = rule

        rule_func_txt = rule.gen(to_token_name, to_first_set, opts=opts)

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
    first_set_mapping_text = json.dumps(
        to_first_set_token_names,
        ensure_ascii=False,
        indent=4,
        sort_keys=True,
    )

    first_set_mapping_text = 'TO_FIRST_SET = {0}'.format(
        first_set_mapping_text
    )

    map_ss_key_to_value[SS_RULE_FIRST_SET_MAPPING] = first_set_mapping_text

    #
    follow_set_mapping_text = json.dumps(
        to_follow_set_token_names,
        ensure_ascii=False,
        indent=4,
        sort_keys=True,
    )

    follow_set_mapping_text = 'TO_FOLLOW_SET = {0}'.format(
        follow_set_mapping_text
    )

    map_ss_key_to_value[SS_RULE_FOLLOW_SET_MAPPING] = follow_set_mapping_text

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

    token_name_to_pattern_info = {}

    for pattern_info, token_name in to_token_name.items():
        token_name_to_pattern_info[token_name] = pattern_info

    for rule in rules:
        token_name = rule.name

        pattern_info = token_name_to_pattern_info.get(token_name)

        if pattern_info is None:
            continue

        if pattern_info[1] == u'0':
            reo_txt = u'(\'{0}\', re.compile({1})),'.format(
                token_name,
                pattern_info[0],
            )
        else:
            reo_txt = u'(\'{0}\', re.compile({1}, {2})),'.format(
                token_name,
                pattern_info[0],
                pattern_info[1],
            )

        reo_txts.append(reo_txt)

    reos_txt = u'_TOKEN_NAME_TO_REGEX_OBJ = OrderedDict([\n{0}\n])\n'.format(
        add_indent('\n'.join(reo_txts))
    )
    reos_txt = add_indent(reos_txt)

    map_ss_key_to_value[SS_RULE_REOS] = reos_txt

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
    parser_txt = replace_ss_keys(tplt_text, map_ss_key_to_value)

    #
    lines = []

    for line in parser_txt.split('\n'):
        line = line.rstrip(' \t')
        lines.append(line)

    parser_txt = '\n'.join(lines)

    return parser_txt


def get_single_pattern(item):
    if isinstance(item, Pattern):
        return item

    if isinstance(item, ExprSeq):
        single_pattern_item = None

        for child_item in item.items:
            if isinstance(child_item, Pattern):
                if single_pattern_item is not None:
                    single_pattern_item = None

                    break
                else:
                    single_pattern_item = child_item
            elif not isinstance(child_item, Code):
                single_pattern_item = None

                break

        return single_pattern_item

    return None


def replace_ss_keys(txt, spec):
    for key, value in spec.items():
        txt = txt.replace('{%s}' % key, value)

    return txt
