import re


def compile_rule(expr, is_sensitive=True):
    if not is_sensitive:
        expr = expr.lower()

    # --------- 操作符转义 ---------
    escape_chrs = {
        '_(_': '$FrPt$',
        '_)_': '$ClPt$',
        '_|_': '$OrOp$',
        '_&_': '$AndOp$',
        '_!_': '$NotOp$',
    }

    for k, v in escape_chrs.items():
        expr = expr.replace(k, v)
    # --------- 操作符转义 ---------

    symbol_dict = {
        '(': '("',
        ')': '" in s)',
        '&': '" in s and "',
        '|': '" in s or "',
    }

    python_code = ''
    for char in expr:
        if char in symbol_dict:
            python_code += symbol_dict[char]
        else:
            python_code += char

    python_code = python_code.replace('"(', "(").replace(')" in s', ")")
    if not python_code.endswith(')'):
        python_code += '" in s'
    if not python_code.startswith('('):
        python_code = '"' + python_code

    # --------- 反转义 ---------
    for k, v in escape_chrs.items():
        pure_chr = k[1:-1]
        python_code = python_code.replace(v, pure_chr)
    # --------- 反转义 ---------

    python_code = f"""
global match_flag
match_flag = {python_code}
        """

    # --------- 转换 not 运算符 ---------
    not_word = re.findall(r'("!.+?" in s)', python_code)
    for each in not_word:
        this_pure_word = each.replace('"!', '', 1).replace('" in s', '', 1)
        replaced_word = f'"{this_pure_word}" not in s'
        python_code = python_code.replace(each, replaced_word, 1)
    # --------- 转换 not 运算符 ---------

    return python_code


if __name__ == '__main__':
    compile_rule(expr="(diversity&inclusion)|(D_&_I)|(equity&inclusion)")

    """
    global match_flag
    match_flag = ("diversity" in s and "inclusion" in s) or ("D&I" in s) or ("equity" in s and "inclusion" in s)
    """