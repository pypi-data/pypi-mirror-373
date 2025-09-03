"""
A module to sorts all the fields of Avro schemas.
"""
import json
from collections import OrderedDict

from avro_preprocessor.colored_json import ColoredJson
from avro_preprocessor.preprocessor_module import PreprocessorModule

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class AvroSorter(PreprocessorModule):
    """
    Sort Avro schemas.
    """

    AVRO_ORDER = [
        'namespace',
        'protocol',  # used in protocols
        'name',
        'doc',
        'deprecated',
        'aliases',
        'partition-field',  # custom extension
        'nullable_optional',  # custom extension
        'default',
        'type',
        'order',
        'fields',
        'symbols',
        'deprecated-symbols',
        'items',
        'values',
        'size',

        'logicalType',  # used in logical types
        'precision',  # used in logical types
        'scale',  # used in logical types

        'types',  # used in protocols
        'messages',  # used in protocols
        'request',  # used in protocols
        'response',  # used in protocols
        'errors',  # used in protocols
        'one-way',  # used in protocols
    ]

    ORDER = {key: i for i, key in enumerate(AVRO_ORDER)}

    def process(self) -> None:
        """Process all schemas."""
        for name, schema in self.processed_schemas_iter():
            self.schemas.processed[name] = self.sort_avro(schema)

    @classmethod
    def sort_avro(cls, schema: OrderedDict) -> OrderedDict:
        """
        Performs the sort.

        :param schema: An Avro schema
        :return: The sorted schema
        """
        schema = schema.copy()
        for key, value in schema.items():
            if isinstance(value, OrderedDict):
                schema[key] = cls.sort_avro(value)
            elif isinstance(value, list):
                schema[key] = [cls.sort_avro(element) if isinstance(element, OrderedDict) else element
                               for element in value]

        return OrderedDict(sorted(schema.items(), key=lambda item: cls.ORDER.get(item[0], 1000)))


class AvroOrderChecker(AvroSorter):
    """
    Checks if input Avro schemas are correctly sorted.
    """
    def process(self) -> None:
        """Process all schemas."""

        for name, schema in self.processed_schemas_iter():
            sorted_schema = self.sort_avro(schema)
            if schema != sorted_schema:
                self.failed_schemas_names.append(name)
                print('########## Schema', name, 'is sorted incorrectly:')
                print(json.dumps(schema, indent=ColoredJson.json_indent))
                print('\n########## Should be:')
                print(json.dumps(sorted_schema, indent=ColoredJson.json_indent))
                print('\n\n')

        if self.failed_schemas_names:
            raise ValueError(
                "Schema properties should be sorted according to the following order:\n\n\t{}"
                "\n\nSchemas with correct order were printed above."
                .format('\n\t'.join(self.AVRO_ORDER))
            )
