"""
A module to pretty print colored JSON
"""
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Dict, cast, Optional, Union

from pygments import highlight
from pygments.formatters.terminal256 import TerminalTrueColorFormatter
from pygments.lexers.data import JsonLexer, YamlLexer

from avro_preprocessor.extended_yaml import ExtendedYAML

__author__ = "Nicola Bova"
__copyright__ = "Copyright 2018, Jaumo GmbH"
__email__ = "nicola.bova@jaumo.com"


@dataclass
class ColoredJson:
    """
    Pretty prints JSON on the terminal
    """
    json_lexer = JsonLexer()
    yaml_lexer = YamlLexer()
    formatter = TerminalTrueColorFormatter(style='monokai')

    json_indent = 4
    yaml_indent = {"mapping": 2, "sequence": 4, "offset": 2}

    @classmethod
    def highlight_json(cls, data: Union[Dict, OrderedDict],
                       indent: Optional[int] = json_indent) -> str:
        """
        Get a colored, highlighted version of a JSON string.
        :param data: The json to highlight
        :param indent: How much to indent fields in the JSON
        """
        json_text = json.dumps(data, indent=indent)
        return cast(str, highlight(json_text, cls.json_lexer, cls.formatter))

    @classmethod
    def highlight_yaml(cls, data: Union[Dict, OrderedDict],
                       indent: Optional[dict] = None) -> str:
        """
        Get a colored, highlighted version of a YAML string.
        :param data: The yaml to highlight
        :param indent: Yaml fields indentation
        """
        if indent is None:
            indent = cls.yaml_indent
        yaml = ExtendedYAML()
        yaml.default_flow_style = False
        yaml.indent(**indent)
        yaml.Representer.add_representer(OrderedDict, yaml.Representer.represent_dict)
        yaml_text = yaml.dump(data)
        return cast(str, highlight(yaml_text, cls.yaml_lexer, cls.formatter))
