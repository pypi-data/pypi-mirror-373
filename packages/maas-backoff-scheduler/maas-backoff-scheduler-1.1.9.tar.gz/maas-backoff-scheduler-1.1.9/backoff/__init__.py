#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务退避管理工具包
"""

import logging
from backoff.utils.logging_utils import init_logging

# 全局初始化日志配置
# import os
# from pathlib import Path
# current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
# config_path = current_dir / 'conf' / 'logging.config.yaml'
# init_logging(config_path)

init_logging()
logger = logging.getLogger()