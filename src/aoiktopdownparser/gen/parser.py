# coding: utf-8
from __future__ import absolute_import

from argparse import ArgumentParser
import codecs
from pprint import pformat
import re
import sys
from traceback import format_exc
from traceback import format_exception

from aoiktopdownparser.gen.ast import AltExpr
from aoiktopdownparser.gen.ast import Code
from aoiktopdownparser.gen.ast import Occ0mExpr
from aoiktopdownparser.gen.ast import Occ01Expr
from aoiktopdownparser.gen.ast import Occ1mExpr
from aoiktopdownparser.gen.ast import Pattern
from aoiktopdownparser.gen.ast import RuleDef
from aoiktopdownparser.gen.ast import RuleRef
from aoiktopdownparser.gen.ast import SeqExpr


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


# Used in backtracking mode.
class ScanOk(Exception):
    pass


class ParsingError(Exception):
    pass


class LexError(ParsingError):

    def __init__(
        self,
        txt,
        pos,
        row,
        col,
        msg=None,
    ):
        # Input string.
        self.txt = txt

        # Input string length.
        self.txt_len = len(txt)

        # Input lines.
        self.lines = txt.split('\n')

        # Current line.
        self.line = self.lines[row]

        # Current position index.
        self.pos = pos

        # Current row index.
        self.row = row

        # Current column index.
        self.col = col

        # Error message.
        self.msg = msg

    def __str__(self):
        narrow_columns_index = get_narrow_column_index(self.line, self.col)

        col_mark = ' ' * narrow_columns_index + '|'

        source_text = (
            '```\n'
            '{0}\n'
            '{1}\n'
            '```'
        ).format(self.line, col_mark)

        text = (
            'Lexer failed at row {row}, column {col}, character {pos}.\n'
            '{msg}'
            '{source_text}'
        ).format(
            row=self.row + 1,
            col=self.col + 1,
            pos=self.pos + 1,
            msg='' if self.msg is None else self.msg + '\n',
            source_text=source_text,
        )

        return text


class SyntaxError(ParsingError):

    def __init__(
        self,
        ctx,
        txt,
        pos,
        row,
        col,
        token_name=None,
        token_names=[],
        eis=None,
        eisp=None,
        msg=None,
    ):
        # Current context.
        self.ctx = ctx

        # Input string.
        self.txt = txt

        # Input lines.
        self.lines = txt.split('\n')

        # Current line.
        self.line = self.lines[row]

        # Current position index.
        self.pos = pos

        # Current row index.
        self.row = row

        # Current column index.
        self.col = col

        # Current token name.
        self.current_token_name = token_name

        # Wanted token names.
        self.wanted_token_names = token_names

        # Scanning exception infos of current branch.
        self.eis = eis

        # Scanning exception infos of previous branch.
        self.eisp = eisp

        # Error message.
        self.msg = msg

    def __str__(self):
        ctx_names = get_ctx_names(self.ctx)

        ctx_msg = ' '.join(ctx_names) if ctx_names else ''

        msg = self.msg

        if msg is None:
            msg = ''

            if self.wanted_token_names:
                msg += 'Wanted tokens: `{0}`。\n'.format(
                    ' | '.join(self.wanted_token_names)
                )

            msg += (
                'Met token: `{0}`。\n'.format(self.current_token_name)
                if self.current_token_name is not None
                else 'end-of-input。\n'
            )

        narrow_columns_index = get_narrow_column_index(self.line, self.col)

        col_mark = ' ' * narrow_columns_index + '|'

        source_text = (
            '```\n'
            '{0}\n'
            '{1}\n'
            '```'
        ).format(self.line, col_mark)

        text = (
            'Rule `{rule_name}` failed at row {row}, column {col},' +
            ' character {pos}.\nContext: {ctx_msg}.\n' +
            msg +
            '{source_text}'
        ).format(
            rule_name=self.ctx.name,
            ctx_msg=ctx_msg,
            row=self.row + 1,
            col=self.col + 1,
            pos=self.pos + 1,
            source_text=source_text,
        )

        return text


class Parser(object):

    _RULE_FUNC_PRF = ''

    _RULE_FUNC_POF = ''

    # `SK` means state dict key.
    #
    # Position index.
    _SK_POS = 'pos'

    # Row index.
    _SK_ROW = 'row'

    # Column index.
    _SK_COL = 'col'

    # Repeated occurrence.
    _SK_OCC = 'occ'

    # Token index.
    _SK_TOK_IDX = 'tok_idx'

    # `DK` means debug dict key.
    #
    # Rule name.
    _DK_NAME = 'name'

    # Input string.
    _DK_TXT = 'txt'

    # Position index.
    _DK_POS = 'pos'

    # Row index.
    _DK_ROW = 'row'

    # Column index.
    _DK_COL = 'col'

    # Scanning level.
    _DK_SLV = 'slv'

    # Scanning is successful.
    _DK_SSS = 'sss'

    WHITESPACE_TOKEN_NAME = ''

    _TOKEN_NAME_AND_REGEX_OBJ_TUPLES = [
        ('end', re.compile('$')),  # noqa
        ('comma', re.compile(',')),  # noqa
        ('colon', re.compile(':')),  # noqa
        ('equal_sign', re.compile('=')),  # noqa
        ('at_sign', re.compile('@')),  # noqa
        ('pipe_sign', re.compile(r'\|')),  # noqa
        ('parenthesis_start', re.compile(r'\(')),  # noqa
        ('parenthesis_end', re.compile(r'\)')),  # noqa
        ('bracket_start', re.compile(r'\[')),  # noqa
        ('bracket_end', re.compile(r'\]')),  # noqa
        ('occ01_trailer', re.compile(r'\?')),  # noqa
        ('occ0m_trailer', re.compile(r'\*')),  # noqa
        ('occ1m_trailer', re.compile(r'\+')),  # noqa
        ('none', re.compile('None(?![a-zA-Z0-9_])')),  # noqa
        ('boolean', re.compile('(True|False)(?![a-zA-Z0-9_])')),  # noqa
        ('number', re.compile(r"""
        ([-+])?         # Sign
        (?=\d|[.]\d)    # Next is an integer part or a fraction part
        (\d*)           # Integer part
        ([.]\d*)?       # Fraction part
        (e[-+]?\d+)?    # Exponent part
        """, re.VERBOSE | re.IGNORECASE)),  # noqa
        ('string', re.compile('r?(\'\'\'|"""|\'|")((?:[^\\\\]|\\\\.)*?)(\\1)')),  # noqa
        ('rule_name', re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?=:)')),  # noqa
        ('name', re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?!:)')),  # noqa
        ('code', re.compile(r'(`+)((?:.|\n)*?)\1')),  # noqa
    ]

    def __init__(self, txt, debug=False):
        self._txt = txt

        self._txt_len = len(txt)

        self._pos = 0

        self._row = 0

        self._col = 0

        self._debug = debug

        self._debug_infos = None

        if self._debug:
            self._debug_infos = []

        self._ws_rep = r'([ \t]*(#[^\n]*)?[\n]?)*'

        self._ws_reo = re.compile(self._ws_rep)\
            if self._ws_rep is not None else None

        # Current rule func's context dict
        self._ctx = None

        # Tokens
        self._tokens = []

        # Tokens count
        self._tokens_count = 0

        # Current token index
        self._token_index = 0

        # Scan level
        self._scan_lv = -1

        # Scan exc info
        self._scan_ei = None

        # Scan exc infos of current branching
        self._scan_eis = []

        # Scan exc infos of previous branching
        self._scan_eis_prev = []

        # Backtracking state stack.
        self._state_stack = []

    def _make_tokens(self):
        self._pos = 0
        self._row = 0
        self._col = 0

        txt_len = len(self._txt)

        while self._pos <= txt_len:
            self._make_whitespace_token()

            for token_name, regex_obj in self._TOKEN_NAME_AND_REGEX_OBJ_TUPLES:
                match_obj = regex_obj.match(self._txt, self._pos)

                if not match_obj:
                    continue

                matched_txt = match_obj.group()

                matched_len = len(matched_txt)

                if matched_len > 0\
                or regex_obj.pattern == '$':
                    self._add_token(token_name, matched_txt, match_obj)

                    if regex_obj.pattern == '$':
                        # Make the loop stop.
                        self._pos = txt_len + 1

                    break
            else:
                if self._pos < txt_len:
                    raise LexError(
                        txt=self._txt,
                        pos=self._pos,
                        row=self._row,
                        col=self._col,
                    )

        self._pos = 0
        self._row = 0
        self._col = 0

        self._tokens_count = len(self._tokens)

    def _make_whitespace_token(self):
        match_obj = self._ws_reo.match(self._txt, self._pos)

        if match_obj:
            matched_txt = match_obj.group()

            if not matched_txt:
                return

            self._add_token(self.WHITESPACE_TOKEN_NAME, matched_txt, match_obj)

    def _add_token(self, token_name, matched_txt, match_obj):
        token_info = AttrDict()

        token_info.pos = self._pos

        token_info.row = self._row

        token_info.col = self._col

        token_info.txt = matched_txt

        token_info.len = len(matched_txt)

        token_info.rows_count = matched_txt.count('\n') + 1

        token_info.end_row = token_info.row + token_info.rows_count - 1

        if token_info.rows_count == 1:
            token_info.end_col = token_info.col + len(matched_txt)
        else:
            last_row_txt = matched_txt[matched_txt.rfind('\n') + 1:]

            token_info.end_col = len(last_row_txt)

        token_info.match_obj = match_obj

        self._tokens.append((token_name, token_info))

        self._update_pos_row_col(token_info)

    def _update_pos_row_col(self, token_info):
        self._pos = token_info.pos + token_info.len

        matched_txt = token_info.txt

        row_cnt = matched_txt.count('\n')

        if row_cnt == 0:
            self._row = token_info.row

            self._col = token_info.col + len(matched_txt)
        else:
            last_row_txt = matched_txt[matched_txt.rfind('\n') + 1:]

            self._row = token_info.row + row_cnt

            self._col = len(last_row_txt)

    def _get_row_col(self, token_index=None, skip_whitespace=False):
        if self._tokens_count == 0:
            raise ValueError(self._tokens_count)

        if token_index is None:
            token_index = self._token_index

        if token_index > self._tokens_count:
            raise ValueError(token_index)

        if skip_whitespace:
            while True:
                if token_index > self._tokens_count:
                    raise ValueError(token_index)

                if token_index == self._tokens_count:
                    _, last_token_info = self._tokens[-1]

                    return (
                        last_token_info.end_row,
                        last_token_info.end_col
                    )

                token_name, token_info = self._tokens[token_index]

                if token_name == self.WHITESPACE_TOKEN_NAME:
                    token_index += 1

                    continue

                break

            return (token_info.row, token_info.col)
        else:
            if token_index == self._tokens_count:
                _, last_token_info = self._tokens[-1]

                return (
                    last_token_info.end_row,
                    last_token_info.end_col
                )

            _, token_info = self._tokens[token_index]

            return (token_info.row, token_info.col)

    def _get_start_row_col(self):
        row, col = self._get_row_col(skip_whitespace=True)
        return (row + 1, col + 1)

    def _get_end_row_col(self):
        row, col = self._get_row_col(skip_whitespace=False)
        return (row + 1, col + 1)

    def _get_token_index(self, skip_whitespace=True):
        token_index = self._token_index

        if skip_whitespace:
            while True:
                if token_index >= self._tokens_count:
                    return None

                current_token_name, _ = self._tokens[token_index]

                if current_token_name == self.WHITESPACE_TOKEN_NAME:
                    token_index += 1

                    continue

                break
        else:
            if token_index >= self._tokens_count:
                return None

        return token_index

    def _get_ctx_attr(self, ctx, attr_name, default=None):
        try:
            return ctx[attr_name]
        except KeyError:
            return default

    def _seek(self, token_index):
        if token_index < 0 or token_index >= self._txt_len:
            raise ValueError(token_index)

        _, token_info = self._tokens[token_index]

        self._pos = token_info.pos
        self._row = token_info.row
        self._col = token_info.col

    def _retract(self, token_index=None):
        if token_index is None:
            token_index = self._token_index

        while True:
            if token_index == 0:
                break

            token_index -= 1

            if token_index < 0:
                raise ValueError(token_index)

            token_name, _ = self._tokens[
                token_index
            ]

            if token_name != self.WHITESPACE_TOKEN_NAME:
                break

        self._seek(token_index)

    def _peek(self, token_names, is_required=False, is_branch=False):
        token_index = self._token_index

        while True:
            if token_index >= self._tokens_count:
                return None

            current_token_name, token_info = self._tokens[token_index]

            if current_token_name == self.WHITESPACE_TOKEN_NAME:
                token_index += 1

                continue

            break

        if current_token_name in token_names:
            return current_token_name

        if is_required:
            self._error(token_names=token_names)
        else:
            return None

    def _scan_token(self, token_name, new_ctx=False):
        while True:
            if self._token_index >= self._tokens_count:
                self._error(token_names=[token_name])

            current_token_name, token_info = self._tokens[
                self._token_index
            ]

            if current_token_name == self.WHITESPACE_TOKEN_NAME:
                self._token_index += 1

                self._update_pos_row_col(token_info)

                continue

            break

        if current_token_name != token_name:
            self._error(token_names=[token_name])

        self._token_index += 1

        self._update_pos_row_col(token_info)

        if new_ctx:
            ctx = AttrDict()

            ctx.name = ''

            ctx.par = self._ctx
        else:
            ctx = self._ctx

        ctx.res = token_info

        return ctx

    def _scan_rule(self, name):
        ctx_par = self._ctx

        self._scan_lv += 1

        ctx_new = AttrDict()

        ctx_new.name = name

        ctx_new.par = ctx_par

        self._ctx = ctx_new

        rule_func = self._rule_func_get(name)

        self._scan_ei = None

        if self._debug:
            debug_info = AttrDict()
            debug_info[self._DK_NAME] = name
            debug_info[self._DK_TXT] = self._txt
            debug_info[self._DK_POS] = self._pos
            debug_info[self._DK_ROW] = self._row
            debug_info[self._DK_COL] = self._col
            debug_info[self._DK_SLV] = self._scan_lv
            debug_info[self._DK_SSS] = False

            self._debug_infos.append(debug_info)

        try:
            rule_func(ctx_new)
        except SyntaxError:
            exc_info = sys.exc_info()

            if self._scan_ei is None or self._scan_ei[1] is not exc_info[1]:
                self._scan_ei = exc_info

                self._scan_eis.append(exc_info)

            raise
        else:
            if self._debug:
                debug_info[self._DK_SSS] = True
        finally:
            self._scan_lv -= 1

            self._ctx = ctx_par

        return ctx_new

    def _rule_func_get(self, name):
        rule_func_name = self._RULE_FUNC_PRF + name + self._RULE_FUNC_POF

        rule_func = getattr(self, rule_func_name)

        return rule_func

    def _error(self, msg=None, token_names=None):
        token_index = self._get_token_index(skip_whitespace=True)

        if token_index is None:
            token_name = None
        else:
            token_name, info = self._tokens[token_index]

            self._pos = info.pos
            self._row = info.row
            self._col = info.col

        raise SyntaxError(
            ctx=self._ctx,
            txt=self._txt,
            pos=self._pos,
            row=self._row,
            col=self._col,
            token_name=token_name,
            token_names=token_names,
            eis=self._scan_eis,
            eisp=self._scan_eis_prev,
            msg=msg,
        )

    def all(self, ctx):
        # ```
        ctx.opts = None
        # ```
        if self._peek([
            'at_sign',
            'rule_name'],
            is_required=True) == 'at_sign':
            args_def = self._scan_rule('args_def')  # noqa
            # ```
            ctx.opts = args_def.res
            # ```
        rule_defs = self._scan_rule('rule_defs')  # noqa
        # ```
        ctx.rule_defs = rule_defs.res
        # ```
        end = self._scan_rule('end')  # noqa

    def end(self, ctx):
        end = self._scan_token('end')  # noqa

    def comma(self, ctx):
        comma = self._scan_token('comma')  # noqa

    def colon(self, ctx):
        colon = self._scan_token('colon')  # noqa

    def equal_sign(self, ctx):
        equal_sign = self._scan_token('equal_sign')  # noqa

    def at_sign(self, ctx):
        at_sign = self._scan_token('at_sign')  # noqa

    def pipe_sign(self, ctx):
        pipe_sign = self._scan_token('pipe_sign')  # noqa

    def parenthesis_start(self, ctx):
        parenthesis_start = self._scan_token('parenthesis_start')  # noqa

    def parenthesis_end(self, ctx):
        parenthesis_end = self._scan_token('parenthesis_end')  # noqa

    def bracket_start(self, ctx):
        bracket_start = self._scan_token('bracket_start')  # noqa

    def bracket_end(self, ctx):
        bracket_end = self._scan_token('bracket_end')  # noqa

    def occ01_trailer(self, ctx):
        occ01_trailer = self._scan_token('occ01_trailer')  # noqa

    def occ0m_trailer(self, ctx):
        occ0m_trailer = self._scan_token('occ0m_trailer')  # noqa

    def occ1m_trailer(self, ctx):
        occ1m_trailer = self._scan_token('occ1m_trailer')  # noqa

    def none(self, ctx):
        none = self._scan_token('none')  # noqa
        # ```
        ctx.res = None
        # ```

    def boolean(self, ctx):
        boolean = self._scan_token('boolean')  # noqa
        # ```
        ctx.res = True if (boolean.res.txt == 'True') else False
        # ```

    def number(self, ctx):
        number = self._scan_token('number')  # noqa
        # ```
        ctx.res = eval(number.res.txt)
        # ```

    def string(self, ctx):
        string = self._scan_token('string')  # noqa
        # ```
        ctx.res = string.res
        # ```

    def literal(self, ctx):
        if self._peek(['none']):
            none = self._scan_rule('none')  # noqa
            # ```
            ctx.res = none.res
            # ```
        elif self._peek(['boolean'], is_branch=True):
            boolean = self._scan_rule('boolean')  # noqa
            # ```
            ctx.res = boolean.res
            # ```
        elif self._peek(['number'], is_branch=True):
            number = self._scan_rule('number')  # noqa
            # ```
            ctx.res = number.res
            # ```
        elif self._peek(['string'], is_branch=True):
            string = self._scan_rule('string')  # noqa
            # ```
            ctx.res = eval(string.res.txt)
            # ```
        else:
            self._error(token_names=[
            'number',
            'string',
            'boolean',
            'none'])

    def rule_name(self, ctx):
        rule_name = self._scan_token('rule_name')  # noqa
        # ```
        ctx.res = rule_name.res
        # ```

    def name(self, ctx):
        name = self._scan_token('name')  # noqa
        # ```
        ctx.res = name.res
        # ```

    def args_def(self, ctx):
        at_sign = self._scan_rule('at_sign')  # noqa
        args_list = self._scan_rule('args_list')  # noqa
        # ```
        ctx.res = dict(args_list.res)
        # ```

    def args_list(self, ctx):
        # ```
        ctx.res = []
        # ```
        parenthesis_start = self._scan_rule('parenthesis_start')  # noqa
        if self._peek(['parenthesis_end']):
            parenthesis_end = self._scan_rule('parenthesis_end')  # noqa
        elif self._peek(['name'], is_branch=True):
            args_list_item = self._scan_rule('args_list_item')  # noqa
        else:
            self._error(token_names=[
            'name',
            'parenthesis_end'])

    def args_list_item(self, ctx):
        # ```
        ctx.res = ctx.par.res
        # ```
        arg_expr = self._scan_rule('arg_expr')  # noqa
        # ```
        ctx.res.append(arg_expr.res)
        # ```
        if self._peek(['parenthesis_end']):
            parenthesis_end = self._scan_rule('parenthesis_end')  # noqa
        elif self._peek(['comma'], is_branch=True):
            comma = self._scan_rule('comma')  # noqa
            if self._peek(['parenthesis_end']):
                parenthesis_end = self._scan_rule('parenthesis_end')  # noqa
            elif self._peek(['name'], is_branch=True):
                args_list_item = self._scan_rule('args_list_item')  # noqa
            else:
                self._error(token_names=[
                'name',
                'parenthesis_end'])
        else:
            self._error(token_names=[
            'parenthesis_end',
            'comma'])

    def arg_expr(self, ctx):
        name = self._scan_rule('name')  # noqa
        equal_sign = self._scan_rule('equal_sign')  # noqa
        literal = self._scan_rule('literal')  # noqa
        # ```
        ctx.res = (name.res.txt, literal.res)
        # ```

    def rule_defs(self, ctx):
        # ```
        ctx.res = []
        # ```
        while True:
            rule_def = self._scan_rule('rule_def')  # noqa
            # ```
            ctx.res.append(rule_def.res)
            # ```
            if self._peek([
                'rule_name',
                'end'],
                is_required=True) != 'rule_name':
                break

    def rule_def(self, ctx):
        rule_name = self._scan_rule('rule_name')  # noqa
        colon = self._scan_rule('colon')  # noqa
        # ```
        args = None
        # ```
        if self._peek([
            'at_sign',
            'string',
            'name',
            'code',
            'parenthesis_start',
            'bracket_start'],
            is_required=True) == 'at_sign':
            args_def = self._scan_rule('args_def')  # noqa
            # ```
            args = args_def.res
            # ```
        or_expr = self._scan_rule('or_expr')  # noqa
        # ```
        ctx.res = RuleDef(
            name=rule_name.res.txt,
            item=or_expr.res,
            args=args,
        )
        # ```

    def or_expr(self, ctx):
        seq_expr = self._scan_rule('seq_expr')  # noqa
        # ```
        items = [seq_expr.res]
        # ```
        while self._peek([
            'pipe_sign',
            'rule_name',
            'parenthesis_end',
            'bracket_end',
            'end'],
            is_required=True) == 'pipe_sign':
            pipe_sign = self._scan_rule('pipe_sign')  # noqa
            seq_expr = self._scan_rule('seq_expr')  # noqa
            # ```
            items.append(seq_expr.res)
            # ```
        # ```
        ctx.res = AltExpr(items) if len(items) > 1 else items[0]
        # ```

    def seq_expr(self, ctx):
        # ```
        items = []
        # ```
        while True:
            while self._peek([
                'code',
                'string',
                'name',
                'parenthesis_start',
                'bracket_start'],
                is_required=True) == 'code':
                code = self._scan_rule('code')  # noqa
                # ```
                items.append(code.res)
                # ```
            occ_expr = self._scan_rule('occ_expr')  # noqa
            # ```
            items.append(occ_expr.res)
            # ```
            while self._peek([
                'code',
                'string',
                'name',
                'rule_name',
                'parenthesis_start',
                'parenthesis_end',
                'bracket_start',
                'bracket_end',
                'pipe_sign',
                'end'],
                is_required=True) == 'code':
                code = self._scan_rule('code')  # noqa
                # ```
                items.append(code.res)
                # ```
            if self._peek([
                'string',
                'name',
                'code',
                'parenthesis_start',
                'bracket_start',
                'rule_name',
                'parenthesis_end',
                'bracket_end',
                'pipe_sign',
                'end'],
                is_required=True) not in [
                'string',
                'name',
                'code',
                'parenthesis_start',
                'bracket_start']:
                break
        # ```
        ctx.res = SeqExpr(items) if len(items) > 1 else items[0]
        # ```

    def code(self, ctx):
        code = self._scan_token('code')  # noqa
        # ```
        ctx.res = Code(code.res.match_obj.group(2))
        # ```

    def occ_expr(self, ctx):
        if self._peek(['bracket_start']):
            occ01_group = self._scan_rule('occ01_group')  # noqa
            # ```
            ctx.res = occ01_group.res
            # ```
        elif self._peek([
            'string',
            'name',
            'parenthesis_start'], is_branch=True):
            atom = self._scan_rule('atom')  # noqa
            # ```
            occ_type = None
            # ```
            if self._peek([
                'occ0m_trailer',
                'occ1m_trailer',
                'occ01_trailer',
                'string',
                'name',
                'rule_name',
                'code',
                'parenthesis_start',
                'parenthesis_end',
                'bracket_start',
                'bracket_end',
                'pipe_sign',
                'end'],
                is_required=True) in [
                'occ0m_trailer',
                'occ1m_trailer',
                'occ01_trailer']:
                if self._peek(['occ01_trailer']):
                    occ01_trailer = self._scan_rule('occ01_trailer')  # noqa
                    # ```
                    occ_type = 0
                    # ```
                elif self._peek(['occ0m_trailer'], is_branch=True):
                    occ0m_trailer = self._scan_rule('occ0m_trailer')  # noqa
                    # ```
                    occ_type = 1
                    # ```
                elif self._peek(['occ1m_trailer'], is_branch=True):
                    occ1m_trailer = self._scan_rule('occ1m_trailer')  # noqa
                    # ```
                    occ_type = 2
                    # ```
                else:
                    self._error(token_names=[
                    'occ0m_trailer',
                    'occ1m_trailer',
                    'occ01_trailer'])
            # ```
            if occ_type is None:
                ctx.res = atom.res
            elif occ_type == 0:
                item = atom.res

                while isinstance(item, Occ01Expr):
                    item = item.item

                if isinstance(item, Occ0mExpr):
                    ctx.res = item
                elif isinstance(item, Occ1mExpr):
                    ctx.res = Occ0mExpr(item.item)
                else:
                    ctx.res = Occ01Expr(item)
            elif occ_type == 1:
                item = atom.res

                while isinstance(item, (Occ01Expr, Occ0mExpr, Occ1mExpr)):
                    item = item.item

                ctx.res = Occ0mExpr(item)
            elif occ_type == 2:
                item = atom.res

                while isinstance(item, Occ1mExpr):
                    item = item.item

                if isinstance(item, Occ01Expr):
                    ctx.res = Occ0mExpr(item.item)
                elif isinstance(item, Occ0mExpr):
                    ctx.res = item
                else:
                    ctx.res = Occ1mExpr(item)
            else:
                raise ValueError(occ_type)
            # ```
        else:
            self._error(token_names=[
            'string',
            'name',
            'parenthesis_start',
            'bracket_start'])

    def occ01_group(self, ctx):
        bracket_start = self._scan_rule('bracket_start')  # noqa
        or_expr = self._scan_rule('or_expr')  # noqa
        bracket_end = self._scan_rule('bracket_end')  # noqa
        # ```
        item = or_expr.res

        while isinstance(item, Occ01Expr):
            item = item.item

        if isinstance(item, Occ0mExpr):
            ctx.res = item
        elif isinstance(item, Occ1mExpr):
            ctx.res = Occ0mExpr(item.item)
        else:
            ctx.res = Occ01Expr(item)
        # ```

    def atom(self, ctx):
        if self._peek(['string']):
            string = self._scan_rule('string')  # noqa
            # ```
            args = None
            # ```
            if self._peek([
                'at_sign',
                'string',
                'name',
                'rule_name',
                'code',
                'parenthesis_start',
                'parenthesis_end',
                'occ0m_trailer',
                'occ1m_trailer',
                'occ01_trailer',
                'bracket_start',
                'bracket_end',
                'pipe_sign',
                'end'],
                is_required=True) == 'at_sign':
                args_def = self._scan_rule('args_def')  # noqa
                # ```
                args = args_def.res
                # ```
            # ```
            ctx.res = Pattern(string.res.txt, args=args)
            # ```
        elif self._peek(['name'], is_branch=True):
            name = self._scan_rule('name')  # noqa
            # ```
            ctx.res = RuleRef(name.res.txt)
            # ```
        elif self._peek(['parenthesis_start'], is_branch=True):
            group = self._scan_rule('group')  # noqa
            # ```
            ctx.res = group.res
            # ```
        else:
            self._error(token_names=[
            'string',
            'name',
            'parenthesis_start'])

    def group(self, ctx):
        parenthesis_start = self._scan_rule('parenthesis_start')  # noqa
        or_expr = self._scan_rule('or_expr')  # noqa
        parenthesis_end = self._scan_rule('parenthesis_end')  # noqa
        # ```
        ctx.res = or_expr.res
        # ```


def parse(txt, rule=None, debug=False):
    parser = Parser(
        txt=txt,
        debug=debug,
    )

    if rule is None:
        rule = 'all'

    parsing_result = None

    exc_info = None

    try:
        parser._make_tokens()

        parsing_result = parser._scan_rule(rule)
    except Exception:
        exc_info = sys.exc_info()

    return parser, parsing_result, exc_info


def debug_infos_to_msg(debug_infos, txt):
    rows = txt.split('\n')

    msgs = []

    for debug_info in debug_infos:
        row_txt = rows[debug_info.row]

        msg = '{indent}{error_sign}{name}: {row}.{col} ({pos}): {txt}'.format(
            indent='  ' * debug_info.slv,
            error_sign='' if debug_info.sss else '!',
            name=debug_info.name,
            row=debug_info.row + 1,
            col=debug_info.col + 1,
            pos=debug_info.pos + 1,
            txt=repr(
                row_txt[:debug_info.col] + '|' + row_txt[debug_info.col:]
            ),
        )

        msgs.append(msg)

    msg = '\n'.join(msgs)

    return msg


def parsing_error_to_msg(
    exc_info,
    lex_error_class,
    syntax_error_class,
    title,
    txt,
):
    msg = title

    exc = exc_info[1]

    if isinstance(exc, lex_error_class):
        return '{0}\n{1}'.format(title, str(exc))

    if not isinstance(exc, syntax_error_class):
        tb_lines = format_exception(*exc_info)

        tb_msg = ''.join(tb_lines)

        msg += '\n---\n{0}---\n'.format(tb_msg)

        return msg

    msgs = []

    msgs.append(msg)

    msgs.append(str(exc))

    # Messages below are for backtracking mode
    reason_exc_infos = []

    if exc.eisp:
        reason_exc_infos.extend(ei for ei in exc.eisp if ei[1] is not exc)

    if exc.eis:
        reason_exc_infos.extend(ei for ei in exc.eis if ei[1] is not exc)

    if reason_exc_infos:
        rows = txt.split('\n')

        msg = 'Possible reasons:'

        msgs.append(msg)

        for reason_exc_info in reason_exc_infos:
            exc = reason_exc_info[1]

            ctx_names = get_ctx_names(exc.ctx)

            ctx_msg = ''

            if ctx_names:
                ctx_msg = ' '.join(ctx_names)

            row_txt = rows[exc.row]

            narrow_columns_index = get_narrow_column_index(row_txt, exc.col)

            col_mark = ' ' * narrow_columns_index + '|'

            msg = (
                'Rule `{rule}` failed at row {row}, column {col},'
                ' character {pos}.\n'
                ' Context: {ctx_msg}.\n'
                '```\n'
                '{row_txt}\n'
                '{col_mark}\n'
                '```'
            ).format(
                rule=exc.ctx.name,
                row=exc.row + 1,
                col=exc.col + 1,
                pos=exc.pos + 1,
                ctx_msg=ctx_msg,
                row_txt=row_txt,
                col_mark=col_mark,
            )

            msgs.append(msg)

    msg = '\n'.join(msgs)

    return msg


def get_ctx_names(ctx):
    ctx_names = []

    ctx_name = getattr(ctx, 'name')

    ctx_names.append(ctx_name)

    while True:
        ctx = getattr(ctx, 'par', None)

        if ctx is None:
            break

        name = getattr(ctx, 'name')

        ctx_names.append(name)

    ctx_names = list(reversed(ctx_names))

    return ctx_names


WIDE_CHARS_REO = re.compile(
    '[\u4e00-\u9fa5，、；：。！？…—‘’“”（）【】《》]+'
)

NON_WIDE_CHARS_REO = re.compile(
    '[^\u4e00-\u9fa5，、；：。！？…—‘’“”（）【】《》]+'
)


def get_narrow_column_index(row_txt, column_index):
    if WIDE_CHARS_REO is None:
        return column_index

    row_txt = row_txt[:column_index]

    row_txt_count = len(row_txt)

    narrow_column_index = 0

    current_index = 0

    while current_index < row_txt_count:
        match_obj = WIDE_CHARS_REO.match(row_txt, current_index)

        if match_obj:
            chars_count = len(match_obj.group())

            narrow_column_index += chars_count * 2

            current_index += chars_count

        match_obj = NON_WIDE_CHARS_REO.match(row_txt, current_index)

        if match_obj:
            chars_count = len(match_obj.group())

            narrow_column_index += chars_count

            current_index += chars_count

    return narrow_column_index


def main(args=None):
    args_parser = ArgumentParser()

    args_parser.add_argument(
        '-s', dest='source_file_path', required=True, help='Source file path.'
    )

    args_parser.add_argument(
        '-d', dest='debug_on', action='store_true', help='Debug message on.'
    )

    args_obj = args_parser.parse_args(args)

    source_file_path = args_obj.source_file_path

    try:
        rules_txt = codecs.open(source_file_path, encoding='utf-8').read()
    except Exception:
        msg = 'Failed reading source file: `{0}`\n---\n{1}---\n'.format(
            source_file_path,
            format_exc(),
        )

        sys.stderr.write(msg)

        return 3

    debug_on = args_obj.debug_on

    parser, parsing_result, exc_info = parse(rules_txt, debug=debug_on)

    if debug_on and parser._debug_infos:
        msg = '# ----- Parser debug info -----\n'

        msg += debug_infos_to_msg(
            debug_infos=parser._debug_infos, txt=rules_txt
        )

        msg += '\n\n'

        sys.stderr.write(msg)

    if exc_info is not None:
        msg = parsing_error_to_msg(
            exc_info=exc_info,
            lex_error_class=LexError,
            syntax_error_class=SyntaxError,
            title='# ----- Parsing error -----',
            txt=rules_txt,
        )

        sys.stderr.write(msg)

        return 4

    msg = '# ----- Parsing result -----\n{0}\n'.format(
        pformat(parsing_result, indent=4, width=1)
    )

    sys.stderr.write(msg)

    return 0


if __name__ == '__main__':
    sys.exit(main())
