# coding: utf-8
from __future__ import absolute_import

from argparse import ArgumentParser

from aoikargutil import Argument
from aoikargutil import OneOf
from aoikargutil import Option
from aoikargutil import ensure_spec

from .argpsr_const import ARG_BACKTRACKING_A
from .argpsr_const import ARG_BACKTRACKING_D
from .argpsr_const import ARG_BACKTRACKING_F
from .argpsr_const import ARG_BACKTRACKING_H
from .argpsr_const import ARG_BACKTRACKING_K
from .argpsr_const import ARG_ENTRY_RULE_URI_D
from .argpsr_const import ARG_ENTRY_RULE_URI_F
from .argpsr_const import ARG_ENTRY_RULE_URI_H
from .argpsr_const import ARG_ENTRY_RULE_URI_K
from .argpsr_const import ARG_ENTRY_RULE_URI_V
from .argpsr_const import ARG_EXT_OPTS_URI_D
from .argpsr_const import ARG_EXT_OPTS_URI_F
from .argpsr_const import ARG_EXT_OPTS_URI_H
from .argpsr_const import ARG_EXT_OPTS_URI_K
from .argpsr_const import ARG_EXT_OPTS_URI_V
from .argpsr_const import ARG_GEN_PSR_DEBUG_A
from .argpsr_const import ARG_GEN_PSR_DEBUG_D
from .argpsr_const import ARG_GEN_PSR_DEBUG_F
from .argpsr_const import ARG_GEN_PSR_DEBUG_H
from .argpsr_const import ARG_GEN_PSR_DEBUG_K
from .argpsr_const import ARG_HELP_ON_F
from .argpsr_const import ARG_HELP_ON_F2
from .argpsr_const import ARG_PSR_FILE_PATH_C
from .argpsr_const import ARG_PSR_FILE_PATH_F
from .argpsr_const import ARG_PSR_FILE_PATH_H
from .argpsr_const import ARG_PSR_FILE_PATH_K
from .argpsr_const import ARG_PSR_FILE_PATH_V
from .argpsr_const import ARG_RULES_FILE_PATH_F
from .argpsr_const import ARG_RULES_FILE_PATH_H
from .argpsr_const import ARG_RULES_FILE_PATH_K
from .argpsr_const import ARG_RULES_FILE_PATH_V
from .argpsr_const import ARG_RULES_PSR_DEBUG_A
from .argpsr_const import ARG_RULES_PSR_DEBUG_D
from .argpsr_const import ARG_RULES_PSR_DEBUG_F
from .argpsr_const import ARG_RULES_PSR_DEBUG_H
from .argpsr_const import ARG_RULES_PSR_DEBUG_K
from .argpsr_const import ARG_SRC_FILE_PATH_F
from .argpsr_const import ARG_SRC_FILE_PATH_H
from .argpsr_const import ARG_SRC_FILE_PATH_K
from .argpsr_const import ARG_SRC_FILE_PATH_V
from .argpsr_const import ARG_TPLT_EXAMPLE_PATH_D
from .argpsr_const import ARG_TPLT_EXAMPLE_PATH_F
from .argpsr_const import ARG_TPLT_EXAMPLE_PATH_H
from .argpsr_const import ARG_TPLT_EXAMPLE_PATH_K
from .argpsr_const import ARG_TPLT_EXAMPLE_PATH_V
from .argpsr_const import ARG_TPLT_FILE_PATH_D
from .argpsr_const import ARG_TPLT_FILE_PATH_F
from .argpsr_const import ARG_TPLT_FILE_PATH_H
from .argpsr_const import ARG_TPLT_FILE_PATH_K
from .argpsr_const import ARG_TPLT_FILE_PATH_V
from .argpsr_const import ARG_VER_ON_A
from .argpsr_const import ARG_VER_ON_F
from .argpsr_const import ARG_VER_ON_H
from .argpsr_const import ARG_VER_ON_K


def parser_make():
    parser = ArgumentParser(add_help=True)

    parser.add_argument(
        ARG_VER_ON_F,
        dest=ARG_VER_ON_K,
        action=ARG_VER_ON_A,
        help=ARG_VER_ON_H,
    )

    parser.add_argument(
        ARG_RULES_FILE_PATH_F,
        dest=ARG_RULES_FILE_PATH_K,
        metavar=ARG_RULES_FILE_PATH_V,
        help=ARG_RULES_FILE_PATH_H,
    )

    parser.add_argument(
        ARG_TPLT_FILE_PATH_F,
        dest=ARG_TPLT_FILE_PATH_K,
        default=ARG_TPLT_FILE_PATH_D,
        metavar=ARG_TPLT_FILE_PATH_V,
        help=ARG_TPLT_FILE_PATH_H,
    )

    parser.add_argument(
        ARG_TPLT_EXAMPLE_PATH_F,
        dest=ARG_TPLT_EXAMPLE_PATH_K,
        default=ARG_TPLT_EXAMPLE_PATH_D,
        metavar=ARG_TPLT_EXAMPLE_PATH_V,
        help=ARG_TPLT_EXAMPLE_PATH_H,
    )

    parser.add_argument(
        ARG_EXT_OPTS_URI_F,
        dest=ARG_EXT_OPTS_URI_K,
        default=ARG_EXT_OPTS_URI_D,
        metavar=ARG_EXT_OPTS_URI_V,
        help=ARG_EXT_OPTS_URI_H,
    )

    parser.add_argument(
        ARG_PSR_FILE_PATH_F,
        dest=ARG_PSR_FILE_PATH_K,
        nargs='?',
        const=ARG_PSR_FILE_PATH_C,
        metavar=ARG_PSR_FILE_PATH_V,
        help=ARG_PSR_FILE_PATH_H,
    )

    parser.add_argument(
        ARG_SRC_FILE_PATH_F,
        dest=ARG_SRC_FILE_PATH_K,
        metavar=ARG_SRC_FILE_PATH_V,
        help=ARG_SRC_FILE_PATH_H,
    )

    parser.add_argument(
        ARG_ENTRY_RULE_URI_F,
        dest=ARG_ENTRY_RULE_URI_K,
        default=ARG_ENTRY_RULE_URI_D,
        metavar=ARG_ENTRY_RULE_URI_V,
        help=ARG_ENTRY_RULE_URI_H,
    )

    parser.add_argument(
        ARG_BACKTRACKING_F,
        dest=ARG_BACKTRACKING_K,
        default=ARG_BACKTRACKING_D,
        action=ARG_BACKTRACKING_A,
        help=ARG_BACKTRACKING_H,
    )

    parser.add_argument(
        ARG_RULES_PSR_DEBUG_F,
        dest=ARG_RULES_PSR_DEBUG_K,
        action=ARG_RULES_PSR_DEBUG_A,
        default=ARG_RULES_PSR_DEBUG_D,
        help=ARG_RULES_PSR_DEBUG_H,
    )

    parser.add_argument(
        ARG_GEN_PSR_DEBUG_F,
        dest=ARG_GEN_PSR_DEBUG_K,
        action=ARG_GEN_PSR_DEBUG_A,
        default=ARG_GEN_PSR_DEBUG_D,
        help=ARG_GEN_PSR_DEBUG_H,
    )

    return parser


def ensure_args_spec(args):
    ensure_spec(
        OneOf(
            ARG_HELP_ON_F,
            ARG_HELP_ON_F2,
            ARG_VER_ON_F,
            ARG_TPLT_EXAMPLE_PATH_F,
            Argument(
                ARG_RULES_FILE_PATH_F,
                OneOf(
                    ARG_PSR_FILE_PATH_F,
                    ARG_SRC_FILE_PATH_F,
                )
            ),
        ),
        args
    )

    ensure_spec(
        Option(
            ARG_ENTRY_RULE_URI_F,
            ARG_SRC_FILE_PATH_F,
        ),
        args
    )
