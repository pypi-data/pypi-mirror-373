"""
Module providing a custom order for json-based Avro schemas.
"""
from collections import OrderedDict
from typing import Union

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

from dataclasses import dataclass


@dataclass
class Avro:  # pylint: disable-all
    """
    Helper class to avoid plain strings as dictionary keys.
    """
    Name = 'name'
    Namespace = 'namespace'
    Type = 'type'
    Fields = 'fields'
    Items = 'items'
    Deprecated = 'deprecated'
    DeprecatedSymbols = 'deprecated-symbols'
    Doc = 'doc'
    Record = 'record'
    Error = 'error'
    Enum = 'enum'
    Default = 'default'
    LogicalType = 'logicalType'
    Symbols = 'symbols'
    Array = 'array'
    Map = 'map'
    Aliases = 'aliases'
    Order = 'order'
    Values = 'values'
    Size = 'size'
    Precision = 'precision'
    Scale = 'scale'

    Protocol = 'protocol'
    Messages = 'messages'
    Request = 'request'
    Response = 'response'
    Types = 'types'
    Errors = 'errors'
    OneWay = 'one-way'

    Optional = 'nullable_optional'
    PartitionKey = 'partition-field'

    Null = 'null'
    Value = 'value'

    Node = Union[str, list, OrderedDict]
    Key = Union[slice, int, None]
