#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
XmiLogger 高级功能模块
包含智能日志过滤、聚合、监控、分布式支持等功能
"""

import asyncio
import json
import time
import os
import sys
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from functools import wraps
from collections import defaultdict, deque
import logging
import hashlib
import pickle
import zlib
import socket
import struct
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import weakref
import gc
import psutil
import signal
from contextlib import contextmanager
import uuid
import inspect
import traceback
from dataclasses import dataclass, field
from enum import Enum
import re
import sqlite3
from pathlib import Path
import tempfile
import shutil
import gzip
import tarfile
import zipfile
import base64
import hmac
import secrets
import ssl
import certifi
import urllib3
from urllib3.util.retry import Retry
from urllib3.util import Timeout

# 新增：智能日志过滤和聚合功能
class LogFilter(Enum):
    """日志过滤器类型"""
    NONE = "none"
    REGEX = "regex"
    KEYWORD = "keyword"
    PATTERN = "pattern"
    CUSTOM = "custom"

class LogAggregator:
    """日志聚合器"""
    def __init__(self, window_size: int = 100, flush_interval: float = 5.0):
        self.window_size = window_size
        self.flush_interval = flush_interval
        self.buffer = deque(maxlen=window_size)
        self.last_flush = time.time()
        self.lock = threading.Lock()
        self._running = True
        self._flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self._flush_thread.start()
    
    def add_log(self, log_entry: Dict[str, Any]) -> None:
        """添加日志到缓冲区"""
        with self.lock:
            self.buffer.append(log_entry)
            if len(self.buffer) >= self.window_size:
                self._flush_buffer()
    
    def _flush_buffer(self) -> None:
        """刷新缓冲区"""
        if not self.buffer:
            return
        
        # 聚合日志
        aggregated = self._aggregate_logs()
        # 这里可以发送到外部系统或存储
        print(f"聚合日志: {len(self.buffer)} 条 -> {len(aggregated)} 条")
        self.buffer.clear()
        self.last_flush = time.time()
    
    def _aggregate_logs(self) -> List[Dict[str, Any]]:
        """聚合日志"""
        if not self.buffer:
            return []
        
        # 按级别和消息模式聚合
        groups = defaultdict(list)
        for log in self.buffer:
            key = f"{log.get('level', 'INFO')}:{log.get('message', '')[:50]}"
            groups[key].append(log)
        
        aggregated = []
        for key, logs in groups.items():
            if len(logs) == 1:
                aggregated.append(logs[0])
            else:
                # 创建聚合日志
                first_log = logs[0]
                aggregated_log = {
                    'level': first_log.get('level', 'INFO'),
                    'message': f"[聚合] {first_log.get('message', '')} (重复 {len(logs)} 次)",
                    'timestamp': first_log.get('timestamp'),
                    'count': len(logs),
                    'original_logs': logs
                }
                aggregated.append(aggregated_log)
        
        return aggregated
    
    def _flush_worker(self) -> None:
        """后台刷新工作线程"""
        while self._running:
            time.sleep(self.flush_interval)
            with self.lock:
                if self.buffer and time.time() - self.last_flush > self.flush_interval:
                    self._flush_buffer()
    
    def stop(self) -> None:
        """停止聚合器"""
        self._running = False
        self._flush_buffer()

# 新增：实时监控和性能分析
class PerformanceMonitor:
    """性能监控器"""
    def __init__(self):
        self.metrics = {
            'log_count': 0,
            'error_count': 0,
            'avg_processing_time': 0.0,
            'memory_usage': 0.0,
            'cpu_usage': 0.0,
            'throughput': 0.0
        }
        self.processing_times = deque(maxlen=1000)
        self.start_time = time.time()
        self.lock = threading.Lock()
        self._monitor_thread = threading.Thread(target=self._monitor_worker, daemon=True)
        self._monitor_thread.start()
    
    def record_log(self, level: str, processing_time: float) -> None:
        """记录日志处理"""
        with self.lock:
            self.metrics['log_count'] += 1
            if level.upper() == 'ERROR':
                self.metrics['error_count'] += 1
            
            self.processing_times.append(processing_time)
            if self.processing_times:
                self.metrics['avg_processing_time'] = sum(self.processing_times) / len(self.processing_times)
    
    def _monitor_worker(self) -> None:
        """监控工作线程"""
        while True:
            try:
                # 监控系统资源
                process = psutil.Process()
                self.metrics['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
                self.metrics['cpu_usage'] = process.cpu_percent()
                
                # 计算吞吐量
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.metrics['throughput'] = self.metrics['log_count'] / elapsed
                
                time.sleep(5)  # 每5秒更新一次
            except Exception:
                time.sleep(5)
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self.lock:
            return self.metrics.copy()

# 新增：分布式日志支持
class DistributedLogger:
    """分布式日志记录器"""
    def __init__(self, node_id: str, cluster_nodes: List[str] = None):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes or []
        self.sequence_number = 0
        self.lock = threading.Lock()
        self._sequence_file = f"sequence_{node_id}.dat"
        self._load_sequence()
    
    def _load_sequence(self) -> None:
        """加载序列号"""
        try:
            if os.path.exists(self._sequence_file):
                with open(self._sequence_file, 'r') as f:
                    self.sequence_number = int(f.read().strip())
        except Exception:
            self.sequence_number = 0
    
    def _save_sequence(self) -> None:
        """保存序列号"""
        try:
            with open(self._sequence_file, 'w') as f:
                f.write(str(self.sequence_number))
        except Exception:
            pass
    
    def get_log_id(self) -> str:
        """获取唯一日志ID"""
        with self.lock:
            self.sequence_number += 1
            self._save_sequence()
            timestamp = int(time.time() * 1000)
            return f"{self.node_id}_{timestamp}_{self.sequence_number}"

# 新增：内存优化和垃圾回收
class MemoryOptimizer:
    """内存优化器"""
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory_mb = max_memory_mb
        self.last_gc_time = time.time()
        self.gc_interval = 60  # 60秒执行一次GC
        self._gc_thread = threading.Thread(target=self._gc_worker, daemon=True)
        self._gc_thread.start()
    
    def check_memory(self) -> bool:
        """检查内存使用情况"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb > self.max_memory_mb
    
    def optimize_memory(self) -> None:
        """优化内存使用"""
        if self.check_memory():
            # 强制垃圾回收
            collected = gc.collect()
            print(f"内存优化: 回收了 {collected} 个对象")
            
            # 清理缓存
            if hasattr(self, '_clear_caches'):
                self._clear_caches()
    
    def _gc_worker(self) -> None:
        """垃圾回收工作线程"""
        while True:
            time.sleep(self.gc_interval)
            self.optimize_memory()

# 新增：智能日志路由
class LogRouter:
    """智能日志路由器"""
    def __init__(self):
        self.routes = {}
        self.default_route = None
        self.lock = threading.Lock()
    
    def add_route(self, condition: Callable, handler: Callable) -> None:
        """添加路由规则"""
        with self.lock:
            route_id = len(self.routes)
            self.routes[route_id] = (condition, handler)
    
    def set_default_route(self, handler: Callable) -> None:
        """设置默认路由"""
        self.default_route = handler
    
    def route_log(self, log_entry: Dict[str, Any]) -> None:
        """路由日志"""
        with self.lock:
            for route_id, (condition, handler) in self.routes.items():
                if condition(log_entry):
                    handler(log_entry)
                    return
            
            if self.default_route:
                self.default_route(log_entry)

# 新增：日志加密和安全
class LogSecurity:
    """日志安全模块"""
    def __init__(self, encryption_key: str = None):
        try:
            from cryptography.fernet import Fernet
            self.encryption_key = encryption_key or Fernet.generate_key()
            self.cipher = Fernet(self.encryption_key)
        except ImportError:
            print("警告: cryptography 未安装，加密功能将不可用")
            self.cipher = None
        
        self.sensitive_patterns = [
            r'(password["\']?\s*[:=]\s*["\'][^"\']*["\'])',
            r'(api_key["\']?\s*[:=]\s*["\'][^"\']*["\'])',
            r'(token["\']?\s*[:=]\s*["\'][^"\']*["\'])',
            r'(secret["\']?\s*[:=]\s*["\'][^"\']*["\'])'
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sensitive_patterns]
    
    def sanitize_message(self, message: str) -> str:
        """清理敏感信息"""
        sanitized = message
        for pattern in self.compiled_patterns:
            sanitized = pattern.sub(r'\1=***', sanitized)
        return sanitized
    
    def encrypt_log(self, log_data: bytes) -> bytes:
        """加密日志数据"""
        if self.cipher is None:
            return log_data
        return self.cipher.encrypt(log_data)
    
    def decrypt_log(self, encrypted_data: bytes) -> bytes:
        """解密日志数据"""
        if self.cipher is None:
            return encrypted_data
        return self.cipher.decrypt(encrypted_data)

# 新增：日志压缩和归档
class LogArchiver:
    """日志归档器"""
    def __init__(self, archive_dir: str = "archives"):
        self.archive_dir = archive_dir
        os.makedirs(archive_dir, exist_ok=True)
    
    def compress_file(self, file_path: str, compression_type: str = "gzip") -> str:
        """压缩文件"""
        if compression_type == "gzip":
            archive_path = f"{file_path}.gz"
            with open(file_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif compression_type == "zip":
            archive_path = f"{file_path}.zip"
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, os.path.basename(file_path))
        elif compression_type == "tar":
            archive_path = f"{file_path}.tar.gz"
            with tarfile.open(archive_path, 'w:gz') as tar:
                tar.add(file_path, arcname=os.path.basename(file_path))
        
        return archive_path
    
    def archive_logs(self, log_dir: str, days_old: int = 7) -> List[str]:
        """归档旧日志"""
        archived_files = []
        current_time = datetime.now()
        
        for file_path in Path(log_dir).glob("*.log"):
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if (current_time - file_time).days >= days_old:
                try:
                    archive_path = self.compress_file(str(file_path))
                    os.remove(file_path)
                    archived_files.append(archive_path)
                except Exception as e:
                    print(f"归档文件失败 {file_path}: {e}")
        
        return archived_files

# 新增：日志数据库支持
class LogDatabase:
    """日志数据库支持"""
    def __init__(self, db_path: str = "logs.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self) -> None:
        """初始化数据库"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    file TEXT,
                    line INTEGER,
                    function TEXT,
                    process_id INTEGER,
                    thread_id INTEGER,
                    extra_data TEXT
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_level ON logs(level)
            """)
    
    def insert_log(self, log_entry: Dict[str, Any]) -> None:
        """插入日志记录"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO logs (timestamp, level, message, file, line, function, process_id, thread_id, extra_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log_entry.get('timestamp'),
                log_entry.get('level'),
                log_entry.get('message'),
                log_entry.get('file'),
                log_entry.get('line'),
                log_entry.get('function'),
                log_entry.get('process_id'),
                log_entry.get('thread_id'),
                json.dumps(log_entry.get('extra_data', {}))
            ))
    
    def query_logs(self, conditions: Dict[str, Any] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """查询日志"""
        query = "SELECT * FROM logs"
        params = []
        
        if conditions:
            where_clauses = []
            for key, value in conditions.items():
                where_clauses.append(f"{key} = ?")
                params.append(value)
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

# 新增：日志流处理
class LogStreamProcessor:
    """日志流处理器"""
    def __init__(self, processors: List[Callable] = None):
        self.processors = processors or []
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self._running = True
        self._processor_thread = threading.Thread(target=self._process_worker, daemon=True)
        self._processor_thread.start()
    
    def add_processor(self, processor: Callable) -> None:
        """添加处理器"""
        self.processors.append(processor)
    
    def process_log(self, log_entry: Dict[str, Any]) -> None:
        """处理日志"""
        self.input_queue.put(log_entry)
    
    def _process_worker(self) -> None:
        """处理工作线程"""
        while self._running:
            try:
                log_entry = self.input_queue.get(timeout=1)
                processed_entry = log_entry
                
                for processor in self.processors:
                    processed_entry = processor(processed_entry)
                
                self.output_queue.put(processed_entry)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"日志处理错误: {e}")
    
    def get_processed_log(self) -> Optional[Dict[str, Any]]:
        """获取处理后的日志"""
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None

# 新增：智能日志分析
class LogAnalyzer:
    """智能日志分析器"""
    def __init__(self):
        self.patterns = {
            'error_patterns': [
                r'Exception|Error|Failed|Timeout|Connection refused',
                r'HTTP \d{3}',
                r'ORA-\d{5}',
                r'MySQL.*error'
            ],
            'warning_patterns': [
                r'Warning|Deprecated|Deprecation',
                r'Slow query|Performance issue',
                r'Resource.*low|Memory.*high'
            ],
            'security_patterns': [
                r'Unauthorized|Forbidden|Authentication failed',
                r'SQL injection|XSS|CSRF',
                r'Failed login|Invalid credentials'
            ]
        }
        self.compiled_patterns = {}
        for category, patterns in self.patterns.items():
            self.compiled_patterns[category] = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    
    def analyze_log(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """分析日志"""
        message = log_entry.get('message', '')
        level = log_entry.get('level', 'INFO')
        
        analysis = {
            'severity': 'normal',
            'categories': [],
            'suggestions': [],
            'patterns_found': []
        }
        
        # 检查错误模式
        for pattern in self.compiled_patterns['error_patterns']:
            if pattern.search(message):
                analysis['severity'] = 'high'
                analysis['categories'].append('error')
                analysis['patterns_found'].append(pattern.pattern)
        
        # 检查警告模式
        for pattern in self.compiled_patterns['warning_patterns']:
            if pattern.search(message):
                if analysis['severity'] == 'normal':
                    analysis['severity'] = 'medium'
                analysis['categories'].append('warning')
                analysis['patterns_found'].append(pattern.pattern)
        
        # 检查安全模式
        for pattern in self.compiled_patterns['security_patterns']:
            if pattern.search(message):
                analysis['severity'] = 'critical'
                analysis['categories'].append('security')
                analysis['patterns_found'].append(pattern.pattern)
        
        # 生成建议
        if 'error' in analysis['categories']:
            analysis['suggestions'].append('检查相关服务和依赖')
        if 'security' in analysis['categories']:
            analysis['suggestions'].append('立即检查安全配置')
        if 'warning' in analysis['categories']:
            analysis['suggestions'].append('监控系统性能')
        
        return analysis

# 新增：日志健康检查
class LogHealthChecker:
    """日志健康检查器"""
    def __init__(self):
        self.health_metrics = {
            'total_logs': 0,
            'error_rate': 0.0,
            'avg_response_time': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'last_check': None
        }
    
    def check_health(self, log_dir: str) -> Dict[str, Any]:
        """检查日志系统健康状态"""
        try:
            # 检查磁盘使用情况
            total, used, free = shutil.disk_usage(log_dir)
            disk_usage_percent = (used / total) * 100
            
            # 检查内存使用情况
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            # 检查日志文件
            log_files = list(Path(log_dir).glob("*.log"))
            total_size = sum(f.stat().st_size for f in log_files)
            
            health_status = {
                'status': 'healthy',
                'disk_usage_percent': disk_usage_percent,
                'memory_usage_mb': memory_usage,
                'log_files_count': len(log_files),
                'total_log_size_mb': total_size / 1024 / 1024,
                'last_check': datetime.now().isoformat()
            }
            
            # 判断健康状态
            if disk_usage_percent > 90:
                health_status['status'] = 'critical'
                health_status['warnings'] = ['磁盘使用率过高']
            elif disk_usage_percent > 80:
                health_status['status'] = 'warning'
                health_status['warnings'] = ['磁盘使用率较高']
            
            if memory_usage > 1024:  # 超过1GB
                health_status['status'] = 'warning'
                if 'warnings' not in health_status:
                    health_status['warnings'] = []
                health_status['warnings'].append('内存使用量较高')
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }

# 新增：日志备份和恢复
class LogBackupManager:
    """日志备份管理器"""
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, log_dir: str, backup_name: str = None) -> str:
        """创建日志备份"""
        if backup_name is None:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.tar.gz")
        
        with tarfile.open(backup_path, 'w:gz') as tar:
            for log_file in Path(log_dir).glob("*.log"):
                tar.add(log_file, arcname=log_file.name)
        
        return backup_path
    
    def restore_backup(self, backup_path: str, restore_dir: str) -> bool:
        """恢复日志备份"""
        try:
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(restore_dir)
            return True
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        backups = []
        for backup_file in Path(self.backup_dir).glob("*.tar.gz"):
            stat = backup_file.stat()
            backups.append({
                'name': backup_file.name,
                'size_mb': stat.st_size / 1024 / 1024,
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        return sorted(backups, key=lambda x: x['created'], reverse=True)

# 导出所有类
__all__ = [
    'LogFilter',
    'LogAggregator', 
    'PerformanceMonitor',
    'DistributedLogger',
    'MemoryOptimizer',
    'LogRouter',
    'LogSecurity',
    'LogArchiver',
    'LogDatabase',
    'LogStreamProcessor',
    'LogAnalyzer',
    'LogHealthChecker',
    'LogBackupManager'
] 