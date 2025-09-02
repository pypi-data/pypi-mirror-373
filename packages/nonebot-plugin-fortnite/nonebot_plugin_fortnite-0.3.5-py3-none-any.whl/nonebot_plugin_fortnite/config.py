from pathlib import Path

from nonebot import get_plugin_config
import nonebot_plugin_localstore as store
from pydantic import BaseModel


class Config(BaseModel):
    fortnite_api_key: str | None = None


fconfig: Config = get_plugin_config(Config)

cache_dir: Path = store.get_plugin_cache_dir()
data_dir: Path = store.get_plugin_data_dir()

FONT_PATH: Path = data_dir / "SourceHanSansSC-Bold-2.otf"
