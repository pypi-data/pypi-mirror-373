"""
A module to expand nullable_optional fields.
"""

from collections import OrderedDict
from typing import Set, Optional, Tuple, cast

from avro_preprocessor.avro_domain import Avro
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class NullableOptionalExpander(PreprocessorModule):
    """
    Expand nullable_optional fields in all schemas.
    """
    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)

        self.per_schema_nullable_optional_records: Set = set()
        self.current_namespace: Optional[str] = None

    def process(self) -> None:
        """Process all schemas."""
        for _, schema in self.processed_schemas_iter():
            # we keep track of the namespace; used to refer to already substituted custom records
            if Avro.Namespace in schema:
                self.current_namespace = schema[Avro.Namespace]
            self.per_schema_nullable_optional_records = set()
            self.traverse_schema(self.substitute_field_type, schema)

    def get_subrecord_name(self, record: OrderedDict) -> Tuple[str, str]:
        """
        Generates the name of the subrecord for nullable optionals

        :param record: The record in input
        :return: The new name and its fully qualified version
        """
        def capitalize_only_first(word: str) -> str:
            return word[0].upper() + word[1:]

        if isinstance(record[Avro.Type], str):
            if '.' in record[Avro.Type]:
                tokens = record[Avro.Type].split('.')
                new_record_name = \
                    '.'.join(
                        tokens[:-1] + ['Optional' + capitalize_only_first(tokens[-1])]
                    )
            else:
                new_record_name = 'Optional' + capitalize_only_first(record[Avro.Type])
        else:
            if Avro.Name in record[Avro.Type] and Avro.Namespace in record[Avro.Type]:
                new_record_name = '.'.join((
                    record[Avro.Type][Avro.Namespace],
                    'Optional' + capitalize_only_first(record[Avro.Type][Avro.Name])
                ))
            else:
                new_record_name = 'Optional' + capitalize_only_first(record[Avro.Name])

        if self.current_namespace:
            if self.schemas.paths.base_namespace not in new_record_name:
                fully_qualified_subrecord_name = \
                    self.current_namespace + '.' + new_record_name
            else:
                fully_qualified_subrecord_name = new_record_name
        else:
            raise ValueError("self.current_namespace was not initialized for"
                             "name {}, type{}".format(record[Avro.Name], record[Avro.Type]))

        return new_record_name, fully_qualified_subrecord_name

    def substitute_field_type(self, record: Avro.Node) -> None:
        """
        Substitutes in place a nullable_optional record with with Optional<Type>
        (e.g. string -> OptionalString).

        Substitutes in place a nullable_optional record with with Optional<Name>
        (e.g. name = address, type = record -> OptionalAddress).
        :param record: The field in input
        """
        if isinstance(record, OrderedDict) and Avro.Optional in record:
            if record[Avro.Optional] is True:

                subrecord_name, fully_qualified_subrecord_name = self.get_subrecord_name(record)

                if fully_qualified_subrecord_name in self.per_schema_nullable_optional_records:

                    # We cannot define the same record twice in the same file,
                    # so we use a reference here
                    record[Avro.Type] = [Avro.Null, fully_qualified_subrecord_name]
                else:

                    # Saving the reference
                    self.per_schema_nullable_optional_records.add(fully_qualified_subrecord_name)

                    def add_null_type() -> list:
                        current_type = record[cast(slice, Avro.Type)]  # cast to make mypy happy
                        if isinstance(current_type, list):
                            # avro type is a union
                            if Avro.Null in current_type:
                                # "null" already in the list
                                return current_type
                            # we add "null" in the first position of the list
                            return [Avro.Null] + current_type
                        return [Avro.Null, current_type]

                    # Substituting the nullable_optional record with a wrapper:
                    # Semantics:
                    # if MyField == null -> not present
                    # if MyField.value == null -> set-to-null
                    # if MyField.value != null -> set-to-value
                    record[Avro.Type] = [
                        Avro.Null,
                        OrderedDict((
                            (Avro.Name, subrecord_name),
                            (Avro.Type, Avro.Record),
                            (Avro.Fields, [
                                OrderedDict((
                                    (Avro.Name, Avro.Value),
                                    (Avro.Doc, "The optional value"),
                                    (Avro.Type, add_null_type())
                                ))
                            ]),
                        ))
                    ]

                    subrecord: OrderedDict = record[Avro.Type][1]

                    if Avro.Doc in record:
                        subrecord[Avro.Doc] = record[Avro.Doc] + ' (Optional Value)'

                    # Avro complex types have additional fields that must be moved to the subrecord
                    additional_fields = \
                        [(field, record[field]) for field in record
                         if field not in
                         (Avro.Name, Avro.Type, Avro.Doc, Avro.Default, Avro.Optional)]
                    for key, value in additional_fields:
                        subrecord[key] = value
                        record.pop(key)

                # necessary to allow 'not present' semantics
                record[Avro.Default] = None

            # property 'nullable_optional' is removed from the schema anyway
            record.pop(Avro.Optional)
