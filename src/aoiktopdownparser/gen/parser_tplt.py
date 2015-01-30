{SS_FILE_PRF}# coding: utf-8
{SS_IMPORTS_PRF}from __future__ import absolute_import
import re
import sys{SS_IMPORTS_POF}

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
class {SS_PSR_CLS_NAME}(object):

    #/
    _RULE_FUNC_PRF = {SS_RULE_FUNC_PRF}
    _RULE_FUNC_POF = {SS_RULE_FUNC_POF}

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
    def __init__(self, {SS_INIT_FUNC_PARGS_PRF}txt{SS_INIT_FUNC_PARGS_POF}, {SS_INIT_FUNC_KARGS_PRF}debug=False{SS_INIT_FUNC_KARGS_POF}):
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
        self._ws_rep = {SS_WS_REP}

        self._ws_reo = re.compile(self._ws_rep)\
            if self._ws_rep is not None else None

        #/ current rule func's context dict
        self._ctx = None

        #/
        self._ctx_k_par = '{SS_CTX_K_PAR}'

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
{SS_INIT_FUNC_END}
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
        ctx_new.{SS_CTX_K_NAME} = name

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
            ctx.{SS_CTX_K_NAME} = ''

            #/
            if self._ctx_k_par:
                ctx[self._ctx_k_par] = self._ctx
        else:
            ctx = self._ctx

        #/
        ctx.{SS_CTX_K_REM} = m

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

{SS_RULE_FUNCS_PRF}{SS_RULE_FUNCS}{SS_RULE_FUNCS_POF}

#/
def parse({SS_INIT_FUNC_PARGS_PRF}txt{SS_INIT_FUNC_PARGS_POF}, {SS_INIT_FUNC_KARGS_PRF}debug=False{SS_INIT_FUNC_KARGS_POF}, rule=None):
    #/
    parser = {SS_PSR_CLS_NAME}(
        {SS_INIT_CALL_PARGS_PRF}txt=txt{SS_INIT_CALL_PARGS_POF},
        {SS_INIT_CALL_KARGS_PRF}debug=debug{SS_INIT_CALL_KARGS_POF},
    )

    #/
    if rule is None:
        rule = '{SS_ENTRY_RULE}'

    #/
    res = None

    ei = None

    try:
        res = parser._scan(rule)
    except Exception:
        ei = sys.exc_info()
{SS_PARSE_FUNC_END}
    #/
    return parser, res, ei
{SS_FILE_POF}