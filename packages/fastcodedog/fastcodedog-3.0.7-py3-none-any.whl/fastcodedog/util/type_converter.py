# -*- coding: utf-8 -*-


def database_type_to_sqlalchemy_type(data_type, length=None):
    data_type_ = data_type.lower()
    if data_type_.startswith('int') or data_type_ == 'integer':
        return 'Integer', 'Integer'
    elif data_type_.startswith('bigint'):
        return 'BigInteger', 'BigInteger'
    elif data_type_ == 'varchar' or data_type_.startswith('varchar'):
        return 'String', 'String(%d)' % length
    elif data_type_ == 'datetime' or data_type_.startswith('timestamp'):
        return 'DateTime', 'DateTime'
    elif data_type_ == 'date' or data_type_.startswith('timestamp'):
        return 'Date', 'Date'
    elif data_type_ == 'time' or data_type_.startswith('timestamp'):
        return 'Time', 'Time'
    elif data_type_ == 'blob' or data_type_ == 'longblob':
        return 'BLOB', 'BLOB'
    elif data_type_.startswith('tinyint') or data_type_.startswith(
            'smallint') or data_type_ == 'boolean':
        return 'Boolean', 'Boolean'
    elif data_type_ == 'text':
        return 'Text', 'Text'
    elif data_type_.startswith('decimal'):
        return 'DECIMAL', 'DECIMAL'
    elif data_type_.startswith('double'):
        return 'Float', 'Float'
    elif data_type_ == 'json':
        return 'JSON', 'JSON'
    else:
        raise Exception('不支持的数据类型%s' % data_type_)


def sqlalchemy_type_to_pydantic_type(data_type, length=None):
    data_type_ = data_type
    if data_type_ == 'Integer':
        return 'int', 'int'
    elif data_type_.startswith('BigInteger'):
        return 'int', 'int'
    elif data_type_.startswith('String'):
        return 'constr', f'constr(max_length={length})' if length else 'constr'
    elif data_type_ == 'Text':
        return 'str', 'str'
    elif data_type_ == 'DateTime':
        return 'datetime', 'datetime'
    elif data_type_ == 'Date':
        # Pydantic does not have a dedicated Date type, using string as an example.
        return 'date', 'date'
    elif data_type_ == 'Time':
        # Similarly, for time, we can use a string representation.
        return 'time', 'time'
    elif data_type_ == 'BLOB':
        # Depending on use case, this could be a byte type or a string (hex encoded).
        return 'bytes', 'bytes'
    elif data_type_ == 'Boolean':
        return 'bool', 'bool'
    elif data_type_.startswith('DECIMAL'):
        # Assuming fixed precision and scale could be defined based on the actual column definition.
        return 'float', 'float'  # Simplified for illustration; Pydantic doesn't have a Decimal type out of the box.
    elif data_type_.startswith('Float'):
        return 'float', 'float'
    elif data_type_.startswith('JSON'):
        return 'Dict', 'Dict'       # 默认dict，还有可能是list
    else:
        raise ValueError(f'unsupported data type {data_type_}.')


def database_type_to_pydantic_type(data_type, length=None):
    data_type_ = data_type.lower()
    if data_type_.startswith('int') or data_type_ == 'integer':
        return 'int', 'int'
    elif data_type_.startswith('bigint'):
        return 'int', 'int'
    elif data_type_.startswith('varchar') or data_type_ == 'varchar':
        return 'constr', f'constr(max_length={length})' if length else 'constr'
    elif data_type_ == 'text':
        return 'str', 'str'
    elif data_type_ == 'datetime' or data_type_.startswith('timestamp'):
        return 'datetime', 'datetime'
    elif data_type_ == 'date' or data_type_.startswith('timestamp'):
        # Pydantic does not have a dedicated Date type, using string as an example.
        return 'date', 'date'
    elif data_type_ == 'time' or data_type_.startswith('timestamp'):
        # Similarly, for time, we can use a string representation.
        return 'time', 'time'
    elif data_type_ == 'blob' or data_type_ == 'longblob':
        # Depending on use case, this could be a byte type or a string (hex encoded).
        return 'bytes', 'bytes'
    elif data_type_.startswith('tinyint') or data_type_.startswith('smallint') or data_type_ == 'boolean':
        return 'bool', 'bool'
    elif data_type_.startswith('decimal'):
        # Assuming fixed precision and scale could be defined based on the actual column definition.
        return 'float', 'float'  # Simplified for illustration; Pydantic doesn't have a Decimal type out of the box.
    elif data_type_.startswith('double'):
        return 'float', 'float'
    elif data_type_.startswith('JSON'):
        return 'Dict', 'Dict'       # 默认dict，还有可能是list
    else:
        raise ValueError(f'unsupported data type {data_type_}.')


def database_type_to_python_type(data_type, length=None):
    data_type_ = data_type.lower()
    if data_type_.startswith('int') or data_type_ == 'integer':
        return 'int'
    elif data_type_.startswith('bigint'):
        return 'int'
    elif data_type_.startswith('varchar') or data_type_ == 'varchar':
        return 'str'
    elif data_type_ == 'text':
        return 'str'
    elif data_type_ == 'datetime' or data_type_.startswith('timestamp'):
        return 'datetime.datetime'
    elif data_type_ == 'date':
        return 'datetime.date'
    elif data_type_ == 'time':
        # Similarly, for time, we can use a string representation.
        return 'datetime.time'
    elif data_type_ == 'blob' or data_type_ == 'longblob':
        # Depending on use case, this could be a byte type or a string (hex encoded).
        return 'bytes'
    elif data_type_.startswith('tinyint') or data_type_.startswith('smallint') or data_type_ == 'boolean':
        return 'bool'
    elif data_type_.startswith('decimal'):
        # Assuming fixed precision and scale could be defined based on the actual column definition.
        return 'float'
    elif data_type_.startswith('double'):
        return 'float'
    elif data_type_.startswith('json'):
        return 'dict'       # 默认dict，还有可能是list
    else:
        raise ValueError(f'unsupported data type {data_type_}.')
