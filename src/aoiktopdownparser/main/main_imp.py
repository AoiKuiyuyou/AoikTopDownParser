# coding: utf-8
from __future__ import absolute_import
from aoikargutil import ensure_spec
from aoikexcutil import get_traceback_stxt
from aoikimportutil import import_module_by_code
from aoikimportutil import load_obj_local_or_remote
from aoikimportutil import uri_split
from aoiktopdownparser.gen.engine import gen
from aoiktopdownparser.gen.opts import OPTS
from aoiktopdownparser.main.argpsr import parser_make
from aoiktopdownparser.main.argpsr_const import ARG_DEBUG_K
from aoiktopdownparser.main.argpsr_const import ARG_ENTRY_RULE_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_EXT_OPTS_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_GEN_PSR_DEBUG_K
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_C
from aoiktopdownparser.main.argpsr_const import ARG_PSR_FILE_PATH_K
from aoiktopdownparser.main.argpsr_const import ARG_RULES_FILE_PATH_K
from aoiktopdownparser.main.argpsr_const import ARG_RULES_OBJ_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_RULES_PSR_DEBUG_K
from aoiktopdownparser.main.argpsr_const import ARG_SPEC
from aoiktopdownparser.main.argpsr_const import ARG_SRC_FILE_PATH_K
from aoiktopdownparser.main.argpsr_const import ARG_SRC_OBJ_URI_K
from aoiktopdownparser.main.argpsr_const import ARG_VER_ON_K
from aoiktopdownparser.main.main_const import MAIN_RET_V_EXC_LEAK_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_EXT_OPTS_LOAD_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_KBINT_OK
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_CODE_CALL_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_CODE_CALL_OK
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_CODE_LOAD_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_CODE_WRITE_FILE_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_CODE_WRITE_FILE_OK
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_CODE_WRITE_STDOUT_OK
from aoiktopdownparser.main.main_const import MAIN_RET_V_PSR_TPLT_FILE_READ_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_RULES_FILE_READ_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_RULES_OBJ_LOAD_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_RULES_OBJ_NOT_STR_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_RULES_PARSE_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_SRC_FILE_READ_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_SRC_OBJ_LOAD_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_SRC_OBJ_NOT_STR_ER
from aoiktopdownparser.main.main_const import MAIN_RET_V_VER_SHOW_OK
from aoiktopdownparser.main.main_const import PSR_CODE_DYN_MOD_NAME
from aoiktopdownparser.parser import ScanError
from aoiktopdownparser.parser import parse
from aoiktopdownparser.version import __version__
from pprint import pformat
import functools
import sys

#/
def parser_debug_infos_to_msg(infos, txt):
    #/
    row_s = txt.split('\n')

    #/
    msg_s = []

    for debug_info in infos:
        row_txt = row_s[debug_info.row]

        msg = '{indent}{err}{name}: {row}.{col}: |{txt}|{row_txt}'.format(
            name=debug_info.name,
            indent='    ' * debug_info.slv,
            err='' if debug_info.sss else '!',
            row=debug_info.row+1,
            col=debug_info.col+1,
            txt=row_txt[debug_info.col:],
            row_txt=(', |' + (row_txt[:debug_info.col] + '^' + \
                row_txt[debug_info.col:]) + '|')\
                if debug_info.col != 0 else '',
        )
        msg_s.append(msg)

    #/
    msg = '\n'.join(msg_s)

    return msg

#/
def ctx_names_get(
    ctx,
    inc=False,
    topdown=False,
    ctx_k_name='name',
    ctx_k_par='par',
):
    #/
    name_s = []

    #/
    if inc:
        name = getattr(ctx, ctx_k_name)

        name_s.append(name)

    #/
    if not ctx_k_par:
        return

    #/
    while True:
        #/
        ctx = getattr(ctx, ctx_k_par, None)

        if ctx is None:
            break

        #/
        name = getattr(ctx, ctx_k_name)

        name_s.append(name)

    #/
    if topdown:
        name_s = list(reversed(name_s))

    #/
    return name_s

#/
def scan_error_to_msg(ei, err_cls, title, txt, dbg_msg_on):
    #/
    msg = title

    #/
    exc = ei[1]

    #/
    if not isinstance(exc, err_cls):
        #/
        msg += '\n---\n{}---\n'.format(get_traceback_stxt(ei))

        return msg

    #/
    msg_s = []

    msg_s.append(msg)

    #/
    ctx_name_s = ctx_names_get(exc.ctx, inc=True, topdown=True)

    ctx_msg = ''

    if ctx_name_s:
        ctx_msg = ' '.join(ctx_name_s)

    #/
    row_s = txt.split('\n')

    #/
    row_txt = row_s[exc.row]

    #/
    col_mark = ' ' * exc.col + '^'

    #/
    msg = ('#// |{rule}| failed at {row}.{col} ({ctx_msg})\n'
           '{row_txt}\n'
           '{col_mark}'
        ).format(
            rule=exc.ctx.name,
            row=exc.row+1,
            col=exc.col+1,
            ctx_msg=ctx_msg,
            row_txt=row_txt,
            col_mark=col_mark,
        )

    #/
    msg_s.append(msg)

    #/
    reason_ei_s = []

    if exc.eisp:
        reason_ei_s.extend(ei for ei in exc.eisp if ei[1] is not exc)

    if exc.eis:
        reason_ei_s.extend(ei for ei in exc.eis if ei[1] is not exc)

    #/
    if reason_ei_s:
        #/
        msg = 'Possible reasons:'

        msg_s.append(msg)

        #/
        for ei_x in reason_ei_s:
            #/
            exc_x = ei_x[1]

            #/
            ctx_name_s = ctx_names_get(exc_x.ctx, inc=True, topdown=True)

            ctx_msg = ''

            if ctx_name_s:
                ctx_msg = ' '.join(ctx_name_s)

            #/
            row_txt = row_s[exc_x.row]

            #/
            col_mark = ' ' * exc_x.col + '^'

            #/
            msg = ('#// |{rule}| failed at {row}.{col} ({ctx_msg})\n'
                   '{row_txt}\n'
                   '{col_mark}'
                ).format(
                    rule=exc_x.ctx.name,
                    row=exc_x.row+1,
                    col=exc_x.col+1,
                    ctx_msg=ctx_msg,
                    row_txt=row_txt,
                    col_mark=col_mark,
                )

            #/
            msg_s.append(msg)

    #/
    res = '\n\n'.join(msg_s)

    #/
    return res

#/
def odf_find_mk(
    opt_key,
    doc_opts,
    ext_opts_uri,
    ext_opts_mod,
    ext_opts,
    rules_fpath,
    rules_obj_uri,
    rules_mod,
    opt_dft=None,
    ):
    #/
    opt_val = ext_opts.get(opt_key, opt_dft)

    #/ if opt_key is specified in options from cmd
    if opt_val is not opt_dft:
        #/
        ## |dfp| means define file path
        uri_parts = uri_split(ext_opts_uri)

        prot = uri_parts[0]

        if prot == 'py':
            #/
            odf = ext_opts_mod.__file__
            #/
        elif prot in ('file', 'http', 'https'):
            #/
            odf = uri_parts[1]
        else:
            #/
            odf = None

    else:
        #/
        opt_val = doc_opts.get(opt_key, opt_dft)

        #/ if opt_key is specified in rules file or string
        if opt_val is not opt_dft:
            #/
            if rules_fpath is not None:
                #/
                odf = rules_fpath
            elif rules_obj_uri is not None:
                #/
                uri_parts = uri_split(rules_obj_uri)

                prot = uri_parts[0]

                #/
                if prot == 'py':
                    #/
                    odf = rules_mod.__file__
                elif prot in ('file', 'http', 'https'):
                    #/
                    odf = uri_parts[1]
                else:
                    #/
                    odf = None
            else:
                #/ ensured by 3irgSHx
                assert 0

        else:
            #/ opt_key is not specified, neither in cmd opts nor in doc opts.
            odf = None

    #/
    return odf

#/
def main_imp():
    #/
    args_parser = parser_make()

    #/
    args_obj = args_parser.parse_args()

    #/
    ensure_spec(args_parser, ARG_SPEC)

    #/
    dbg_msg_on = getattr(args_obj, ARG_DEBUG_K)

    #/
    ver_on = getattr(args_obj, ARG_VER_ON_K)

    #/
    if ver_on:
        #/
        print(__version__)

        #/
        return MAIN_RET_V_VER_SHOW_OK

    #/
    rules_fpath = getattr(args_obj, ARG_RULES_FILE_PATH_K)

    rules_obj_uri = getattr(args_obj, ARG_RULES_OBJ_URI_K)

    #/
    if rules_fpath is not None:
        #/
        try:
            rules_txt = open(rules_fpath).read()
        except Exception:
            #/
            msg = '#/ Error\nFailed reading rules file.\n'\
                'File path is |{}|.\n'\
                .format(rules_fpath)

            #/
            sys.stderr.write(msg)

            #/
            if dbg_msg_on:
                tb_msg = get_traceback_stxt()

                sys.stderr.write('---\n{}---\n'.format(tb_msg))

            #/
            return MAIN_RET_V_RULES_FILE_READ_ER

    elif rules_obj_uri is not None:
        #/
        try:
            rules_mod, rules_txt = load_obj_local_or_remote(
                rules_obj_uri, retn_mod=True)
        except Exception:
            #/
            msg = '#/ Error\nFailed loading rule spec object.\n'\
                'Object URI is |{}|.\n'\
                .format(rules_obj_uri)

            #/
            sys.stderr.write(msg)

            #/
            if dbg_msg_on:
                tb_msg = get_traceback_stxt()

                sys.stderr.write('---\n{}---\n'.format(tb_msg))

            #/
            return MAIN_RET_V_RULES_OBJ_LOAD_ER

        #/
        if not isinstance(rules_txt, str):
            #/
            msg = '#/ Error\nRules data object is not string.\n'\
                'Object URI is |{}|.\n'\
                .format(rules_obj_uri)

            #/
            sys.stderr.write(msg)

            #/
            return MAIN_RET_V_RULES_OBJ_NOT_STR_ER
    else:
        #/ ensured by 3irgSHx
        assert 0

    #/
    opts = OPTS.copy()

    #/
    ext_opts_uri = getattr(args_obj, ARG_EXT_OPTS_URI_K)

    #/
    if ext_opts_uri is None:
        #/
        ext_opts = None

        ext_opts_mod = None
    else:
        #/
        try:
            ext_opts_mod, ext_opts = load_obj_local_or_remote(
                ext_opts_uri, retn_mod=True)
        except Exception:
            #/
            msg = '#/ Error\nFailed loading opts dict.\n'\
                'URI is |{}|.\n'\
                .format(ext_opts_uri)

            #/
            sys.stderr.write(msg)

            #/
            if dbg_msg_on:
                tb_msg = get_traceback_stxt()

                sys.stderr.write('---\n{}---\n'.format(tb_msg))

            #/
            return MAIN_RET_V_EXT_OPTS_LOAD_ER

    #/
    if ext_opts is None:
        ext_opts = {}

    #/
    if ext_opts:
        opts.update(ext_opts)

    #/
    rules_psr_debug = getattr(args_obj, ARG_RULES_PSR_DEBUG_K)

    #/
    parser, res, ei = parse(rules_txt, debug=rules_psr_debug)

    #/
    if rules_psr_debug and parser._debug_info_s:
        #/
        msg = '#/ Rules parser debug info\n'

        msg += parser_debug_infos_to_msg(
            infos=parser._debug_info_s, txt=rules_txt)

        msg += '\n\n'

        sys.stderr.write(msg)

    #/
    if ei is not None:
        #/
        msg = scan_error_to_msg(
            ei=ei,
            err_cls=ScanError,
            title='#/ Error\nFailed parsing rules for generating parser.\n',
            txt=rules_txt,
            dbg_msg_on=dbg_msg_on,
        )

        sys.stderr.write(msg)

        #/
        return MAIN_RET_V_RULES_PARSE_ER

    #/
    doc_opts = res.args

    if doc_opts is None:
        doc_opts = {}

    #/
    if doc_opts:
        #/
        opts.update(doc_opts)

        #/ |ext_opts| should override |doc_opts|
        if ext_opts:
            opts.update(ext_opts)

    #/
    odf_find = functools.partial(odf_find_mk,
        doc_opts=doc_opts,
        ext_opts_uri=ext_opts_uri,
        ext_opts_mod=ext_opts_mod if ext_opts_uri is not None else None,
        ext_opts=ext_opts,
        rules_fpath=rules_fpath,
        rules_obj_uri=rules_obj_uri,
        rules_mod=rules_mod if rules_obj_uri is not None else None,
    )

    #/
    try:
        #/
        psr_txt = gen(
            rules=res.rule_def_s,
            opts=opts,
            odf_find=odf_find,
        )
    except Exception:
        #/
        msg = '#/ Error\nFailed generating parser code.\n'

        sys.stderr.write(msg)

        #/
        if dbg_msg_on:
            tb_msg = get_traceback_stxt()

            sys.stderr.write('---\n{}---\n'.format(tb_msg))

        #/
        return MAIN_RET_V_PSR_TPLT_FILE_READ_ER

    #/
    psr_out_fpath = getattr(args_obj, ARG_PSR_FILE_PATH_K)

    if psr_out_fpath is not None:
        #/
        if psr_out_fpath == ARG_PSR_FILE_PATH_C:
            #/
            sys.stdout.write(psr_txt)

            #/
            return MAIN_RET_V_PSR_CODE_WRITE_STDOUT_OK

        #/
        else:
            try:
                #/
                with open(psr_out_fpath, mode='w') as gen_parser_file:
                    gen_parser_file.write(psr_txt)

            except Exception:
                #/
                msg = '#/ Error\nFailed creating parser file.\n'\
                    + 'File path is |{}|.\n'\
                    .format(psr_out_fpath)

                #/
                sys.stderr.write(msg)

                #/
                if dbg_msg_on:
                    tb_msg = get_traceback_stxt()

                    sys.stderr.write('---\n{}---\n'.format(tb_msg))

                #/
                return MAIN_RET_V_PSR_CODE_WRITE_FILE_ER

            #/
            msg = '#/ Generated parser\nParser file path is |{}|.\n'\
                .format(psr_out_fpath)

            sys.stderr.write(msg)

            #/
            return MAIN_RET_V_PSR_CODE_WRITE_FILE_OK

        assert 0

    #/
    src_file_path = getattr(args_obj, ARG_SRC_FILE_PATH_K)

    src_obj_uri = getattr(args_obj, ARG_SRC_OBJ_URI_K)

    #/
    src_txt = None

    if src_file_path is not None:
        #/
        try:
            #/
            src_file = open(src_file_path)

            #/
            src_txt = src_file.read()

        except Exception:
            #/
            msg = '#/ Error\nFailed reading source data file.\n'\
                + 'File path is |{}|.\n'\
                .format(src_file_path)

            #/
            sys.stderr.write(msg)

            #/
            if dbg_msg_on:
                tb_msg = get_traceback_stxt()

                sys.stderr.write('---\n{}---\n'.format(tb_msg))

            #/
            return MAIN_RET_V_SRC_FILE_READ_ER

    #/
    elif src_obj_uri is not None:
        #/
        try:
            #/
            src_txt = load_obj_local_or_remote(src_obj_uri)

        except Exception:
            #/
            msg = '#/ Error\nFailed loading source data object.\n'\
                + 'Object URI is |{}|.\n'\
                .format(src_obj_uri)

            #/
            sys.stderr.write(msg)

            #/
            if dbg_msg_on:
                tb_msg = get_traceback_stxt()

                sys.stderr.write('---\n{}---\n'.format(tb_msg))

            #/
            return MAIN_RET_V_SRC_OBJ_LOAD_ER

        #/
        if not isinstance(src_txt, str):
            #/
            msg = '#/ Error\nSource data object is not string.\n'\
                'Object URI is |{}|.\n'\
                .format(src_obj_uri)

            #/
            sys.stderr.write(msg)

            #/
            return MAIN_RET_V_SRC_OBJ_NOT_STR_ER
    else:
        #/ ensured by 3dFfrgl
        assert 0

    #/
    assert psr_txt is not None

    try:
        psr_mod = import_module_by_code(psr_txt,
            mod_name=PSR_CODE_DYN_MOD_NAME)
    except Exception:
        #/
        msg = '#/ Error\nFailed loading generated parser module.\n'

        #/
        sys.stderr.write(msg)

        #/
        if dbg_msg_on:
            tb_msg = get_traceback_stxt()

            sys.stderr.write('---\n{}---\n'.format(tb_msg))

        #/
        return MAIN_RET_V_PSR_CODE_LOAD_ER

    #/
    assert src_txt is not None

    #/
    entry_rule = getattr(args_obj, ARG_ENTRY_RULE_URI_K)

    #/
    gen_psr_debug = getattr(args_obj, ARG_GEN_PSR_DEBUG_K)

    #/
    parser, res, ei = psr_mod.parse(
        src_txt,
        rule=entry_rule,
        debug=gen_psr_debug,
    )

    #/
    msg_s = []

    #/
    if gen_psr_debug and parser._debug_info_s:
        #/
        msg = '#/ Generated parser debug info\n'

        msg += parser_debug_infos_to_msg(
            infos=parser._debug_info_s, txt=src_txt)

        msg_s.append(msg)

    #/
    if ei is not None:
        #/
        msg = scan_error_to_msg(
            ei=ei,
            err_cls=psr_mod.ScanError,
            title='#/ Error\nFailed parsing source data.',
            txt=src_txt,
            dbg_msg_on=dbg_msg_on,
        )

        msg_s.append(msg)

        #/
        sys.stderr.write('\n\n'.join(msg_s) + '\n')

        #/
        return MAIN_RET_V_PSR_CODE_CALL_ER

    #/
    msg = pformat(res, indent=4, width=1)

    msg_s.append(msg)

    sys.stderr.write('\n\n'.join(msg_s) + '\n')

    #/
    return MAIN_RET_V_PSR_CODE_CALL_OK

#/
def main():
    #/
    try:
        #/
        return main_imp()
    #/
    except KeyboardInterrupt:
        #/
        return MAIN_RET_V_KBINT_OK
    #/
    except Exception:
        #/
        tb_msg = get_traceback_stxt()

        sys.stderr.write('#/ Uncaught exception\n---\n{}---\n'.format(tb_msg))

        #/
        return MAIN_RET_V_EXC_LEAK_ER
