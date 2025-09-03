"""
A module to analyze schema dependencies in a path
"""

from collections import OrderedDict
from typing import Optional

import networkx as nx

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class SchemaDependenciesChecker(PreprocessorModule):
    """
    Checks schema dependencies - exception thrown if it detects cycles.

    NOTE: Records defined within schemas are ignored.
    """
    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)

        self.record_dependencies: OrderedDict = OrderedDict()
        self.record_dependencies_graph = nx.DiGraph()

        self.current_schema_fully_qualified_name: Optional[str] = None

    def process(self) -> None:
        """Detects all dependencies among schemas."""
        for _, schema in self.processed_schemas_iter():
            self.find_dependencies_in_schema(schema)

        dependencies = {record: sorted(nx.descendants(self.record_dependencies_graph, record))
                        for record in self.record_dependencies_graph}

        self.record_dependencies = \
            OrderedDict(sorted(dependencies.items(), key=lambda kv: len(kv[1])))

        if self.schemas.verbose:
            for idx, (record, dependencies) in enumerate(self.record_dependencies.items()):
                print(idx, '# deps:', len(dependencies), record, dependencies)

        # let's assert there are no cycles
        try:
            cycle = nx.find_cycle(self.record_dependencies_graph, "original")
            print(cycle)
            raise ValueError("The supplied list of schemas contains cyclic dependencies!")
        except nx.exception.NetworkXNoCycle:
            pass  # this is the expected outcome. No cycles should be found.

    def find_dependencies_in_schema(self, schema: OrderedDict) -> None:
        """
        Detects dependencies for a schema.
        :param schema: The schema
        """
        self.current_schema_fully_qualified_name = \
            '.'.join((schema[Avro.Namespace], schema.get(Avro.Name, schema.get(Avro.Protocol))))
        self.record_dependencies_graph.add_node(self.current_schema_fully_qualified_name)

        self.traverse_schema(self.store_dependencies_of_field, schema)

    def store_dependencies_of_field(self, node: Avro.Node) -> None:
        """
        Store dependencies of other records in a node in a private dict
        :param node: The input node
        """

        if isinstance(node, str):
            if '.' in node and node in self.schemas.processed:
                self.record_dependencies_graph.add_edge(
                    self.current_schema_fully_qualified_name, node)
