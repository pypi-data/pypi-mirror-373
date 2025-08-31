import os
from pathlib import Path

from ROTools.Helpers.Attr import setattr_ex, getattr_ex
from ROTools.Helpers.DictObj import DictObj

class Config(DictObj):
    def __init__(self, parent):
        super().__init__(parent)


    def process_secrets(self, secrets_config):
        import yaml
        if secrets_config is None:
            return

        if isinstance(secrets_config.files, str):
            secrets_config.files = [secrets_config.files]

        secrets = None
        for item in secrets_config.files:
            if Path(item).exists():
                secrets = DictObj(yaml.safe_load(open(item)))
                break

        if secrets is None:
            return

        for item in secrets_config.targets:
            value_name = item.get("value") or item.name
            value = secrets.get(value_name, None)

            if self.has(item.name) and value is not None:
                self.set(item.name, value)

    def add_env_data(self, prefix):
        extra_config = [(key[len(prefix):].lower(), value) for key, value in os.environ.items() if key.startswith(prefix)]

        for key, value in extra_config:
            _old_value = getattr_ex(self, key)
            if _old_value is not None and isinstance(_old_value, bool):
                setattr_ex(self, key, value in ["true", "True", "TRUE", "1", ])
                continue

            if _old_value is not None and isinstance(_old_value, int):
                setattr_ex(self, key, int(value))
                continue

            if _old_value is not None and isinstance(_old_value, float):
                setattr_ex(self, key, float(value))
                continue

            if _old_value is not None:
                setattr_ex(self, key, value)

    def set_common_override(self, source, target_path):
        if source is None:
            return

        values_to_override = source.fields_list()
        for element in self.get(target_path).values():
            element.set_values(values_to_override, only_if_exists=False)

    def set_common_default(self, source, target_path):
        if source is None:
            return

        values_default = source.fields_list()
        for element in self.get(target_path).values():
            for path, nev_value in values_default:
                if element.get(path) is None:
                    element.set(path, nev_value)

    def dump_config(self):
        print()
        print("========")
        self.dump()
        print("========")
        print()
