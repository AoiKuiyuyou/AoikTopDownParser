# coding: utf-8
from __future__ import absolute_import

import re
import sys

from ..util.indent_util import add_indent
from .opts_const import GS_BACKTRACKING_ON
from .opts_const import GS_CODE_POF
from .opts_const import GS_CODE_POF_V_DFT
from .opts_const import GS_CODE_PRF
from .opts_const import GS_CODE_PRF_V_DFT
from .opts_const import GS_RULE_FUNC_NAME_POF
from .opts_const import GS_RULE_FUNC_NAME_POF_V_DFT
from .opts_const import GS_RULE_FUNC_NAME_PRF
from .opts_const import GS_RULE_FUNC_NAME_PRF_V_DFT


EMPTY_PATTERN_INFO = ("''", '0')

EMPTY_PATTERN_INFOS = [
    ("''", '0'),
    ('""', '0'),
    ("r''", '0'),
    ('r""', '0'),
    ("''''''", '0'),
    ('""""""', '0'),
    ("r''''''", '0'),
    ('r""""""', '0'),
]


class GrammarError(Exception):
    pass


class AstNode(object):

    def __init__(self):
        # Items are pattern infos.
        # A pattern info is tuple of (_RE_PATTERN_, _RE_FLAGS_STR_).
        self.first_set = set()

        self.follow_set = set()

    def get_pattern_infos(self):
        raise NotImplementedError()

    def get_rule_refs(self):
        raise NotImplementedError()

    def get_first_set(self):
        return self.first_set

    def calc_first_set(self, to_first_set):
        raise NotImplementedError()

    def get_follow_set(self):
        return self.follow_set

    def add_follow_set(self, follow_set):
        assert not has_empty_pattern_info(follow_set)
        self.follow_set.update(follow_set)

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        raise NotImplementedError()

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        """
        @param to_token_name: Map pattern info to token name.
        Pattern info is a tuple of (_RE_PATTERN_, _RE_FLAGS_STR_).

        @param to_first_set: Map rule name to first set.

        @param opts: Options dict.
        """
        raise NotImplementedError()


class Pattern(AstNode):

    ARG_K_FLAGS = 'flags'

    def __init__(self, pattern, args=None):
        super(Pattern, self).__init__()

        self.pattern = pattern

        self.args = args if args is not None else {}

        self.flags_str = self.args.get(Pattern.ARG_K_FLAGS, '0')

        assert re

        # `flags_str` can be like `re.VERBOSE | re.IGNORECASE`
        self.flags = eval(self.flags_str)

    def get_pattern_infos(self):
        return {(self.pattern, self.flags_str)}

    def get_rule_refs(self):
        return set()

    def calc_first_set(self, to_first_set):
        self.first_set = {(self.pattern, self.flags_str)}

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        # The follow set is not used.
        self.follow_set = None

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        name = kwargs.get('name', None)

        res = '{res_name} = self._scan_token(\'{token_name}\')  # noqa'.format(
            res_name=name or '_',
            token_name=to_token_name[(self.pattern, self.flags_str)],
        )

        return res


class Code(AstNode):

    def __init__(self, code):
        super(Code, self).__init__()

        self.code = code.rstrip()

        if self.code.startswith('\n'):
            self.code = self.code[1:]

    def get_pattern_infos(self):
        return set()

    def get_rule_refs(self):
        return set()

    def calc_first_set(self, to_first_set):
        self.first_set = {EMPTY_PATTERN_INFO}

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        # The follow set is not used.
        self.follow_set = None

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        res = self.code

        res = add_indent(res, 0)

        code_prf = opts.get(GS_CODE_PRF, GS_CODE_PRF_V_DFT)

        if code_prf:
            res = code_prf + res

        code_pof = opts.get(GS_CODE_POF, GS_CODE_POF_V_DFT)

        if code_pof:
            res = res + code_pof

        return res


class RuleDef(AstNode):

    def __init__(self, name, item, args=None):
        super(RuleDef, self).__init__()

        self.name = name

        self.args = args

        self.item = item

        self.is_follow_set_changed = False

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def calc_first_set(self, to_first_set):
        self.first_set = set(self.item.calc_first_set(to_first_set))

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        self.add_follow_set(follow_set)

        self.item.calc_follow_set(
            self.get_follow_set(), to_first_set, to_rule_def
        )

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        func_prf = opts.get(GS_RULE_FUNC_NAME_PRF, GS_RULE_FUNC_NAME_PRF_V_DFT)

        func_pof = opts.get(GS_RULE_FUNC_NAME_POF, GS_RULE_FUNC_NAME_POF_V_DFT)

        func_def_fmt = 'def {func_prf}{name}{func_pof}(self, ctx):'

        func_def_txt = func_def_fmt.format(
            func_prf=func_prf,
            name=self.name,
            func_pof=func_pof,
        )

        # If the expression is a pattern or a sequence containing a single
        # pattern and optionally codes, generate output like this:
        # `_RULE_NAME_ = self._scan_token('number')`, i.e. the result variable
        # name will be the rule name. Otherwise the result variable name will
        # be `_`.
        if isinstance(self.item, Pattern):
            func_body_txt = self.item.gen(
                to_token_name,
                to_first_set,
                opts=opts,
                name=self.name,
            )
        else:
            single_pattern_item = None

            if isinstance(self.item, SeqExpr):
                seq_txts = []

                for item in self.item.items:
                    if isinstance(item, Pattern):
                        # If have more than one pattern in this rule
                        if single_pattern_item is not None:
                            single_pattern_item = None

                            break

                        single_pattern_item = item

                        seq_txt = item.gen(
                            to_token_name,
                            to_first_set,
                            opts=opts,
                            name=self.name,
                        )

                        seq_txts.append(seq_txt)
                    else:
                        if isinstance(item, Code):
                            seq_txt = item.gen(
                                to_token_name, to_first_set, opts=opts
                            )
                            seq_txts.append(seq_txt)
                        else:
                            single_pattern_item = None

                            break

            if single_pattern_item is not None:
                func_body_txt = '\n'.join(seq_txts)
            else:
                func_body_txt = self.item.gen(
                    to_token_name,
                    to_first_set,
                    opts=opts
                )

        res = func_def_txt + '\n' + add_indent(func_body_txt)

        return res


class RuleRef(AstNode):

    def __init__(self, name):
        super(RuleRef, self).__init__()

        self.name = name

    def get_pattern_infos(self):
        return set()

    def get_rule_refs(self):
        return {self.name}

    def calc_first_set(self, to_first_set):
        first_set = to_first_set.get(self.name, None)

        if first_set is None:
            msg = 'Undefined rule name: `{0}`.'.format(self.name)

            raise GrammarError(msg)

        self.first_set = first_set

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        rule_def = to_rule_def.get(self.name, None)

        if rule_def is None:
            msg = 'Undefined rule name: `{0}`.'.format(self.name)

            raise GrammarError(msg)

        if rule_def.is_follow_set_changed:
            rule_def.add_follow_set(follow_set)
        else:
            old_set_count = len(rule_def.get_follow_set())

            rule_def.add_follow_set(follow_set)

            new_set_count = len(rule_def.get_follow_set())

            rule_def.is_follow_set_changed = new_set_count != old_set_count

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        res = "{name} = self._scan_rule('{name}')  # noqa".format(
            name=self.name,
        )

        return res


class SeqExpr(AstNode):

    def __init__(self, items):
        super(SeqExpr, self).__init__()

        assert len(items) > 1
        self.items = items

    def get_pattern_infos(self):
        pattern_infos = set()

        for item in self.items:
            item_pattern_infos = item.get_pattern_infos()

            pattern_infos.update(item_pattern_infos)

        return pattern_infos

    def get_rule_refs(self):
        rule_refs = set()

        for item in self.items:
            item_rule_refs = item.get_rule_refs()

            rule_refs.update(item_rule_refs)

        return rule_refs

    def calc_first_set(self, to_first_set):
        for item in self.items:
            item.calc_first_set(to_first_set)

        first_set = set()

        for item in self.items:
            item_first_set = item.get_first_set()

            has_empty_pattern = add_nonempty_pattern_infos(
                first_set, item_first_set
            )

            if has_empty_pattern:
                continue

            break
        else:
            first_set.add(EMPTY_PATTERN_INFO)

        self.first_set = first_set

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        self.add_follow_set(follow_set)

        items_count = len(self.items)

        for item_index in range(items_count):
            item = self.items[item_index]

            item_follow_set = set()

            for later_item_index in range(item_index + 1, items_count):
                later_item = self.items[later_item_index]

                later_item_first_set = later_item.get_first_set()

                has_empty_pattern = add_nonempty_pattern_infos(
                    item_follow_set, later_item_first_set
                )

                if not has_empty_pattern:
                    break
            else:
                item_follow_set.update(self.get_follow_set())

            item.calc_follow_set(item_follow_set, to_first_set, to_rule_def)

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        txts = []

        for item in self.items:
            txt = item.gen(to_token_name, to_first_set, opts=opts)

            txts.append(txt)

        res = '\n'.join(txts)

        return res


class AltExpr(AstNode):

    def __init__(self, items):
        super(AltExpr, self).__init__()

        assert len(items) > 1
        self.items = items

    def get_pattern_infos(self):
        pattern_infos = set()

        for item in self.items:
            item_pattern_infos = item.get_pattern_infos()

            pattern_infos.update(item_pattern_infos)

        return pattern_infos

    def get_rule_refs(self):
        rule_refs = set()

        for item in self.items:
            item_rule_refs = item.get_rule_refs()

            rule_refs.update(item_rule_refs)

        return rule_refs

    def calc_first_set(self, to_first_set):
        first_set = set()

        for item in self.items:
            item_first_set = item.calc_first_set(to_first_set)

            first_set.update(item_first_set)

        self.first_set = first_set

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        self.add_follow_set(follow_set)

        new_follow_set = self.get_follow_set()

        for item in self.items:
            item.calc_follow_set(new_follow_set, to_first_set, to_rule_def)

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        txts = []

        backtracking_on = opts.get(GS_BACKTRACKING_ON, None) == 1

        if backtracking_on:
            # E.g.
            # ```
            # self._or()
            # try:
            #     self._ori()
            #     try:
            #         ...
            #     except SyntaxError: self._ori(0)
            #     else: self._ori(1)
            #     self._ori()
            #     try:
            #         ...
            #     except SyntaxError: self._ori(0)
            #     else: self._ori(1)
            # except ScanOk: self._or(1)
            # else: self._or(0)
            # ```

            for item in self.items:
                txts.append(r'self._ori()')
                txts.append(r'try:')

                item_txt = item.gen(to_token_name, to_first_set, opts=opts)

                txts.append(add_indent(item_txt))

                txts.append(r'except SyntaxError: self._ori(0)')
                txts.append(r'else: self._ori(1)')

            res = '\n'.join(txts)

            res = 'self._or()\n' +\
                  'try:\n' + add_indent(res) \
                  + '\nexcept ScanOk: self._or(1)' \
                  + '\nelse: self._or(0)'
        else:
            nullable_item_infos = []

            met_pattern_infos = set()

            is_first_item = True

            is_branches_disjoint = True

            for item in self.items:
                item_first_set = item.get_first_set()

                if has_empty_pattern_info(item_first_set):
                    nullable_item_infos.append((item, item_first_set))

                    continue

                if item_first_set & met_pattern_infos:
                    is_branches_disjoint = False

                peek_args_txt = get_peek_args_txt(
                    item_first_set, to_token_name
                )

                txt = '{0} self._peek({1}{2}):'.format(
                    'if' if is_first_item else 'elif',
                    peek_args_txt,
                    '' if is_first_item else ', is_branch=True',
                )

                txts.append(txt)

                item_txt = item.gen(to_token_name, to_first_set, opts=opts)

                txts.append(add_indent(item_txt))

                is_first_item = False

                met_pattern_infos.update(item_first_set)

            for item, item_first_set in nullable_item_infos:
                item_first_set = get_nonempty_pattern_infos(item_first_set)

                union_set = set(item_first_set)

                follow_set = self.get_follow_set()

                if not follow_set:
                    txt = '{0} True:'.format('if' if is_first_item else 'elif')
                else:
                    union_set.update(follow_set)

                    peek_args_txt = get_peek_args_txt(union_set, to_token_name)

                    txt = '{0} self._peek({1}{2}):'.format(
                        'if' if is_first_item else 'elif',
                        peek_args_txt,
                        '' if is_first_item else ', is_branch=True',
                    )

                txts.append(txt)

                item_txt = item.gen(
                    to_token_name, to_first_set, opts=opts, is_in_expror=True
                )

                txts.append(add_indent(item_txt))

                is_first_item = False

                if union_set & met_pattern_infos:
                    is_branches_disjoint = False

                met_pattern_infos.update(union_set)

            pattern_infos = sort_pattern_infos(met_pattern_infos)

            token_names = [to_token_name[x] for x in pattern_infos]

            txts.append('else:')
            txts.append('    self._error(token_names={0})'.format(
                format_args(token_names)
            ))

            res = '\n'.join(txts)

            need_print_code = False

            if not is_branches_disjoint:
                msg = 'Warning: Branches are not disjoint.\n'

                sys.stderr.write(msg)

                need_print_code = True

            if len(nullable_item_infos) > 1:
                msg = 'Warning: Exists multiple nullable branches.\n'

                sys.stderr.write(msg)

                need_print_code = True

            if need_print_code:
                msg = 'Generated code:\n```\n{0}\n```\n'.format(res)

                sys.stderr.write(msg)

        return res


class Occ01Expr(AstNode):

    def __init__(self, item):
        super(Occ01Expr, self).__init__()

        self.item = item

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def calc_first_set(self, to_first_set):
        item_first_set = self.item.calc_first_set(to_first_set)

        first_set = set(item_first_set)

        first_set.add(EMPTY_PATTERN_INFO)

        self.first_set = first_set

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        self.add_follow_set(follow_set)

        self.item.calc_follow_set(
            self.get_follow_set(), to_first_set, to_rule_def
        )

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        txts = []

        backtracking_on = opts.get(GS_BACKTRACKING_ON, None) == 1

        if backtracking_on:
            # E.g.
            # ```
            # self._o01()
            # try:
            #     ...
            # except SyntaxError: self._o01(0)
            # else: self._o01(1)
            # ```

            txts.append('self._o01()')
            txts.append('try:')

            item_txt = self.item.gen(to_token_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

            txts.append('except SyntaxError: self._o01(0)')
            txts.append('else: self._o01(1)')
        else:
            is_in_expror = kwargs.get('is_in_expror', False)

            if is_in_expror:
                # The parent AltExpr item already generated the if test, so no
                # need to generate the Occ01Expr item's if test.
                #
                # Note this reduction is allowed with the requirement that the
                # Occ01Expr item and the child item have the same follow set,
                # and that the parent AltExpr item will peek the first set and
                # follow set for a nullable item such as Occ01Expr, just as an
                # Occ01Expr item will do.
                #
                item_txt = self.item.gen(
                    to_token_name,
                    to_first_set,
                    opts=opts,
                )

                return item_txt

            item_first_set = self.item.get_first_set()

            item_first_set = get_nonempty_pattern_infos(item_first_set)

            follow_set = self.get_follow_set()

            if not item_first_set and not follow_set:
                txt = 'if True:'
            else:
                peek_args_txt2 = get_peek_args_txt2(
                    item_first_set, follow_set, to_token_name
                )

                if not item_first_set \
                        or has_empty_pattern_info(self.item.get_first_set()):
                    txt = 'if self._peek({0},\n    is_required=True):'.format(
                        peek_args_txt2,
                    )
                else:
                    peek_args_txt = get_peek_args_txt(
                        item_first_set, to_token_name
                    )

                    txt = 'if self._peek({0},\n    is_required=True) {1}'\
                        .format(
                            peek_args_txt2,
                            '== \'{0}\':'.format(
                                to_token_name[next(iter(item_first_set))]
                            )
                            if len(item_first_set) == 1
                            else 'in {0}:'.format(peek_args_txt)
                        )

            txts.append(txt)

            item_txt = self.item.gen(to_token_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

        res = '\n'.join(txts)

        return res


class Occ0mExpr(AstNode):

    def __init__(self, item):
        super(Occ0mExpr, self).__init__()

        self.item = item

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def calc_first_set(self, to_first_set):
        item_first_set = self.item.calc_first_set(to_first_set)

        first_set = set(item_first_set)

        first_set.add(EMPTY_PATTERN_INFO)

        self.first_set = first_set

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        self.add_follow_set(follow_set)

        # Use first set as follow set because the item can appear after itself.
        item_follow_set = set(self.item.get_first_set())

        add_nonempty_pattern_infos(item_follow_set, self.get_follow_set())

        self.item.calc_follow_set(item_follow_set, to_first_set, to_rule_def)

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        txts = []

        backtracking_on = opts.get(GS_BACKTRACKING_ON, None) == 1

        if backtracking_on:
            # E.g.
            # ```
            # self._o0m()
            # try:
            #     while 1:
            #         ...
            #         self._o0m(1)
            # except SyntaxError: self._o0m(0)
            # ```

            txts.append('self._o0m()')
            txts.append('try:')
            txts.append('    while 1:')

            item_txt = self.item.gen(to_token_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt, 2))

            txts.append('        self._o0m(1)')
            txts.append('except SyntaxError: self._o0m(0)')
        else:
            item_first_set = self.item.get_first_set()

            item_first_set = get_nonempty_pattern_infos(item_first_set)

            peek_args_txt = get_peek_args_txt(item_first_set, to_token_name)

            peek_args_txt2 = get_peek_args_txt2(
                item_first_set, self.get_follow_set(), to_token_name
            )

            txt = 'while self._peek({0},\n    is_required=True) {1}'.format(
                peek_args_txt2,
                '== \'{0}\':'.format(
                    to_token_name[next(iter(item_first_set))]
                )
                if len(item_first_set) == 1
                else 'in {0}:'.format(peek_args_txt)
            )

            txts.append(txt)

            item_txt = self.item.gen(to_token_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

        res = '\n'.join(txts)

        return res


class Occ1mExpr(AstNode):

    def __init__(self, item):
        super(Occ1mExpr, self).__init__()

        self.item = item

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def calc_first_set(self, to_first_set):
        self.first_set = set(self.item.calc_first_set(to_first_set))

        return self.first_set

    def calc_follow_set(self, follow_set, to_first_set, to_rule_def):
        self.add_follow_set(follow_set)

        item_follow_set = set(self.item.get_first_set())

        add_nonempty_pattern_infos(item_follow_set, self.get_follow_set())

        self.item.calc_follow_set(item_follow_set, to_first_set, to_rule_def)

    def gen(self, to_token_name, to_first_set, opts, **kwargs):
        txts = []

        backtracking_on = opts.get(GS_BACKTRACKING_ON, None) == 1

        if backtracking_on:
            # E.g.
            # ```
            # self._o1m()
            # try:
            #     while 1:
            #         ...
            #         self._o1m(1)
            # except SyntaxError: self._o1m(0)
            # ```

            txts.append('self._o1m()')
            txts.append('try:')
            txts.append('    while 1:')

            item_txt = self.item.gen(to_token_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt, 2))

            txts.append('        self._o1m(1)')
            txts.append('except SyntaxError: self._o1m(0)')
        else:
            item_first_set = self.item.get_first_set()

            item_first_set_old_count = len(item_first_set)

            item_first_set = get_nonempty_pattern_infos(item_first_set)

            item_first_set_new_count = len(item_first_set)

            has_empty_pattern = \
                item_first_set_new_count != item_first_set_old_count

            if has_empty_pattern:
                peek_args_txt = get_peek_args_txt(
                    item_first_set, to_token_name
                )

                peek_args_txt2 = get_peek_args_txt2(
                    item_first_set, self.get_follow_set(), to_token_name
                )

                # Change `+` to `*`
                txt = 'while self._peek({0},\n    is_required=True) {1}'\
                    .format(
                        peek_args_txt2,
                        '== \'{0}\':'.format(
                            to_token_name[next(iter(item_first_set))]
                        )
                        if len(item_first_set) == 1
                        else 'in {0}:'.format(peek_args_txt)
                    )

                txts.append(txt)

                item_txt = self.item.gen(
                    to_token_name, to_first_set, opts=opts
                )

                txts.append(add_indent(item_txt))

            else:
                txts.append('while True:')

                item_txt = self.item.gen(
                    to_token_name, to_first_set, opts=opts
                )

                txts.append(add_indent(item_txt))

                peek_args_txt = get_peek_args_txt(
                    item_first_set, to_token_name, 2
                )

                peek_args_txt2 = get_peek_args_txt2(
                    item_first_set, self.get_follow_set(), to_token_name, 2
                )

                txt = '    if self._peek({0},\n        is_required=True) {1}'\
                    .format(
                        peek_args_txt2,
                        '!= \'{0}\':'.format(
                            to_token_name[next(iter(item_first_set))]
                        )
                        if len(item_first_set) == 1
                        else 'not in {0}:'.format(peek_args_txt)
                    )

                txts.append(txt)
                txts.append('        break')

        res = '\n'.join(txts)

        return res


def has_empty_pattern_info(pattern_infos):
    for pattern_info in pattern_infos:
        if pattern_info in EMPTY_PATTERN_INFOS:
            return True

    return False


def add_nonempty_pattern_infos(to_set, from_set):
    has_empty_pattern = False

    for pattern_info in from_set:
        if pattern_info in EMPTY_PATTERN_INFOS:
            has_empty_pattern = True
        else:
            to_set.add(pattern_info)

    return has_empty_pattern


def get_nonempty_pattern_infos(pattern_infos):
    nonempty_pattern_infos = set()

    for pattern_info in pattern_infos:
        if pattern_info not in EMPTY_PATTERN_INFOS:
            nonempty_pattern_infos.add(pattern_info)

    return nonempty_pattern_infos


def format_args(args, indent=1):
    text = (',\n' + '    ' * indent).join(
        '\'{0}\''.format(x) for x in args
    )

    text = '[{0}{1}]'.format(
        ('\n' + '    ' * indent) if len(args) > 1 else '',
        text,
    )

    return text


def get_peek_args_txt(first_set, to_token_name, indent=1):
    pattern_infos = sort_pattern_infos(first_set)

    token_names = [to_token_name[x] for x in pattern_infos]

    text = format_args(token_names, indent=indent)

    return text


def get_peek_args_txt2(first_set, follow_set, to_token_name, indent=1):
    pattern_infos1 = sort_pattern_infos(first_set)

    pattern_infos2 = sort_pattern_infos(follow_set)

    pattern_infos = []

    for pattern_info in pattern_infos1:
        if pattern_info not in pattern_infos:
            pattern_infos.append(pattern_info)

    for pattern_info in pattern_infos2:
        if pattern_info not in pattern_infos:
            pattern_infos.append(pattern_info)

    token_names = [to_token_name[x] for x in pattern_infos]

    text = format_args(token_names, indent=indent)

    return text


def sort_pattern_infos(pattern_infos):
    pattern_infos = list(pattern_infos)

    for i in range(1, len(pattern_infos)):
        j = i - 1

        item = pattern_infos[i]

        while (j >= 0) and (pattern_info_greater_than(pattern_infos[j], item)):
            pattern_infos[j + 1] = pattern_infos[j]

            j -= 1

        pattern_infos[j + 1] = item

    return pattern_infos


def pattern_info_greater_than(a, b):
    # The longer pattern appears first
    if len(a[0]) < len(b[0]):
        return True

    if len(a[0]) > len(b[0]):
        return False

    # If same length, sort alphabetically
    return a[0] > b[0]
