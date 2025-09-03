"""
A module to check that every field has appropriate documentation and duplications
due to copy/paste.
"""
import copy
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Tuple

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.modules.avro_sorter import AvroSorter
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


@dataclass
class Schema:
    """
    Helper class to store schemas
    """
    name: str
    schema: str


class DocumentationChecker(PreprocessorModule):
    """
    Checks documentation fields ('doc').
    """

    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)

        self.documented_nodes: Tuple = (Avro.Name, Avro.Protocol, Avro.Request, Avro.Response)

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.check_documentation, schema)

        if self.failed_schemas_names:
            raise ValueError("Naming conventions are mandatory, see above for specific errors.")

    def check_documentation(self, schema: Avro.Node) -> None:
        """
        Checks that a (sub) schema complies with the documentation policies:

        1. (sub) schemas with a "name" property MUST have a "doc" property.
        2. (sub) schemas without a "name" property MUST NOT have a "doc" property.

        :param schema: The (sub) schema
        """

        if isinstance(schema, OrderedDict):

            if Avro.Doc in schema:
                if all(field not in schema for field in self.documented_nodes):
                    self.failed_schemas_names.append(self.current_schema_name)
                    print(
                        'Error: sub-schema with no "name" property has "doc":   ',
                        self.current_schema_name,
                        '   subschema: ', self.json_of(schema)
                    )

            else:
                if any(field in schema for field in self.documented_nodes):
                    self.failed_schemas_names.append(self.current_schema_name)
                    print(
                        'Error: no "doc" field in schema   ',
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
        schema_copy = copy.deepcopy(schema)
        if Avro.PartitionKey in schema_copy:
            schema_copy.pop(Avro.PartitionKey)
        return json.dumps(AvroSorter.sort_avro(schema_copy), indent=None)
