"""
# Support to use a list for lists as "doc" field to deal with JSON obnoxious lack of
# newline support in strings
"""
from collections import OrderedDict

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class DocumentationCondenser(PreprocessorModule):
    """
    Condense documentation fields ('doc').
    """

    def process(self) -> None:
        """Process all schemas."""

        # This module has to be applied even to the original schemas
        for _, schema in self.original_schemas_iter():
            self.traverse_schema(self.condense_documentation, schema)

        for _, schema in self.processed_schemas_iter():
            self.traverse_schema(self.condense_documentation, schema)

    @staticmethod
    def condense_documentation(node: Avro.Node) -> None:
        """
        Condense the "doc" field from list to one string

        :param node: The (sub) node
        """

        if isinstance(node, OrderedDict):
            if Avro.Doc in node:
                if isinstance(node[Avro.Doc], list):
                    node[Avro.Doc] = ' '.join(node[Avro.Doc])
