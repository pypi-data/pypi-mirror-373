"""
A module to check that the directory structure corresponds to the schema declared namespace.
"""

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class NamespaceChecker(PreprocessorModule):
    """
    Checks schema namespace.
    """
    def process(self) -> None:
        """Process all schemas."""
        for name, schema in self.processed_schemas_iter():
            class_declared_name = schema[Avro.Namespace] + '.' + \
                                  schema.get(Avro.Name, schema.get(Avro.Protocol))
            # print(name, '=?=', class_declared_name)
            if name != class_declared_name:
                raise ValueError(
                    "File tree path and in schema namespace + name should coincide {} != {}"
                    .format(name, class_declared_name)
                )
