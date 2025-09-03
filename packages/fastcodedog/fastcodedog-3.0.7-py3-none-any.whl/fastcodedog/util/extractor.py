# -*- coding: utf-8 -*-
import ast


def extract_variables(code):
    # 还有些语法不能正常解析
    if code.startswith('@'):
        code = code[1:]
    # if code.find(' -> ') != -1:
    #     code = code.replace(' -> ', ' ')
    tree = ast.parse(code)
    variable_names = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.Name)):
            variable_names.append(node.id)

    [variable_names.pop(i) for i in range(len(variable_names) - 1, -1, -1) if
     variable_names[i] in variable_names[:i]]  # 保留顺序去重
    return variable_names


if __name__ == '__main__':
    str = """
presign = f'{presing}{accessToken}'
sign = hashlib.md5(presign.encode('utf-8')).hexdigest()
headers.update({
    "accessToken": accessToken,
    "sign": sign,
    "Content-Type": "application/json"
})
leng = len(headers)
"""
    # print(extract_all(str))
    print(extract_variables(str))
    print(extract_variables("User.enabled2 == enabled"))
    print(extract_variables("User.name2.like(f'%{name}%')"))
