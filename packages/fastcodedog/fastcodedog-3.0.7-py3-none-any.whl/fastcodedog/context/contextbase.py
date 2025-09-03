# -*- coding: utf-8 -*-
from collections.abc import Iterable


class ContextBase:
    def __init__(self):
        self._types = {}  # 模型类型映射，用于校验list，dict或者默认为None的数据的配置类型是否争取

    def load(self, json):
        if not isinstance(json, dict):
            raise Exception(f'装载对象需要是一个字典。 {self.__class__}')
        for k, v in json.items():
            if v is None:
                continue
            if hasattr(self, k) and isinstance(getattr(self, k), ContextBase):
                # 已经初始了Base类型的对象，直接使用对象进行装载
                getattr(self, k).load(v)
            elif hasattr(self, k) and isinstance(getattr(self, k), dict):
                # 已经初始化了dict类型的对象，根据字典的类型定义进行装载
                if not isinstance(v, dict):
                    raise Exception(f'{k} 需要是一个字典。 {self.__class__}')
                for kk, vv in v.items():
                    instance = self.new_instance(k, vv)  # 根据_types中预设，创建对应的value对象
                    if isinstance(instance, ContextBase):
                        # 如果是Base类型的对象，需要传入json进行装载
                        if not isinstance(vv, dict):
                            raise Exception(f'{k} 需要是一个字典。 {self.__class__}')
                        instance.load(vv)  # 递归装载
                        getattr(self, k)[kk] = instance  # 设置值
                    elif type(vv).__name__ == type(instance).__name__:
                        # 不是Base类型的对象，但是类型一致，直接赋型
                        getattr(self, k)[kk] = vv
                    else:
                        raise Exception(f'{v} 和需要的类型不一致。 {type(instance).__name__}')
            elif hasattr(self, k) and isinstance(getattr(self, k), list):
                if not isinstance(v, list):
                    raise Exception(f'{k} 需要是一个列表。 {self.__class__}')
                for vv in v:
                    instance = self.new_instance(k, vv)  # 根据_types中预设，创建对应的value对象
                    if isinstance(instance, ContextBase):
                        # 如果是Base类型的对象，需要传入json进行装载
                        instance.load(vv)
                        getattr(self, k).append(instance)
                    elif type(vv).__name__ == type(instance).__name__:
                        # 不是Base类型的对象，但是类型一致，直接赋型
                        getattr(self, k).append(vv)
                    else:
                        raise Exception(f'{v} 和需要的类型不一致。 {type(instance).__name__}')
            elif hasattr(self, k) and getattr(self, k) is None:
                instance = self.new_instance(k, v)  # 根据_types中预设，创建对应的value对象
                if isinstance(instance, ContextBase):
                    # 如果是Base类型的对象，需要传入json进行装载
                    instance.load(v)
                    setattr(self, k, instance)
                elif type(v).__name__ == type(instance).__name__:
                    # 不是Base类型的对象，但是类型一致，直接赋型
                    setattr(self, k, v)
                else:
                    raise Exception(f'{v} 和需要的类型不一致。 {type(instance).__name__}')
            elif hasattr(self, k) and type(v).__name__ == type(getattr(self, k)).__name__:
                setattr(self, k, v)
            elif hasattr(self, k) and type(v).__name__ != type(getattr(self, k)).__name__:
                raise Exception(f'{k} 和需要的类型不一致。 需要的类型{type(getattr(self, k)).__name__}')
            else:
                raise Exception(f'{k} 不是一个有效的配置项。 {self.__class__}')

    def new_instance(self, config_name, value=None):
        if config_name not in self._types.keys():
            raise Exception(f'{config_name} 未指定类型。 {self.__class__}')
        if isinstance(self._types[config_name], list):
            for type_ in self._types[config_name]:
                if type_ == type(value):
                    return type_()
                if isinstance(value, dict):     # 是ContextBase的类型，尝试是否匹配
                    ins = type_()
                    matched = True
                    for key in value.keys():
                        if not hasattr(ins, key):
                            matched = False
                            break
                    if matched:
                        return ins
            raise Exception(f'{config_name}当前值{value}不是指定的类型{self._types[config_name]}。 {self.__class__}')
        return self._types[config_name]()
