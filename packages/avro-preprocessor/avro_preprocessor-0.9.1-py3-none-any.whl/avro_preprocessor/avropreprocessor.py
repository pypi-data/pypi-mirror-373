#!/usr/bin/env python

"""
Command line entrypoint for avro preprocessor
"""

import argparse
import json
from pathlib import Path

from avro_preprocessor.avro_paths import AvroPaths
from avro_preprocessor.preprocessor import AvroPreprocessor

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"

if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='Pre-processor for extended Avro schemata.')

    PARSER.add_argument('-a', '--avro-tools', dest='avro_tools', type=str, default=None)

    PARSER.add_argument('-i', '--input-path', dest='input_path', type=str, required=True)
    PARSER.add_argument('-o', '--output-path', dest='output_path', type=str, required=True)

    PARSER.add_argument('-b', '--base-namespace', dest='base_namespace', type=str, required=True)

    PARSER.add_argument(
        '-en', '--extra-namespaces', dest='extra_namespaces', type=str, default=None)

    PARSER.add_argument('-tp', '--topic-prefix', dest='topic_prefix', type=str, default=None)

    TYPES = PARSER.add_mutually_exclusive_group(required=True)
    TYPES.add_argument('-t', '--types-namespace', dest='types_namespace', type=str)
    TYPES.add_argument(
        '-n', '--no-types-namespace', dest='types_namespace', action='store_const', const=None)

    RPC = PARSER.add_mutually_exclusive_group(required=True)
    RPC.add_argument('-r', '--rpc-namespace', dest='rpc_namespace', type=str)
    RPC.add_argument(
        '-e', '--no-rpc-namespace', dest='rpc_namespace', action='store_const', const=None)

    PARSER.add_argument(
        '-ke', '--exclude-from-key-generation', dest='key_generation_exclude', type=str, default=None)

    PARSER.add_argument('-d', '--metadata-schema', dest='metadata_schema', type=str, default=None)
    PARSER.add_argument(
        '-de', '--metadata-exclude', dest='metadata_exclude', type=str, default=None)

    PARSER.add_argument('-k', '--key-schema', dest='key_schema', type=str, default=None)

    PARSER.add_argument(
        '-ksns',
        '--key-subject-name-strategy',
        dest='key_subject_name_strategy',
        type=str,
        default='TopicRecordNameStrategy'
    )

    PARSER.add_argument(
        '-p', '--schema-mapping-path', dest='schema_mapping_path', type=str, default=None)
    PARSER.add_argument(
        '-pe',
        '--exclude-from-schema-mapping',
        dest='exclude_from_schema_mapping',
        type=str,
        default=None
    )
    PARSER.add_argument(
        '-pet',
        '--user-id-types-exclude-from-schema-mapping',
        dest='user_id_types_exclude_from_schema_mapping',
        type=str,
        default=None
    )

    PARSER.add_argument(
        '-ie', '--input-schema-file-extension', dest='input_schema_file_extension', type=str,
        default='exavsc', help="Comma separated list of extensions, e.g. 'exavsc,yexavsc'")

    PARSER.add_argument(
        '-oe', '--output-schema-file-extension', dest='output_schema_file_extension', type=str,
        default='avsc')

    PARSER.add_argument(
        '-if', '--input-schema-file-format', dest='input_schema_file_format', type=str,
        default='json', help="Can be json or yaml")

    PARSER.add_argument(
        '-of', '--output-schema-file-format', dest='output_schema_file_format', type=str,
        default='json', help="Can be json or yaml")

    PARSER.add_argument(
        '-u', '--update-summary-path', dest='update_summary_path', type=str, default=None)

    PARSER.add_argument('-v', '--verbose', dest='verbose', action='store_true')
    PARSER.set_defaults(verbose=False)

    PARSER.add_argument('-s', '--schema-registry', dest='schema_registry', type=str, default='')

    INDENT = PARSER.add_mutually_exclusive_group()
    INDENT.add_argument('-j', '--json_indent', dest='json_indent', type=int, default=4)
    INDENT.add_argument(
        '-c', '--json_compact', dest='json_indent', action='store_const', const=None)

    PARSER.add_argument('-tc', '--json-trailing-commas', dest='json_trailing_commas', action='store_true')

    PARSER.add_argument('-y', '--yaml_indent', dest='yaml_indent', type=json.loads,
                        default='{"mapping":2,"sequence":4,"offset":2}',
                        help="yaml indentation (as json), see "
                             "https://yaml.readthedocs.io/en/latest/"
                             "detail.html?highlight=indent#indentation-of-block-sequences "
                             """use {"mapping": 2, "sequence": 2, "offset": 0} """ 
                             "for avoid indenting sequence values")

    AVAILABLE_MODULES = ' '.join(AvroPreprocessor.available_preprocessing_modules.keys())
    PARSER.add_argument('-m', '--modules', dest='modules', nargs='*', default=None,
                        help='Available modules: {}'.format(AVAILABLE_MODULES))

    PARSER.add_argument(
        '-dp', '--deprecation-mapping-path', dest='deprecation_mapping_path', type=str, default=None)

    ARGS = PARSER.parse_args()

    EXTRA_NAMESPACES = ARGS.extra_namespaces.split(',') if ARGS.extra_namespaces else None

    SCHEMA_MAPPING_PATH = Path(ARGS.schema_mapping_path).absolute() if ARGS.schema_mapping_path \
        else Path('./schema-mapping.json')

    DEPRECATION_MAPPING_PATH = Path(ARGS.deprecation_mapping_path).absolute() if ARGS.deprecation_mapping_path \
        else Path('./deprecation-mapping.json')

    UPDATE_SUMMARY_PATH = Path(ARGS.update_summary_path).absolute() if ARGS.update_summary_path else None

    METADATA_EXCLUDE = ARGS.metadata_exclude.split(',') if ARGS.metadata_exclude else None

    SCHEMA_MAPPING_EXCLUDE = ARGS.exclude_from_schema_mapping \
        .split(',') if ARGS.exclude_from_schema_mapping else None

    KEY_GENERATION_EXCLUDE = ARGS.key_generation_exclude \
        .split(',') if ARGS.key_generation_exclude else None

    SCHEMA_MAPPING_USER_ID_TYPES_EXCLUDE = ARGS.user_id_types_exclude_from_schema_mapping \
        .split(',') if ARGS.user_id_types_exclude_from_schema_mapping else None

    AVRO_PREPROCESSOR: AvroPreprocessor = AvroPreprocessor(
        AvroPaths(
            input_path=ARGS.input_path,
            output_path=ARGS.output_path,
            base_namespace=ARGS.base_namespace,
            extra_namespaces=EXTRA_NAMESPACES,
            topic_prefix=ARGS.topic_prefix,
            types_namespace=ARGS.types_namespace,
            rpc_namespace=ARGS.rpc_namespace,
            metadata_schema=ARGS.metadata_schema,
            metadata_exclude=METADATA_EXCLUDE,
            key_schema=ARGS.key_schema,
            key_subject_name_strategy=ARGS.key_subject_name_strategy,
            key_generation_exclude=KEY_GENERATION_EXCLUDE,
            input_schema_file_extension=ARGS.input_schema_file_extension,
            output_schema_file_extension=ARGS.output_schema_file_extension,
            input_schema_file_format=ARGS.input_schema_file_format,
            output_schema_file_format=ARGS.output_schema_file_format,
            schema_mapping_path=SCHEMA_MAPPING_PATH,
            schema_mapping_exclude=SCHEMA_MAPPING_EXCLUDE,
            schema_mapping_user_id_types_exclude=SCHEMA_MAPPING_USER_ID_TYPES_EXCLUDE,
            avro_tools_path=ARGS.avro_tools,
            deprecation_mapping_path=DEPRECATION_MAPPING_PATH,
            update_summary_path=UPDATE_SUMMARY_PATH
        ),
        verbose=ARGS.verbose,
        json_trailing_commas=ARGS.json_trailing_commas,
        json_indent=ARGS.json_indent,
        yaml_indent=ARGS.yaml_indent,
        schema_registry_url=ARGS.schema_registry
    )

    AVRO_PREPROCESSOR.process(ARGS.modules)
