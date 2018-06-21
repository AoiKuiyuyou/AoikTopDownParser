# coding: utf-8
from __future__ import absolute_import

import re

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


class AstNode(object):

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        """
        @param to_reo_name: Map pattern info to RE object name as parser class
            attribute. Pattern info is a tuple of (RE_PATTERN, RE_FLAGS_STR).

        @param to_first_set: Map rule name to first set of pattern infos.
        """
        raise NotImplementedError()

    def get_pattern_infos(self):
        raise NotImplementedError()

    def get_rule_refs(self):
        raise NotImplementedError()

    def get_first_set(self, to_first_set):
        raise NotImplementedError()


class Pattern(AstNode):

    ARG_K_FLAGS = 'flags'

    def __init__(self, pat, args=None):
        super(Pattern, self).__init__()

        self.pat = pat

        self.args = args if args is not None else {}

        self.flags_str = self.args.get(Pattern.ARG_K_FLAGS, '0')

        assert re

        # `flags_str` can be like `re.VERBOSE | re.IGNORECASE`
        self.flags = eval(self.flags_str)

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        name = kwargs.get('name', None)

        res = "{res_var} = self._scan_reo({reo_var})".format(
            res_var=name or '_',
            reo_var='self.{0}'.format(to_reo_name[(self.pat, self.flags_str)]),
        )

        return res

    def get_pattern_infos(self):
        return {(self.pat, self.flags_str)}

    def get_rule_refs(self):
        return set()

    def get_first_set(self, to_first_set):
        return {(self.pat, self.flags_str)}


class Code(AstNode):

    def __init__(self, code):
        super(Code, self).__init__()

        self.code = code.strip()

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        res = self.code

        code_prf = opts.get(GS_CODE_PRF, GS_CODE_PRF_V_DFT)

        if code_prf:
            res = code_prf + res

        code_pof = opts.get(GS_CODE_POF, GS_CODE_POF_V_DFT)

        if code_pof:
            res = res + code_pof

        return res

    def get_pattern_infos(self):
        return set()

    def get_rule_refs(self):
        return set()

    def get_first_set(self, to_first_set):
        return {EMPTY_PATTERN_INFO}


class RuleDef(AstNode):

    def __init__(self, name, expr, args=None):
        super(RuleDef, self).__init__()

        self.name = name

        self.args = args

        self.expr = expr

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        func_prf = opts.get(GS_RULE_FUNC_NAME_PRF, GS_RULE_FUNC_NAME_PRF_V_DFT)

        func_pof = opts.get(GS_RULE_FUNC_NAME_POF, GS_RULE_FUNC_NAME_POF_V_DFT)

        func_def_fmt = 'def {func_prf}{name}{func_pof}(self, ctx):'

        func_def_txt = func_def_fmt.format(
            func_prf=func_prf,
            name=self.name,
            func_pof=func_pof,
        )

        if isinstance(self.expr, Pattern):
            func_body_txt = self.expr.gen(
                to_reo_name,
                to_first_set,
                opts=opts,
                name=self.name,
            )
        else:
            only_pattern_node = None

            if isinstance(self.expr, ExprSeq):
                seq_txts = []

                for item in self.expr.items:
                    if isinstance(item, Pattern):
                        # If have more than one pattern in this rule
                        if only_pattern_node:
                            only_pattern_node = None

                            break
                        else:
                            only_pattern_node = item

                            seq_txt = item.gen(
                                to_reo_name,
                                to_first_set,
                                opts=opts,
                                name=self.name,
                            )

                            seq_txts.append(seq_txt)
                    else:
                        if isinstance(item, Code):
                            seq_txt = item.gen(
                                to_reo_name, to_first_set, opts=opts
                            )
                            seq_txts.append(seq_txt)
                        else:
                            only_pattern_node = None

                            break

            if only_pattern_node is not None:
                func_body_txt = '\n'.join(seq_txts)
            else:
                func_body_txt = self.expr.gen(
                    to_reo_name,
                    to_first_set,
                    opts=opts
                )

        res = func_def_txt + '\n' + add_indent(func_body_txt)

        return res

    def get_pattern_infos(self):
        return self.expr.get_pattern_infos()

    def get_rule_refs(self):
        return self.expr.get_rule_refs()

    def get_first_set(self, to_first_set):
        return self.expr.get_first_set(to_first_set)


class RuleRef(AstNode):

    def __init__(self, name):
        self.name = name

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        res = "{name} = self._scan_rule('{name}')".format(
            name=self.name,
        )

        return res

    def get_pattern_infos(self):
        return set()

    def get_rule_refs(self):
        return {self.name}

    def get_first_set(self, to_first_set):
        return to_first_set[self.name]


class ExprSeq(AstNode):

    def __init__(self, items):
        super(ExprSeq, self).__init__()

        self.items = items

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        txts = []

        for item in self.items:
            txt = item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(txt)

        res = '\n'.join(txts)

        return res

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

    def get_first_set(self, to_first_set):
        first_set = set()

        for item in self.items:
            item_first_set = item.get_first_set(to_first_set)

            has_empty_pattern_info = False

            for pattern_info in item_first_set:
                if pattern_info in EMPTY_PATTERN_INFOS:
                    has_empty_pattern_info = True
                else:
                    first_set.add(pattern_info)

            if has_empty_pattern_info:
                continue
            else:
                break
        else:
            first_set.add(EMPTY_PATTERN_INFO)

        return first_set


class ExprOr(AstNode):

    def __init__(self, items):
        self.items = items

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
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
            #     except Er: self._ori(0)
            #     else: self._ori(1)
            #     self._ori()
            #     try:
            #         ...
            #     except Er: self._ori(0)
            #     else: self._ori(1)
            # except Ok: self._or(1)
            # else: self._or(0)
            # ```

            for item in self.items:
                txts.append(r'self._ori()')
                txts.append(r'try:')

                item_txt = item.gen(to_reo_name, to_first_set, opts=opts)

                txts.append(add_indent(item_txt))

                txts.append(r'except Er: self._ori(0)')
                txts.append(r'else: self._ori(1)')

            res = '\n'.join(txts)

            res = 'self._or()\n' +\
                  'try:\n' + add_indent(res) \
                  + '\nexcept Ok: self._or(1)' \
                  + '\nelse: self._or(0)'
        else:
            for item_index, item in enumerate(self.items):
                item_first_set = item.get_first_set(to_first_set)

                peek_args_txt = get_peek_args_txt(item_first_set, to_reo_name)

                txts.append(
                    '{0} self._peek({1}):'.format(
                        'if' if item_index == 0 else 'elif',
                        peek_args_txt
                    )
                )

                item_txt = item.gen(to_reo_name, to_first_set, opts=opts)

                txts.append(add_indent(item_txt))

            txts.append('else:')
            txts.append('    self._error()')

            res = '\n'.join(txts)

        return res

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

    def get_first_set(self, to_first_set):
        first_set = set()

        for item in self.items:
            item_first_set = item.get_first_set(to_first_set)

            first_set.update(item_first_set)

        return first_set


class ExprOcc01(AstNode):

    def __init__(self, item):
        super(ExprOcc01, self).__init__()

        self.item = item

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
        txts = []

        backtracking_on = opts.get(GS_BACKTRACKING_ON, None) == 1

        if backtracking_on:
            # E.g.
            # ```
            # self._o01()
            # try:
            #     ...
            # except Er: self._o01(0)
            # else: self._o01(1)
            # ```

            txts.append('self._o01()')
            txts.append('try:')

            item_txt = self.item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

            txts.append('except Er: self._o01(0)')
            txts.append('else: self._o01(1)')
        else:
            item_first_set = self.item.get_first_set(to_first_set)

            peek_args_txt = get_peek_args_txt(item_first_set, to_reo_name)

            txts.append('if self._peek({0}):'.format(peek_args_txt))

            item_txt = self.item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

        res = '\n'.join(txts)

        return res

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def get_first_set(self, to_first_set):
        first_set = self.item.get_first_set(to_first_set)

        first_set.add(EMPTY_PATTERN_INFO)

        return first_set


class ExprOcc0m(AstNode):

    def __init__(self, item):
        super(ExprOcc0m, self).__init__()

        self.item = item

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
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
            # except Er: self._o0m(0)
            # ```

            txts.append('self._o0m()')
            txts.append('try:')
            txts.append('    while 1:')

            item_txt = self.item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt, 2))

            txts.append('        self._o0m(1)')
            txts.append('except Er: self._o0m(0)')
        else:
            item_first_set = self.item.get_first_set(to_first_set)

            peek_args_txt = get_peek_args_txt(item_first_set, to_reo_name)

            txts.append('while self._peek({0}):'.format(peek_args_txt))

            item_txt = self.item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

        res = '\n'.join(txts)

        return res

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def get_first_set(self, to_first_set):
        first_set = self.item.get_first_set(to_first_set)

        first_set.add(EMPTY_PATTERN_INFO)

        return first_set


class ExprOcc1m(AstNode):

    def __init__(self, item):
        super(ExprOcc1m, self).__init__()

        self.item = item

    def gen(self, to_reo_name, to_first_set, opts, **kwargs):
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
            # except Er: self._o1m(0)
            # ```

            txts.append('self._o1m()')
            txts.append('try:')
            txts.append('    while 1:')

            item_txt = self.item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt, 2))

            txts.append('        self._o1m(1)')
            txts.append('except Er: self._o1m(0)')
        else:
            item_first_set = self.item.get_first_set(to_first_set)

            peek_args_txt = get_peek_args_txt(item_first_set, to_reo_name)

            txts.append('if not self._peek({0}):'.format(peek_args_txt))
            txts.append('    self._error()')

            txts.append('while self._peek({0}):'.format(peek_args_txt))

            item_txt = self.item.gen(to_reo_name, to_first_set, opts=opts)

            txts.append(add_indent(item_txt))

        res = '\n'.join(txts)

        return res

    def get_pattern_infos(self):
        return self.item.get_pattern_infos()

    def get_rule_refs(self):
        return self.item.get_rule_refs()

    def get_first_set(self, to_first_set):
        return self.item.get_first_set(to_first_set)


def get_peek_args_txt(first_set, to_reo_name):
    pattern_infos = sorted(first_set, key=(lambda x: (len(x[0]), x[0])))

    reo_names = [to_reo_name[x] for x in pattern_infos]

    peek_args_txt = ',\n    '.join('self.{0}'.format(x) for x in reo_names)

    peek_args_txt = '[{0}]'.format(peek_args_txt)

    return peek_args_txt
