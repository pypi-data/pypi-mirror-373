# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable


class Config(File):
    def __init__(self, comment=None, possible_imports: list | str = None, parent=None):
        super().__init__('config',
                         file_path=LocationFinder.get_path('config', 'config'),
                         package=LocationFinder.get_package('config', 'config'), comment=comment, parent=parent)
        self.ini_file = self.file_path[:-3] + '.ini'
        self.ini_content = self._get_ini_content()
        self._init_blocks_and_imports()

    def _init_blocks_and_imports(self):
        get_config = Function('get_config',
                              params={'section': Function.Parameter('section'), 'key': Function.Parameter('key'),
                                      'default': Function.Parameter('default')})
        get_config.blocks.append(Text(f"""global _all_configs_
if _all_configs_ is None:
    _all_configs_ = {{}}
    confif_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = configparser.ConfigParser()
    config.read(confif_file)
    for section_ in config.sections():
        _all_configs_[section_] = {{}}
        for option in config.options(section_):
            _all_configs_[section_][option] = config.get(section_, option)
if section in _all_configs_ and key in _all_configs_[section]:
    return _all_configs_[section][key]
return default
""", possible_imports=['configparser', 'os']))
        self.blocks.append(get_config)
        get_configs = Function('get_configs',
                               params={'section': Function.Parameter('section')})
        get_configs.blocks.append(Text(f"""global _all_configs_
if _all_configs_ is None:
    _all_configs_ = {{}}
    confif_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = configparser.ConfigParser()
    config.read(confif_file)
    for section_ in config.sections():
        _all_configs_[section_] = {{}}
        for option in config.options(section_):
            _all_configs_[section_][option] = config.get(section_, option)
if section in _all_configs_:
    return _all_configs_[section]
return {{}}""", possible_imports=['configparser', 'os']))
        self.blocks.append(get_configs)
        self.blocks.append(Variable('_all_configs_', type='dict'))
        self.blocks.append(Variable('logging_config', value="get_configs('logging')"))
        self.blocks.append(Variable('port', value="get_config('app', 'port', 8000)"))
        self.blocks.append(Variable('db_url', value="get_config('database', 'url', None)"))

        for key, sub_items in ctx_instance.config.user_configs.items():
            for k, v in sub_items.items():
                self.blocks.append(Variable(f'{key}_{k}', value=f"get_config('{key}', '{k}')"))

    def save(self):
        super().save()
        open(self.ini_file, 'w', encoding='utf-8').write(self.ini_content)

    @staticmethod
    def _get_ini_content():
        content = ""
        for section, config in ctx_instance.config.__dict__.items():
            if section.startswith('_'):
                continue
            if isinstance(config, dict):
                for key, sub_items in config.items():
                    content += f"[{key}]\n"
                    for k, v in sub_items.items():
                        content += f"{k} = {v}\n"
            else:
                content += f"[{section}]\n"
                for key, value in config.__dict__.items():
                    if key.startswith('_'):
                        continue
                    content += f"{key} = {value}\n"
        return content
