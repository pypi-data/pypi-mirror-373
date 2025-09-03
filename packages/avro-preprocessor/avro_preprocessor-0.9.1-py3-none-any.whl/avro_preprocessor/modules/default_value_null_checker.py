"""
A module to make sure no default values other than null are used
"""
import json
from collections import OrderedDict

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.modules.avro_sorter import AvroSorter
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Tobias Hermann"
__copyright__ = "Copyright 2021, Jaumo GmbH"
__email__ = "tobias.hermann@jaumo.com"


class DefaultValueNullChecker(PreprocessorModule):
    """
    Checks default values of fields for being null.
    """

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.validate_default_value, schema)

        if self.failed_schemas_names:
            raise ValueError("Invalid default values detected, see above for specific errors.")

    def validate_default_value(self, schema: Avro.Node) -> None:
        """
        Makes sure no default values other than null are used.

        :param schema: The (sub) schema
        """

        if isinstance(schema, OrderedDict):
            if Avro.Default in schema:
                if schema[Avro.Default] is not None:
                    self.failed_schemas_names.append(self.current_schema_name)
                    print(
                        'Error: null is the only allowed default value for fields:   ',
                        self.current_schema_name,
                        '   subschema: ', self.json_of(schema)
                    )

    @staticmethod
    def json_of(schema: OrderedDict) -> str:
        """
        Gets a compact, sorted JSON representation of a (sub) schema
        :param schema: The (sub) schema
        :return: The string representation
        """
        return json.dumps(AvroSorter.sort_avro(schema), indent=None)
