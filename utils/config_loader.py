from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config(config_path=DEFAULT_CONFIG_PATH):
    # 集中读取配置，后续切换环境时只改配置文件
    with open(config_path, encoding="utf-8") as file:
        return yaml.safe_load(file) or {}
