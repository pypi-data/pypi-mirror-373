from __future__ import annotations
import json
import os
from typing import Optional, Any
from .constants import CONFIG_DIR, CONFIG_FILE


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def get_config_value(key: str, default: Optional[str] = None) -> Optional[str]:
    if key in os.environ:
        return os.environ[key]
    cfg = load_config()
    val = cfg.get(key)
    if val is None:
        return default
    return str(val)


def set_config_value(key: str, value: Any) -> None:
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def ensure_env_from_config(keys: list[str]) -> None:
    # Populate missing env vars from config file if present
    cfg = load_config()
    for k in keys:
        if k not in os.environ and k in cfg:
            os.environ[k] = str(cfg[k])
