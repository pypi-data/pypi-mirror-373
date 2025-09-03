import pathlib
import tomllib

CONFIG_FILE = "~/.config/xum/xum.toml"


class Config:
    def __init__(self, data: dict = {}):
        # search paths
        self.search_paths: list[pathlib.Path] = []
        for p in data.get("search_paths", ["~"]):
            # validate p is a valid path string
            path = pathlib.Path(p).expanduser().absolute()
            if path.exists():
                self.search_paths.append(path)
            else:
                print(f"{path} not found. I'm going to ignore it.")

        # custom paths
        self.custom_paths: list[pathlib.Path] = []
        for p in data.get("custom_paths", []):
            # validate p is a valid path string
            path = pathlib.Path(p).expanduser().absolute()
            if path.exists():
                self.custom_paths.append(path)
            else:
                print(f"{path} not found. I'm going to ignore it.")


def load_config():
    """Load configuration from ~/.config/xum/xum.toml or default config"""

    config_file = pathlib.Path(CONFIG_FILE).expanduser().absolute()
    # load config dict from file
    if config_file.exists():
        with open(config_file, "r") as f:
            data = tomllib.loads(f.read())
    else:
        data = {}

    config = Config(data)

    return config


config = load_config()
