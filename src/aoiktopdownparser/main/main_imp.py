# coding: utf-8
from __future__ import absolute_import

import codecs
import functools
import os.path
from pprint import pformat
import sys
from traceback import format_exc

from aoikargutil import SpecViolationError
from aoikimportutil import import_code
from aoikimportutil import import_obj

from .. import __version__
from ..gen.generator import get_parser_txt
from ..gen.opts import OPTS
from ..gen.opts_const import GS_BACKTRACKING_ON
from ..gen.parser import LexError
from ..gen.parser import SyntaxError
from ..gen.parser import debug_infos_to_msg
from ..gen.parser import parse
from ..gen.parser import parsing_error_to_msg
from .argpsr import ensure_args_spec
from .argpsr import parser_make
from .argpsr_const import ARG_BACKTRACKING_K
from .argpsr_const import ARG_ENTRY_RULE_URI_K
from .argpsr_const import ARG_EXT_OPTS_URI_K
from .argpsr_const import ARG_GEN_PSR_DEBUG_K
from .argpsr_const import ARG_PSR_FILE_PATH_C
from .argpsr_const import ARG_PSR_FILE_PATH_K
from .argpsr_const import ARG_RULES_FILE_PATH_K
from .argpsr_const import ARG_RULES_PSR_DEBUG_K
from .argpsr_const import ARG_SRC_FILE_PATH_K
from .argpsr_const import ARG_TPLT_FILE_PATH_K
from .argpsr_const import ARG_VER_ON_K
from .main_const import MAIN_RET_V_EXT_OPTS_LOAD_ERR
from .main_const import MAIN_RET_V_PSR_CODE_CALL_ERR
from .main_const import MAIN_RET_V_PSR_CODE_LOAD_ERR
from .main_const import MAIN_RET_V_PSR_CODE_WRITE_FILE_ERR
from .main_const import MAIN_RET_V_PSR_TPLT_FILE_READ_ERR
from .main_const import MAIN_RET_V_RULES_FILE_READ_ERR
from .main_const import MAIN_RET_V_RULES_PARSE_ERR
from .main_const import MAIN_RET_V_SRC_FILE_READ_ERR
from .main_const import MAIN_RET_V_TPLT_FILE_READ_ERR


def main_imp(args=None):
    if args is None:
        args = sys.argv[1:]

    try:
        ensure_args_spec(args)
    except SpecViolationError as exc:
        msg = exc.args[0]

        sys.stderr.write(msg)

        sys.exit(1)

    args_parser = parser_make()

    args_obj = args_parser.parse_args(args)

    version_on = getattr(args_obj, ARG_VER_ON_K)

    if version_on:
        print(__version__)

        return 0

    debug_on = True

    rules_file_path = getattr(args_obj, ARG_RULES_FILE_PATH_K)

    if rules_file_path is not None:
        try:
            rules_txt = codecs.open(rules_file_path, encoding='utf-8').read()
        except Exception:
            msg = '# Error\nFailed reading rules file.\n'\
                'File path is `{}`.\n'\
                .format(rules_file_path)

            sys.stderr.write(msg)

            if debug_on:
                sys.stderr.write('---\n{}---\n'.format(format_exc()))

            return MAIN_RET_V_RULES_FILE_READ_ERR
    else:
        assert 0

    tplt_file_path = getattr(args_obj, ARG_TPLT_FILE_PATH_K)

    if tplt_file_path is None:
        tplt_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'gen/parser_tplt.py'
        )

    tplt_file_path = os.path.join('.', tplt_file_path)

    if not os.path.isfile(tplt_file_path):
        msg = '# Error\nParser template file not exists: {0}.\n'.format(
            tplt_file_path
        )

        sys.stderr.write(msg)

        return MAIN_RET_V_TPLT_FILE_READ_ERR

    try:
        parser_tplt_text = codecs.open(tplt_file_path, encoding='utf-8').read()
    except Exception:
        msg = '# Error\nFailed reading parser template file: {0}.\n'.format(
            tplt_file_path
        )

        sys.stderr.write(msg)

        if debug_on:
            sys.stderr.write('---\n{}---\n'.format(format_exc()))

        return MAIN_RET_V_TPLT_FILE_READ_ERR

    opts = OPTS.copy()

    ext_opts_uri = getattr(args_obj, ARG_EXT_OPTS_URI_K)

    if ext_opts_uri is None:
        ext_opts = None

        ext_opts_mod = None
    else:
        try:
            ext_opts_mod, ext_opts = import_obj(
                ext_opts_uri,
                mod_name='aoiktopdownparser._tmpmod_ext_opts',
                retn_mod=True,
            )
        except Exception:
            msg = '# Error\nFailed loading opts dict.\n'\
                'URI is `{}`.\n'\
                .format(ext_opts_uri)

            sys.stderr.write(msg)

            if debug_on:
                sys.stderr.write('---\n{}---\n'.format(format_exc()))

            return MAIN_RET_V_EXT_OPTS_LOAD_ERR

    if ext_opts is None:
        ext_opts = {}

    if ext_opts:
        opts.update(ext_opts)

    backtracking = getattr(args_obj, ARG_BACKTRACKING_K)

    if backtracking:
        opts[GS_BACKTRACKING_ON] = True

    rules_parser_debug_on = getattr(args_obj, ARG_RULES_PSR_DEBUG_K)

    parser, parsing_result, exc_info = parse(
        rules_txt, debug=rules_parser_debug_on
    )

    if rules_parser_debug_on and parser._debug_infos:
        msg = '# Rules parser debug info\n'

        msg += debug_infos_to_msg(
            debug_infos=parser._debug_infos, txt=rules_txt)

        msg += '\n\n'

        sys.stderr.write(msg)

    if exc_info is not None:
        msg = parsing_error_to_msg(
            exc_info=exc_info,
            lex_error_class=LexError,
            syntax_error_class=SyntaxError,
            title='# Error\nFailed parsing rules for generating parser.',
            txt=rules_txt,
        )

        sys.stderr.write(msg)

        return MAIN_RET_V_RULES_PARSE_ERR

    inline_opts = parsing_result.opts

    if inline_opts is None:
        inline_opts = {}

    if inline_opts:
        opts.update(inline_opts)

        if ext_opts:
            # `ext_opts` should override `inline_opts`
            opts.update(ext_opts)

    # `odf` means option-defining-file path.
    find_odf = functools.partial(
        find_odf_v2,
        inline_opts=inline_opts,
        ext_opts_uri=ext_opts_uri,
        ext_opts_mod=ext_opts_mod if ext_opts_uri is not None else None,
        ext_opts=ext_opts,
        rules_file_path=rules_file_path,
    )

    try:
        parser_txt = get_parser_txt(
            rules=parsing_result.rule_defs,
            tplt_text=parser_tplt_text,
            opts=opts,
            find_odf=find_odf,
        )
    except Exception:
        msg = '# Error\nFailed generating parser code.\n'

        sys.stderr.write(msg)

        if debug_on:
            sys.stderr.write('---\n{}---\n'.format(format_exc()))

        return MAIN_RET_V_PSR_TPLT_FILE_READ_ERR

    parser_output_file_path = getattr(args_obj, ARG_PSR_FILE_PATH_K)

    if parser_output_file_path is not None:
        if parser_output_file_path == ARG_PSR_FILE_PATH_C:
            sys.stdout.write(parser_txt)

            return 0

        else:
            try:
                with codecs.open(
                    parser_output_file_path, mode='w', encoding='utf-8'
                ) as parser_output_file:
                    parser_output_file.write(parser_txt)

            except Exception:
                msg = '# Error\nFailed creating parser file.\n'\
                    + 'File path is `{}`.\n'\
                    .format(parser_output_file_path)

                sys.stderr.write(msg)

                if debug_on:
                    sys.stderr.write('---\n{}---\n'.format(format_exc()))

                return MAIN_RET_V_PSR_CODE_WRITE_FILE_ERR

            msg = 'Generated parser file: `{}`.\n'\
                .format(parser_output_file_path)

            sys.stderr.write(msg)

            return 0

        assert 0

    src_file_path = getattr(args_obj, ARG_SRC_FILE_PATH_K)

    src_txt = None

    if src_file_path is not None:
        try:
            src_file = codecs.open(src_file_path, encoding='utf-8')

            src_txt = src_file.read()
        except Exception:
            msg = '# Error\nFailed reading source data file.\n'\
                + 'File path is `{}`.\n'\
                .format(src_file_path)

            sys.stderr.write(msg)

            if debug_on:
                sys.stderr.write('---\n{}---\n'.format(format_exc()))

            return MAIN_RET_V_SRC_FILE_READ_ERR
    else:
        assert 0

    try:
        parser_mod = import_code(
            parser_txt,
            mod_name='aoiktopdownparser._tmpmod_parser'
        )
    except Exception:
        msg = '# Error\nFailed loading the generated parser module.\n'

        sys.stderr.write(msg)

        if debug_on:
            sys.stderr.write('---\n{}---\n'.format(format_exc()))

        return MAIN_RET_V_PSR_CODE_LOAD_ERR

    entry_rule = getattr(args_obj, ARG_ENTRY_RULE_URI_K)

    gen_psr_debug = getattr(args_obj, ARG_GEN_PSR_DEBUG_K)

    parser, parsing_result, exc_info = getattr(parser_mod, 'parse')(
        src_txt,
        rule=entry_rule,
        debug=gen_psr_debug,
    )

    msgs = []

    if gen_psr_debug and parser._debug_infos:
        msg = '# Generated parser debug info\n'

        msg += debug_infos_to_msg(
            debug_infos=parser._debug_infos, txt=src_txt
        )

        msgs.append(msg)

    if exc_info is not None:
        msg = parsing_error_to_msg(
            exc_info=exc_info,
            lex_error_class=getattr(parser_mod, 'LexError'),
            syntax_error_class=getattr(parser_mod, 'SyntaxError'),
            title='# Error\nGenerated parser failed parsing source data.',
            txt=src_txt,
        )

        msgs.append(msg)

        sys.stderr.write('\n\n'.join(msgs) + '\n')

        return MAIN_RET_V_PSR_CODE_CALL_ERR

    msg = '# Generated parser parsing result\n{0}\n'.format(
        pformat(parsing_result, indent=4, width=1)
    )

    msgs.append(msg)

    sys.stderr.write('\n\n'.join(msgs) + '\n')

    return 0


def find_odf_v2(
    opt_key,
    inline_opts,
    ext_opts_uri,
    ext_opts_mod,
    ext_opts,
    rules_file_path,
    opt_dft=None,
):
    # Find the file that defines given option.

    opt_val = ext_opts.get(opt_key, opt_dft)

    if opt_val is not opt_dft:
        uri_parts = split_uri(ext_opts_uri)

        protocol = uri_parts[0]

        if protocol == 'py':
            odf = ext_opts_mod.__file__
        elif protocol == 'file':
            odf = uri_parts[1]
        else:
            odf = None

    else:
        opt_val = inline_opts.get(opt_key, opt_dft)

        if opt_val is not opt_dft:
            if rules_file_path is not None:
                odf = rules_file_path
            else:
                assert 0

        else:
            odf = None

    return odf


def split_uri(uri, mod_attr_sep='::'):
    """Split given URI into a tuple of (protocol, module URI, attribute chain).

    @param mod_attr_sep: the separator between module name and attribute name.
    """
    uri_parts = uri.split(mod_attr_sep, 1)

    if len(uri_parts) == 2:
        mod_uri, attr_chain = uri_parts
    else:
        mod_uri = uri_parts[0]

        attr_chain = None

    if mod_uri.startswith('py://'):
        protocol = 'py'

        mod_uri = mod_uri[5:]

    elif mod_uri.startswith('file://'):
        protocol = 'file'

        mod_uri = mod_uri[7:]

    # If no protocol prefix is present, and the uri ends with `.py`, then
    # consider the uri as module file path instead of module name.
    elif mod_uri.endswith('.py'):
        protocol = 'file'

    else:
        protocol = 'py'

    info = (protocol, mod_uri, attr_chain)

    return info
