# -*- coding: utf-8 -*-
import json5

from fastcodedog.context.api.api import Api
from fastcodedog.context.api.oauth2 import OAuth2
from fastcodedog.context.contextbase import ContextBase
from fastcodedog.context.crud.crud import Crud
from fastcodedog.context.model.model import Model
from fastcodedog.context.schema.schema import Schema
from fastcodedog.context.setting.config import Config
from fastcodedog.context.setting.extend_app import ExtendApp
from fastcodedog.context.setting.project import Project
from fastcodedog.context.setting.source_directory import SourceDirectory
from fastcodedog.util.find_file import find
from fastcodedog.util.singleton import Singleton


@Singleton
class Context(ContextBase):
    def __init__(self):
        super().__init__()
        self.project = Project()
        self.config = Config()
        self.source_directory = SourceDirectory()
        self.oauth2 = OAuth2()
        self.extend_apps = {}
        self.models = {}
        self.schemas = {}
        self.cruds = {}
        self.apis = {}

    def load(self, json_file, with_prepared_source=True):
        data = json5.load(open(json_file, 'r', encoding='utf-8'))
        self.project.load(data['project'])
        self.config.load(data['config'])
        self.source_directory.load(data['source_directory'])
        self.oauth2.load(data['oauth2'])
        for k, v in data['extend_apps'].items():
            extend_app = ExtendApp()
            extend_app.load(v)
            self.extend_apps[k] = extend_app
        if with_prepared_source:
            self.load_models(self.source_directory.model)
            self.load_schemas(self.source_directory.schema)
            self.load_cruds(self.source_directory.crud)
            self.load_apis(self.source_directory.api)

    def load_models(self, model_directory):
        files = find(model_directory, '*/*.json5')
        for file in files:
            model = Model()
            model.load(json5.load(open(file, 'r', encoding='utf-8')))
            if model.module not in self.models:
                self.models[model.module] = {}
            self.models[model.module][model.name] = model

    def load_schemas(self, schema_directory):
        files = find(schema_directory, '*/*.json5')
        for file in files:
            schema = Schema()
            schema.load(json5.load(open(file, 'r', encoding='utf-8')))
            if schema.module not in self.schemas:
                self.schemas[schema.module] = {}
            self.schemas[schema.module][schema.name] = schema

    def load_cruds(self, crud_directory):
        files = find(crud_directory, '*/*.json5')
        for file in files:
            crud = Crud()
            crud.load(json5.load(open(file, 'r', encoding='utf-8')))
            if crud.module not in self.cruds:
                self.cruds[crud.module] = {}
            self.cruds[crud.module][crud.name] = crud

    def load_apis(self, api_directory):
        files = find(api_directory, '*/*.json5')
        for file in files:
            api = Api()
            api.load(json5.load(open(file, 'r', encoding='utf-8')))
            if api.module not in self.apis:
                self.apis[api.module] = {}
            self.apis[api.module][api.name] = api


ctx_instance = Context()
