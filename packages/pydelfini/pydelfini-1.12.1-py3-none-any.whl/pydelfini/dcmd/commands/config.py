import json
import sys
from typing import Any

import yaml
from pydelfini.delfini_core.api.admin import admin_get_config
from pydelfini.delfini_core.api.admin import admin_put_config
from pydelfini.delfini_core.models import SystemConfiguration

from .base_commands import BaseCommands


def setattr_conv(d: dict[str, Any], key: str, value: str) -> None:
    """Set a dictionary key, converting value if needed."""
    new_value: Any
    if key in d:
        old_value = d[key]

        if isinstance(old_value, str):
            new_value = value
        elif isinstance(old_value, bool):
            new_value = bool(json.loads(value.lower()))
        elif isinstance(old_value, int):
            new_value = int(value)
        elif isinstance(old_value, float):
            new_value = float(value)
        else:
            new_value = json.loads(value)
    else:
        try:
            new_value = json.loads(value)
        except json.JSONDecodeError:
            new_value = value

    d[key] = new_value


def traverse_path(path: str, root: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    path_list = list(reversed(path.split(".")))
    obj = root
    while len(path_list) > 1:
        next_path = path_list.pop()
        obj = obj[next_path]

    assert isinstance(obj, dict)

    return path_list.pop(), obj


class ConfigCommands(BaseCommands):
    """Admin operations on Delfini configuration"""

    def get(self) -> None:
        """Retrieve the current configuration."""
        config = admin_get_config.sync(client=self.core)

        self._output(config.to_dict())

    @BaseCommands._with_arg("config_path", help="dot-separated path to config option")
    @BaseCommands._with_arg("value", help="new value to set")
    def set(self) -> None:
        """Set a single config value."""
        config = admin_get_config.sync(client=self.core).to_dict()

        name, obj = traverse_path(self.args.config_path, config)
        setattr_conv(obj, name, self.args.value)

        self._output(config, "--- setting new config ---")
        admin_put_config.sync(
            body=SystemConfiguration.from_dict(config), client=self.core
        )

    @BaseCommands._with_arg("config_path", help="dot-separated path to config option")
    def delete(self) -> None:
        """Remove a node from the config structure."""
        config = admin_get_config.sync(client=self.core).to_dict()

        name, obj = traverse_path(self.args.config_path, config)
        del obj[name]

        self._output(config, "--- setting new config ---")
        admin_put_config.sync(
            body=SystemConfiguration.from_dict(config), client=self.core
        )

    @BaseCommands._with_arg(
        "filename", default="-", help="complete configuration in YAML format"
    )
    def put(self) -> None:
        """Write the entire configuration."""
        if self.args.filename == "-":
            input_stream = sys.stdin
        else:
            input_stream = open(self.args.filename)

        config = yaml.safe_load(input_stream)

        admin_put_config.sync(
            body=SystemConfiguration.from_dict(config), client=self.core
        )
