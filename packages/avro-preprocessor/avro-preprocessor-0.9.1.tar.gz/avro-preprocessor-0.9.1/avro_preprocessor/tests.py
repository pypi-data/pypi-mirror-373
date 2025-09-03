#!/usr/bin/env python3
"""
Test class for the Avro schema extension.
"""
import json
import os
import unittest
from collections import OrderedDict
from pathlib import Path
from typing import Set, Any, Dict

from avro_preprocessor.avro_paths import AvroPaths
from avro_preprocessor.modules.java_classes_creator import JavaClassesCreator
from avro_preprocessor.modules.schema_mapping_generator import SchemaMappingGenerator
from avro_preprocessor.modules.schema_registrar import SchemaRegistrar
from avro_preprocessor.modules.schema_registry_checker import SchemaRegistryChecker
from avro_preprocessor.preprocessor import AvroPreprocessor
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

ROOT_DIR = Path(__file__).absolute().parent.parent
FIXTURES_DIR = ROOT_DIR.joinpath('fixtures/')
JAVA_CLASSES_DIR = ROOT_DIR.joinpath('java_classes/')
AVRO_TOOLS_JAR = str(ROOT_DIR.joinpath('avro-tools-1.9.0.jar'))


class AvroPreprocessorTest(unittest.TestCase):
    """
    Test class for the Avro schema extension.
    """

    try:
        schema_registry_url = os.environ['SCHEMA_REGISTRY']
    except KeyError as e:
        schema_registry_url = 'http://localhost:8081'

    SUCCESS = 0

    schema_header = """
    {
        "namespace": "com.jaumo.event.domain.user.users",
        "name": "TestRecord",
        "doc": "Test extended record",
        "type": "record",
        "fields": [
    """

    schema_footer = """
        ]
    }
    """

    @unittest.skip("fixture not available")
    def test_large_set(self) -> None:
        """
        Test on a large set of schemas.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('../../event_schema/schema/')),
                output_path=str(FIXTURES_DIR.joinpath('../../event_schema/build/schema/')),
                base_namespace='com.jaumo.message_schema',
                types_namespace='com.jaumo.message_schema.type',
                rpc_namespace='com.jaumo.message_schema.rpc',
                metadata_schema='com.jaumo.message_schema.type.domain.metadata.Metadata',
                metadata_exclude=['com.jaumo.message_schema.simple_rpc'],
                key_schema='com.jaumo.message_schema.type.domain.key.DefaultKey',
                key_subject_name_strategy='RecordNameStrategy',
                input_schema_file_extension='exavsc',
                schema_mapping_path=
                ROOT_DIR.joinpath('../event_schema/build/schema-mapping.json'),
                schema_mapping_exclude=[
                    'com.jaumo.message_schema.simple_rpc', 'com.jaumo.message_schema.mqtt'],
                schema_mapping_user_id_types_exclude=['array', 'map'],
                avro_tools_path=AVRO_TOOLS_JAR,
            ),
            verbose=True,
            json_indent=4
        )

        # avro_preprocessor.process()
        import copy
        avro_preprocessor.process([
            m.__name__ for m in
            copy.deepcopy(AvroPreprocessor.preprocessing_modules)
            if m not in [JavaClassesCreator]
            # if m not in [SchemaRegistrar, JavaClassesCreator]
        ])

        # self.assert_trees_equals(
        #     '../../event_schema/build/schema/', '../../event_schema/build/schema_expected/')

    def test_full_t1(self) -> None:
        """
        Full test on fixture 't1_input'.
        """
        paths = AvroPaths(
            input_path=str(FIXTURES_DIR.joinpath('t1_input/')),
            output_path=str(FIXTURES_DIR.joinpath('t1_output/')),
            base_namespace='com.jaumo',
            types_namespace='com.jaumo.type',
            metadata_schema='com.jaumo.type.Metadata',
            key_generation_exclude=['com.jaumo'],
            input_schema_file_extension='exavsc',
            schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
            avro_tools_path=AVRO_TOOLS_JAR
        )

        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths, verbose=True, json_indent=4, schema_registry_url=self.schema_registry_url)
        avro_preprocessor.process()

        self.assert_trees_equals('t1_expected/', 't1_output/')

        self.assertEqual(
            JavaClassesCreator(avro_preprocessor.schemas).get_java_classes_names(),
            sorted({
                'Address',
                'OptionalAddress',
                'OptionalInt_or_string',
                'OptionalString',
                'TestRecursive',
                'Kind',
                'Letter',
                'OptionalInt',
                'OptionalKind',
                'OptionalLetter',
                'OptionalString',
                'UserUpdate'
            }))

    def test_full_t2(self) -> None:
        """
        Full test on fixture 't2_input_unsorted'.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t2_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t2_output/')),
                base_namespace='com.jaumo.event',
                types_namespace='com.jaumo.event.type',
                metadata_schema='com.jaumo.event.type.Metadata',
                input_schema_file_extension='exavsc',
                schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
                avro_tools_path=AVRO_TOOLS_JAR
            ),
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        avro_preprocessor.process()

        self.assert_trees_equals('t2_expected/', 't2_output/')

    def test_full_t3(self) -> None:
        """
        Full test on fixture 't3_input'.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t3_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t3_output/')),
                base_namespace='com.jaumo.schema',
                types_namespace='com.jaumo.schema.type',
                rpc_namespace='com.jaumo.schema.rpc',
                metadata_schema='com.jaumo.schema.type.Metadata',
                input_schema_file_extension='exavsc',
                schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
                avro_tools_path=AVRO_TOOLS_JAR
            ),
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        avro_preprocessor.process()

        self.assert_trees_equals('t3_expected/', 't3_output/')

    def test_full_t3_yaml(self) -> None:
        """
        Full test on fixture 't3_input' but converting to yaml first.
        """
        preproc_args = {
            'verbose': True,
            'schema_registry_url': self.schema_registry_url,
        }

        paths_args = {
            'base_namespace': 'com.jaumo.schema',
            'types_namespace': 'com.jaumo.schema.type',
            'rpc_namespace': 'com.jaumo.schema.rpc',
            'metadata_schema': 'com.jaumo.schema.type.Metadata',
            'schema_mapping_path': ROOT_DIR.joinpath('./schema-mapping.json'),
            'avro_tools_path': AVRO_TOOLS_JAR
        }

        def get_preprocessor(
                input_path: str, input_extension: str, input_format: str,
                output_path: str, output_extension: str, output_format: str) -> AvroPreprocessor:
            paths: Dict[Any, Any] = {**paths_args, **{
                'input_path': str(FIXTURES_DIR.joinpath(input_path)),
                'output_path': str(FIXTURES_DIR.joinpath(output_path)),
                'input_schema_file_extension': input_extension,
                'output_schema_file_extension': output_extension,
                'input_schema_file_format': input_format,
                'output_schema_file_format': output_format,
            }}
            args: Dict[Any, Any] = {**preproc_args, **{'paths': AvroPaths(**paths)}}
            return AvroPreprocessor(**args)

        from avro_preprocessor.modules.documentation_list_condenser import DocumentationCondenser

        # exavsc to yexavsc
        get_preprocessor(
            't3_input/', 'exavsc', 'json',
            't3_yaml/', 'yexavsc', 'yaml'
        ).process([DocumentationCondenser.__name__])

        self.assert_trees_equals('t3_yaml_expected/', 't3_yaml/', 'yexavsc', 'yexavsc', input_format='yaml')

        # yexavsc to avsc
        get_preprocessor(
            't3_yaml/', 'yexavsc', 'yaml',
            't3_output/', 'avsc', 'json'
        ).process()

        self.assert_trees_equals('t3_expected/', 't3_output/')

    def test_full_t4(self) -> None:
        """
        Full test on fixture 't4_input'.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t4_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t4_output/')),
                base_namespace='com.jaumo.schema',
                types_namespace='com.jaumo.schema.type',
                metadata_schema='com.jaumo.schema.type.Metadata',
                metadata_exclude=['com.jaumo.schema.simple_rpc'],
                key_generation_exclude=['com.jaumo.schema.simple_rpc'],
                input_schema_file_extension='exavsc',
                schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
                schema_mapping_exclude=['com.jaumo.schema.simple_rpc'],
                avro_tools_path=AVRO_TOOLS_JAR
            ),
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        avro_preprocessor.process()

        self.assert_trees_equals('t4_expected/', 't4_output/')

    def test_full_t5(self) -> None:
        """
        Full test on fixture 't5_input'.
        Checking that simple fields with logical type user_id are added to the schema mapping
        while collections of user_ids are not.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t5_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t5_output/')),
                base_namespace='com.jaumo.schema',
                types_namespace='com.jaumo.schema.type',
                metadata_schema='com.jaumo.schema.type.Metadata',
                metadata_exclude=['com.jaumo.schema.simple_rpc'],
                key_generation_exclude=['com.jaumo.schema.domain.user'],
                input_schema_file_extension='exavsc',
                schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
                schema_mapping_exclude=['com.jaumo.schema.simple_rpc'],
                schema_mapping_user_id_types_exclude=['array', 'map'],
                avro_tools_path=AVRO_TOOLS_JAR,
            ),
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        avro_preprocessor.process()

        with open(ROOT_DIR.joinpath('./schema-mapping.json')) as smf:
            sm = json.load(smf)
        user_id_fields = sm["com.jaumo.schema.domain.user.TestEvent"]["user-id-fields"]
        self.assertEqual(user_id_fields, ['user_id'])

    def test_full_t6(self) -> None:
        """
        Full test on fixture 't6_input'.
        Makes sure non-null defaults are rejected.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t6_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t6_output/')),
                base_namespace='com.jaumo.schema',
                types_namespace='com.jaumo.schema.type',
                metadata_schema='com.jaumo.schema.type.Metadata',
                metadata_exclude=['com.jaumo.schema.simple_rpc'],
                input_schema_file_extension='exavsc',
                schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
                schema_mapping_exclude=['com.jaumo.schema.simple_rpc'],
                schema_mapping_user_id_types_exclude=['array', 'map'],
                avro_tools_path=AVRO_TOOLS_JAR,
            ),
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        with self.assertRaises(ValueError):
            avro_preprocessor.process()

    def test_t7(self) -> None:
        """
        Test on fixture 't7_input' containing deprecated schemas, sub-schemas and fields.
        Checking that deprecated fields and schemas are added to the deprecation mapping
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t7_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t7_output/')),
                base_namespace='com.jaumo.schema',
                key_generation_exclude=['com.jaumo.schema'],
                input_schema_file_extension='exavsc',
                deprecation_mapping_path=ROOT_DIR.joinpath('./deprecation-mapping.json')
            ),
            verbose=True,
            json_indent=4
        )
        import copy
        avro_preprocessor.process([
            m.__name__ for m in copy.deepcopy(AvroPreprocessor.preprocessing_modules)
            if m not in [SchemaMappingGenerator, JavaClassesCreator, SchemaRegistryChecker, SchemaRegistrar]
        ])

        self.assert_trees_equals('t7_expected/', 't7_output/')

        with open(ROOT_DIR.joinpath('./deprecation-mapping.json')) as dmf:
            dm = json.load(dmf)
        self.assertEqual(dm["com.jaumo.schema.EventPayload"]["deprecated-fields"],
                         [{'name': 'user_id', 'doc': 'Deprecated user_id'},
                          {'name': 'array_of_user_ids', 'doc': 'Deprecated array_of_user_ids'}])
        self.assertEqual(dm["com.jaumo.schema.EventType"]["deprecated"], 'Deprecated enum')
        self.assertEqual(dm["com.jaumo.schema.EventType"]["deprecated-symbols"], ["B"])
        self.assertEqual(dm["com.jaumo.schema.UserUpdate"]["deprecated"], 'Deprecated schema UserUpdate')
        self.assertEqual(dm["com.jaumo.schema.UserUpdate"]["deprecated-fields"],
                         [{'name': 'id', 'doc': 'Deprecated id'}])
        self.assertEqual(dm["com.jaumo.schema.UserInfo"]["deprecated"], 'Deprecated UserInfo')
        self.assertEqual(dm["com.jaumo.schema.UserInfo"]["deprecated-fields"],
                         [{'name': 'email', 'doc': 'Deprecated email'}])

    def test_t8(self) -> None:
        """
        Test on fixture 't8_input' containing fields with mixed naming conventions.
        Checking that naming consistency is enforced.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t8_input/')),
                output_path=str(FIXTURES_DIR.joinpath('t8_output/')),
                base_namespace='com.jaumo',
                key_generation_exclude=['com.jaumo'],
                input_schema_file_extension='exavsc',
            ),
            verbose=True,
            json_indent=4
        )
        import copy
        with self.assertRaises(ValueError):
            avro_preprocessor.process([
                m.__name__ for m in copy.deepcopy(AvroPreprocessor.preprocessing_modules)
                if m not in [SchemaMappingGenerator, JavaClassesCreator, SchemaRegistryChecker, SchemaRegistrar]
            ])
        
    def test_input_sorting(self) -> None:
        """
        Test on input sorting.
        """
        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths=AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath('t2_input_unsorted/')),
                output_path=str(FIXTURES_DIR.joinpath('t2_sorted/')),
                base_namespace='com.jaumo.event',
                types_namespace='com.jaumo.event.type',
                metadata_schema='com.jaumo.event.type.Metadata',
                input_schema_file_extension='exavsc',
                output_schema_file_extension='exavsc',
                schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
                avro_tools_path=AVRO_TOOLS_JAR
            ),
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        avro_preprocessor.process(['AvroSorter'])

        for name, original_schema in avro_preprocessor.schemas.original.items():
            processed_schema = avro_preprocessor.schemas.processed[name]

            original_schema_without_order = json.loads(json.dumps(original_schema))
            processed_schema_without_order = json.loads(json.dumps(processed_schema))

            self.assertNotEqual(original_schema, processed_schema)
            self.assertEqual(original_schema_without_order, processed_schema_without_order)

    def assert_trees_equals(self,
                            expected: str,
                            processed: str,
                            expected_extension: str = 'avsc',
                            processed_extension: str = 'avsc',
                            assess_schema_string: bool = True,
                            input_format: str = 'json',
                            ) -> None:
        """
        Asserts two schema trees are equal
        :param expected: Path of the expected tree
        :param processed: Path of the processed tree
        :param expected_extension: The extension of files in the expected tree
        :param processed_extension: The extension of files in the processed tree
        :param assess_schema_string: Also assess the string representation of the result
        :param input_format: The format of the input schemas
        """
        container_expected = SchemasContainer(
            AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath(expected)),
                output_path="",
                base_namespace='',
                input_schema_file_extension=expected_extension,
                input_schema_file_format=input_format
            )
        )
        container_expected.read_schemas()
        expected_schemas = OrderedDict(sorted({
                                                  **container_expected.original,
                                                  **container_expected.autogenerated_keys
                                              }.items()))

        container_processed = SchemasContainer(
            AvroPaths(
                input_path=str(FIXTURES_DIR.joinpath(processed)),
                output_path="",
                base_namespace='',
                input_schema_file_extension=processed_extension,
                input_schema_file_format=input_format
            )
        )
        container_processed.read_schemas()
        processed_schemas = OrderedDict(sorted({
                                                   **container_processed.original,
                                                   **container_processed.autogenerated_keys
                                               }.items()))

        self.assertNotEqual(len(expected_schemas), 0)
        self.assertNotEqual(len(processed_schemas), 0)

        expected_schemas_names = set(expected_schemas)
        processed_schemas_names = set(processed_schemas)
        self.assertEqual(expected_schemas_names, processed_schemas_names)

        # self.assertEqual(len(expected_schemas), len(processed_schemas))

        for name, expected_schema in expected_schemas.items():
            print('Asserting', name)
            self.assertEqual(expected_schema, processed_schemas[name])

        if assess_schema_string:
            for name, expected_schema in container_expected.original_string.items():
                print('Asserting string', name)
                self.assertEqual(expected_schema.strip(),  # leading and trailing spaces
                                 container_processed.original_string[name].strip())

    def test_union_field(self) -> None:
        """
        Test the union
        """
        schema = self.build("""
        {
            "name": "int_or_string",
            "doc": "The address of the user",
            "nullable_optional": true,
            "type": ["int", "string"]
        }
        """)

        expected = self.build("""
        {
            "name": "int_or_string",
            "doc": "The address of the user",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalInt_or_string",
                    "doc": "The address of the user (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                "int",
                                "string"
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {'OptionalInt_or_string', 'TestRecord'})

    def test_enum_field(self) -> None:
        """
        Test the enum field
        """
        schema = self.build("""
        {
            "name": "kind",
            "doc": "The foo enum",
            "nullable_optional": true,
            "type": {
                "name": "Kind",
                "doc": "myenum",
                "type": "enum",
                "symbols": [
                    "ONE",
                    "TWO",
                    "THREE"
                ]
            }
        }
        """)

        expected = self.build("""
        {
            "name": "kind",
            "doc": "The foo enum",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalKind",
                    "doc": "The foo enum (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                {
                                    "name": "Kind",
                                    "doc": "myenum",
                                    "type": "enum",
                                    "symbols": [
                                        "ONE",
                                        "TWO",
                                        "THREE"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {'Kind', 'OptionalKind', 'TestRecord'})

    def test_union_enum(self) -> None:
        """
        Test enum inside union. The expected result is THE SAME of the previous case.
        """
        schema = self.build("""
        {
            "name": "kind",
            "doc": "The foo enum",
            "nullable_optional": true,
            "type": [
                "null",
                {
                    "name": "Kind",
                    "doc": "the kind enum values",
                    "type": "enum",
                    "symbols": [
                        "ONE",
                        "TWO",
                        "THREE"
                    ]
                }
            ]
        }
        """)

        expected = self.build("""
        {
            "name": "kind",
            "doc": "The foo enum",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalKind",
                    "doc": "The foo enum (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                {
                                    "name": "Kind",
                                    "doc": "the kind enum values",
                                    "type": "enum",
                                    "symbols": [
                                        "ONE",
                                        "TWO",
                                        "THREE"
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {'Kind', 'OptionalKind', 'TestRecord'})

    def test_union_record(self) -> None:
        """
        Test records inside union.
        """
        schema = self.build("""
        {
            "name": "request_response",
            "doc": "the request response",
            "nullable_optional": true,
            "type": [
                {
                    "name": "RecordRequest",
                    "doc": "the request",
                    "type": "record",
                    "fields": [
                        {
                            "name": "request_id",
                            "doc": "the request id",
                            "type": "int"
                        },
                        {
                            "name": "message_type",
                            "doc": "the message type",
                            "type": "int"
                        },
                        {
                            "name": "users",
                            "doc": "the users",
                            "type": "string"
                        }
                    ]
                },
                {
                    "name": "RecordResponse",
                    "doc": "the response",
                    "type": "record",
                    "fields": [
                        {
                            "name": "request_id",
                            "doc": "the response id",
                            "type": "int"
                        },
                        {
                            "name": "response_code",
                            "doc": "the code",
                            "type": "string"
                        },
                        {
                            "name": "response_count",
                            "doc": "the count",
                            "type": "int"
                        },
                        {
                            "name": "reason_code",
                            "doc": "the reason",
                            "type": "string"
                        }
                    ]
                }
            ]
        }
        """)

        expected = self.build("""
        {
            "name": "request_response",
            "doc": "the request response",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalRequest_response",
                    "doc": "the request response (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                {
                                    "name": "RecordRequest",
                                    "doc": "the request",
                                    "type": "record",
                                    "fields": [
                                        {
                                            "name": "request_id",
                                            "doc": "the request id",
                                            "type": "int"
                                        },
                                        {
                                            "name": "message_type",
                                            "doc": "the message type",
                                            "type": "int"
                                        },
                                        {
                                            "name": "users",
                                            "doc": "the users",
                                            "type": "string"
                                        }
                                    ]
                                },
                                {
                                    "name": "RecordResponse",
                                    "doc": "the response",
                                    "type": "record",
                                    "fields": [
                                        {
                                            "name": "request_id",
                                            "doc": "the response id",
                                            "type": "int"
                                        },
                                        {
                                            "name": "response_code",
                                            "doc": "the code",
                                            "type": "string"
                                        },
                                        {
                                            "name": "response_count",
                                            "doc": "the count",
                                            "type": "int"
                                        },
                                        {
                                            "name": "reason_code",
                                            "doc": "the reason",
                                            "type": "string"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {
            'OptionalRequest_response',
            'RecordRequest',
            'RecordResponse',
            'TestRecord'
        })

    def test_array(self) -> None:
        """
        Test array.
        """
        schema = self.build("""
        {
            "name": "children",
            "doc": "test array",
            "nullable_optional": true,
            "type": {
                "type": "array",  
                "items":{
                    "name": "Child",
                    "doc": "child",
                    "type": "record",
                    "fields": [
                        {
                            "name": "name",
                            "doc": "my name",
                            "type": "string"
                        }
                    ]
                }
            }
        }
        """)

        expected = self.build("""
        {
            "name": "children",
            "doc": "test array",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalChildren",
                    "doc": "test array (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                {
                                    "type": "array",
                                    "items": {
                                        "name": "Child",
                                        "doc": "child",
                                        "type": "record",
                                        "fields": [
                                            {
                                                "name": "name",
                                                "doc": "my name",
                                                "type": "string"
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {'Child', 'OptionalChildren', 'TestRecord'})

    def test_map(self) -> None:
        """
        Test map.
        """
        schema = self.build("""
        {
            "name": "children",
            "doc": "the map",
            "nullable_optional": true,
            "type": {
                "type": "map", 
                "values": "string"
            }
        }
        """)

        expected = self.build("""
        {
            "name": "children",
            "doc": "the map",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalChildren",
                    "doc": "the map (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                {
                                    "type": "map",
                                    "values": "string"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {'OptionalChildren', 'TestRecord'})

    def test_fixed(self) -> None:
        """
        Test fixed.
        """
        schema = self.build("""
        {
            "name": "children",
            "doc": "the kids",
            "nullable_optional": true,
            "type": {
                "name": "md5",
                "doc": "fixed field",
                "type": "fixed",
                "size": 16
            }
        }
        """)

        expected = self.build("""
        {
            "name": "children",
            "doc": "the kids",
            "default": null,
            "type": [
                "null",
                {
                    "name": "OptionalChildren",
                    "doc": "the kids (Optional Value)",
                    "type": "record",
                    "fields": [
                        {
                            "name": "value",
                            "doc": "The optional value",
                            "type": [
                                "null",
                                {
                                    "name": "md5",
                                    "doc": "fixed field",
                                    "type": "fixed",
                                    "size": 16
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        """)

        self.assert_extension(schema, expected, {'OptionalChildren', 'TestRecord', 'md5'})

    def assert_extension(self, schema: str, expected: str, java_classes_names: Set[str]) -> None:
        """
        Asserts that the extension works.

        :param schema: Schema in input
        :param expected: First (and only) field of the extended schema
        :param java_classes_names: expected names of created java classes
        """
        AvroPaths.reset_directory(str(FIXTURES_DIR.joinpath('/tmp/')))
        filename = 'tmp/input/com/jaumo/event/domain/user/users/TestRecord.exavsc'
        test_record_path = Path(FIXTURES_DIR.joinpath(filename))
        test_record_path.parent.mkdir(parents=True, exist_ok=True)
        test_record_path.write_text(schema)

        paths = AvroPaths(
            input_path=str(FIXTURES_DIR.joinpath('tmp/input/')),
            output_path=str(FIXTURES_DIR.joinpath('tmp/output/')),
            base_namespace='com.jaumo.event',
            types_namespace='com.jaumo.event.type',
            metadata_schema='com.jaumo.event.type.Metadata',
            key_generation_exclude=['com.jaumo.event'],
            input_schema_file_extension='exavsc',
            schema_mapping_path=ROOT_DIR.joinpath('./schema-mapping.json'),
            avro_tools_path=AVRO_TOOLS_JAR
        )

        avro_preprocessor: AvroPreprocessor = AvroPreprocessor(
            paths,
            verbose=True,
            json_indent=4,
            schema_registry_url=self.schema_registry_url
        )
        avro_preprocessor.process()

        filename = 'tmp/output/com/jaumo/event/domain/user/users/TestRecord.avsc'
        test_record_path = Path(FIXTURES_DIR.joinpath(filename))
        output_schema = test_record_path.read_text()
        self.assertEqual(output_schema, expected)
        self.assertEqual(
            sorted(java_classes_names),
            JavaClassesCreator(avro_preprocessor.schemas).get_java_classes_names()
        )

    def build(self, fields: str) -> str:
        """
        Create a schema given its fields
        :param fields: the fields
        :return: The schema
        """
        self.delete_test_record_subject()
        schema = self.schema_header + fields + self.schema_footer
        return json.dumps(json.loads(schema, object_pairs_hook=OrderedDict), indent=4)

    def delete_test_record_subject(self) -> None:
        """
        Deletes the subject associated to TestRecord in the Schema Registry because
        it is used multiple times with incompatible schemas
        """
        subject_to_delete = "domain.user.users-com.jaumo.event.domain.user.users.TestRecord"
        url = self.schema_registry_url + "/subjects/" + subject_to_delete
        import requests
        requests.delete(url)
