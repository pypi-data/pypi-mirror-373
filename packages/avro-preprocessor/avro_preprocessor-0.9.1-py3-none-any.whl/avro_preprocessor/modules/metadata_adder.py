"""
A module to add a standard metadata record to every event.
"""
import copy
from collections import OrderedDict

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class MetadataAdder(PreprocessorModule):
    """
    Adds the metadata type to every event.
    """

    def process(self) -> None:
        """Process all schemas."""

        # If types namespace was defined by the user
        if self.schemas.paths.types_namespace:

            # Let's check if the metadata type exists
            metadata_fully_qualified_name = self.schemas.paths.metadata_schema
            if metadata_fully_qualified_name in self.schemas.original:

                metadata = self.schemas.original[metadata_fully_qualified_name]
                metadata_field = OrderedDict((
                    (Avro.Name, "metadata"),
                    (Avro.Doc, 'Standard metadata for all schemas'),
                    (Avro.Type, metadata)
                ))

                for name, schema in self.processed_schemas_iter():

                    # metadata added only to domain schemas (that are not excluded).
                    # Added as first element in the fields list
                    if self.schemas.paths.is_event_resource(name) and all(
                            not name.startswith(exclude)
                            for exclude in self.schemas.paths.metadata_exclude
                    ):
                        schema[Avro.Fields].insert(0, copy.deepcopy(metadata_field))
