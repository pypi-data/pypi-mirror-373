# XmiLogger

基于 Loguru 的增强日志记录器，支持多语言、异步操作和高级统计功能。

## 特性

- 🚀 高性能：使用 LRU 缓存和异步处理
- 🌐 多语言支持：支持中文和英文日志输出
- 📊 高级统计：支持日志分类统计和趋势分析
- 🔄 异步支持：支持异步函数日志记录
- 📝 自定义格式：支持自定义日志格式
- 🔒 安全性：内置错误处理和配置验证
- 📦 日志轮转：支持按大小和时间轮转
- 🌍 远程日志：支持异步远程日志收集
- 🐛 增强错误信息：显示详细的错误位置、调用链和代码行
- ⚡ 性能优化：智能缓存、连接池、内存优化

## 安装

```bash
pip install xmi-logger
```

## 快速开始

### 基本使用

```python
from xmi_logger import XmiLogger

# 创建日志记录器实例
logger = XmiLogger(
    file_name="app",
    log_dir="logs",
    language="zh"  # 使用中文输出
)

# 记录不同级别的日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

### 异步函数支持

```python
import asyncio

@logger.log_decorator()
async def async_function():
    await asyncio.sleep(1)
    return "异步操作完成"

# 使用异步函数
async def main():
    result = await async_function()
    logger.info(f"异步函数结果: {result}")

asyncio.run(main())
```

### 增强错误信息

```python
# 错误日志现在会显示详细的位置信息
@logger.log_decorator("除零错误", level="ERROR")
def divide_numbers(a, b):
    return a / b

try:
    result = divide_numbers(1, 0)
except ZeroDivisionError:
    logger.exception("捕获到除零错误")
    # 输出示例：
    # 2025-01-03 10:30:15.123 | ERROR    | ReqID:REQ-123 | app.py:25:divide_numbers | 12345 | 除零错误 [ZeroDivisionError]: division by zero | 位置: app.py:25:divide_numbers | 代码: return a / b
    # 调用链: app.py:25:divide_numbers -> main.py:10:main
```

### 带位置信息的日志

```python
# 使用 log_with_location 方法记录带位置信息的日志
logger.log_with_location("INFO", "这是带位置信息的日志")
# 输出示例：
# 2025-01-03 10:30:15.123 | INFO     | ReqID:REQ-123 | app.py:30:main | 12345 | [app.py:30:main] 这是带位置信息的日志
```

### 性能监控

```python
# 获取性能统计信息
perf_stats = logger.get_performance_stats()
print(json.dumps(perf_stats, indent=2))

# 清除缓存
logger.clear_caches()

# 性能优化配置
logger = XmiLogger(
    file_name="app",
    cache_size=512,        # 增加缓存大小
    enable_stats=True      # 启用统计功能
)
```

### 批量日志处理

```python
# 批量记录日志
batch_logs = [
    {'level': 'INFO', 'message': '消息1', 'tag': 'BATCH'},
    {'level': 'WARNING', 'message': '消息2', 'category': 'SYSTEM'},
    {'level': 'ERROR', 'message': '消息3'}
]

logger.batch_log(batch_logs)  # 同步批量记录
logger.async_batch_log(batch_logs)  # 异步批量记录
```

### 上下文日志

```python
# 带上下文的日志记录
context = {
    'user_id': 12345,
    'session_id': 'sess_abc123',
    'request_id': 'req_xyz789'
}

logger.log_with_context("INFO", "用户登录", context)
logger.log_with_timing("INFO", "API请求完成", {'db_query': 0.125, 'total': 0.467})
```

### 自适应日志级别

```python
# 启用自适应级别
logger = XmiLogger(
    file_name="app",
    adaptive_level=True,    # 启用自适应级别
    performance_mode=True   # 启用性能模式
)

# 根据错误率自动调整级别
logger.set_adaptive_level(error_rate_threshold=0.1)
```

### 日志管理

```python
# 压缩旧日志
logger.compress_logs(days_old=7)

# 归档日志
logger.archive_logs()

# 清理旧日志
logger.cleanup_old_logs(max_days=30)
```

### 日志分析

```python
# 分析日志
analysis = logger.analyze_logs(hours=24)
print(f"错误率: {analysis['error_rate']:.2%}")

# 生成报告
report = logger.generate_log_report(hours=24)
print(report)

# 导出日志
logger.export_logs_to_json("logs.json", hours=24)
```

### 智能分析功能

```python
from xmi_logger.advanced_features import *

# 智能日志分析
analyzer = LogAnalyzer()
analysis = analyzer.analyze_log({
    'message': '数据库连接失败: Connection refused',
    'level': 'ERROR'
})
print(f"严重程度: {analysis['severity']}")  # high
print(f"类别: {analysis['categories']}")    # ['error']
print(f"建议: {analysis['suggestions']}")   # ['检查相关服务和依赖']

# 分布式日志支持
dist_logger = DistributedLogger("node-001")
log_id = dist_logger.get_log_id()  # node-001_1640995200000_1
logger.info(f"分布式日志消息 (ID: {log_id})")

# 日志安全功能
security = LogSecurity()
original = "用户密码: 123456"
sanitized = security.sanitize_message(original)
print(sanitized)  # 用户密码=***

# 性能监控
monitor = PerformanceMonitor()
monitor.record_log("INFO", 0.05)  # 记录处理时间
metrics = monitor.get_metrics()
print(f"总日志数: {metrics['log_count']}")
print(f"平均处理时间: {metrics['avg_processing_time']:.2f}ms")

# 日志聚合
aggregator = LogAggregator(window_size=100, flush_interval=5.0)
for i in range(20):
    aggregator.add_log({
        'level': 'INFO',
        'message': '重复的日志消息',
        'timestamp': time.time()
    })
# 自动聚合为: [聚合] 重复的日志消息 (重复 20 次)

# 流处理
processor = LogStreamProcessor()

def add_timestamp(log_entry):
    log_entry['processed_timestamp'] = time.time()
    return log_entry

def add_checksum(log_entry):
    message = log_entry.get('message', '')
    log_entry['checksum'] = hashlib.md5(message.encode()).hexdigest()[:8]
    return log_entry

processor.add_processor(add_timestamp)
processor.add_processor(add_checksum)

# 处理日志
processor.process_log({'level': 'INFO', 'message': '测试消息'})
processed_log = processor.get_processed_log()

# 数据库支持
db = LogDatabase("logs.db")
db.insert_log({
    'timestamp': datetime.now().isoformat(),
    'level': 'ERROR',
    'message': '数据库连接失败',
    'file': 'app.py',
    'line': 100,
    'function': 'connect_db'
})

# 查询错误日志
logs = db.query_logs({'level': 'ERROR'}, limit=10)

# 健康检查
checker = LogHealthChecker()
health = checker.check_health("logs")
print(f"状态: {health['status']}")  # healthy/warning/critical
print(f"磁盘使用率: {health['disk_usage_percent']:.1f}%")

# 备份管理
backup_mgr = LogBackupManager("backups")
backup_path = backup_mgr.create_backup("logs", "daily_backup")

# 列出备份
backups = backup_mgr.list_backups()
for backup in backups:
    print(f"{backup['name']} - {backup['size_mb']:.2f}MB")

# 内存优化
optimizer = MemoryOptimizer(max_memory_mb=512)
if optimizer.check_memory():
    optimizer.optimize_memory()  # 自动清理内存

# 智能路由
router = LogRouter()

def error_handler(log_entry):
    print(f"🚨 错误日志: {log_entry['message']}")

def security_handler(log_entry):
    print(f"🔒 安全日志: {log_entry['message']}")

router.add_route(lambda entry: entry.get('level') == 'ERROR', error_handler)
router.add_route(lambda entry: 'password' in entry.get('message', ''), security_handler)

router.route_log({'level': 'ERROR', 'message': '系统错误'})

# 日志归档
archiver = LogArchiver("archives")
archived_files = archiver.archive_logs("logs", days_old=7)
print(f"归档了 {len(archived_files)} 个文件")
```

### 远程日志收集

```python
logger = XmiLogger(
    file_name="app",
    remote_log_url="https://your-log-server.com/logs",
    max_workers=3
)
```

### 日志统计功能

```python
# 启用统计功能
logger = XmiLogger(
    file_name="app",
    enable_stats=True
)

# 获取统计信息
stats = logger.get_stats()
print(logger.get_stats_summary())

# 获取错误趋势
error_trend = logger.get_error_trend()

# 获取分类分布
category_dist = logger.get_category_distribution()
```

## 高级配置

### 完整配置示例

```python
logger = XmiLogger(
    file_name="app",                    # 日志文件名
    log_dir="logs",                     # 日志目录
    max_size=14,                        # 单个日志文件最大大小（MB）
    retention="7 days",                 # 日志保留时间
    remote_log_url=None,                # 远程日志服务器URL
    max_workers=3,                      # 远程日志发送线程数
    work_type=False,                    # 工作模式（False为测试环境）
    language="zh",                      # 日志语言（zh/en）
    rotation_time="1 day",              # 日志轮转时间
    custom_format=None,                 # 自定义日志格式
    filter_level="DEBUG",               # 日志过滤级别
    compression="zip",                  # 日志压缩格式
    enable_stats=False,                 # 是否启用统计
    categories=None,                    # 日志分类列表
    cache_size=128                      # 缓存大小
)
```

### 自定义日志格式

```python
custom_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "ReqID:{extra[request_id]} | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger = XmiLogger(
    file_name="app",
    custom_format=custom_format
)
```

## 主要功能

### 1. 日志记录
- 支持所有标准日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 支持自定义日志级别
- 支持带标签和分类的日志记录

### 2. 日志管理
- 自动日志轮转
- 日志压缩
- 日志保留策略
- 多文件输出（按级别分文件）

### 3. 统计功能
- 日志总数统计
- 错误率统计
- 按类别统计
- 按时间统计
- 错误趋势分析

### 4. 远程日志
- 异步远程日志发送
- 自动重试机制
- 线程池管理
- 错误处理

### 5. 装饰器支持
- 函数执行时间记录
- 异常捕获和记录
- 支持同步和异步函数

### 6. 增强错误信息
- 显示错误发生的具体文件、行号和函数名
- 显示错误发生时的代码行内容
- 显示调用链信息（最后3层调用）
- 支持全局异常处理器
- 提供带位置信息的日志记录方法

### 7. 性能优化
- 智能缓存机制减少重复计算
- 连接池优化网络请求性能
- 内存优化减少对象创建
- 统计缓存提高查询效率
- 线程本地缓存提升并发性能

### 8. 高级功能
- 批量日志处理提高大量日志记录性能
- 上下文日志自动添加相关上下文信息
- 自适应级别根据系统状态自动调整日志级别
- 日志管理压缩、归档、清理功能
- 日志分析智能分析日志内容和趋势
- 性能监控实时监控缓存和性能指标

### 9. 智能分析功能
- 智能日志分析自动识别错误、警告、安全事件
- 分布式日志支持多节点环境，提供唯一日志ID
- 日志安全功能敏感信息清理和加密
- 性能监控实时监控系统资源使用
- 日志聚合自动聚合重复日志
- 流处理可扩展的日志处理管道
- 数据库支持结构化日志存储和查询
- 健康检查系统状态监控
- 备份管理自动备份和恢复
- 内存优化智能垃圾回收
- 智能路由基于条件的日志分发
- 日志归档自动压缩和归档

## 错误处理

```python
try:
    logger = XmiLogger("app", log_dir="/path/to/logs")
except RuntimeError as e:
    print(f"日志配置失败: {e}")
```

## 注意事项

1. 确保日志目录具有写入权限
2. 远程日志URL必须是有效的HTTP(S)地址
3. 建议在生产环境中启用统计功能
4. 异步操作时注意正确处理异常

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

