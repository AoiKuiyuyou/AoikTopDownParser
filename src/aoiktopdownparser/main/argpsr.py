# coding: utf-8
from __future__ import absolute_import
from aoikargutil import bool_0or1
from aoiktopdownparser.main.argpsr_const import ARG_DEBUG_D
from aoiktopdownparser.main.argpsr_const import ARG_DEBUG_F
from aoiktopdownparser.main.argpsr_const import ARG_DEBUG_H
from aoiktopdownparser.main.argpsr_const import ARG_DEBUG_K
from aoiktopdownparser.main.argpsr_const import ARG_DEBUG_V
from aoiktopdownparser.main.argpsr_const import ARG_ENTRY_RULE_URI_D
from aoiktopdownparser.main.argpsr_const import ARG_ENTRY_RULE_URI_F
from aoiktopdownparser.main.argpsr_const import ARG_ENTRY_RULE_URI_H
from aoiktopdownparser.main.argpsr_const import ARG_ENTRY_RULE_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_ENTRY_RULE_URI_V
from aoiktopdownparser.main.argpsr_const import ARG_EXT_OPTS_URI_D
from aoiktopdownparser.main.argpsr_const import ARG_EXT_OPTS_URI_F
from aoiktopdownparser.main.argpsr_const import ARG_EXT_OPTS_URI_H
from aoiktopdownparser.main.argpsr_const import ARG_EXT_OPTS_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_EXT_OPTS_URI_V
from aoiktopdownparser.main.argpsr_const import ARG_GEN_PSR_DEBUG_D
from aoiktopdownparser.main.argpsr_const import ARG_GEN_PSR_DEBUG_F
from aoiktopdownparser.main.argpsr_const import ARG_GEN_PSR_DEBUG_H
from aoiktopdownparser.main.argpsr_const import ARG_GEN_PSR_DEBUG_K
from aoiktopdownparser.main.argpsr_const import ARG_GEN_PSR_DEBUG_V
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_C
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_F
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_H
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_K
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_V
from aoiktopdownparser.main.argpsr_const import ARG_RULES_FILE_PATH_F
from aoiktopdownparser.main.argpsr_const import ARG_RULES_FILE_PATH_H
from aoiktopdownparser.main.argpsr_const import ARG_RULES_FILE_PATH_K
from aoiktopdownparser.main.argpsr_const import ARG_RULES_FILE_PATH_V
from aoiktopdownparser.main.argpsr_const import ARG_RULES_OBJ_URI_F
from aoiktopdownparser.main.argpsr_const import ARG_RULES_OBJ_URI_H
from aoiktopdownparser.main.argpsr_const import ARG_RULES_OBJ_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_RULES_OBJ_URI_V
from aoiktopdownparser.main.argpsr_const import ARG_RULES_PSR_DEBUG_D
from aoiktopdownparser.main.argpsr_const import ARG_RULES_PSR_DEBUG_F
from aoiktopdownparser.main.argpsr_const import ARG_RULES_PSR_DEBUG_H
from aoiktopdownparser.main.argpsr_const import ARG_RULES_PSR_DEBUG_K
from aoiktopdownparser.main.argpsr_const import ARG_RULES_PSR_DEBUG_V
from aoiktopdownparser.main.argpsr_const import ARG_SRC_FILE_PATH_F
from aoiktopdownparser.main.argpsr_const import ARG_SRC_FILE_PATH_H
from aoiktopdownparser.main.argpsr_const import ARG_SRC_FILE_PATH_K
from aoiktopdownparser.main.argpsr_const import ARG_SRC_FILE_PATH_V
from aoiktopdownparser.main.argpsr_const import ARG_SRC_OBJ_URI_F
from aoiktopdownparser.main.argpsr_const import ARG_SRC_OBJ_URI_H
from aoiktopdownparser.main.argpsr_const import ARG_SRC_OBJ_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_SRC_OBJ_URI_V
from aoiktopdownparser.main.argpsr_const import ARG_VER_ON_A
from aoiktopdownparser.main.argpsr_const import ARG_VER_ON_F
from aoiktopdownparser.main.argpsr_const import ARG_VER_ON_H
from aoiktopdownparser.main.argpsr_const import ARG_VER_ON_K
from argparse import ArgumentParser

#/
def parser_make():
    #/
    parser = ArgumentParser(add_help=True)

    #/
    parser.add_argument(
        ARG_VER_ON_F,
        dest=ARG_VER_ON_K,
        action=ARG_VER_ON_A,
        help=ARG_VER_ON_H,
    )

    #/
    parser.add_argument(
        ARG_RULES_FILE_PATH_F,
        dest=ARG_RULES_FILE_PATH_K,
        metavar=ARG_RULES_FILE_PATH_V,
        help=ARG_RULES_FILE_PATH_H,
    )

    #/
    parser.add_argument(
        ARG_RULES_OBJ_URI_F,
        dest=ARG_RULES_OBJ_URI_K,
        metavar=ARG_RULES_OBJ_URI_V,
        help=ARG_RULES_OBJ_URI_H,
    )

    #/
    parser.add_argument(
        ARG_EXT_OPTS_URI_F,
        dest=ARG_EXT_OPTS_URI_K,
        default=ARG_EXT_OPTS_URI_D,
        metavar=ARG_EXT_OPTS_URI_V,
        help=ARG_EXT_OPTS_URI_H,
    )

    #/
    parser.add_argument(
        ARG_PSR_FILE_PATH_F,
        dest=ARG_PSR_FILE_PATH_K,
        nargs='?',
        const=ARG_PSR_FILE_PATH_C,
        metavar=ARG_PSR_FILE_PATH_V,
        help=ARG_PSR_FILE_PATH_H,
    )

    #/
    parser.add_argument(
        ARG_SRC_FILE_PATH_F,
        dest=ARG_SRC_FILE_PATH_K,
        metavar=ARG_SRC_FILE_PATH_V,
        help=ARG_SRC_FILE_PATH_H,
    )

    #/
    parser.add_argument(
        ARG_SRC_OBJ_URI_F,
        dest=ARG_SRC_OBJ_URI_K,
        metavar=ARG_SRC_OBJ_URI_V,
        help=ARG_SRC_OBJ_URI_H,
    )

    #/
    parser.add_argument(
        ARG_ENTRY_RULE_URI_F,
        dest=ARG_ENTRY_RULE_URI_K,
        default=ARG_ENTRY_RULE_URI_D,
        metavar=ARG_ENTRY_RULE_URI_V,
        help=ARG_ENTRY_RULE_URI_H,
    )

    #/
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

    #/
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

    #/
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

    #/
    return parser
