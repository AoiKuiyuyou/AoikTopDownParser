
#/
def main():
    #/
    import sys
    import traceback
    from pprint import pformat

    #/
    MAIN_RET_V_ARGS_LEN_ER = 1
    MAIN_RET_V_SRC_DATA_READ_ER = 2
    MAIN_RET_V_SRC_DATA_PARSE_ER = 3
    MAIN_RET_V_SRC_DATA_PARSE_OK = 0

    #/
    args_cnt = len(sys.argv) - 1

    if args_cnt < 1 or args_cnt > 3:
        #/
        msg = ('#/ Error\n'
               'Please specify source file path and optionally a rule name.')

        sys.stderr.write(msg)

        #/
        return MAIN_RET_V_ARGS_LEN_ER

    #/
    src_file_path = sys.argv[1]

    #/
    rule_name = None

    if args_cnt >= 2:
        rule_name = sys.argv[2]

        if rule_name == '':
            rule_name = None

    #/
    debug_on = False

    if args_cnt >= 3:
        debug_on = (sys.argv[3] == '-d')

    #/
    def get_traceback_stxt(exc_info=None):
        #/
        if exc_info is None:
            exc_info = sys.exc_info()

        #/
        exc_cls, exc_obj, tb_obj = exc_info

        #/
        txt_s = traceback.format_exception(exc_cls, exc_obj, tb_obj)

        #/
        res = ''.join(txt_s)

        return res

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
        ctx_k_name='{SS_CTX_K_NAME}',
        ctx_k_par='{SS_CTX_K_PAR}',
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
    try:
        src_txt = open(src_file_path).read()
    except Exception:
        #/
        msg = ('#/ Error\nFailed reading source data.\n'
            'File path is: |{}|\n'
        ).format(src_file_path)

        sys.stderr.write(msg)

        #/
        tb_msg = get_traceback_stxt()

        sys.stderr.write('---\n{}---\n'.format(tb_msg))

        #/
        return MAIN_RET_V_SRC_DATA_READ_ER

    #/
    parser, res, ei = parse(src_txt, rule=rule_name, debug=debug_on)

    #/
    if debug_on and parser._debug_info_s:
        #/
        msg = '#/ Parser debug info\n'

        msg += parser_debug_infos_to_msg(
            infos=parser._debug_info_s, txt=src_txt)

        msg += '\n\n'

        sys.stderr.write(msg)

    #/
    if ei is not None:
        #/
        msg = scan_error_to_msg(
            ei=ei,
            err_cls=ScanError,
            title='#/ Error\nFailed parsing source data.',
            txt=src_txt,
            dbg_msg_on=True,
        )

        sys.stderr.write(msg)

        #/
        return MAIN_RET_V_SRC_DATA_PARSE_ER

    #/
    print(pformat(res, indent=4, width=1))

    #/
    return MAIN_RET_V_SRC_DATA_PARSE_OK

#/
if __name__ == '__main__':
    #/
    import sys

    sys.exit(main())
