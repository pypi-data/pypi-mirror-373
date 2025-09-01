import dataclasses, yaml, yaml.scanner, os, enum
import logging, json

from filelock import FileLock

logger = logging.getLogger(__name__)
# TODO add filelock to ensure that the file is not written to by multiple threads at the same time.
class settings_saver:
    _config_file: str = None
    
    @classmethod
    def load(cls):
        if not os.path.isfile(cls._config_file):
            cls.write()
            return cls
        else:
            config = load_config(cls._config_file)

            fields = dataclasses.fields(cls)
            kwargs = {k.name : None for k in fields}
            for field in fields:
                if field.name in config.keys():
                    if issubclass(field.type, enum.Enum):
                        setattr(cls, field.name , field.type(config[field.name]))
                    elif issubclass(field.type, dict):
                        if config[field.name] is None:
                            setattr(cls, field.name , None)
                        else:
                            setattr(cls, field.name , json.loads(config[field.name]))
                    else:
                        setattr(cls, field.name , config[field.name])
        
            return cls(**kwargs)

    @classmethod
    def write(cls):
        config = load_config(cls._config_file)

        fields = dataclasses.fields(cls)
        for field in fields:
            config[field.name] = getattr(cls, field.name)
        
        with FileLock(f"{cls._config_file}.lock"):
            with open(cls._config_file, 'w') as file:
                yaml.dump(clean_data_for_saving(config, fields), file)
        return config

def load_config(config_file):
    if not os.path.isfile(config_file):
        return {}
    try:
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file) or {}
    except (yaml.YAMLError, yaml.scanner.ScannerError) as e:
        logger.exception(f"Error loading config file {config_file}: {e}")
        config = {}
    return config


def clean_data_for_saving(data, fields):
    for field in fields:
        if field.name in data.keys():
            if issubclass(field.type, enum.Enum):
                data[field.name] = data[field.name].value
            elif issubclass(field.type, dict):
                data[field.name] = json.dumps(data[field.name])

    return data