"""
A module to create a map fully_qualified_class_name -> topic name.
"""
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, List, Any

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.avro_naming import AvroNaming
from avro_preprocessor.colored_json import ColoredJson
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


@dataclass
class SchemaMappingFields:  # pylint: disable=R0902
    """
    Fields for the schema mapping file
    """
    topic = 'topic'

    value_fqcn = 'value-fqcn'
    value_subject = 'value-subject'

    default_key_fqcn = 'default-key-fqcn'
    default_key_subject = 'default-key-subject'

    partition_key_fqcn = 'partition-key-fqcn'
    partition_key_subject = 'partition-key-subject'

    partition_fields = 'partition-fields'
    user_id_fields = 'user-id-fields'


SMF = SchemaMappingFields


class SchemaMappingGenerator(PreprocessorModule):
    """
    Generates and saves the schema mapping.
    """

    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)
        self.current_schema_name: str = ""
        self.schema_mapping: Dict[Any, Any] = {}

    def process(self) -> None:
        """Process all schemas."""

        for name, schema in self.processed_schemas_iter():
            if all(not name.startswith(exclude) for exclude in self.schemas.paths.schema_mapping_exclude):
                if name.startswith(self.schemas.paths.base_namespace):
                    self.schema_mapping[name] = OrderedDict((

                        (SMF.topic, AvroNaming.get_topic(
                            self.schemas.paths.base_namespace, name, self.schemas.paths.topic_prefix)),

                        (SMF.value_fqcn, name),
                        (SMF.value_subject, AvroNaming.get_subject_name_for_value(
                            self.schemas.paths.base_namespace, name, self.schemas.paths.topic_prefix)),

                        # Default common key uses RecordNameStrategy in the schema registry
                        (SMF.default_key_fqcn, self.schemas.paths.key_schema),
                        (SMF.default_key_subject, self.schemas.paths.key_schema),

                        (SMF.partition_key_fqcn, AvroNaming.get_key_fully_qualified_name(name)),
                        (SMF.partition_key_subject, AvroNaming.get_subject_name_for_key(
                            self.schemas.paths.base_namespace,
                            AvroNaming.get_key_fully_qualified_name(name),
                            self.schemas.paths.topic_prefix)),

                        (SMF.partition_fields, []),
                        (SMF.user_id_fields, [])

                    ))
                else:
                    # for extra schemas, only the value subject makes sense and is needed in the schema-mapping
                    self.schema_mapping[name] = OrderedDict((
                        (SMF.topic, ''),
                        (SMF.value_fqcn, name),
                        (SMF.value_subject, name),
                        (SMF.default_key_fqcn, ''),
                        (SMF.default_key_subject, ''),
                        (SMF.partition_key_fqcn, ''),
                        (SMF.partition_key_subject, ''),
                        (SMF.partition_fields, []),
                        (SMF.user_id_fields, [])
                    ))

                self.current_schema_name = name

                self.traverse_schema(self.find_partition_keys, schema)
                self.schema_mapping[name][SMF.partition_fields] = \
                    sorted(self.schema_mapping[name][SMF.partition_fields])

                self.traverse_schema(self.find_logical_types, schema)
                self.schema_mapping[name][SMF.user_id_fields] = \
                    sorted(self.schema_mapping[name][SMF.user_id_fields])

        sorted_schema_mapping = OrderedDict(sorted(self.schema_mapping.items()))
        sorted_schema_mapping_text = \
            json.dumps(sorted_schema_mapping, indent=ColoredJson.json_indent)
        if self.schemas.verbose:
            print('Schema Mapping:')
            print(sorted_schema_mapping_text)
            print()

        self.schemas.paths.schema_mapping_path.parent.mkdir(parents=True, exist_ok=True)
        self.schemas.paths.schema_mapping_path.write_text(sorted_schema_mapping_text)

        # we now check if schemas inside the same topic have the same key
        last_key_list: List[str] = []
        last_topic = ""
        for name, mapping in sorted_schema_mapping.items():
            self.current_schema_name = name
            topic = AvroNaming.get_topic(self.schemas.paths.base_namespace, name, self.schemas.paths.topic_prefix)
            key_list = mapping[SMF.partition_fields]
            if topic == last_topic:
                if key_list != last_key_list:
                    raise ValueError(
                        "Key list must be the same inside a topic:\n"
                        "\tcurrent schema: {}, key list: {}\n"
                        "\tlast seen key list in the same topic {}:"
                        .format(name, key_list, last_key_list)
                    )

            last_topic = topic
            last_key_list = key_list

    def find_partition_keys(self, node: Avro.Node) -> None:
        """
        Finds property 'partition-field' inside schemas and saves them in the schema mapping.
        :param node: The node
        """
        if isinstance(node, OrderedDict) and Avro.PartitionKey in node:
            if node[Avro.PartitionKey]:
                self.schema_mapping[self.current_schema_name][SMF.partition_fields] \
                    .append(node[Avro.Name])

            # property 'partition-field' is removed from the schema anyway
            node.pop(Avro.PartitionKey)

    def find_logical_types(self, node: Avro.Node) -> None:
        """
        Finds logicalType 'user-id-fields' inside schemas and saves them in the schema mapping.
        :param node: The node
        """
        if self.ancestors and isinstance(node, OrderedDict):
            if Avro.LogicalType in node and node[Avro.LogicalType] == 'user_id':
                fully_qualified_field_name: List[str] = []

                for ancestor in reversed(self.ancestors):
                    if Avro.Type in ancestor.node \
                            and isinstance(ancestor.node, OrderedDict) \
                            and ancestor.node[Avro.Type] in \
                            self.schemas.paths.schema_mapping_user_id_types_exclude:
                        return

                for ancestor in self.ancestors:
                    if Avro.Name in ancestor.node \
                            and isinstance(ancestor.node, OrderedDict) \
                            and Avro.Type in ancestor.node \
                            and ancestor.node[Avro.Type] != Avro.Record:
                        fully_qualified_field_name.append(ancestor.node[Avro.Name])

                if len(fully_qualified_field_name) >= 1:
                    field_name = '.'.join(fully_qualified_field_name)
                    user_id_fields = \
                        self.schema_mapping[self.current_schema_name][SMF.user_id_fields]
                    if field_name not in user_id_fields:
                        user_id_fields.append(field_name)
