"""Configuration management for AIS."""

import base64
import toml
from pathlib import Path
from typing import Any, Dict


def get_config_path() -> Path:
    """Get the configuration file path."""
    config_dir = Path.home() / ".config" / "ais"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.toml"


def _get_obfuscated_key() -> str:
    """Get the obfuscated default API key."""
    # Base64编码的默认API key，不是真正的加密，只是简单混淆
    encoded = (
        "c2stb3ItdjEtY2FhOTRlMzRiMWE0YjhkOThhYTQ3YjVlOTU5ODNiZTkwNTk4NmI0NDlmNWZiYjNk"
        "ZjgwYTg5NGNkNDBkM2JiYg=="
    )
    return base64.b64decode(encoded).decode()


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration."""
    return {
        "default_provider": "free",
        "auto_analysis": True,
        "context_level": "detailed",
        "sensitive_dirs": ["~/.ssh", "~/.config/ais", "~/.aws"],
        "ui": {
            "enable_colors": True,
            "max_history_display": 10,
        },
        "providers": {
            "free": {
                "base_url": "https://openrouter.ai/api/v1/chat/completions",
                "model_name": "openai/gpt-oss-20b:free",
                "api_key": _get_obfuscated_key(),
            }
        },
        "advanced": {
            "max_context_length": 4000,
            "async_analysis": True,
            "cache_analysis": True,
            "analysis_cooldown": 60,  # 重复分析避免间隔时间（秒）
            "request_timeout": 120,  # HTTP请求超时时间（秒）
        },
        "ask": {
            "context_level": "minimal",  # minimal, standard, detailed
        },
    }


def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    config_path = get_config_path()

    try:
        if config_path.exists():
            with open(config_path, "r") as f:
                config = toml.load(f)

            # Merge with defaults
            default_config = get_default_config()
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
    except Exception:
        pass

    # Fallback to default and save
    config = get_default_config()
    save_config(config)
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    config_path = get_config_path()

    with open(config_path, "w") as f:
        toml.dump(config, f)


def set_config(key: str, value: Any) -> None:
    """设置配置项。"""
    config = get_config()

    # 支持嵌套键，如 "ask.context_level"
    if "." in key:
        keys = key.split(".")
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    else:
        config[key] = value

    save_config(config)


def _validate_provider_exists(config: Dict[str, Any], name: str) -> None:
    """验证提供商是否存在。"""
    if name not in config.get("providers", {}):
        raise ValueError(f"提供商 '{name}' 不存在")


def add_provider(name: str, base_url: str, model_name: str, api_key: str = None) -> None:
    """添加新的 AI 服务商。"""
    config = get_config()

    if "providers" not in config:
        config["providers"] = {}

    provider = {"base_url": base_url, "model_name": model_name}
    if api_key:
        provider["api_key"] = api_key

    config["providers"][name] = provider
    save_config(config)


def remove_provider(name: str) -> None:
    """删除 AI 服务商。"""
    config = get_config()
    _validate_provider_exists(config, name)

    if name == config.get("default_provider"):
        raise ValueError("不能删除当前使用的默认提供商")

    del config["providers"][name]
    save_config(config)


def use_provider(name: str) -> None:
    """切换默认 AI 服务商。"""
    config = get_config()
    _validate_provider_exists(config, name)
    config["default_provider"] = name
    save_config(config)


def init_config(force: bool = False) -> bool:
    """初始化配置文件。

    Args:
        force: 是否强制覆盖已存在的配置文件

    Returns:
        bool: 是否成功创建/覆盖了配置文件
    """
    config_path = get_config_path()

    # 检查文件是否存在
    if config_path.exists() and not force:
        return False

    # 创建默认配置并保存
    default_config = get_default_config()
    save_config(default_config)
    return True
