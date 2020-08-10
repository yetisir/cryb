import os
import pathlib

import configurator
import dotenv


def lookup_environment(config):
    """Recursively substitute all environemnt vairables if they exist"""

    for parameter, value in config.items():
        if isinstance(value, dict):
            config[parameter] = lookup_environment(value)
        elif isinstance(value, str):
            if value.startswith('${') and value.endswith('}'):
                config[parameter] = os.environ.get(value[2:-1])
    return config


# load environment variables from .env
dotenv.load_dotenv()

# load raw config from config.yml
settings_path = pathlib.Path(__file__).parent / 'config.yml'
raw_config = configurator.Config.from_path(settings_path)

# substitute all environment variables
config = configurator.Config(lookup_environment(raw_config.data))
