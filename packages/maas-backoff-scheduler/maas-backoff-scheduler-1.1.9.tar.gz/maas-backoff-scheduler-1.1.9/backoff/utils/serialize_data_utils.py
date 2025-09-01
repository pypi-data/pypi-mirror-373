#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import json


logger = logging.getLogger()


def dumps_data(data) -> str:
    """
    将数据序列化为字符串（支持字典、列表、基础类型等）

    规则：
    - 若为字典或列表：使用JSON序列化（保留中文，容错处理）
    - 其他类型（包括None）：直接转换为字符串

    参数:
        data: 待序列化的数据（可任意类型）

    返回:
        str: 序列化后的字符串
    """
    # 处理字典和列表：JSON序列化
    if isinstance(data, (dict, list)):
        try:
            return json.dumps(
                data,
                ensure_ascii=False,
                default=str,
            )
        except Exception as e:
            logger.warning(
                f"JSON序列化失败，降级为字符串处理，数据: {str(data)}, 异常: {e}"
            )
            return str(data)

    # 其他类型：直接转字符串（包括None、str、int、bool等）
    return str(data)


def load_parse_params(param: str) -> dict:
    """
    解析任务实体中的param参数（JSON字符串转字典）

    规则：
    - 若task_entity为None或param为空：返回空字典
    - 若param为JSON字符串：解析为字典返回
    - 若解析失败：返回空字典并记录警告日志

    参数:
        task_entity: 任务实体对象（需包含param属性，可能为None）

    返回:
        dict: 解析后的参数字典（解析失败或无参数时返回空字典）
    """
    try:
        return json.loads(param)
    except json.JSONDecodeError as e:
        logger.warning(f"任务参数JSON解析失败，param: {param}, 错误: {str(e)}")
    except Exception as e:
        logger.warning(f"解析任务参数时发生异常，param: {param}, 错误: {str(e)}")

    return {}
