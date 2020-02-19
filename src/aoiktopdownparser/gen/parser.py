# coding: utf-8
from __future__ import absolute_import

from argparse import ArgumentParser
from pprint import pformat
import re
import sys
from traceback import format_exception

from aoiktopdownparser.gen.ast import Code
from aoiktopdownparser.gen.ast import ExprOcc0m
from aoiktopdownparser.gen.ast import ExprOcc01
from aoiktopdownparser.gen.ast import ExprOcc1m
from aoiktopdownparser.gen.ast import ExprOr
from aoiktopdownparser.gen.ast import ExprSeq
from aoiktopdownparser.gen.ast import Pattern
from aoiktopdownparser.gen.ast import RuleDef
from aoiktopdownparser.gen.ast import RuleRef


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class ScanError(Exception):

    def __init__(
        self, ctx, txt, pos, row, col, token_names, eis=None, eisp=None
    ):
        self.ctx = ctx

        self.txt = txt

        self.lines = txt.split('\n')

        self.line = self.lines[row]

        self.pos = pos

        self.row = row

        self.col = col

        # Expected token names
        self.token_names = token_names

        # Scan exception infos of current branch
        self.eis = eis

        # Scan exception infos of previous branch
        self.eisp = eisp

    def __str__(self):
        ctx_names = get_ctx_names(self.ctx)

        ctx_msg = ' '.join(ctx_names) if ctx_names else ''

        col_mark = ' ' * self.col + '^'

        source_text = (
            '```\n'
            '{0}\n'
            '{1}\n'
            '```'
        ).format(self.line, col_mark)

        text = (
            'Rule `{rule_name}` failed at row {row} column {col} (char {pos}) (ctx: {ctx_msg}).\n'
            'Expect token `{token_names}`.\n'
            '{source_text}'
        ).format(
            rule_name=self.ctx.name,
            ctx_msg=ctx_msg,
            row=self.row + 1,
            col=self.col + 1,
            pos=self.pos + 1,
            token_names=' | '.join(self.token_names),
            source_text=source_text,
        )

        return text


# Used in backtracking mode.
class ScanOk(Exception):
    pass


class Parser(object):

    _RULE_FUNC_PRF = ''
    _RULE_FUNC_POF = ''

    # `SK` means state dict key
    #
    # Text to parse
    _SK_TXT = 'txt'

    # Row number (0-based)
    _SK_ROW = 'row'

    # Column number (0-based)
    _SK_COL = 'col'

    # Repeated occurrence
    _SK_OCC = 'occ'

    # `DK` means debug dict key
    #
    # Rule name
    _DK_NAME = 'name'

    # Text to parse
    _DK_TXT = 'txt'

    # Position number (0-based)
    _DK_POS = 'pos'

    # Row number (0-based)
    _DK_ROW = 'row'

    # Column number (0-based)
    _DK_COL = 'col'

    # Scan level
    _DK_SLV = 'slv'

    # Scan is success
    _DK_SSS = 'sss'

    _TOKEN_REOS = {
        'arg_kvsep': re.compile('='),
        'arg_sep': re.compile(','),
        'args_sign': re.compile('@'),
        'brkt_beg': re.compile(r'\('),
        'brkt_end': re.compile(r'\)'),
        'code': re.compile(r'(`+)((?:.|\n)*?)\1'),
        'end': re.compile('$'),
        'lit_bool': re.compile('(True|False)(?![a-zA-Z0-9_])'),
        'lit_none': re.compile('None(?![a-zA-Z0-9_])'),
        'lit_num': re.compile(r"""
        ([-+])?         # Sign
        (?=\d|[.]\d)    # Next is an integer part or a fraction part
        (\d*)           # Integer part
        ([.]\d*)?       # Fraction part
        (e[-+]?\d+)?    # Exponent part
        """, re.VERBOSE | re.IGNORECASE),
        'occ01_trailer': re.compile(r'\?'),
        'occ0m_trailer': re.compile(r'\*'),
        'occ1m_trailer': re.compile(r'\+'),
        'or_expr_op': re.compile(r'\|'),
        'regex_str': re.compile('r?(\'\'\'|"""|\'|")((?:[^\\\\]|\\\\.)*?)(\\1)'),
        'rule_colon': re.compile(':'),
        'rule_name': re.compile('[a-zA-Z_][a-zA-Z0-9_]*'),
        'rule_ref': re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)(?![a-zA-Z0-9_])[\s]*(?![:])'),
        'sqrbrkt_beg': re.compile(r'\['),
        'sqrbrkt_end': re.compile(r'\]'),
    }

    def __init__(self, txt, debug=False):
        self._txt = txt

        self._pos = 0

        self._row = 0

        self._col = 0

        self._debug = debug

        self._debug_infos = None

        if self._debug:
            self._debug_infos = []

        self._ws_rep = r'([\s]*(#[^\n]*)?)*'

        self._ws_reo = re.compile(self._ws_rep)\
            if self._ws_rep is not None else None

        # Current rule func's context dict
        self._ctx = None

        # Scan level
        self._scan_lv = -1

        # Scan exc info
        self._scan_ei = None

        # Scan exc infos of current branching
        self._scan_eis = []

        # Scan exc infos of previous branching
        self._scan_eis_prev = []

        self._state_stack = []

    def _peek(self, token_names, is_required=False, is_branch=False):
        for token_name in token_names:
            reo = self._TOKEN_REOS[token_name]

            matched = reo.match(self._txt, self._pos)

            if matched:
                return token_name

        if is_required:
            self._error(token_names=token_names)
        else:
            return None

    def _scan_token(self, token_name, new_ctx=False):
        reo = self._TOKEN_REOS[token_name]

        matched = self._match(reo)

        if matched is None:
            self._error(token_names=[token_name])

        if new_ctx:
            ctx = AttrDict()

            ctx.name = ''

            ctx.par = self._ctx
        else:
            ctx = self._ctx

        ctx.res = matched

        return ctx

    def _scan_rule(self, name):
        ctx_par = self._ctx

        self._scan_lv += 1

        if self._ws_reo:
            self._match(self._ws_reo)

        ctx_new = AttrDict()

        ctx_new.name = name

        ctx_new.par = ctx_par

        self._ctx = ctx_new

        rule_func = self._rule_func_get(name)

        # Scan exc info
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
        except ScanError:
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

        if self._ws_reo:
            self._match(self._ws_reo)

        return ctx_new

    def _match(self, reo):
        matched = reo.match(self._txt, self._pos)

        if matched:
            matched_txt = matched.group()

            matched_len = len(matched_txt)

            if matched_len > 0:
                self._pos += matched_len

                self._update_state(matched_txt)

        return matched

    def _update_state(self, matched_txt):
        row_cnt = matched_txt.count('\n')

        if row_cnt == 0:
            last_row_txt = matched_txt

            self._col += len(last_row_txt)
        else:
            last_row_txt = matched_txt[matched_txt.rfind('\n') + 1:]

            self._row += row_cnt

            self._col = len(last_row_txt)

    def _rule_func_get(self, name):
        rule_func_name = self._RULE_FUNC_PRF + name + self._RULE_FUNC_POF

        rule_func = getattr(self, rule_func_name)

        return rule_func

    def _error(self, token_names):
        raise ScanError(
            ctx=self._ctx,
            txt=self._txt,
            pos=self._pos,
            row=self._row,
            col=self._col,
            token_names=token_names,
            eis=self._scan_eis,
            eisp=self._scan_eis_prev,
        )

    def all(self, ctx):
        # ```
        ctx.opts = None
        # ```
        if self._peek([
            'args_sign',
            'rule_name'],
            is_required=True) == 'args_sign':
            args_def = self._scan_rule('args_def')
            # ```
            ctx.opts = args_def.res
            # ```
        rule_seq = self._scan_rule('rule_seq')
        # ```
        ctx.rule_defs = rule_seq.res
        # ```
        end = self._scan_rule('end')

    def end(self, ctx):
        end = self._scan_token('end')

    def args_def(self, ctx):
        args_sign = self._scan_rule('args_sign')
        args_group = self._scan_rule('args_group')
        # ```
        pairs = []
        item = args_group
        while 'arg_item' in item:
            pairs.append(item.arg_item.res)
            item = item.arg_item
        args = dict(pairs)
        ctx.res = args
        # ```

    def args_sign(self, ctx):
        args_sign = self._scan_token('args_sign')

    def args_group(self, ctx):
        brkt_beg = self._scan_rule('brkt_beg')
        if self._peek(['brkt_end']):
            brkt_end = self._scan_rule('brkt_end')
        elif self._peek(['rule_name'], is_branch=True):
            arg_item = self._scan_rule('arg_item')
        else:
            self._error([
            'rule_name',
            'brkt_end'])

    def brkt_beg(self, ctx):
        brkt_beg = self._scan_token('brkt_beg')

    def brkt_end(self, ctx):
        brkt_end = self._scan_token('brkt_end')

    def arg_item(self, ctx):
        arg_expr = self._scan_rule('arg_expr')
        # ```
        ctx.res = arg_expr.res
        ctx.par.arg_item = ctx
        # ```
        if self._peek(['brkt_end']):
            brkt_end = self._scan_rule('brkt_end')
        elif self._peek(['arg_sep'], is_branch=True):
            arg_sep = self._scan_rule('arg_sep')
            if self._peek(['brkt_end']):
                brkt_end = self._scan_rule('brkt_end')
            elif self._peek(['rule_name'], is_branch=True):
                arg_item = self._scan_rule('arg_item')
            else:
                self._error([
                'rule_name',
                'brkt_end'])
        else:
            self._error([
            'brkt_end',
            'arg_sep'])

    def arg_expr(self, ctx):
        arg_key = self._scan_rule('arg_key')
        arg_kvsep = self._scan_rule('arg_kvsep')
        arg_val = self._scan_rule('arg_val')
        # ```
        ctx.res = (arg_key.res, arg_val.res)
        # ```

    def arg_key(self, ctx):
        arg_key = self._scan_token('rule_name')
        # ```
        ctx.res = arg_key.res.group()
        # ```

    def arg_kvsep(self, ctx):
        arg_kvsep = self._scan_token('arg_kvsep')

    def arg_val(self, ctx):
        lit_val = self._scan_rule('lit_val')
        # ```
        ctx.res = lit_val.res
        # ```

    def lit_val(self, ctx):
        if self._peek(['regex_str']):
            lit_str = self._scan_rule('lit_str')
            # ```
            ctx.res = lit_str.res
            # ```
        elif self._peek(['lit_num'], is_branch=True):
            lit_num = self._scan_rule('lit_num')
            # ```
            ctx.res = lit_num.res
            # ```
        elif self._peek(['lit_bool'], is_branch=True):
            lit_bool = self._scan_rule('lit_bool')
            # ```
            ctx.res = lit_bool.res
            # ```
        elif self._peek(['lit_none'], is_branch=True):
            lit_none = self._scan_rule('lit_none')
            # ```
            ctx.res = lit_none.res
            # ```
        else:
            self._error([
            'lit_num',
            'regex_str',
            'lit_bool',
            'lit_none'])

    def lit_str(self, ctx):
        lit_str = self._scan_token('regex_str')
        # ```
        ctx.res = eval(lit_str.res.group())
        # ```

    def lit_num(self, ctx):
        lit_num = self._scan_token('lit_num')
        # ```
        ctx.res = eval(lit_num.res.group())
        # ```

    def lit_bool(self, ctx):
        lit_bool = self._scan_token('lit_bool')
        # ```
        ctx.res = True if (lit_bool.res.group() == 'True') else False
        # ```

    def lit_none(self, ctx):
        lit_none = self._scan_token('lit_none')
        # ```
        ctx.res = None
        # ```

    def arg_sep(self, ctx):
        arg_sep = self._scan_token('arg_sep')

    def rule_seq(self, ctx):
        # ```
        ctx.res = []
        # ```
        while True:
            rule_def = self._scan_rule('rule_def')
            # ```
            ctx.res.append(rule_def.res)
            # ```
            if self._peek([
                'rule_name',
                'end'],
                is_required=True) != 'rule_name':
                break

    def rule_def(self, ctx):
        rule_name = self._scan_rule('rule_name')
        rule_colon = self._scan_rule('rule_colon')
        # ```
        args = None
        # ```
        if self._peek([
            'args_sign',
            'rule_ref',
            'regex_str',
            'code',
            'brkt_beg',
            'sqrbrkt_beg'],
            is_required=True) == 'args_sign':
            args_def = self._scan_rule('args_def')
            # ```
            args = args_def.res
            # ```
        or_expr = self._scan_rule('or_expr')
        # ```
        ctx.res = RuleDef(name=rule_name.res, item=or_expr.res, args=args)
        # ```

    def rule_name(self, ctx):
        rule_name = self._scan_token('rule_name')
        # ```
        ctx.res = rule_name.res.group()
        # ```

    def rule_colon(self, ctx):
        rule_colon = self._scan_token('rule_colon')

    def or_expr(self, ctx):
        seq_expr = self._scan_rule('seq_expr')
        # ```
        items = [seq_expr.res]
        # ```
        while self._peek([
            'or_expr_op',
            'rule_name',
            'brkt_end',
            'sqrbrkt_end',
            'end'],
            is_required=True) == 'or_expr_op':
            or_expr_op = self._scan_rule('or_expr_op')
            seq_expr = self._scan_rule('seq_expr')
            # ```
            items.append(seq_expr.res)
            # ```
        # ```
        ctx.res = ExprOr(items) if len(items) > 1 else items[0]
        # ```

    def or_expr_op(self, ctx):
        or_expr_op = self._scan_token('or_expr_op')

    def seq_expr(self, ctx):
        # ```
        items = []
        # ```
        while True:
            while self._peek([
                'code',
                'rule_ref',
                'regex_str',
                'brkt_beg',
                'sqrbrkt_beg'],
                is_required=True) == 'code':
                code = self._scan_rule('code')
                # ```
                items.append(code.res)
                # ```
            occ_expr = self._scan_rule('occ_expr')
            # ```
            items.append(occ_expr.res)
            # ```
            while self._peek([
                'code',
                'rule_ref',
                'regex_str',
                'rule_name',
                'brkt_beg',
                'brkt_end',
                'sqrbrkt_beg',
                'sqrbrkt_end',
                'or_expr_op',
                'end'],
                is_required=True) == 'code':
                code = self._scan_rule('code')
                # ```
                items.append(code.res)
                # ```
            if self._peek([
                'rule_ref',
                'regex_str',
                'code',
                'brkt_beg',
                'sqrbrkt_beg',
                'rule_name',
                'brkt_end',
                'sqrbrkt_end',
                'or_expr_op',
                'end'],
                is_required=True) not in [
                'rule_ref',
                'regex_str',
                'code',
                'brkt_beg',
                'sqrbrkt_beg']:
                break
        # ```
        ctx.res = ExprSeq(items) if len(items) > 1 else items[0]
        # ```

    def code(self, ctx):
        code = self._scan_token('code')
        # ```
        ctx.res = Code(code.res.group(2))
        # ```

    def occ_expr(self, ctx):
        if self._peek(['sqrbrkt_beg']):
            occ01_group = self._scan_rule('occ01_group')
            # ```
            ctx.res = occ01_group.res
            # ```
        elif self._peek([
            'rule_ref',
            'regex_str',
            'brkt_beg'], is_branch=True):
            atom = self._scan_rule('atom')
            # ```
            occ_type = None
            # ```
            if self._peek([
                'occ0m_trailer',
                'occ1m_trailer',
                'occ01_trailer',
                'rule_ref',
                'regex_str',
                'rule_name',
                'code',
                'brkt_beg',
                'brkt_end',
                'sqrbrkt_beg',
                'sqrbrkt_end',
                'or_expr_op',
                'end'],
                is_required=True) in [
                'occ0m_trailer',
                'occ1m_trailer',
                'occ01_trailer']:
                if self._peek(['occ01_trailer']):
                    occ01_trailer = self._scan_rule('occ01_trailer')
                    # ```
                    occ_type = 0
                    # ```
                elif self._peek(['occ0m_trailer'], is_branch=True):
                    occ0m_trailer = self._scan_rule('occ0m_trailer')
                    # ```
                    occ_type = 1
                    # ```
                elif self._peek(['occ1m_trailer'], is_branch=True):
                    occ1m_trailer = self._scan_rule('occ1m_trailer')
                    # ```
                    occ_type = 2
                    # ```
                else:
                    self._error([
                    'occ0m_trailer',
                    'occ1m_trailer',
                    'occ01_trailer'])
            # ```
            if occ_type is None:
                ctx.res = atom.res
            elif occ_type == 0:
                item = atom.res

                while isinstance(item, ExprOcc01):
                    item = item.item

                if isinstance(item, ExprOcc0m):
                    ctx.res = item
                elif isinstance(item, ExprOcc1m):
                    ctx.res = ExprOcc0m(item.item)
                else:
                    ctx.res = ExprOcc01(item)
            elif occ_type == 1:
                item = atom.res

                while isinstance(item, (ExprOcc01, ExprOcc0m, ExprOcc1m)):
                    item = item.item

                ctx.res = ExprOcc0m(item)
            elif occ_type == 2:
                item = atom.res

                while isinstance(item, ExprOcc1m):
                    item = item.item

                if isinstance(item, ExprOcc01):
                    ctx.res = ExprOcc0m(item.item)
                elif isinstance(item, ExprOcc0m):
                    ctx.res = item
                else:
                    ctx.res = ExprOcc1m(item)
            else:
                assert 0
            # ```
        else:
            self._error([
            'rule_ref',
            'regex_str',
            'brkt_beg',
            'sqrbrkt_beg'])

    def occ01_group(self, ctx):
        sqrbrkt_beg = self._scan_rule('sqrbrkt_beg')
        or_expr = self._scan_rule('or_expr')
        sqrbrkt_end = self._scan_rule('sqrbrkt_end')
        # ```
        item = or_expr.res

        while isinstance(item, ExprOcc01):
            item = item.item

        if isinstance(item, ExprOcc0m):
            ctx.res = item
        elif isinstance(item, ExprOcc1m):
            ctx.res = ExprOcc0m(item.item)
        else:
            ctx.res = ExprOcc01(item)
        # ```

    def sqrbrkt_beg(self, ctx):
        sqrbrkt_beg = self._scan_token('sqrbrkt_beg')

    def sqrbrkt_end(self, ctx):
        sqrbrkt_end = self._scan_token('sqrbrkt_end')

    def occ01_trailer(self, ctx):
        occ01_trailer = self._scan_token('occ01_trailer')

    def occ0m_trailer(self, ctx):
        occ0m_trailer = self._scan_token('occ0m_trailer')

    def occ1m_trailer(self, ctx):
        occ1m_trailer = self._scan_token('occ1m_trailer')

    def atom(self, ctx):
        if self._peek(['regex_str']):
            regex_str = self._scan_rule('regex_str')
            # ```
            args = None
            # ```
            if self._peek([
                'args_sign',
                'rule_ref',
                'regex_str',
                'rule_name',
                'code',
                'brkt_beg',
                'brkt_end',
                'occ0m_trailer',
                'occ1m_trailer',
                'occ01_trailer',
                'sqrbrkt_beg',
                'sqrbrkt_end',
                'or_expr_op',
                'end'],
                is_required=True) == 'args_sign':
                args_def = self._scan_rule('args_def')
                # ```
                args = args_def.res
                # ```
            # ```
            ctx.res = Pattern(regex_str.res, args=args)
            # ```
        elif self._peek(['rule_ref'], is_branch=True):
            rule_ref = self._scan_rule('rule_ref')
            # ```
            ctx.res = rule_ref.res
            # ```
        elif self._peek(['brkt_beg'], is_branch=True):
            group = self._scan_rule('group')
            # ```
            ctx.res = group.res
            # ```
        else:
            self._error([
            'rule_ref',
            'regex_str',
            'brkt_beg'])

    def regex_str(self, ctx):
        regex_str = self._scan_token('regex_str')
        # ```
        ctx.res = regex_str.res.group()
        # ```

    def rule_ref(self, ctx):
        rule_ref = self._scan_token('rule_ref')
        # ```
        name = rule_ref.res.group(1)
        ctx.res = RuleRef(name)
        # ```

    def group(self, ctx):
        brkt_beg = self._scan_rule('brkt_beg')
        or_expr = self._scan_rule('or_expr')
        brkt_end = self._scan_rule('brkt_end')
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
            indent='    ' * debug_info.slv,
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


def scan_error_to_msg(exc_info, scan_error_class, title, txt):
    msg = title

    exc = exc_info[1]

    if not isinstance(exc, scan_error_class):
        tb_lines = format_exception(*exc_info)

        tb_msg = ''.join(tb_lines)

        msg += '\n---\n{}---\n'.format(tb_msg)

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
        msg = 'Possible reasons:'

        msgs.append(msg)

        for reason_exc_info in reason_exc_infos:
            exc = reason_exc_info[1]

            ctx_names = get_ctx_names(exc.ctx)

            ctx_msg = ''

            if ctx_names:
                ctx_msg = ' '.join(ctx_names)

            row_txt = rows[exc.row]

            col_mark = ' ' * exc.col + '^'

            msg = (
                'Rule `{rule}` failed at {row}.{col} ({pos})'
                ' (ctx: {ctx_msg}):\n'
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
        rules_txt = open(source_file_path).read()
    except Exception:
        msg = 'Failed reading source file: `{0}`\n'.format(source_file_path)

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
        msg = scan_error_to_msg(
            exc_info=exc_info,
            scan_error_class=ScanError,
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
    exit(main())
