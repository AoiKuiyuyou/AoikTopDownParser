# coding: utf-8
from __future__ import absolute_import

#/ |GS| below means parser generator's setting key
##
## The parser generator means AoikTopDownParser's parser generator, which
##  generates your custom parser.

#/ rules parser version
##  i.e. which version of AoikTopDownParser should be used to parse the rules
GS_VER = 'GS_VER'

#/ parser template file path
GS_TPLT = 'GS_TPLT'
#/ default is using "aoiktopdownparser.gen.parser_tplt.py"
GS_TPLT_V_DFT = None

#/ re obj's name prefix
GS_REO_PRF = 'GS_REO_PRF'
#/ default
GS_REO_PRF_V_DFT = ''

#/ re obj's name postfix
GS_REO_POF = 'GS_REO_POF'
#/ default
GS_REO_POF_V_DFT = '_REO'

#/ make sure re obj' name prefix and postfix are not equal to rule func's name
##  prefix and postfix.

#/ rule func's name prefix
GS_FUNC_PRF = 'GS_FUNC_PRF'
#/ default
GS_FUNC_PRF_V_DFT = ''

#/ rule func' name postfix
GS_FUNC_POF = 'GS_FUNC_POF'
#/ default
GS_FUNC_POF_V_DFT = ''

#/ rule func's context variable's name
GS_CTX_VAR = 'GS_CTX_VAR'
#/ default
GS_CTX_VAR_V_DFT = '_ctx'

#/ result variable name of scanning a rule
GS_RES_VAR = 'GS_RES_VAR'
#/ default is using the rule name, e.g.
##  num = self._scan('num')
GS_RES_VAR_V_DFT = None

#/ result variable name of scanning a non-rule re pattern
GS_REP_VAR = 'GS_REP_VAR'
#/ default is "_rep", e.g.
##  _rep = self._scan_rep(r'[(]')
GS_REP_VAR_V_DFT = '_rep'

#/ code before embedded code
## A typical use case is adding some comments to enhance readability.
GS_CODE_PRF = 'GS_CODE_PRF'
#/ default
GS_CODE_PRF_V_DFT = '#```\n'

#/ code after embedded code
## A typical use case is adding some comments to enhance readability.
GS_CODE_POF = 'GS_CODE_POF'
#/ default
GS_CODE_POF_V_DFT = '\n#```'

#/ entry rule name
GS_ENTRY = 'GS_ENTRY'
#/ default is using the first non-terminal rule,
##  or the first terminal rule if no non-terminal rule exists.
## The default algorithm is implemented at 4r6wOwv.
GS_ENTRY_V_DFT = None

#/ |SS| below means parser template's substitution setting key
##
## The parser template means the one used by AoikTopDownParser's parser
##  generator to generate your custom parser.
##
## What substitution settings are effective is determined by the parser template
##  in use. Settings below are effective for the default template, i.e.
##  "aoiktopdownparser.gen.parser_tplt.py". You are not limited to these
##  settings if a custom parser template is in use.

#/ what prefix a setting key must have to be a substitution setting key.
## Do not change this.
SS_PRF = 'SS_'

#/ substitution settings below are "internal".
## Do not specify values for them.
## Their values are computed, according to your custom parser's rules and other
##  "GS_" settings.
## ---BEG

#/ rule funcs' generated code
SS_RULE_FUNCS = 'SS_RULE_FUNCS'

#/ entry rule name
SS_ENTRY_RULE = 'SS_ENTRY_RULE'

#/ rule func' name prefix
SS_RULE_FUNC_PRF = 'SS_RULE_FUNC_PRF'

#/ rule func' name postfix
SS_RULE_FUNC_POF = 'SS_RULE_FUNC_POF'

## ---END

#/ substitution settings below can be specified.

#/ parser class name
SS_PSR_CLS_NAME = 'SS_PSR_CLS_NAME'

#/ re pattern for white spaces
## If specified, the scan function will scan and discard white spaces before and
##  after the scanning of each rule.
SS_WS_REP = 'SS_WS_REP'

#/ context dict's key name for rule name
SS_CTX_K_NAME = 'SS_CTX_K_NAME'

#/ context dict's key name for parent context dict
SS_CTX_K_PAR = 'SS_CTX_K_PAR'

#/ context dict's key name for re match result
SS_CTX_K_REM = 'SS_CTX_K_REM'

#/ code at top of the file
SS_FILE_PRF = 'SS_FILE_PRF'

#/ code at end of the file
SS_FILE_POF = 'SS_FILE_POF'

#/ code before import statements
SS_IMPORTS_PRF = 'SS_IMPORTS_PRF'

#/ code after import statements
SS_IMPORTS_POF = 'SS_IMPORTS_POF'

#/ code before rule funcs' code
SS_RULE_FUNCS_PRF = 'SS_RULE_FUNCS_PRF'

#/ code after rule funcs' code
SS_RULE_FUNCS_POF = 'SS_RULE_FUNCS_POF'

#/ code before parser class' init function's positional arguments
SS_INIT_FUNC_PARGS_PRF = 'SS_INIT_FUNC_PARGS_PRF'

#/ code after parser class' init function's positional arguments
SS_INIT_FUNC_PARGS_POF = 'SS_INIT_FUNC_PARGS_POF'

#/ code before parser class' init function's keyword arguments
SS_INIT_FUNC_KARGS_PRF = 'SS_INIT_FUNC_KARGS_PRF'

#/ code after parser class' init function's keyword arguments
SS_INIT_FUNC_KARGS_POF = 'SS_INIT_FUNC_KARGS_POF'

#/ code at end of the parser class' init function
SS_INIT_FUNC_END = 'SS_INIT_FUNC_END'

#/ code before parser object init call's positional arguments in parse function
SS_INIT_CALL_PARGS_PRF = 'SS_INIT_CALL_PARGS_PRF'

#/ code after parser object init call's positional arguments in parse function
SS_INIT_CALL_PARGS_POF = 'SS_INIT_CALL_PARGS_POF'

#/ code before parser object init call's keyword arguments in parse function
SS_INIT_CALL_KARGS_PRF = 'SS_INIT_CALL_KARGS_PRF'

#/ code after parser object init call's keyword arguments in parse function
SS_INIT_CALL_KARGS_POF = 'SS_INIT_CALL_KARGS_POF'

#/ code at end of the parse function
SS_PARSE_FUNC_END = 'SS_PARSE_FUNC_END'
