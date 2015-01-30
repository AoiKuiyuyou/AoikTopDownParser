# coding: utf-8
from __future__ import absolute_import
from aoikindentutil import indent_add
from aoiktopdownparser.gen.opts_const import GS_CODE_POF
from aoiktopdownparser.gen.opts_const import GS_CODE_POF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_CODE_PRF
from aoiktopdownparser.gen.opts_const import GS_CODE_PRF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_CTX_VAR
from aoiktopdownparser.gen.opts_const import GS_CTX_VAR_V_DFT
from aoiktopdownparser.gen.opts_const import GS_FUNC_POF
from aoiktopdownparser.gen.opts_const import GS_FUNC_POF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_FUNC_PRF
from aoiktopdownparser.gen.opts_const import GS_FUNC_PRF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_REO_POF
from aoiktopdownparser.gen.opts_const import GS_REO_POF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_REO_PRF
from aoiktopdownparser.gen.opts_const import GS_REO_PRF_V_DFT
from aoiktopdownparser.gen.opts_const import GS_REP_VAR
from aoiktopdownparser.gen.opts_const import GS_REP_VAR_V_DFT
from aoiktopdownparser.gen.opts_const import GS_RES_VAR
from aoiktopdownparser.gen.opts_const import GS_RES_VAR_V_DFT

#/
class AstNode(object):

    def gen(self, opts={}, **kwargs):
        raise NotImplementedError()

#/
class Code(AstNode):

    def __init__(self, code):
        self.code = code.strip()

    def gen(self, opts={}):
        #/
        res = self.code

        #/
        code_prf = opts.get(GS_CODE_PRF,
            GS_CODE_PRF_V_DFT)

        if code_prf:
            res = code_prf + res

        #/
        code_pof = opts.get(GS_CODE_POF,
            GS_CODE_POF_V_DFT)

        if code_pof:
            res = res + code_pof

        #/
        return res

#/
class Pattern(AstNode):

    ARG_K_FLAGS = 'flags'

    ARG_K_CODE_PRF = 'code_prf'

    ARG_K_CODE_POF = 'code_pof'

    def __init__(self, pat, is_code, args=None):
        self.pat = pat

        self.is_code = is_code

        self.args = args if args is not None else {}

    def gen(self, opts={}, name=None, is_rule=False):
        #/
        reo_prf = opts.get(GS_REO_PRF, GS_REO_PRF_V_DFT)

        reo_pof = opts.get(GS_REO_POF, GS_REO_POF_V_DFT)

        #/
        if is_rule:
            res_var_name = opts.get(GS_RES_VAR, GS_RES_VAR_V_DFT)
            if res_var_name is GS_RES_VAR_V_DFT:
                res_var_name = name

            reo_var = 'self.{reo_prf}{rule_name}{reo_pof}'.format(
                reo_prf=reo_prf,
                rule_name=name,
                reo_pof=reo_pof,
            )

            res = "{res_var_name} = self._scan_reo({reo_var})".format(
                res_var_name=res_var_name,
                reo_var=reo_var,
            )
        else:
            res_var_name = opts.get(GS_REP_VAR, GS_REP_VAR_V_DFT)

            res = "{res_var_name} = self._scan_rep({rep})".format(
                res_var_name=res_var_name,
                rep=self.pat,
            )

        return res

class RuleDef(AstNode):

    ARG_K_CODE_PRF = 'code_prf'

    ARG_K_CODE_POF = 'code_pof'

    def __init__(self, name, expr, args=None):
        #/
        super(RuleDef, self).__init__()

        #/
        self.name = name

        self.args = args

        self.expr = expr

    def gen(self, opts={}):
        #/
        code_prf = self.args.get(self.ARG_K_CODE_PRF, '') if self.args else ''

        code_pof = self.args.get(self.ARG_K_CODE_POF, '') if self.args else ''

        #/
        func_prf = opts.get(GS_FUNC_PRF, GS_FUNC_PRF_V_DFT)

        func_pof = opts.get(GS_FUNC_POF, GS_FUNC_POF_V_DFT)

        #/
        reo_prf = opts.get(GS_REO_PRF, GS_REO_PRF_V_DFT)

        reo_pof = opts.get(GS_REO_POF, GS_REO_POF_V_DFT)

        #/
        ctx_var_name = opts.get(GS_CTX_VAR, GS_CTX_VAR_V_DFT)

        #/ because it follows |self|
        ctx_var_name = (', ' + ctx_var_name) if ctx_var_name else ''

        #/
        func_def_fmt = 'def {func_prf}{name}{func_pof}(self' + ctx_var_name + '):'

        func_def_txt = func_def_fmt.format(
            func_prf=func_prf,
            name=self.name,
            func_pof=func_pof,
        )

        #/ generate REO attribute if a ExprSeq matches only one terminal
        ##  pattern, along with optional code snippets.
        term_node = None

        if isinstance(self.expr, ExprSeq):
            seq_txt_s = []

            #/
            for item in self.expr.items:
                if isinstance(item, Pattern):
                    #/ if more than one term pattern in this rule
                    if term_node:
                        term_node = None
                        break
                    else:
                        term_node = item
                        seq_txt = item.gen(opts=opts, name=self.name, is_rule=True)
                        seq_txt_s.append(seq_txt)
                else:
                    if isinstance(item, Code):
                        seq_txt = item.gen(opts=opts)
                        seq_txt_s.append(seq_txt)
                    else:
                        term_node = None
                        break

        #/
        if term_node is not None or isinstance(self.expr, Pattern):
            #/
            if term_node is not None:
                #/
                _term_node = term_node

                #/
                func_body_txt = '\n'.join(seq_txt_s)
            else:
                #/
                _term_node = self.expr

                #/
                func_body_txt = self.expr.gen(opts=opts, name=self.name, is_rule=True)

            #/
            reo_code_prf = _term_node.args.get(Pattern.ARG_K_CODE_PRF, '')

            reo_code_pof = _term_node.args.get(Pattern.ARG_K_CODE_POF, '')

            flags = _term_node.args.get(Pattern.ARG_K_FLAGS, None)

            reo_def_txt = (
                '{reo_code_prf}{reo_prf}{name}{reo_pof}'
                ' = re.compile({rep}{flags}){reo_code_pof}'
                ).format(
                    reo_code_prf=reo_code_prf,
                    reo_prf=reo_prf,
                    name=self.name,
                    reo_pof=reo_pof,
                    rep=_term_node.pat,
                    flags=(', ' + flags) if flags else '',
                    reo_code_pof=reo_code_pof,
                )

            #/
            res = reo_def_txt + '\n' + func_def_txt + '\n' + indent_add(func_body_txt)
        else:
            #/
            func_body_txt = self.expr.gen(opts=opts)

            #/
            res = func_def_txt + '\n' + indent_add(func_body_txt)

        #/
        res = code_prf + res + code_pof

        #/
        return res

#/
class RuleRef(AstNode):

    def __init__(self, name):
        self.name = name

    def gen(self, opts={}):
        res_var = opts.get(GS_RES_VAR, GS_RES_VAR_V_DFT)
        if res_var is GS_RES_VAR_V_DFT:
            res_var = self.name
        res = "{res_var} = self._scan('{name}')".format(
            res_var=res_var,
            name=self.name,
        )
        return res

#/
class ExprSeq(AstNode):

    def __init__(self, items):
        #/
        super(ExprSeq, self).__init__()

        #/
        self.items = items

    def gen(self, opts={}):
        #/
        txt_s = []

        #/
        for item in self.items:
            txt = item.gen(opts=opts)
            txt_s.append(txt)

        #/
        res = '\n'.join(txt_s)

        return res

#/
class ExprOr(AstNode):

    def __init__(self, items):
        self.items = items

    def gen(self, opts={}):
        #/
        txt_s = []

        for item in self.items:
            txt_s.append(r'#/')
            txt_s.append(r'self._ori()')
            txt_s.append(r'try:')
            item_txt = item.gen(opts=opts)
            txt_s.append(indent_add(item_txt))
            txt_s.append(r'except Er: self._ori(0)')
            txt_s.append(r'else: self._ori(1)')

        res = '\n'.join(txt_s)

        res = '#/\nself._or()\n' +\
              'try:\n' + indent_add(res) \
              + '\nexcept Ok: self._or(1)' \
              + '\nelse: self._or(0)'

        return res

#/
class ExprOcc01(AstNode):

    def __init__(self, item):
        #/
        super(ExprOcc01, self).__init__()

        #/
        self.item = item

    def gen(self, opts={}):
        item_txt = self.item.gen(opts=opts)
        txt_s = []
        txt_s.append('#/')
        txt_s.append('self._o01()')
        txt_s.append('try:')
        txt_s.append(indent_add(item_txt))
        txt_s.append('except Er: self._o01(0)')
        txt_s.append('else: self._o01(1)')
        res = '\n'.join(txt_s)
        return res

#/
class ExprOcc0m(AstNode):

    def __init__(self, item):
        #/
        super(ExprOcc0m, self).__init__()

        #/
        self.item = item

    def gen(self, opts={}):
        item_txt = self.item.gen(opts=opts)
        txt_s = []
        txt_s.append('#/')
        txt_s.append('self._o0m()')
        txt_s.append('try:')
        txt_s.append('    while 1:')
        txt_s.append(indent_add(item_txt, 2))
        txt_s.append('        self._o0m(1)')
        txt_s.append('except Er: self._o0m(0)')
        res = '\n'.join(txt_s)
        return res

#/
class ExprOcc1m(AstNode):

    def __init__(self, item):
        #/
        super(ExprOcc1m, self).__init__()

        #/
        self.item = item

    def gen(self, opts={}):
        item_txt = self.item.gen(opts=opts)
        txt_s = []
        txt_s.append('#/')
        txt_s.append('self._o1m()')
        txt_s.append('try:')
        txt_s.append('    while 1:')
        txt_s.append(indent_add(item_txt, 2))
        txt_s.append('        self._o1m(1)')
        txt_s.append('except Er: self._o1m(0)')
        res = '\n'.join(txt_s)
        return res
