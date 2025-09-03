"""
A module to create java classes from Avro schemas.
"""
import glob
import subprocess
from pathlib import Path
from typing import Tuple, List, cast

from avro_preprocessor.avro_paths import AvroPaths
from avro_preprocessor.preprocessor_module import PreprocessorModule
from avro_preprocessor.schemas_container import SchemasContainer

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class JavaClassesCreator(PreprocessorModule):
    """
    Create Java classes for all schemas.
    """
    def __init__(self, schemas: SchemasContainer):
        super().__init__(schemas)
        self.java_classes_dir = Path(self.schemas.paths.input_path).parent.joinpath('java_classes')

    def process(self) -> None:
        """Process all schemas."""
        self.delete_java_classes()
        self.schemas.write_schemas()

        for name, _ in self.processed_schemas_and_keys_iter():
            if not self.schemas.paths.is_type_resource(name):
                schema_path = self.schemas.paths.to_output_path(name)
                ret_code, _, _ = self.schema_to_java(
                    schema_path, self.java_classes_dir,
                    'protocol' if self.schemas.paths.is_rpc_resource(name) else 'schema'
                )
                if ret_code != 0:
                    raise ValueError("The Java classes creation failed.")

    def schema_to_java(self,
                       schema_path: Path,
                       destination_path: Path,
                       schema_type: str) -> Tuple[int, str, str]:
        """
        Compile Java classes with Avro tools and check if the work correctly.
        :param schema_path: The path of the schema in input
        :param destination_path: The destination path to output the Java classes
        :param schema_type: 'schema' or 'protocol'
        :return: Returns the return code of avro-tools
        """

        command = [
            'java',
            '-jar',
            str(Path(cast(str, self.schemas.paths.avro_tools_path)).absolute()),
            'compile',
            schema_type,
            str(schema_path),
            str(destination_path)
        ]

        if self.schemas.verbose:
            print(' '.join(command))

        process = subprocess.run(command, capture_output=True, text=True)

        if process.returncode != 0:
            print(process.stdout)
            print(process.stderr)
            print(process.returncode)
        return process.returncode, process.stdout, process.stderr

    def get_java_classes_names(self) -> List[str]:
        """
        Checks that the generated Java classes have the expected names.
        :return: The names found.
        """
        found_classes = set(
            str(Path(fname).with_suffix('').name)
            for fname in glob.glob(str(self.java_classes_dir) + '/**/*.java', recursive=True)
        )
        return sorted(found_classes)

    def delete_java_classes(self) -> None:
        """
        Delete generated java classes.
        """
        # let's cleanup the classes directory first
        AvroPaths.reset_directory(str(self.java_classes_dir))
