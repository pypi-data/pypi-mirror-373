# -*- coding: utf-8 -*-
from fastcodedog.generation.api.config import Config
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable


class Db(File):
    def __init__(self, comment=None, possible_imports: list | str = None, parent=None):
        super().__init__('db',
                         file_path=LocationFinder.get_path('db'),
                         package=LocationFinder.get_package('db'), comment=comment, parent=parent)
        self._init_blocks_and_imports()

    def _init_blocks_and_imports(self):
        self.blocks.append(Variable('engine', value=f"""create_engine(db_url, connect_args={{"check_same_thread": False}}
                       ) if db_url.startswith('sqlite') else create_engine(db_url)""",
                                    possible_imports=['from sqlalchemy import create_engine',
                                                      Import('db_url', Config().package)]))
        self.blocks.append(Variable('Session', value='sessionmaker(bind=engine)',
                                    possible_imports=['from sqlalchemy.orm import sessionmaker']))
        get_session = Function('get_session')
        get_session.blocks.append(Text(f"""session = Session()
try:
    yield session
finally:
    session.close()"""))
        self.blocks.append(get_session)
