import re

definitions_re = re.compile(
    r'''
        \b (contract | library | interface |
        constructor | function |
        modifier | event | struct | enum) \b
        ([^;{]*)
    ''', re.VERBOSE | re.MULTILINE)


def parse_sol(src):
    return definitions_re.findall(src)
