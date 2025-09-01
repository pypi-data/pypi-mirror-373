# MaaS 任务退避重试框架

[![Python](https://img.shields.io/badge/Python-3-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

一个基于Redis的分布式任务退避重试框架，支持多种退避策略和并发执行。

## ✨ 核心特性

- 🔄 **多种退避策略**: 固定间隔、指数退避、线性退避
- 🚀 **高并发执行**: 支持线程池/进程池并发处理
- 📊 **任务优先级**: 支持任务优先级管理
- ⏱️ **超时控制**: 任务执行超时和失败处理
- 📈 **状态监控**: 完整的任务状态管理和监控
- 🎯 **灵活调度**: 可配置的定时调度间隔
- 🔒 **分布式锁**: 基于Redis的分布式任务队列

## 📦 安装

```bash
pip install maas-backoff-scheduler
```

## 🚀 快速开始

### 基础使用示例

```python
from backoff.scheduler.backoff_scheduler import (
    TaskBackoffScheduler,
    TaskBackoffConfig,
    TaskEntity,
    TaskConfig,
    StorageConfig,
    ThreadPoolConfig,
    SchedulerConfig,
    ResultEntity,
)

# 1. 创建配置
config = TaskBackoffConfig()

# Redis存储配置
config.storage = StorageConfig(
    type="redis", 
    host="localhost", 
    port=6379, 
    database=0, 
    password=""
)

# 任务配置
config.task = TaskConfig(
    biz_prefix="my_service",
    batch_size=10,
    max_retry_count=3,
    backoff_strategy="exponential",
    backoff_interval=30,
    backoff_multiplier=2.0,
    min_gpu_memory_gb=0.5,
    min_gpu_utilization=10
)

# 线程池配置
config.threadpool = ThreadPoolConfig(
    concurrency=5, 
    exec_timeout=300, 
    proc_mode="process"
)

# 调度器配置
config.scheduler = SchedulerConfig(interval=10)

# 2. 创建调度器
scheduler = TaskBackoffScheduler(config)

# 3. 定义任务处理器
def task_handler(task: TaskEntity):
    # 您的业务逻辑
    print(f"处理任务: {task.task_id}")
    return ResultEntity.ok(
        result={"status": "success", "data": "处理完成"},
        task_id=task.task_id,
    )

def exception_handler(task: TaskEntity):
    # 异常处理逻辑
    return ResultEntity.fail(
        code=-1,
        message="任务执行失败",
        task_id=task.task_id,
    )

# 4. 注册处理器
scheduler.set_custom_task_handler(task_handler)
scheduler.set_custom_task_exception_handler(exception_handler)

# 5. 启动调度器
scheduler.start()
```

## 📚 API 参考

### 处理器管理

```python
# 注册处理器
scheduler.set_custom_task_handler(task_handler)

scheduler.set_custom_task_exception_handler(exception_handler)
```


### 任务管理

```python
# 创建任务
task_id = scheduler.create_task(
    task_params={"key": "value"},
    task_id="unique_task_id"
)

# 查询任务
task = scheduler.get_task(task_id)

# 撤销任务（仅限pending状态）
success = scheduler.cancel_task(task_id)

# 获取队列统计
stats = scheduler.get_queue_stats()
```

### 任务状态管理

```python
# 标记任务完成
scheduler.mark_task_completed(task_id, "执行结果")

# 标记任务失败
scheduler.mark_task_failed(task_id, "失败原因")

# 标记任务处理中
scheduler.mark_task_processing(task_id)

# 更新任务进度
scheduler.update_task_progress(task_id, 75)  # 75%
```

### 调度器控制

```python
# 启动调度器
scheduler.start()

# 关闭调度器
scheduler.shutdown()
```

## ⚙️ 配置详解

### StorageConfig (存储配置)

| 参数     | 类型   | 必填 | 默认值    | 说明           |
|----------|--------|------|-----------|----------------|
| type     | string | 是   | -         | 存储类型       |
| host     | string | 是   | -         | Redis主机地址  |
| port     | int    | 是   | -         | Redis端口      |
| database | int    | 否   | 0         | Redis数据库    |
| password | string | 否   | ""        | Redis密码      |

### TaskConfig (任务配置)

| 参数                | 类型   | 必填 | 默认值        | 说明                    |
|---------------------|--------|------|---------------|-------------------------|
| biz_prefix          | string | 是   | -             | 业务前缀                |
| max_retry_count     | int    | 否   | 3             | 最大重试次数            |
| backoff_strategy    | string | 否   | exponential   | 退避策略                |
| backoff_interval    | int    | 否   | 30            | 初始退避间隔(秒)        |
| backoff_multiplier  | float  | 否   | 2.0           | 退避倍数                |
| batch_size          | int    | 否   | 100           | 批次大小                |
| min_gpu_memory_gb   | float  | 否   | 0             | 最小GPU内存(GB)         |
| min_gpu_utilization | int    | 否   | 0             | 最小GPU利用率(%)        |

**退避策略说明:**
- `fixed`: 固定间隔重试
- `exponential`: 指数退避 (推荐)
- `linear`: 线性退避

### ThreadPoolConfig (线程池配置)

| 参数          | 类型   | 必填 | 默认值 | 说明                    |
|---------------|--------|------|--------|-------------------------|
| concurrency   | int    | 否   | 10     | 并发线程/进程数         |
| proc_mode     | string | 否   | thread | 执行模式                |
| exec_timeout  | int    | 否   | 300    | 任务超时时间(秒)        |

**执行模式说明:**
- `thread`: 线程池模式 (适合IO密集型)
- `process`: 进程池模式 (适合CPU密集型)

### SchedulerConfig (调度器配置)

| 参数     | 类型 | 必填 | 默认值 | 说明           |
|----------|------|------|--------|----------------|
| interval | int  | 否   | 10     | 轮询间隔(秒)   |

## 🔧 高级用法

### 自定义退避策略

```python
# 指数退避示例
config.task.backoff_strategy = "exponential"
config.task.backoff_interval = 30  # 初始30秒
config.task.backoff_multiplier = 2.0  # 每次翻倍

# 重试间隔: 30s → 60s → 120s → 240s
```

### GPU资源管理

```python
# 配置GPU资源要求
config.task.min_gpu_memory_gb = 4.0  # 需要4GB显存
config.task.min_gpu_utilization = 20  # GPU利用率低于20%才执行
```

### 批量任务处理

```python
# 创建多个任务
for i in range(100):
    task_id = scheduler.create_task(
        task_params={"index": i, "data": f"task_{i}"},
        task_id=f"batch_task_{i}"
    )
```

## 📊 监控和调试

### 获取队列状态

```python
stats = scheduler.get_queue_stats()
print(f"待处理任务: {stats.pending_count}")
print(f"处理中任务: {stats.processing_count}")
print(f"已完成任务: {stats.completed_count}")
print(f"失败任务: {stats.failed_count}")
```

### 任务状态查询

```python
task = scheduler.get_task(task_id)
print(f"任务ID: {task.task_id}")
print(f"状态: {task.status}")
print(f"重试次数: {task.retry_count}")
print(f"下次执行时间: {task.next_execute_time}")
```

## 🐛 常见问题

### Q: 如何选择合适的退避策略？
A: 
- **固定间隔**: 适合对时间要求严格的任务
- **指数退避**: 适合网络请求等可能临时失败的任务 (推荐)
- **线性退避**: 适合资源竞争类任务

### Q: 如何设置合适的并发数？
A: 
- **IO密集型**: 并发数 = CPU核心数 × (1 + 等待时间/计算时间)
- **CPU密集型**: 并发数 = CPU核心数

### Q: 任务执行超时怎么办？
A: 检查 `exec_timeout` 配置，确保任务能在指定时间内完成，或优化任务逻辑。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者
