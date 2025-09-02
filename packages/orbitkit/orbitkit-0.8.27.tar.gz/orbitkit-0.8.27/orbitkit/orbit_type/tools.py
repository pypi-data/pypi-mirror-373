import re


def is_valid_regex(pattern):
    """
    检测正则表达式是否正确
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def logical_expr_match(expr: str, s: str):
    """
    用于逻辑表达式的校验、测试
    """

    expr = expr.strip()

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

    namespace = {'match_flag': False, 's': s}
    try:
        exec(python_code, namespace)
    except Exception as e:
        # print(e)
        return {'match_flag': False, 'reason': '表达式编译失败，存在语法错误！'}

    # --------- 补充校验 ---------
    current_layer = 0
    current_opts = ['' for _ in range(expr.count('(')+1)]

    for index, each_chr in enumerate(expr):
        if each_chr == '(':
            current_layer += 1
        elif each_chr == ')':
            current_opts[current_layer] = ''
            current_layer -= 1
        elif each_chr == '&' or each_chr == '|':
            if not current_opts[current_layer]:
                current_opts[current_layer] = each_chr
            else:
                if each_chr != current_opts[current_layer]:
                    reason = f"同一层级中，and 操作符和 or 操作符不能同时存在！错误位置：第{index+1}个字符 '{each_chr}'"
                    return {'match_flag': False, 'reason': reason}
    # --------- 补充校验 ---------

    return {'match_flag': namespace['match_flag'], 'reason': ''}
