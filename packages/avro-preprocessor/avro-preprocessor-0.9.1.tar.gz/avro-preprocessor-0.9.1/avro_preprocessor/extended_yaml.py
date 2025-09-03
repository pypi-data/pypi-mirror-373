from typing import Any

from ruamel.yaml import YAML, StringIO  # type: ignore


class ExtendedYAML(YAML):
    def dump_str(self, data: Any, **kw: Any) -> str:
        stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        string: str = stream.getvalue()
        stream.close()
        return string
