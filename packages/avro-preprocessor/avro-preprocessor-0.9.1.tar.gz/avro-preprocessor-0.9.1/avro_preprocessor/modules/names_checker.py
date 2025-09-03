"""
A module to check that schemas and fields names have appropriate format.
"""
import json
from collections import Counter, OrderedDict
from typing import Dict, List

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.modules.avro_sorter import AvroSorter
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class NamesChecker(PreprocessorModule):
    """
    Checks names of schemas and fields for appropriate format.
    """
    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)

        self.current_schema_name: str = ""
        self.field_names: Dict[str, List[str]] = {}
        self.naming_conventions = {
            "snake_case": self.is_snake_case,
            "camelCase": self.is_camel_case,
        }
        self.convention_counts: Counter[str] = Counter()

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.process_schema, schema)

        if self.convention_counts:
            most_common_convention = self.convention_counts.most_common(1)[0][0]
            naming_convention = self.naming_conventions[most_common_convention]
            print(f"Detected fields naming convention: {most_common_convention}")
            inconsistent_fields = []
            for schema_name, field_names in self.field_names.items():
                for field_name in field_names:
                    if not naming_convention(field_name):
                        inconsistent_fields.append((schema_name, field_name))
                        self.failed_schemas_names.append(schema_name)

            if inconsistent_fields:
                print(f"Inconsistent fields: {inconsistent_fields}")

        if self.failed_schemas_names:
            raise ValueError("Naming conventions are mandatory, see above for specific errors.")

    def process_schema(self, schema: Avro.Node) -> None:
        if not isinstance(schema, OrderedDict):
            return

        if Avro.Protocol in schema:
            if not self.is_pascal_case(schema[Avro.Protocol]):
                self.failed_schemas_names.append(self.current_schema_name)
                print(
                    'Error: schema "protocol" does not comply to policy (camel case):   ',
                    self.current_schema_name,
                    '   subschema: ', self.json_of(schema)
                )

        if Avro.Name in schema:
            if Avro.Type in schema and schema[Avro.Type] in (Avro.Record, Avro.Enum, Avro.Error):
                if not self.is_pascal_case(schema[Avro.Name]):
                    self.failed_schemas_names.append(self.current_schema_name)
                    print(
                        'Error: schema/record "name" does not comply to policy (camel case):   ',
                        self.current_schema_name,
                        '   subschema: ', self.json_of(schema)
                    )

                if Avro.Fields in schema:
                    if self.current_schema_name not in self.field_names:
                        self.field_names[self.current_schema_name] = []

                    for field in schema[Avro.Fields]:
                        self.field_names[self.current_schema_name].append(field[Avro.Name])
                        for convenation_name, convention in self.naming_conventions.items():
                            if convention(field[Avro.Name]):
                                self.convention_counts[convenation_name] += 1

    @staticmethod
    def is_snake_case(string: str) -> bool:
        """
        Check if a string is snake_case.
        """
        return string == string.lower()

    @staticmethod
    def is_pascal_case(string: str) -> bool:
        """
        Check if a string is PascalCase.
        """
        return '_' not in string and string[0].isupper()

    @staticmethod
    def is_camel_case(string: str) -> bool:
        """
        Check if a string is camelCase.
        """
        return '_' not in string and string[0].islower()

    @staticmethod
    def json_of(schema: OrderedDict) -> str:
        """
        Gets a compact, sorted JSON representation of a (sub) schema
        :param schema: The (sub) schema
        :return: The string representation
        """
        return json.dumps(AvroSorter.sort_avro(schema), indent=None)
