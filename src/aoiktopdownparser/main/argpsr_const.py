# coding: utf-8
from __future__ import absolute_import


ARG_HELP_ON_F = '-h'
ARG_HELP_ON_F2 = '--help'


ARG_VER_ON_F = '--ver'
ARG_VER_ON_K = 'ARG_VER_ON_K'
ARG_VER_ON_A = 'store_true'
ARG_VER_ON_H = 'Show version.'


ARG_RULES_FILE_PATH_F = '-r'
ARG_RULES_FILE_PATH_K = 'ARG_RULES_FILE_PATH_K'
ARG_RULES_FILE_PATH_V = 'RULES_FILE'
ARG_RULES_FILE_PATH_H = 'Parser rules file path.'


ARG_TPLT_FILE_PATH_F = '-t'
ARG_TPLT_FILE_PATH_K = 'ARG_TPLT_FILE_PATH_K'
ARG_TPLT_FILE_PATH_D = None
ARG_TPLT_FILE_PATH_V = 'TPLT_FILE'
ARG_TPLT_FILE_PATH_H = 'Parser template file path.'


ARG_TPLT_EXAMPLE_PATH_F = '-e'
ARG_TPLT_EXAMPLE_PATH_K = 'ARG_TPLT_EXAMPLE_PATH_K'
ARG_TPLT_EXAMPLE_PATH_D = None
ARG_TPLT_EXAMPLE_PATH_V = 'PSR_TPLT_EG_FILE.'
ARG_TPLT_EXAMPLE_PATH_H = 'Create parser template example file.'


ARG_PSR_FILE_PATH_F = '-o'
ARG_PSR_FILE_PATH_K = 'ARG_PSR_FILE_PATH_K'
ARG_PSR_FILE_PATH_C = None.__class__
ARG_PSR_FILE_PATH_V = 'PSR_FILE'
ARG_PSR_FILE_PATH_H = (
    'Parser output file path.'
    ' If set on without path given, default is stdout.'
    ' If set off, no parser file is created, the generated parser code is'
    ' loaded dynamically to parse the source data specified.'
)


ARG_EXT_OPTS_URI_F = '-x'
ARG_EXT_OPTS_URI_K = 'ARG_EXT_OPTS_URI_K'
ARG_EXT_OPTS_URI_D = None
ARG_EXT_OPTS_URI_V = 'OPTS_URI'
ARG_EXT_OPTS_URI_H = "Options dict's URI."


ARG_BACKTRACKING_F = '-b'
ARG_BACKTRACKING_K = 'ARG_BACKTRACKING_K'
ARG_BACKTRACKING_A = 'store_true'
ARG_BACKTRACKING_D = False
ARG_BACKTRACKING_H = 'Generate backtracking parser.'


ARG_SRC_FILE_PATH_F = '-s'
ARG_SRC_FILE_PATH_K = 'ARG_SRC_FILE_PATH_K'
ARG_SRC_FILE_PATH_V = 'SRC_FILE'
ARG_SRC_FILE_PATH_H = 'Source file path.'


ARG_ENTRY_RULE_URI_F = '-m'
ARG_ENTRY_RULE_URI_K = 'ARG_ENTRY_RULE_URI_K'
ARG_ENTRY_RULE_URI_D = None
ARG_ENTRY_RULE_URI_V = 'ENTRY_RULE'
ARG_ENTRY_RULE_URI_H = 'Entry rule. Used with argument {0}.'\
    .format(ARG_SRC_FILE_PATH_F)


ARG_RULES_PSR_DEBUG_F = '-p'
ARG_RULES_PSR_DEBUG_K = 'ARG_RULES_PSR_DEBUG_K'
ARG_RULES_PSR_DEBUG_A = 'store_true'
ARG_RULES_PSR_DEBUG_D = False
ARG_RULES_PSR_DEBUG_H = 'Show rules parser\'s debug messages.'


ARG_GEN_PSR_DEBUG_F = '-q'
ARG_GEN_PSR_DEBUG_K = 'ARG_GEN_PSR_DEBUG_K'
ARG_GEN_PSR_DEBUG_A = 'store_true'
ARG_GEN_PSR_DEBUG_D = False
ARG_GEN_PSR_DEBUG_H = 'Show generated parser\'s debug messages.'
