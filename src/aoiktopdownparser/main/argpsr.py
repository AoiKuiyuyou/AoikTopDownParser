# coding: utf-8
from __future__ import absolute_import

from argparse import ArgumentParser

from aoikargutil import Argument
from aoikargutil import OneOf
from aoikargutil import Option
from aoikargutil import bool_0or1
from aoikargutil import ensure_spec

from .argpsr_const import ARG_DEBUG_D
from .argpsr_const import ARG_DEBUG_F
from .argpsr_const import ARG_DEBUG_H
from .argpsr_const import ARG_DEBUG_K
from .argpsr_const import ARG_DEBUG_V
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
from .argpsr_const import ARG_GEN_PSR_DEBUG_D
from .argpsr_const import ARG_GEN_PSR_DEBUG_F
from .argpsr_const import ARG_GEN_PSR_DEBUG_H
from .argpsr_const import ARG_GEN_PSR_DEBUG_K
from .argpsr_const import ARG_GEN_PSR_DEBUG_V
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
from .argpsr_const import ARG_RULES_OBJ_URI_F
from .argpsr_const import ARG_RULES_OBJ_URI_H
from .argpsr_const import ARG_RULES_OBJ_URI_K
from .argpsr_const import ARG_RULES_OBJ_URI_V
from .argpsr_const import ARG_RULES_PSR_DEBUG_D
from .argpsr_const import ARG_RULES_PSR_DEBUG_F
from .argpsr_const import ARG_RULES_PSR_DEBUG_H
from .argpsr_const import ARG_RULES_PSR_DEBUG_K
from .argpsr_const import ARG_RULES_PSR_DEBUG_V
from .argpsr_const import ARG_SRC_FILE_PATH_F
from .argpsr_const import ARG_SRC_FILE_PATH_H
from .argpsr_const import ARG_SRC_FILE_PATH_K
from .argpsr_const import ARG_SRC_FILE_PATH_V
from .argpsr_const import ARG_SRC_OBJ_URI_F
from .argpsr_const import ARG_SRC_OBJ_URI_H
from .argpsr_const import ARG_SRC_OBJ_URI_K
from .argpsr_const import ARG_SRC_OBJ_URI_V
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
        ARG_RULES_OBJ_URI_F,
        dest=ARG_RULES_OBJ_URI_K,
        metavar=ARG_RULES_OBJ_URI_V,
        help=ARG_RULES_OBJ_URI_H,
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
        ARG_SRC_OBJ_URI_F,
        dest=ARG_SRC_OBJ_URI_K,
        metavar=ARG_SRC_OBJ_URI_V,
        help=ARG_SRC_OBJ_URI_H,
    )

    parser.add_argument(
        ARG_ENTRY_RULE_URI_F,
        dest=ARG_ENTRY_RULE_URI_K,
        default=ARG_ENTRY_RULE_URI_D,
        metavar=ARG_ENTRY_RULE_URI_V,
        help=ARG_ENTRY_RULE_URI_H,
    )

    parser.add_argument(
        ARG_RULES_PSR_DEBUG_F,
        dest=ARG_RULES_PSR_DEBUG_K,
        type=bool_0or1,
        nargs='?',
        const=True,
        default=ARG_RULES_PSR_DEBUG_D,
        metavar=ARG_RULES_PSR_DEBUG_V,
        help=ARG_RULES_PSR_DEBUG_H,
    )

    parser.add_argument(
        ARG_GEN_PSR_DEBUG_F,
        dest=ARG_GEN_PSR_DEBUG_K,
        type=bool_0or1,
        nargs='?',
        const=True,
        default=ARG_GEN_PSR_DEBUG_D,
        metavar=ARG_GEN_PSR_DEBUG_V,
        help=ARG_GEN_PSR_DEBUG_H,
    )

    parser.add_argument(
        ARG_DEBUG_F,
        dest=ARG_DEBUG_K,
        type=bool_0or1,
        nargs='?',
        const=True,
        default=ARG_DEBUG_D,
        metavar=ARG_DEBUG_V,
        help=ARG_DEBUG_H,
    )

    return parser


def ensure_args_spec(args):
    ensure_spec(
        OneOf(
            ARG_HELP_ON_F,
            ARG_HELP_ON_F2,
            ARG_VER_ON_F,
            Argument(
                ARG_RULES_FILE_PATH_F,
                OneOf(
                    ARG_PSR_FILE_PATH_F,
                    ARG_SRC_FILE_PATH_F,
                    ARG_SRC_OBJ_URI_F,
                )
            ),
            Argument(
                ARG_RULES_OBJ_URI_F,
                OneOf(
                    ARG_PSR_FILE_PATH_F,
                    ARG_SRC_FILE_PATH_F,
                    ARG_SRC_OBJ_URI_F,
                )
            ),
        ),
        args
    )

    ensure_spec(
        Option(
            ARG_ENTRY_RULE_URI_F,
            OneOf(
                ARG_SRC_FILE_PATH_F,
                ARG_SRC_OBJ_URI_F,
            )
        ),
        args
    )
