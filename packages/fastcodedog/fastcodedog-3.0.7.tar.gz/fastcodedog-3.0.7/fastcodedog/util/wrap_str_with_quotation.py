# -*- coding: utf-8 -*-
def wrap_quotation(str, allowed=["'", '"']):
    if str.find('\n') == -1:
        if str.find("'") == -1 and "'" in allowed:
            return f"'{str}'"
        if str.find('"') == -1 and '"' in allowed:
            return f'"{str}"'
    if str.find("'''") == -1 and "'" in allowed:
        return f"'''{str}'''"
    if str.find('"""') == -1 and '"' in allowed:
        return f'"""{str}"""'
    ns = str.replace('"""', "'''")
    return f'"""{ns}"""'
