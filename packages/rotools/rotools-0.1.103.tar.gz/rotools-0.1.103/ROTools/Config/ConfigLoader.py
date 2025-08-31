import os

from ROTools.Config.Config import Config
from ROTools.Helpers.DictObj import DictObj


def load_config(config_file):
    import yaml
    return Config(DictObj(yaml.safe_load(open(config_file))))

def load_config_directory(directory, config_file):
    import yaml
    files = os.listdir(directory)
    files = [a for a in files if not a.startswith("_")]
    files = [file for file in files if os.path.isfile(os.path.join(directory, file))]
    files = [os.path.join(directory, a) for a in files if a.endswith(('.yaml', '.yml'))]

    main_file_name = os.path.join(directory, config_file)
    if main_file_name not in files:
        raise Exception("Config file not found!")

    files = [a for a in files if a != main_file_name]

    config = Config(DictObj(yaml.safe_load(open(main_file_name))))

    for file in files:
        sub_config = DictObj(yaml.safe_load(open(file)))
        for key, value in sub_config.items():
            config.set(key, value)

    return config


