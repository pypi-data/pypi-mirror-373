#!/usr/bin/env python3
"""
Script transforming Extended Avro (.exavsc) to regular Avro (.avsc) schema files.
Extends Avro schema definition with 'nullable_optional' keyword.
"""
from collections import OrderedDict
from typing import List, Optional, Union

from avro_preprocessor.avro_paths import AvroPaths
from avro_preprocessor.colored_json import ColoredJson
from avro_preprocessor.modules.avro_sorter import AvroSorter, AvroOrderChecker
from avro_preprocessor.modules.deprecation_mapping_generator import DeprecationMappingGenerator
from avro_preprocessor.modules.documentation_checker import DocumentationChecker
from avro_preprocessor.modules.default_value_null_checker import DefaultValueNullChecker
from avro_preprocessor.modules.documentation_list_condenser import DocumentationCondenser
from avro_preprocessor.modules.java_classes_creator import JavaClassesCreator
from avro_preprocessor.modules.keys_generator import KeysGenerator
from avro_preprocessor.modules.logical_type_checker import LogicalTypeChecker
from avro_preprocessor.modules.metadata_adder import MetadataAdder
from avro_preprocessor.modules.names_checker import NamesChecker
from avro_preprocessor.modules.namespace_checker import NamespaceChecker
from avro_preprocessor.modules.nullable_optional_expander import NullableOptionalExpander
from avro_preprocessor.modules.references_expander import ReferencesExpander
from avro_preprocessor.modules.schema_dependencies_checker import SchemaDependenciesChecker
from avro_preprocessor.modules.schema_mapping_generator import SchemaMappingGenerator
from avro_preprocessor.modules.schema_registrar import SchemaRegistrar
from avro_preprocessor.modules.schema_registry_checker import SchemaRegistryChecker
from avro_preprocessor.preprocessor_module import PreprocessorModule  # pylint: disable=W0611
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class AvroPreprocessor:
    """
    Avro extender main class.
    """

    #: When adding a module, add it here to make it available
    preprocessing_modules = [
        DocumentationCondenser,
        NamespaceChecker,
        DocumentationChecker,
        DefaultValueNullChecker,
        NamesChecker,
        AvroOrderChecker,
        MetadataAdder,
        SchemaDependenciesChecker,
        ReferencesExpander,
        NullableOptionalExpander,
        LogicalTypeChecker,
        AvroSorter,
        KeysGenerator,
        SchemaMappingGenerator,
        DeprecationMappingGenerator,
        JavaClassesCreator,
        SchemaRegistryChecker,
        SchemaRegistrar
    ]

    #: OrderedDict of module_name -> module_class
    available_preprocessing_modules = OrderedDict((
        (m.__name__, m) for m in preprocessing_modules
    ))

    def __init__(self,
                 paths: AvroPaths,
                 verbose: bool = True,
                 json_trailing_commas: bool = False,
                 json_indent: int = 4,
                 yaml_indent: Union[dict, None] = None,
                 schema_registry_url: str = 'http://localhost:8081') -> None:
        """
        Initialization function.

        :param paths: The paths of the input and output directories
        :param verbose: Verbose flag
        :param json_trailing_commas: Whether to put trailing commas when writing schemas as JSON
        :param json_indent: How much to indent JSON strings
        :param yaml_indent: How much to indent YAML strings
        :param schema_registry_url: The URL of the Confluent Schema Registry
        """
        if yaml_indent is None:
            yaml_indent = {"mapping": 2, "sequence": 4, "offset": 2}
        self.paths = paths
        self.verbose = verbose
        self.json_trailing_commas = json_trailing_commas
        ColoredJson.json_indent = json_indent
        ColoredJson.yaml_indent = yaml_indent
        SchemaRegistrar.schema_registry_url = schema_registry_url

        self.schemas: SchemasContainer = self._get_schemas_container()

        self.modules: 'OrderedDict[str, PreprocessorModule]' = OrderedDict()

    def _get_schemas_container(self) -> SchemasContainer:
        return SchemasContainer(self.paths, self.verbose)

    def process(self, requested_modules: Optional[List[str]] = None) -> None:
        """
        Process all the schemas using the modules pipeline.
        Standard schemas are saved in .avsc
        (or whatever set by the output_schema_file_extension parameter)
        files in the output path.

        :param requested_modules: The modules to activate, all available ones if set to None
        """

        self.schemas.read_schemas()
        self.modules = self.get_requested_modules(requested_modules)
        self._do_process(self.modules)
        self.schemas.write_schemas(self.json_trailing_commas)

    def _do_process(self, requested_modules: 'OrderedDict[str, PreprocessorModule]') -> None:
        self.schemas.modules = requested_modules

        for module_name, module in requested_modules.items():
            # self.schemas.print_schemas('json')
            try:
                module.process()
            except Exception as e:
                import sys
                schemas_list = ', '.join(
                    set(module.failed_schemas_names)) if module.failed_schemas_names else module.current_schema_name
                custom_message = f'\n\n{"*" * 100}\nException in module "{module_name}" while ' \
                                 f'processing schema(s): {schemas_list}\n{"*" * 100}'
                raise type(e)(f'{str(e)} {custom_message}').with_traceback(sys.exc_info()[2])

    def get_requested_modules(self, requested_modules_names: Optional[List[str]]) \
            -> 'OrderedDict[str, PreprocessorModule]':
        """
        Process the requested modules creating an instance of each of them.

        :param requested_modules_names: The names of the requested modules
        :return: List of modules
        """

        if requested_modules_names:
            for module in requested_modules_names:
                if module not in self.available_preprocessing_modules:
                    raise ValueError("No such module {}".format(module))
            requested_modules_names_checked = requested_modules_names
        else:
            requested_modules_names_checked = list(self.available_preprocessing_modules)

        modules: OrderedDict = OrderedDict()
        for module in self.available_preprocessing_modules:
            if module in requested_modules_names_checked:
                mod = self.available_preprocessing_modules[module]
                modules[mod.__name__] = mod(self.schemas)  # type: ignore
        return modules
