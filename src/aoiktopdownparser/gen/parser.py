# coding: utf-8
from __future__ import absolute_import

from pprint import pformat
import re
import sys
from traceback import format_exception

from aoiktopdownparser.gen.ast import Code
from aoiktopdownparser.gen.ast import ExprOcc01
from aoiktopdownparser.gen.ast import ExprOcc0m
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

    def __init__(self, ctx, txt, row, col, rep=None, eis=None, eisp=None):
        self.ctx = ctx

        newline_idx = txt.find('\n')
        if newline_idx >= 0:
            self.txt = txt[:newline_idx]
        else:
            self.txt = txt

        self.row = row

        self.col = col

        self.rep = rep

        # scan exc infos of current branching
        self.eis = eis

        # scan exc infos of previous branching
        self.eisp = eisp


Er = ScanError


class ScanOk(Exception):
    pass


Ok = ScanOk


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

    # Row number (0-based)
    _DK_ROW = 'row'

    # Column number (0-based)
    _DK_COL = 'col'

    # Scan level
    _DK_SLV = 'slv'

    # Scan is success
    _DK_SSS = 'sss'


    _REO_01 = re.compile('$')
    _REO_02 = re.compile('@')
    _REO_03 = re.compile('[(]')
    _REO_04 = re.compile('[)]')
    _REO_05 = re.compile('[*]')
    _REO_06 = re.compile('[+]')
    _REO_07 = re.compile('[,]')
    _REO_08 = re.compile('[:]')
    _REO_09 = re.compile('[=]')
    _REO_10 = re.compile('[?]')
    _REO_11 = re.compile('[|]')
    _REO_12 = re.compile(r'\[')
    _REO_13 = re.compile(r'\]')
    _REO_14 = re.compile(r'(`+)((?:.|\n)*?)\1')
    _REO_15 = re.compile('None(?![a-zA-Z0-9_])')
    _REO_16 = re.compile('[a-zA-Z_][a-zA-Z0-9_]*')
    _REO_17 = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    _REO_18 = re.compile('(True|False)(?![a-zA-Z0-9_])')
    _REO_19 = re.compile('r?(\'\'\'|"""|\'|")((?:[^\\\\]|\\\\.)*?)(\\1)')
    _REO_20 = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)(?![a-zA-Z0-9_])[\s]*(?![:])')
    _REO_21 = re.compile(r"""
    ([-+])?         # Sign
    (?=\d|[.]\d)    # Next is an integer part or a fraction part
    (\d*)           # Integer part
    ([.]\d*)?       # Fraction part
    (e[-+]?\d+)?    # Exponent part
    """, re.VERBOSE | re.IGNORECASE)

    def __init__(self, txt, debug=False):
        self._txt = txt

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

    def _rule_func_get(self, name):
        rule_func_name = self._RULE_FUNC_PRF + name + self._RULE_FUNC_POF

        rule_func = getattr(self, rule_func_name)

        return rule_func

    def _match(self, reo, txt):
        matched = reo.match(txt)

        if matched:
            matched_len = len(matched.group())

            if matched_len > 0:
                matched_txt = txt[:matched_len]

                self._update_state(matched_txt)

                txt = txt[matched_len:]

        return matched, txt

    def _peek(self, reos):
        for reo in reos:

            matched = reo.match(self._txt)

            if matched:
                return True

        return False

    def _scan_rule(self, name):
        ctx_par = self._ctx

        self._scan_lv += 1

        if self._ws_reo:
            _, self._txt = self._match(self._ws_reo, self._txt)

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
            _, self._txt = self._match(self._ws_reo, self._txt)

        return ctx_new

    def _scan_reo(self, reo, new_ctx=False):
        matched, self._txt = self._match(reo, self._txt)

        if matched is None:
            self._error(rep=reo.pattern)

        if new_ctx:
            ctx = AttrDict()

            ctx.name = ''

            ctx.par = self._ctx
        else:
            ctx = self._ctx

        ctx.rem = matched

        return ctx

    def _update_state(self, matched_txt):
        row_cnt = matched_txt.count('\n')

        if row_cnt == 0:
            last_row_txt = matched_txt

            self._col += len(last_row_txt)
        else:
            last_row_txt = matched_txt[matched_txt.rfind('\n') + 1:]

            self._row += row_cnt

            self._col = len(last_row_txt)

    def _error(self, rep=None):
        raise ScanError(
            ctx=self._ctx,
            txt=self._txt,
            row=self._row,
            col=self._col,
            rep=rep,
            eis=self._scan_eis,
            eisp=self._scan_eis_prev,
        )

    def all(self, ctx):
        #```
        ctx.opts = None
        #```
        if self._peek([self._REO_02]):
            args_def = self._scan_rule('args_def')
            #```
            ctx.opts = args_def.res
            #```
        rule_seq = self._scan_rule('rule_seq')
        #```
        ctx.rule_defs = rule_seq.res
        #```
        _ = self._scan_reo(self._REO_01)
    
    def args_def(self, ctx):
        args_sign = self._scan_rule('args_sign')
        args_group = self._scan_rule('args_group')
        #```
        pairs = []
        item = args_group
        while 'arg_item' in item:
            pairs.append(item.arg_item.res)
            item = item.arg_item
        args = dict(pairs)
        ctx.res = args
        #```
    
    def args_sign(self, ctx):
        args_sign = self._scan_reo(self._REO_02)
    
    def args_group(self, ctx):
        brkt_beg = self._scan_rule('brkt_beg')
        if self._peek([self._REO_04]):
            brkt_end = self._scan_rule('brkt_end')
        elif self._peek([self._REO_16]):
            arg_item = self._scan_rule('arg_item')
        else:
            self._error()
    
    def brkt_beg(self, ctx):
        brkt_beg = self._scan_reo(self._REO_03)
    
    def brkt_end(self, ctx):
        brkt_end = self._scan_reo(self._REO_04)
    
    def arg_item(self, ctx):
        arg_expr = self._scan_rule('arg_expr')
        #```
        ctx.res = arg_expr.res
        ctx.par.arg_item = ctx
        #```
        if self._peek([self._REO_04]):
            brkt_end = self._scan_rule('brkt_end')
        elif self._peek([self._REO_07]):
            arg_sep = self._scan_rule('arg_sep')
            if self._peek([self._REO_04]):
                brkt_end = self._scan_rule('brkt_end')
            elif self._peek([self._REO_16]):
                arg_item = self._scan_rule('arg_item')
            else:
                self._error()
        else:
            self._error()
    
    def arg_expr(self, ctx):
        arg_key = self._scan_rule('arg_key')
        arg_kvsep = self._scan_rule('arg_kvsep')
        arg_val = self._scan_rule('arg_val')
        #```
        ctx.res = (arg_key.res, arg_val.res)
        #```
    
    def arg_key(self, ctx):
        arg_key = self._scan_reo(self._REO_16)
        #```
        ctx.res = arg_key.rem.group()
        #```
    
    def arg_kvsep(self, ctx):
        arg_kvsep = self._scan_reo(self._REO_09)
    
    def arg_val(self, ctx):
        lit_val = self._scan_rule('lit_val')
        #```
        ctx.res = lit_val.res
        #```
    
    def lit_val(self, ctx):
        if self._peek([self._REO_19]):
            lit_str = self._scan_rule('lit_str')
            #```
            ctx.res = lit_str.res
            #```
        elif self._peek([self._REO_21]):
            lit_num = self._scan_rule('lit_num')
            #```
            ctx.res = lit_num.res
            #```
        elif self._peek([self._REO_18]):
            lit_bool = self._scan_rule('lit_bool')
            #```
            ctx.res = lit_bool.res
            #```
        elif self._peek([self._REO_15]):
            lit_none = self._scan_rule('lit_none')
            #```
            ctx.res = lit_none.res
            #```
        else:
            self._error()
    
    def lit_str(self, ctx):
        lit_str = self._scan_reo(self._REO_19)
        #```
        ctx.res = eval(lit_str.rem.group())
        #```
    
    def lit_num(self, ctx):
        lit_num = self._scan_reo(self._REO_21)
        #```
        ctx.res = eval(lit_num.rem.group())
        #```
    
    def lit_bool(self, ctx):
        lit_bool = self._scan_reo(self._REO_18)
        #```
        ctx.res = True if (lit_bool.rem.group() == 'True') else False
        #```
    
    def lit_none(self, ctx):
        lit_none = self._scan_reo(self._REO_15)
        #```
        ctx.res = None
        #```
    
    def arg_sep(self, ctx):
        arg_sep = self._scan_reo(self._REO_07)
    
    def rule_seq(self, ctx):
        #```
        ctx.res = []
        #```
        if not self._peek([self._REO_17]):
            self._error()
        while self._peek([self._REO_17]):
            rule_def = self._scan_rule('rule_def')
            #```
            ctx.res.append(rule_def.res)
            #```
    
    def rule_def(self, ctx):
        rule_name = self._scan_rule('rule_name')
        rule_colon = self._scan_rule('rule_colon')
        #```
        args = None
        #```
        if self._peek([self._REO_02]):
            args_def = self._scan_rule('args_def')
            #```
            args = args_def.res
            #```
        or_expr = self._scan_rule('or_expr')
        #```
        ctx.res = RuleDef(name=rule_name.res, expr=or_expr.res, args=args)
        #```
    
    def rule_name(self, ctx):
        rule_name = self._scan_reo(self._REO_17)
        #```
        ctx.res = rule_name.rem.group()
        #```
    
    def rule_colon(self, ctx):
        rule_colon = self._scan_reo(self._REO_08)
    
    def or_expr(self, ctx):
        seq_expr = self._scan_rule('seq_expr')
        #```
        items = [seq_expr.res]
        #```
        while self._peek([self._REO_11]):
            or_expr_op = self._scan_rule('or_expr_op')
            seq_expr = self._scan_rule('seq_expr')
            #```
            items.append(seq_expr.res)
            #```
        #```
        ctx.res = ExprOr(items) if len(items) > 1 else items[0]
        #```
    
    def or_expr_op(self, ctx):
        or_expr_op = self._scan_reo(self._REO_11)
    
    def seq_expr(self, ctx):
        #```
        items = []
        #```
        if not self._peek([self._REO_03,
            self._REO_12,
            self._REO_14,
            self._REO_19,
            self._REO_20]):
            self._error()
        while self._peek([self._REO_03,
            self._REO_12,
            self._REO_14,
            self._REO_19,
            self._REO_20]):
            while self._peek([self._REO_14]):
                code = self._scan_rule('code')
                #```
                items.append(code.res)
                #```
            occ_expr = self._scan_rule('occ_expr')
            #```
            items.append(occ_expr.res)
            #```
            while self._peek([self._REO_14]):
                code = self._scan_rule('code')
                #```
                items.append(code.res)
                #```
        #```
        ctx.res = ExprSeq(items) if len(items) > 1 else items[0]
        #```
    
    def code(self, ctx):
        code = self._scan_reo(self._REO_14)
        #```
        ctx.res = Code(code.rem.group(2))
        #```
    
    def occ_expr(self, ctx):
        if self._peek([self._REO_12]):
            occ01_group = self._scan_rule('occ01_group')
            #```
            ctx.res = ExprOcc01(occ01_group.res)
            #```
        elif self._peek([self._REO_03,
            self._REO_19,
            self._REO_20]):
            atom = self._scan_rule('atom')
            #```
            occ_type = None
            #```
            if self._peek([self._REO_05,
                self._REO_06,
                self._REO_10]):
                if self._peek([self._REO_10]):
                    occ01_trailer = self._scan_rule('occ01_trailer')
                    #```
                    occ_type = 0
                    #```
                elif self._peek([self._REO_05]):
                    occ0m_trailer = self._scan_rule('occ0m_trailer')
                    #```
                    occ_type = 1
                    #```
                elif self._peek([self._REO_06]):
                    occ1m_trailer = self._scan_rule('occ1m_trailer')
                    #```
                    occ_type = 2
                    #```
                else:
                    self._error()
            #```
            if occ_type is None:
                ctx.res = atom.res
            elif occ_type == 0:
                ctx.res = ExprOcc01(atom.res)
            elif occ_type == 1:
                ctx.res = ExprOcc0m(atom.res)
            elif occ_type == 2:
                ctx.res = ExprOcc1m(atom.res)
            else:
                assert 0
            #```
        else:
            self._error()
    
    def occ01_group(self, ctx):
        sqrbrkt_beg = self._scan_rule('sqrbrkt_beg')
        or_expr = self._scan_rule('or_expr')
        sqrbrkt_end = self._scan_rule('sqrbrkt_end')
        #```
        ctx.res = or_expr.res
        #```
    
    def sqrbrkt_beg(self, ctx):
        sqrbrkt_beg = self._scan_reo(self._REO_12)
    
    def sqrbrkt_end(self, ctx):
        sqrbrkt_end = self._scan_reo(self._REO_13)
    
    def occ01_trailer(self, ctx):
        occ01_trailer = self._scan_reo(self._REO_10)
    
    def occ0m_trailer(self, ctx):
        occ0m_trailer = self._scan_reo(self._REO_05)
    
    def occ1m_trailer(self, ctx):
        occ1m_trailer = self._scan_reo(self._REO_06)
    
    def atom(self, ctx):
        if self._peek([self._REO_19]):
            regex_str = self._scan_rule('regex_str')
            #```
            args = None
            #```
            if self._peek([self._REO_02]):
                args_def = self._scan_rule('args_def')
                #```
                args = args_def.res
                #```
            #```
            ctx.res = Pattern(regex_str.res, args=args)
            #```
        elif self._peek([self._REO_20]):
            rule_ref = self._scan_rule('rule_ref')
            #```
            ctx.res = rule_ref.res
            #```
        elif self._peek([self._REO_03]):
            group = self._scan_rule('group')
            #```
            ctx.res = group.res
            #```
        else:
            self._error()
    
    def regex_str(self, ctx):
        regex_str = self._scan_reo(self._REO_19)
        #```
        ctx.res = regex_str.rem.group()
        #```
    
    def rule_ref(self, ctx):
        rule_ref = self._scan_reo(self._REO_20)
        #```
        name = rule_ref.rem.group(1)
        ctx.res = RuleRef(name)
        #```
    
    def group(self, ctx):
        brkt_beg = self._scan_rule('brkt_beg')
        or_expr = self._scan_rule('or_expr')
        brkt_end = self._scan_rule('brkt_end')
        #```
        ctx.res = or_expr.res
        #```


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


def parser_debug_infos_to_msg(debug_infos, txt):
    rows = txt.split('\n')

    msgs = []

    for debug_info in debug_infos:
        row_txt = rows[debug_info.row]

        msg = '{indent}{err}{name}: {row}.{col}: |{txt}|{row_txt}'.format(
            name=debug_info.name,
            indent='    ' * debug_info.slv,
            err='' if debug_info.sss else '!',
            row=debug_info.row + 1,
            col=debug_info.col + 1,
            txt=row_txt[debug_info.col:],
            row_txt=(
                ', |' + row_txt[:debug_info.col] + '^' +
                row_txt[debug_info.col:] + '|'
            )
            if debug_info.col != 0 else '',
        )

        msgs.append(msg)

    msg = '\n'.join(msgs)

    return msg


def scan_errror_to_msg(exc_info, exc_class, title, txt):
    msg = title

    exc = exc_info[1]

    if not isinstance(exc, exc_class):
        tb_lines = format_exception(*exc_info)

        tb_msg = ''.join(tb_lines)

        msg += '\n---\n{}---\n'.format(tb_msg)

        return msg

    msgs = []

    msgs.append(msg)

    ctx_names = get_ctx_names(exc.ctx)

    ctx_msg = ''

    if ctx_names:
        ctx_msg = ' '.join(ctx_names)

    rows = txt.split('\n')

    row_txt = rows[exc.row]

    col_mark = ' ' * exc.col + '^'

    msg = (
        '# `{rule}` failed at {row}.{col} ({ctx_msg})\n'
        '{row_txt}\n'
        '{col_mark}'
    ).format(
        rule=exc.ctx.name,
        row=exc.row + 1,
        col=exc.col + 1,
        ctx_msg=ctx_msg,
        row_txt=row_txt,
        col_mark=col_mark,
    )

    msgs.append(msg)

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
                '# `{rule}` failed at {row}.{col} ({ctx_msg})\n'
                '{row_txt}\n'
                '{col_mark}'
            ).format(
                rule=exc.ctx.name,
                row=exc.row + 1,
                col=exc.col + 1,
                ctx_msg=ctx_msg,
                row_txt=row_txt,
                col_mark=col_mark,
            )

            msgs.append(msg)

    msg = '\n\n'.join(msgs)

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
    from argparse import ArgumentParser

    args_parser = ArgumentParser()

    args_parser.add_argument('-f', dest='input_file_path', required=True)

    args_parser.add_argument('-d', dest='debug_on', action='store_true')

    args_obj = args_parser.parse_args(args)

    input_file_path = args_obj.input_file_path

    try:
        rules_txt = open(input_file_path).read()
    except Exception:
        msg = 'Failed reading input file: `{0}`\n'.format(input_file_path)

        sys.stderr.write(msg)

        return 1

    debug_on = args_obj.debug_on

    parser, parsing_result, exc_info = parse(rules_txt, debug=debug_on)

    if debug_on and parser._debug_infos:
        msg = '# Parser debug info\n'

        msg += parser_debug_infos_to_msg(
            debug_infos=parser._debug_infos, txt=rules_txt
        )

        msg += '\n\n'

        sys.stderr.write(msg)

    if exc_info is not None:
        msg = scan_errror_to_msg(
            exc_info=exc_info,
            exc_class=ScanError,
            title='# Parsing error',
            txt=rules_txt,
        )

        sys.stderr.write(msg)

        return 2

    msg = '# Parsing result\n{0}\n'.format(
        pformat(parsing_result, indent=4, width=1)
    )

    sys.stderr.write(msg)

    return 0


if __name__ == '__main__':
    exit(main())
