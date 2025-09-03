"""
A module to register Avro schemas to Confluent Schema Registry.
It uses the fully qualified name of a schema according to the strategy
"io.confluent.kafka.serializers.subject.TopicRecordNameStrategy".
It is used to employ multiple schemas per topic.
See [https://www.confluent.io/blog/put-several-event-types-kafka-topic/]
"""

import json
from collections import OrderedDict

import requests
from requests import Response

from avro_preprocessor.modules.schema_registrar import SchemaRegistrar

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


class SchemaRegistryChecker(SchemaRegistrar):
    """
    Checks the compatibility of a schema on the schema registry.
    """

    def process_schema(self, subject_name: str, schema: OrderedDict) -> None:
        self.perform_request_to_schema_registry(subject_name, schema)

    def get_request_url(self, subject: str) -> str:
        """
        Returns the URL for this request
        :param subject: The Avro subject name
        :return: The full URL
        """
        url = self.schema_registry_url + "/compatibility/subjects/" + subject + "/versions/latest"
        return url

    def process_response(self, response: Response) -> None:
        """
        Process the response.
        :param response: The response
        """

        if response.status_code not in (requests.codes.ok, 404):  # pylint: disable=E1101
            print(response)
            response.raise_for_status()

        result = json.loads(response.content)
        if self.schemas.verbose:
            print('Response:', result, '\n')

        if 'is_compatible' in result and not result['is_compatible']:
            raise ValueError("Schema Registry compatibility failed for \n\tschema: {} \n\turl: {}"
                             .format(self.current_schema_name, self.url))
