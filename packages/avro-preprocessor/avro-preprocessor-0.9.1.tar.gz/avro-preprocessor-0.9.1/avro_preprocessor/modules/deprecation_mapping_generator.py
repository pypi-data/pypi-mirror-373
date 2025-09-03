"""
A module to create a map fully_qualified_class_name -> deprecations info.
"""
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, Any

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.colored_json import ColoredJson
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Pavel Cofman"
__copyright__ = "Copyright 2023, Jaumo GmbH"
__email__ = "paul@jaumo.com"


@dataclass
class DeprecationsFields:  # pylint: disable=R0902
    fields = 'deprecated-fields'
    deprecated = 'deprecated'
    deprecated_symbols = 'deprecated-symbols'
    name = 'name'
    doc = 'doc'


DF = DeprecationsFields


class DeprecationMappingGenerator(PreprocessorModule):
    """
    Generates and saves the deprecations mapping JSON.
    """

    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)
        self.deprecations_mapping: Dict[Any, Any] = {}

    def process(self) -> None:
        """Process all schemas."""

        for name, schema in self.processed_schemas_iter():
            self.traverse_schema(self.find_deprecations, schema)

        sorted_deprecations_mapping = OrderedDict(sorted(self.deprecations_mapping.items()))
        sorted_deprecations_text = \
            json.dumps(sorted_deprecations_mapping, indent=ColoredJson.json_indent)
        if self.schemas.verbose:
            print('Deprecations:')
            print(sorted_deprecations_text)
            print()

        self.schemas.paths.deprecation_mapping_path.parent.mkdir(parents=True, exist_ok=True)
        self.schemas.paths.deprecation_mapping_path.write_text(sorted_deprecations_text)

    def init_mapping_entry(self, name: str) -> None:
        if name not in self.deprecations_mapping:
            self.deprecations_mapping[name] = OrderedDict((
                (DF.fields, []),
            ))

    @staticmethod
    def assert_string_type(v: Any) -> None:
        if not isinstance(v, str):
            raise ValueError("Deprecated property requires string value")

    def get_current_record_fqn(self, current_node: Avro.Node) -> str:
        name = None
        for node in [current_node] + list(map(lambda a: a.node, reversed(self.ancestors))):
            if name is None and Avro.Name in node \
                    and isinstance(node, OrderedDict) \
                    and node.get(Avro.Type) in [Avro.Record, Avro.Enum]:
                name = node[Avro.Name]
            if Avro.Namespace in node and isinstance(node, OrderedDict):
                if name is None:
                    raise ValueError("Record without name")
                return f"{node[Avro.Namespace]}.{name}"
        raise ValueError("Can't determine current records' FQN")

    def find_deprecations(self, node: Avro.Node) -> None:
        """
        Finds "deprecated" and "deprecated-symbols" properties and saves docs into the deprecations mapping.
        :param node: The node
        """
        if isinstance(node, OrderedDict) and node.get(Avro.Type) == Avro.Enum and Avro.DeprecatedSymbols in node:
            fqn = self.get_current_record_fqn(node)
            self.init_mapping_entry(fqn)
            if DF.deprecated_symbols not in self.deprecations_mapping[fqn]:
                self.deprecations_mapping[fqn][DF.deprecated_symbols] = node.get(Avro.DeprecatedSymbols)
            node.pop(Avro.DeprecatedSymbols)

        if isinstance(node, OrderedDict) and Avro.Deprecated in node:
            deprecation_doc = node[DF.deprecated]
            self.assert_string_type(deprecation_doc)
            node.pop(Avro.Deprecated)
            fqn = self.get_current_record_fqn(node)
            self.init_mapping_entry(fqn)
            if node.get(Avro.Type) in [Avro.Record, Avro.Enum]:
                self.deprecations_mapping[fqn][DF.deprecated] = deprecation_doc
            else:
                field_name = node[Avro.Name]
                if all(f[DF.name] != field_name for f in self.deprecations_mapping[fqn][DF.fields]):
                    self.deprecations_mapping[fqn][DF.fields].append({DF.name: field_name, DF.doc: deprecation_doc})
