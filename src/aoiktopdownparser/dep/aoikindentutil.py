# coding: utf-8

#/
def indent_add(txt, step=1, indent=' '*4):
    prefix = indent * step
    return '\n'.join(prefix + x for x in txt.splitlines())

#/
def indent_del(txt, spcnt=4):
    indent = ' ' * spcnt

    line_s = []
    for line in txt.splitlines():
        if line.startswith(indent):
            line = line[spcnt:]
        else:
            line = line.lstrip(' ')

        line_s.append(line)

    res = '\n'.join(line_s)

    return res
