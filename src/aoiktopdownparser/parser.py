# coding: utf-8
from __future__ import absolute_import
import re
import sys
from aoiktopdownparser.gen.ast import Code
from aoiktopdownparser.gen.ast import ExprOcc01
from aoiktopdownparser.gen.ast import ExprOcc0m
from aoiktopdownparser.gen.ast import ExprOcc1m
from aoiktopdownparser.gen.ast import ExprOr
from aoiktopdownparser.gen.ast import ExprSeq
from aoiktopdownparser.gen.ast import Pattern
from aoiktopdownparser.gen.ast import RuleDef
from aoiktopdownparser.gen.ast import RuleRef

#/
class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

#/
class ScanError(Exception):

    def __init__(self, ctx, txt, row, col, rep=None, eis=None, eisp=None):
        #/
        self.ctx = ctx

        #/
        newline_idx = txt.find('\n')
        if newline_idx >= 0:
            self.txt = txt[:newline_idx]
        else:
            self.txt = txt

        #/
        self.row = row

        self.col = col

        #/
        self.rep = rep

        #/ scan exc infos of current branching
        self.eis = eis

        #/ scan exc infos of previous branching
        self.eisp = eisp

Er = ScanError

#/
class ScanOk(Exception):
    pass

Ok = ScanOk

#/
class Parser(object):

    #/
    _RULE_FUNC_PRF = ''
    _RULE_FUNC_POF = ''

    #/ |SK| means state dict key
    _SK_TXT = 'txt'
    _SK_ROW = 'row'
    _SK_COL = 'col'
    _SK_OCC = 'occ'

    #/ |DK| means debug dict key
    _DK_NAME = 'name'
    _DK_TXT = 'txt'
    _DK_ROW = 'row'
    _DK_COL = 'col'
    _DK_SLV = 'slv'
    _DK_SSS = 'sss' # scan is success

    #/
    def __init__(self, txt, debug=False):
        #/
        self._txt = txt

        self._row = 0

        self._col = 0

        #/
        self._debug = debug

        #/
        self._debug_info_s = None

        if self._debug:
            self._debug_info_s = []

        #/
        self._ws_rep = r'([\s]*(#[^\n]*)?)*'

        self._ws_reo = re.compile(self._ws_rep)\
            if self._ws_rep is not None else None

        #/ current rule func's context dict
        self._ctx = None

        #/
        self._ctx_k_par = 'par'

        #/ scan level
        self._scan_lv = -1

        #/ scan exc info
        self._scan_ei = None

        #/ scan exc infos of current branching
        self._scan_ei_s = []

        #/ scan exc infos of previous branching
        self._scan_ei_sp = []

        #/ map rep to reo
        self._reo_d = {}

        #/
        self._state_stack = []

    def _rule_func_get(self, name):
        #/
        rule_func_name = self._RULE_FUNC_PRF + name + self._RULE_FUNC_POF

        #/
        rule_func = getattr(self, rule_func_name)

        #/
        return rule_func

    def _rule_reo_get(self, name):
        #/
        reo_name = self._RULE_REO_PRF \
            + name \
            + self._RULE_REO_POF

        #/
        reo = getattr(self, reo_name)

        #/
        return reo

    def _match(self, reo, txt):
        #/
        m = reo.match(txt)

        #/
        if m:
            mlen = len(m.group())

            if mlen > 0:
                m_txt = txt[:mlen]

                self._state_upd(m_txt)

                txt = txt[mlen:]

        #/
        return m, txt

    def _scan(self, name):
        #/
        ctx_par = self._ctx

        #/
        self._scan_lv += 1

        #/
        if self._ws_reo:
            _, self._txt = self._match(self._ws_reo, self._txt)

        #/
        ctx_new = AttrDict()

        #/
        ctx_new.name = name

        #/
        if self._ctx_k_par:
            ctx_new[self._ctx_k_par] = ctx_par

        #/
        self._ctx = ctx_new

        #/
        rule_func = self._rule_func_get(name)

        #/ scan success
        self._ss = False

        #/ scan exc info
        self._scan_ei = None

        #/
        if self._debug:
            #/
            debug_info = AttrDict()
            debug_info[self._DK_NAME] = name
            debug_info[self._DK_TXT] = self._txt
            debug_info[self._DK_ROW] = self._row
            debug_info[self._DK_COL] = self._col
            debug_info[self._DK_SLV] = self._scan_lv
            debug_info[self._DK_SSS] = False

            #/
            self._debug_info_s.append(debug_info)

        #/
        try:
            rule_func(ctx_new)
        except ScanError:
            #/
            ei = sys.exc_info()

            #/
            if self._scan_ei is None or self._scan_ei[1] is not ei[1]:
                self._scan_ei = ei

                self._scan_ei_s.append(ei)

            #/
            raise
        else:
            #/
            if self._debug:
                debug_info[self._DK_SSS] = True
        finally:
            self._scan_lv -= 1

            self._ctx = ctx_par

        #/
        self._ss = True

        #/
        if self._ws_reo:
            _, self._txt = self._match(self._ws_reo, self._txt)

        #/
        return ctx_new

    def _scan_reo(self, reo, new_ctx=False):
        #/
        m, self._txt = self._match(reo, self._txt)

        #/
        if m is None:
            self._error(rep=reo.pattern)

        #/
        if new_ctx:
            #/
            ctx = AttrDict()

            #/
            ctx.name = ''

            #/
            if self._ctx_k_par:
                ctx[self._ctx_k_par] = self._ctx
        else:
            ctx = self._ctx

        #/
        ctx.rem = m

        #/
        return ctx

    def _scan_rep(self, rep):
        #/
        reo = self._reo_d.get(rep, None)

        if reo is None:
            reo = self._reo_d[rep] = re.compile(rep)

        #/
        return self._scan_reo(reo, new_ctx=True)

    def _state_push(self):
        self._state_stack.append({
            self._SK_TXT: self._txt,
            self._SK_ROW: self._row,
            self._SK_COL: self._col,
            self._SK_OCC: 0,
        })

    def _state_pop(self):
        res = self._state_stack.pop()
        self._txt = res[self._SK_TXT]
        self._row = res[self._SK_ROW]
        self._col = res[self._SK_COL]
        return res

    def _state_save(self):
        self._state_stack[-1][self._SK_TXT] = self._txt
        self._state_stack[-1][self._SK_ROW] = self._row
        self._state_stack[-1][self._SK_COL] = self._col
        self._state_stack[-1][self._SK_OCC] += 1

    def _state_upd(self, m_txt):
        row_cnt = m_txt.count('\n')

        if row_cnt == 0:
            last_row_txt = m_txt

            self._col += len(last_row_txt)
        else:
            last_row_txt = m_txt[m_txt.rfind('\n')+1:]

            self._row += row_cnt

            self._col = len(last_row_txt)

    def _or(self, succ=None):
        if succ is None:
            self._or_beg()
        else:
            self._or_end(succ)

    def _or_beg(self):
        #/
        self._scan_ei_sp = self._scan_ei_s

        self._scan_ei_s = []

    def _or_end(self, succ):
        if not succ:
            self._error()

    def _ori(self, succ=None):
        if succ is None:
            self._ori_beg()
        else:
            self._ori_end(succ)

    def _ori_beg(self):
        #/
        self._state_push()

    def _ori_end(self, succ):
        #/
        if succ:
            #/
            self._state_save()

        #/
        self._state_pop()

        #/
        if succ:
            raise ScanOk()

    def _o01(self, succ=None):
        if succ is None:
            self._o01_beg()
        else:
            self._o01_end(succ)

    def _o01_beg(self):
        #/
        self._scan_ei_sp = self._scan_ei_s

        self._scan_ei_s = []

        #/
        self._state_push()

    def _o01_end(self, succ):
        #/
        if succ:
            #/
            self._state_save()

        #/
        self._state_pop()

        #/
        self._ss = True

    def _o0m(self, succ=None):
        if succ is None:
            self._o0m_beg()
        elif succ:
            self._state_save()
        else:
            self._o0m_end()

    def _o0m_beg(self):
        #/
        self._scan_ei_sp = self._scan_ei_s

        self._scan_ei_s = []

        #/
        self._state_push()

    def _o0m_end(self):
        #/
        self._state_pop()

        #/
        self._ss = True

    def _o1m(self, succ=None):
        if succ is None:
            self._o1m_beg()
        elif succ:
            self._state_save()
        else:
            self._o1m_end()

    def _o1m_beg(self):
        #/
        self._scan_ei_sp = self._scan_ei_s

        self._scan_ei_s = []

        #/
        self._state_push()

    def _o1m_end(self):
        #/
        res = self._state_pop()

        #/
        self._ss = res[self._SK_OCC] > 0

        #/
        if not self._ss:
            self._error()

    def _error(self, rep=None):
        raise ScanError(
            ctx=self._ctx,
            txt=self._txt,
            row=self._row,
            col=self._col,
            rep=rep,
            eis=self._scan_ei_s,
            eisp=self._scan_ei_sp,
        )

    @staticmethod
    def _opts_get(arg_group):
        #/
        pair_s = []
        item = arg_group
        while 'arg_item' in item:
            pair_s.append(item.arg_item.res)
            item = item.arg_item
        opts = dict(pair_s)
        return opts

    def all(self, _ctx):
        #/
        self._o01()
        try:
            #```
            _ctx.args = None
            #```
            args_def = self._scan('args_def')
            #```
            _ctx.args = args_def.res
            #```
        except Er: self._o01(0)
        else: self._o01(1)
        rule_seq = self._scan('rule_seq')
        #```
        _ctx.rule_def_s = rule_seq.res
        #```
        _rep = self._scan_rep('$')
    
    def args_def(self, _ctx):
        args_sign = self._scan('args_sign')
        args_group = self._scan('args_group')
        #```
        _ctx.res = self._opts_get(args_group)
        #```
    
    args_sign_REO = re.compile(r'@')
    def args_sign(self, _ctx):
        args_sign = self._scan_reo(self.args_sign_REO)
    
    def args_group(self, _ctx):
        brkt_beg = self._scan('brkt_beg')
        #/
        self._or()
        try:
            #/
            self._ori()
            try:
                brkt_end = self._scan('brkt_end')
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                arg_item = self._scan('arg_item')
            except Er: self._ori(0)
            else: self._ori(1)
        except Ok: self._or(1)
        else: self._or(0)
    
    brkt_beg_REO = re.compile(r'[(]')
    def brkt_beg(self, _ctx):
        brkt_beg = self._scan_reo(self.brkt_beg_REO)
    
    brkt_end_REO = re.compile(r'[)]')
    def brkt_end(self, _ctx):
        brkt_end = self._scan_reo(self.brkt_end_REO)
    
    def arg_item(self, _ctx):
        arg_expr = self._scan('arg_expr')
        #```
        _ctx.res = arg_expr.res
        _ctx.par.arg_item = _ctx
        #```
        #/
        self._or()
        try:
            #/
            self._ori()
            try:
                brkt_end = self._scan('brkt_end')
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                arg_sep = self._scan('arg_sep')
                #/
                self._or()
                try:
                    #/
                    self._ori()
                    try:
                        brkt_end = self._scan('brkt_end')
                    except Er: self._ori(0)
                    else: self._ori(1)
                    #/
                    self._ori()
                    try:
                        arg_item = self._scan('arg_item')
                    except Er: self._ori(0)
                    else: self._ori(1)
                except Ok: self._or(1)
                else: self._or(0)
            except Er: self._ori(0)
            else: self._ori(1)
        except Ok: self._or(1)
        else: self._or(0)
    
    def arg_expr(self, _ctx):
        arg_key = self._scan('arg_key')
        arg_kvsep = self._scan('arg_kvsep')
        arg_val = self._scan('arg_val')
        #```
        _ctx.res = (arg_key.res, arg_val.res)
        #```
    
    arg_key_REO = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def arg_key(self, _ctx):
        arg_key = self._scan_reo(self.arg_key_REO)
        #```
        _ctx.res = arg_key.rem.group()
        #```
    
    arg_kvsep_REO = re.compile(r'[=]')
    def arg_kvsep(self, _ctx):
        arg_kvsep = self._scan_reo(self.arg_kvsep_REO)
    
    def arg_val(self, _ctx):
        lit_val = self._scan('lit_val')
        #```
        _ctx.res = lit_val.res
        #```
    
    def lit_val(self, _ctx):
        #/
        self._or()
        try:
            #/
            self._ori()
            try:
                lit_str = self._scan('lit_str')
                #```
                _ctx.res = lit_str.res
                #```
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                lit_num = self._scan('lit_num')
                #```
                _ctx.res = lit_num.res
                #```
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                lit_bool = self._scan('lit_bool')
                #```
                _ctx.res = lit_bool.res
                #```
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                lit_none = self._scan('lit_none')
                #```
                _ctx.res = lit_none.res
                #```
            except Er: self._ori(0)
            else: self._ori(1)
        except Ok: self._or(1)
        else: self._or(0)
    
    lit_str_REO = re.compile('r?(\'\'\'|"""|\'|")((?:[^\\\\]|\\\\.)*?)(\\1)')
    def lit_str(self, _ctx):
        lit_str = self._scan_reo(self.lit_str_REO)
        #```
        _ctx.res = eval(lit_str.rem.group())
        #```
    
    lit_num_REO = re.compile(r"""
    ([-+])?         # sign
    (?=\d|[.]\d)    # next is an integer part or a fraction part
    (\d*)           # integer part
    ([.]\d*)?       # fraction part
    (e[-+]?\d+)?    # exponent part
    """, re.VERBOSE | re.IGNORECASE)
    def lit_num(self, _ctx):
        lit_num = self._scan_reo(self.lit_num_REO)
        #```
        _ctx.res = eval(lit_num.rem.group())
        #```
    
    lit_bool_REO = re.compile(r'(True|False)(?![a-zA-Z0-9_])')
    def lit_bool(self, _ctx):
        lit_bool = self._scan_reo(self.lit_bool_REO)
        #```
        _ctx.res = True if (lit_bool.rem.group() == 'True') else False
        #```
    
    lit_none_REO = re.compile(r'None(?![a-zA-Z0-9_])')
    def lit_none(self, _ctx):
        lit_none = self._scan_reo(self.lit_none_REO)
        #```
        _ctx.res = None
        #```
    
    arg_sep_REO = re.compile(r'[,]')
    def arg_sep(self, _ctx):
        arg_sep = self._scan_reo(self.arg_sep_REO)
    
    def rule_seq(self, _ctx):
        #```
        _ctx.res = []
        #```
        #/
        self._o1m()
        try:
            while 1:
                rule_def = self._scan('rule_def')
                #```
                _ctx.res.append(rule_def.res)
                #```
                self._o1m(1)
        except Er: self._o1m(0)
    
    def rule_def(self, _ctx):
        rule_name = self._scan('rule_name')
        rule_colon = self._scan('rule_colon')
        #```
        args = None
        #```
        #/
        self._o01()
        try:
            args_def = self._scan('args_def')
            #```
            args = args_def.res
            #```
        except Er: self._o01(0)
        else: self._o01(1)
        rexpr_or = self._scan('rexpr_or')
        #```
        _ctx.res = RuleDef(name=rule_name.res, expr=rexpr_or.res, args=args)
        #```
    
    rule_name_REO = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def rule_name(self, _ctx):
        rule_name = self._scan_reo(self.rule_name_REO)
        #```
        _ctx.res = rule_name.rem.group()
        #```
    
    rule_colon_REO = re.compile(r'[:]')
    def rule_colon(self, _ctx):
        rule_colon = self._scan_reo(self.rule_colon_REO)
    
    def rexpr_or(self, _ctx):
        rexpr_seq = self._scan('rexpr_seq')
        #```
        item_s = [rexpr_seq.res]
        #```
        #/
        self._o0m()
        try:
            while 1:
                rexpr_op = self._scan('rexpr_op')
                rexpr_seq = self._scan('rexpr_seq')
                #```
                item_s.append(rexpr_seq.res)
                #```
                self._o0m(1)
        except Er: self._o0m(0)
        #```
        _ctx.res = ExprOr(item_s) if len(item_s) > 1 else item_s[0]
        #```
    
    rexpr_op_REO = re.compile(r'[|]')
    def rexpr_op(self, _ctx):
        rexpr_op = self._scan_reo(self.rexpr_op_REO)
    
    def rexpr_seq(self, _ctx):
        #```
        item_s = []
        #```
        #/
        self._o1m()
        try:
            while 1:
                #/
                self._o0m()
                try:
                    while 1:
                        code = self._scan('code')
                        #```
                        item_s.append(code.res)
                        #```
                        self._o0m(1)
                except Er: self._o0m(0)
                rexpr_occ = self._scan('rexpr_occ')
                #```
                item_s.append(rexpr_occ.res)
                #```
                #/
                self._o0m()
                try:
                    while 1:
                        code = self._scan('code')
                        #```
                        item_s.append(code.res)
                        #```
                        self._o0m(1)
                except Er: self._o0m(0)
                self._o1m(1)
        except Er: self._o1m(0)
        #```
        _ctx.res = ExprSeq(item_s) if len(item_s) > 1 else item_s[0]
        #```
    
    code_REO = re.compile(r'(`+)((?:.|\n)*?)\1')
    def code(self, _ctx):
        code = self._scan_reo(self.code_REO)
        #```
        _ctx.res = Code(code.rem.group(2))
        #```
    
    def rexpr_occ(self, _ctx):
        rexpr_btm = self._scan('rexpr_btm')
        #```
        occ_type = None
        #```
        #/
        self._o01()
        try:
            #/
            self._or()
            try:
                #/
                self._ori()
                try:
                    rexpr_occ01 = self._scan('rexpr_occ01')
                    #```
                    occ_type = '01'
                    #```
                except Er: self._ori(0)
                else: self._ori(1)
                #/
                self._ori()
                try:
                    rexpr_occ0m = self._scan('rexpr_occ0m')
                    #```
                    occ_type = '0m'
                    #```
                except Er: self._ori(0)
                else: self._ori(1)
                #/
                self._ori()
                try:
                    rexpr_occ1m = self._scan('rexpr_occ1m')
                    #```
                    occ_type = '1m'
                    #```
                except Er: self._ori(0)
                else: self._ori(1)
            except Ok: self._or(1)
            else: self._or(0)
        except Er: self._o01(0)
        else: self._o01(1)
        #```
        if occ_type is None:
            _ctx.res = rexpr_btm.res
        elif occ_type == '01':
            _ctx.res = ExprOcc01(rexpr_btm.res)
        elif occ_type == '0m':
            _ctx.res = ExprOcc0m(rexpr_btm.res)
        elif occ_type == '1m':
            _ctx.res = ExprOcc1m(rexpr_btm.res)
        else:
            assert 0
        #```
    
    rexpr_occ01_REO = re.compile(r'[?]')
    def rexpr_occ01(self, _ctx):
        rexpr_occ01 = self._scan_reo(self.rexpr_occ01_REO)
    
    rexpr_occ0m_REO = re.compile(r'[*]')
    def rexpr_occ0m(self, _ctx):
        rexpr_occ0m = self._scan_reo(self.rexpr_occ0m_REO)
    
    rexpr_occ1m_REO = re.compile(r'[+]')
    def rexpr_occ1m(self, _ctx):
        rexpr_occ1m = self._scan_reo(self.rexpr_occ1m_REO)
    
    def rexpr_btm(self, _ctx):
        #/
        self._or()
        try:
            #/
            self._ori()
            try:
                pattern = self._scan('pattern')
                #```
                args = None
                #```
                #/
                self._o01()
                try:
                    args_def = self._scan('args_def')
                    #```
                    args = args_def.res
                    #```
                except Er: self._o01(0)
                else: self._o01(1)
                #```
                _ctx.res = Pattern(pattern.res, is_code=pattern.is_code, args=args)
                #```
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                rule_ref = self._scan('rule_ref')
                #```
                _ctx.res = rule_ref.res
                #```
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                rexpr_group = self._scan('rexpr_group')
                #```
                _ctx.res = rexpr_group.res
                #```
            except Er: self._ori(0)
            else: self._ori(1)
        except Ok: self._or(1)
        else: self._or(0)
    
    def pattern(self, _ctx):
        #/
        self._or()
        try:
            #/
            self._ori()
            try:
                pattern_str = self._scan('pattern_str')
                #```
                _ctx.res = pattern_str.res
                _ctx.is_code = False
                #```
            except Er: self._ori(0)
            else: self._ori(1)
            #/
            self._ori()
            try:
                pattern_code = self._scan('pattern_code')
                #```
                _ctx.res = pattern_code.res
                _ctx.is_code = True
                #```
            except Er: self._ori(0)
            else: self._ori(1)
        except Ok: self._or(1)
        else: self._or(0)
    
    pattern_str_REO = re.compile('r?(\'\'\'|"""|\'|")((?:[^\\\\]|\\\\.)*?)(\\1)')
    def pattern_str(self, _ctx):
        pattern_str = self._scan_reo(self.pattern_str_REO)
        #```
        _ctx.res = pattern_str.rem.group()
        #```
    
    pattern_code_REO = re.compile(r'(%+)((?:.|\n)*?)(\1)')
    def pattern_code(self, _ctx):
        pattern_code = self._scan_reo(self.pattern_code_REO)
        #```
        _ctx.res = pattern_code.rem.group(2)
        #```
    
    rule_ref_REO = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)(?![a-zA-Z0-9_])[\s]*(?![:])')
    def rule_ref(self, _ctx):
        rule_ref = self._scan_reo(self.rule_ref_REO)
        #```
        name = rule_ref.rem.group(1)
        _ctx.res = RuleRef(name)
        #```
    
    def rexpr_group(self, _ctx):
        brkt_beg = self._scan('brkt_beg')
        rexpr_or = self._scan('rexpr_or')
        brkt_end = self._scan('brkt_end')
        #```
        _ctx.res = rexpr_or.res
        #```

#/
def parse(txt, debug=False, rule=None):
    #/
    parser = Parser(
        txt=txt,
        debug=debug,
    )

    #/
    if rule is None:
        rule = 'all'

    #/
    res = None

    ei = None

    try:
        res = parser._scan(rule)
    except Exception:
        ei = sys.exc_info()

    #/
    return parser, res, ei
