# -*- coding: utf-8 -*-
class Import:
    # def __init__(self, from_: str, import_: str, as_: str = None):
    #     self.from_ = from_
    #     self.import_ = import_
    #     self.as_ = as_
    def __init__(self, *args, **kwargs):
        """
        入参三种形式。
        1、传入原始import字符串如：from os import path as os_path。
        2、传入Import相似结构的变量如：RequiredImport，Import('path', from_='os', as_='os_path')
        3、传入args有1-3个，分别是import字符串，from字符串，as字符串。可以用import_,from_,as_指示
        :param args: 传变量，形式有三种
                    1、args只有一个，直接是原始的import字符串：from os import path as os_path
                    2、args只有一个，Import变量：Import('path', from_='os', as_='os_path')
                    3、args有1-3个，分别是import字符串，from字符串，as字符串
        :param kwargs:
                    import_: str
                    from_: str
                    as_: str
        :return:
        """
        self.import_ = None
        self.from_ = None
        self.as_ = None
        if len(args) >= 1:  # 从args中获取入参
            imp = args[0]
            if isinstance(imp, str) and 'import' in imp:
                imp_string = imp.strip()
                if ' as ' in imp_string:
                    imp_string, as_string = imp_string.split(' as ')
                    self.as_ = as_string.strip()
                if imp_string.startswith('from '):
                    imp_string, import_string = imp_string.split(' import ')
                    self.import_ = import_string.strip()
                    self.from_ = imp_string[len('from '):].strip()
                else:
                    self.import_ = imp_string[len('import '):].strip()
            elif isinstance(imp, str):
                self.import_ = imp
            else:
                if not imp:
                    raise ValueError(f'unknown type: {type(imp)}')
                self.import_ = imp.import_
                self.from_ = imp.from_
                self.as_ = imp.as_
        if len(args) >= 2:
            if args[1] and not isinstance(args[1], str):
                raise ValueError(f'unknown type: {type(args[1])}')
            self.from_ = args[1]
        if len(args) >= 3:
            if args[2] and not isinstance(args[2], str):
                raise ValueError(f'unknown type: {type(args[1])}')
            self.as_ = args[2]

        # 从kwargs中获取入参
        self.import_ = kwargs.get('import_', self.import_)
        self.from_ = kwargs.get('from_', self.from_)
        self.as_ = kwargs.get('as_', self.as_)


class RequiredImport:
    def __init__(self):
        """需要import"""
        self.imports = {}  # key: import的name或者别名。如果有别名，优先使用别名。value: Import对象

    def add(self, *args, **kwargs):
        import_statement = Import(*args, **kwargs)
        # 加入新的import
        if import_statement.as_:
            if import_statement.as_ not in self.imports:
                self.imports[import_statement.as_] = import_statement
        elif import_statement.import_ not in self.imports:
            self.imports[import_statement.import_] = import_statement

        return self  # 返回自身，以便于链式调用

    def update(self, other):
        for import_ in other.imports.values():
            self.add(import_)
        return self  # 返回自身，以便于链式调用

    def serialize(self, delimiter='\n', with_comment=True):
        """序列化。本方法里不能调用Block.get_required_imports()，因为可能会有循环依赖"""
        # 把同一个from的写到一起
        prepared_imports = {}  # key: from_, value: (import_, as_)
        content = ''
        for import_ in self.imports.values():
            if import_.from_ not in prepared_imports:
                prepared_imports[import_.from_] = [(import_.import_, import_.as_)]
            else:
                prepared_imports[import_.from_].append((import_.import_, import_.as_))
        for from_, imports in prepared_imports.items():
            line = f'from {from_} import ' if from_ else 'import '
            line += f"{', '.join([f'{import_} as {as_}' if as_ else import_ for import_, as_ in imports])}"
            content += f'{line}{delimiter}'

        return content
