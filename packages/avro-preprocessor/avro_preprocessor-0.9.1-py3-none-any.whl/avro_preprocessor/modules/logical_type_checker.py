"""
A module to check for valid usage of logicalType.
"""
from collections import OrderedDict

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule

__author__ = "Paul Kofmann"
__copyright__ = "Copyright 2024, Jaumo GmbH"
__email__ = "paul.kofmann@jaumo.com"


REQUIRED_TYPE_MAPPING = {
    'uuid': 'string',
    'decimal': 'bytes',
    'date': 'int',
    'time-millis': 'int',
    'time-micros': 'long',
    'timestamp-millis': 'long',
    'timestamp-micros': 'long',
}


class LogicalTypeChecker(PreprocessorModule):
    """
    Checks for conflicts between logicalType and type.
    """

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.check_logical_type, schema)

    def check_logical_type(self, record: Avro.Node) -> None:
        """
        Finds property 'logicalType' inside schemas and checks for consistency with 'type'.
        :param record: The schema
        """
        if isinstance(record, OrderedDict) and Avro.LogicalType in record:
            logical_type = record[Avro.LogicalType]
            required_type = REQUIRED_TYPE_MAPPING.get(logical_type, None)
            if required_type is not None:
                type = record[Avro.Type]
                if isinstance(type, list):
                    type = next((x for x in type if x != "null"), None)
                if type != required_type:
                    raise ValueError(
                        'logicalType "{}" requires type "{}" in schema {}'
                        .format(logical_type, required_type, self.current_schema_name)
                    )
