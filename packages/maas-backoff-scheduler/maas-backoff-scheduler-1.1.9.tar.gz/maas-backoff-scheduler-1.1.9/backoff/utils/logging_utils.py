#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志初始化工具
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Optional, Union
from pathlib import Path
from typing import Optional, Union

try:
    import importlib.resources as pkg_res
except Exception:
    pkg_res = None

try:
    import yaml
except Exception:
    yaml = None


DEFAULT_PACKAGE = "backoff.conf"
DEFAULT_FILENAME = "logging.config.yaml"

# 全局标志，用于防止重复初始化
_LOGGING_INITIALIZED = False


def init_logging(
    config_path: Optional[Union[str, Path]] = None,
    *,
    fallback_level: int = logging.INFO,
    force: bool = False,
) -> None:
    """初始化日志配置。

    优先级：
    1) 指定的 config_path
    2) 默认配置文件路径 `backoff/conf/logging.config.yaml`
    3) 包内默认 `backoff/conf/logging.config.yaml`
    4) 回退到 basicConfig

    Args:
        config_path: 日志配置文件路径，可选
        fallback_level: 回退日志级别，默认为 INFO
        force: 是否强制重新初始化，默认为 False
    """
    global _LOGGING_INITIALIZED


    # 如果已经初始化过且不强制重新初始化，则直接返回
    if _LOGGING_INITIALIZED and not force:
        return

    # 标记为已初始化
    _LOGGING_INITIALIZED = True
    
    # 优先使用外部传入路径
    if config_path:
        _load_from_path(Path(config_path), fallback_level)
        return

    # 其次尝试默认配置文件路径
    try:
        import os
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        default_config_path = current_dir.parent / 'conf' / 'logging.config.yaml'
        if default_config_path.exists():
            _load_from_path(default_config_path, fallback_level)
            return
    except Exception as e:
        pass

    # 再次尝试包内资源
    if pkg_res is not None and yaml is not None:
        try:
            with pkg_res.files(DEFAULT_PACKAGE).joinpath(DEFAULT_FILENAME).open(
                "r", encoding="utf-8"
            ) as f:
                config = yaml.safe_load(f)
            logging.getLogger().info(
                "Logging configured from package resource: %s/%s",
                DEFAULT_PACKAGE,
                DEFAULT_FILENAME,
            )
            logging.config.dictConfig(config)
            return
        except Exception as e:
            logging.basicConfig(level=fallback_level)
            return

    logging.basicConfig(level=fallback_level)


def _load_from_path(path: Path, fallback_level: int) -> None:
    if yaml is None:
        logging.basicConfig(level=fallback_level)
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    except Exception as e:
        logging.basicConfig(level=fallback_level)
