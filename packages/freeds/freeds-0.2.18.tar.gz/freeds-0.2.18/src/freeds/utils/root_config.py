from pathlib import Path
import yaml
import os
class RootConfig:
    def freeds_file_path(self) -> Path:
        return Path.home() / ".freeds"

    def __init__(self):
        self.data:dict[str, str] = {}
        self.root_path:Path = None
        self.configs_path:Path = None
        self.locals_path:Path = None
        try:
            self.load()
        except (FileNotFoundError, ValueError):
            pass

    def load(self):
        p = os.environ.get('FREEDS_ROOT_PATH')
        if p:
            self.root_path = Path(p)
        else:
            with open(self.freeds_file_path(), "r") as file:
                self.data  = yaml.safe_load(file)
                cfg = self.data.get('config',{})
                self.root_path = Path(cfg.get('root_path'))

        self.configs_path = Path(
            os.environ.get(
            'FREEDS_CONFIGS_PATH',
            self.root_path / "freeds-config" / "configs")
        )
        self.locals_path = Path(
            os.environ.get(
                'FREEDS_LOCALS_PATH',
                self.root_path / "local_configs")
        )
        self.is_loaded = self.root_path is not None
        if not self.is_loaded:
            raise ValueError('could not find root config')

    def set_default(self, root_path):
        cfg = {
            "config": {
                "root_path": str(root_path)
            }
        }
        with open(self.freeds_file_path() , "w") as f:
            yaml.dump(cfg, f, default_flow_style=False)
        self.load()
