"""
A module to expand references of types in schemas using a Depth First strategy.
"""

import copy
from collections import OrderedDict
from typing import Set, Union, cast

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class ReferencesExpander(PreprocessorModule):
    """
    Expands References in all schemas.
    """
    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)

        self.per_schema_already_expanded_records: Set = set()

    def process(self) -> None:
        """Process all schemas."""

        for _, schema in self.processed_schemas_iter():
            self.per_schema_already_expanded_records = set()
            self.traverse_schema(self.expand_ref_in_record, schema)

    def expand_ref_in_record(self, node: Avro.Node) -> bool:
        """
        Expands references in an Avro Node.
        :param node: The node
        """
        if self.ancestors and isinstance(node, str):
            original_value = cast(OrderedDict, self.ancestors[-1].node)[self.ancestors[-1].key]
            modified_value = self.do_expand(node)

            if modified_value != original_value:
                cast(OrderedDict, self.ancestors[-1].node)[self.ancestors[-1].key] = modified_value
                return True

        return False

    def do_expand(self, resource_to_expand: str) -> Union[str, OrderedDict]:
        """
        Here we do_expand a resource (e.g. com.example.event.type.Gender) if it complies with
        certain criteria (they are in the "if").

        :param resource_to_expand: the resource
        :return: Whether the criteria were met or not
        """
        if '.' in resource_to_expand \
                and resource_to_expand not in self.per_schema_already_expanded_records \
                and resource_to_expand in self.schemas.original:

            self.per_schema_already_expanded_records.add(resource_to_expand)
            return cast(OrderedDict, copy.deepcopy(self.schemas.original[resource_to_expand]))

        return resource_to_expand
