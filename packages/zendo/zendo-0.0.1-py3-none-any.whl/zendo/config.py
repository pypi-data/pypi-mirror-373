from dataclasses import dataclass, field
from pathlib import Path

import platformdirs as dirs

appname = "zendo"
appauthor = appname


def get_user_config_dir() -> Path:
    """Get the user configuration directory for the application."""
    pth = dirs.user_config_dir(appname, appauthor, ensure_exists=True)
    return Path(pth).resolve()


@dataclass
class Config:
    user_config_dir: Path = field(default_factory=get_user_config_dir)

    @property
    def applets_dir(self) -> Path:
        """Get the configuration directory."""
        pth = self.user_config_dir / "applets"
        pth.mkdir(parents=True, exist_ok=True)
        return pth


config = Config()


if __name__ == "__main__":
    print(f"User config directory: {config.user_config_dir}")
    print(f"Config object: {config}")
    print(f"Config object type: {type(config)}")
    print(f"Config user_config_dir type: {type(config.user_config_dir)}")
    print(f"Config user_config_dir exists: {config.user_config_dir.exists()}")
