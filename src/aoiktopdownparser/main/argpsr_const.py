# coding: utf-8
from __future__ import absolute_import
from aoikargutil import SPEC_DI_K_ONE
from aoikargutil import SPEC_DI_K_TWO

#/
ARG_HELP_ON_F = '-h'
ARG_HELP_ON_F2 = '--help'

#/
ARG_VER_ON_F = '--ver'
ARG_VER_ON_K = '3sCySUG'
ARG_VER_ON_A = 'store_true'
ARG_VER_ON_H = 'Show version.'

#/
ARG_RULES_FILE_PATH_F = '-r'
ARG_RULES_FILE_PATH_K = '2jiDJZn'
ARG_RULES_FILE_PATH_V = 'RULES_FILE'
ARG_RULES_FILE_PATH_H = 'Rules file path.'

#/
ARG_RULES_OBJ_URI_F = '-R'
ARG_RULES_OBJ_URI_K = '3e2PrwA'
ARG_RULES_OBJ_URI_V = 'RULES_URI'
ARG_RULES_OBJ_URI_H = "Rules string's URI."

#/
ARG_EXT_OPTS_URI_F = '-o'
ARG_EXT_OPTS_URI_K = '2kP1X04'
ARG_EXT_OPTS_URI_D = None
ARG_EXT_OPTS_URI_V = 'OPTS_URI'
ARG_EXT_OPTS_URI_H = "Options dict's URI."

#/
ARG_PSR_FILE_PATH_F = '-g'
ARG_PSR_FILE_PATH_K = '4uWC33x'
ARG_PSR_FILE_PATH_C = None.__class__
ARG_PSR_FILE_PATH_V = 'PSR_FILE'
ARG_PSR_FILE_PATH_H = ('Parser output file path.'
    ' If set on without path given, default is stdout.'
    ' If set off, no parser file is created, the generated parser code is'
    ' loaded dynamically to parse the source data specified.')

#/
ARG_SRC_FILE_PATH_F = '-s'
ARG_SRC_FILE_PATH_K = '4mL5ObN'
ARG_SRC_FILE_PATH_V = 'SRC_FILE'
ARG_SRC_FILE_PATH_H = 'Source file path.'

#/
ARG_SRC_OBJ_URI_F = '-S'
ARG_SRC_OBJ_URI_K = '4k0PVhn'
ARG_SRC_OBJ_URI_V = 'SRC_URI'
ARG_SRC_OBJ_URI_H = "Source string's URI."

#/
ARG_ENTRY_RULE_URI_F = '-e'
ARG_ENTRY_RULE_URI_K = '4v7yx1e'
ARG_ENTRY_RULE_URI_D = None
ARG_ENTRY_RULE_URI_V = 'ENTRY_RULE'
ARG_ENTRY_RULE_URI_H = 'Entry rule. Used with arg {} or {}.'\
    .format(
        ARG_SRC_FILE_PATH_F,
        ARG_SRC_OBJ_URI_F,
    )

#/
ARG_RULES_PSR_DEBUG_F = '--rd'
ARG_RULES_PSR_DEBUG_K = '2oL5zs5'
ARG_RULES_PSR_DEBUG_D = False
ARG_RULES_PSR_DEBUG_V = '1|0'
ARG_RULES_PSR_DEBUG_H = """Rules parser's debug messages on/off. Default is {}."""\
    .format('on' if ARG_RULES_PSR_DEBUG_D else 'off')

#/
ARG_GEN_PSR_DEBUG_F = '--gd'
ARG_GEN_PSR_DEBUG_K = '2pSZyFP'
ARG_GEN_PSR_DEBUG_D = False
ARG_GEN_PSR_DEBUG_V = '1|0'
ARG_GEN_PSR_DEBUG_H = """Generated parser's debug messages on/off. Default is {}."""\
    .format('on' if ARG_GEN_PSR_DEBUG_D else 'off')

#/
ARG_DEBUG_F = '-V'
ARG_DEBUG_K = '3e04c3R'
ARG_DEBUG_D = True
ARG_DEBUG_V = '1|0'
ARG_DEBUG_H = """Program's debug messages on/off. Default is {}."""\
    .format('on' if ARG_DEBUG_D else 'off')

#/
ARG_SPEC_SUB = {
    #/
    SPEC_DI_K_ONE: (
        #/ 3dFfrgl
        ARG_PSR_FILE_PATH_F,
        ARG_SRC_FILE_PATH_F,
        ARG_SRC_OBJ_URI_F,
    ),
}

#/
ARG_SPEC = {
    SPEC_DI_K_ONE: (
        ARG_HELP_ON_F,
        ARG_HELP_ON_F2,
        ARG_VER_ON_F,
        #/ 3irgSHx
        [ARG_RULES_FILE_PATH_F, ARG_SPEC_SUB],
        [ARG_RULES_OBJ_URI_F, ARG_SPEC_SUB],
    ),
    SPEC_DI_K_TWO: (ARG_ENTRY_RULE_URI_F, [
        ARG_SRC_FILE_PATH_F, ARG_SRC_OBJ_URI_F
    ]),
}
