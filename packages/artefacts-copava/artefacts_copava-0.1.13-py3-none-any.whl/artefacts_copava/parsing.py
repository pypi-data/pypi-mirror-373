from io import StringIO
import logging
import os
from typing import Optional, Union

import yaml


logging.basicConfig()
logging.getLogger().setLevel("INFO")


class ParsingError(Exception):
    pass


class Parser:
    def parse(self, config: Union[str, dict]) -> Optional[dict]:
        if type(config) is str:
            try:
                if os.path.exists(config):
                    #
                    # From a file
                    #
                    with open(config) as f:
                        return yaml.safe_load(f)
                else:
                    #
                    # From a YAML string
                    #
                    return yaml.safe_load(StringIO(config))
            except Exception as e:
                logging.error(f"Unable to parse the configuration YAML text: {e}")
                return None
        elif type(config) is dict:
            return dict(config)
        else:
            raise NotImplementedError(f"Cannot parse an input of type {type(config)}")
