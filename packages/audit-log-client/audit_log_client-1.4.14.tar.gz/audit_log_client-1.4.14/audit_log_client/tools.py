# tools.py
import json
from datetime import datetime
import logging
from typing import Any, Dict, List, Union

from .models import AuditLog

def serialize_audit_log(log: AuditLog) -> Dict[str, Any]:
    """将审计日志对象转换为可JSON序列化的字典
    
    处理:
    1. 日期时间字段转换为ISO格式字符串
    2. 字段名适配(如ip_address -> IPAddress)
    3. 处理可能存在的额外字段
    """
    # 使用Pydantic的model_dump方法获取字典表示
    log_dict = log.model_dump()
    
    # 处理日期时间字段 - 转换为ISO格式字符串
    datetime_fields = ['timestamp', 'created_at', 'updated_at', 'deleted_at']
    for field in datetime_fields:
        if field in log_dict and isinstance(log_dict[field], datetime):
            log_dict[field] = log_dict[field].isoformat()
    
    # 字段名适配
    field_mappings = {
        'ip_address': 'IPAddress',
        'user_agent': 'UserAgent',
        'request_path': 'RequestPath',
        'method': 'Method',
        'status_code': 'StatusCode',
    }
    
    for old_name, new_name in field_mappings.items():
        if old_name in log_dict:
            log_dict[new_name] = log_dict.pop(old_name)
    
    return log_dict

def deserialize_audit_log(data: Dict[str, Any]) -> AuditLog:
    """将字典数据反序列化为审计日志对象
    
    处理:
    1. 将ISO格式字符串转换为datetime对象
    2. 反向字段名适配
    """
    # 反向字段名适配
    reverse_mappings = {
        'IPAddress': 'ip_address',
        'UserAgent': 'user_agent',
        'RequestPath': 'request_path',
        'Method': 'method',
        'StatusCode': 'status_code',
    }
    
    for new_name, old_name in reverse_mappings.items():
        if new_name in data:
            data[old_name] = data.pop(new_name)
    
    # 处理日期时间字段 - 将ISO字符串转换为datetime对象
    datetime_fields = ['timestamp', 'created_at', 'updated_at', 'deleted_at']
    for field in datetime_fields:
        if field in data and isinstance(data[field], str):
            try:
                # 尝试解析带时区的ISO格式
                data[field] = datetime.fromisoformat(data[field])
            except ValueError:
                # 如果失败，尝试解析不带时区的格式
                try:
                    data[field] = datetime.strptime(data[field], "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    # 如果还是失败，保留原始值
                    pass
    
    return AuditLog(**data)

def prepare_logs_for_transport(logs: List[AuditLog]) -> List[Dict[str, Any]]:
    """批量准备日志用于传输"""
    return [serialize_audit_log(log) for log in logs]

def write_logs_to_file(logs: List[AuditLog], filename: str = "audit_fallback.log"):
    """将日志写入本地文件（降级策略）"""
    try:
        with open(filename, "a", encoding="utf-8") as f:
            for log in logs:
                log_dict = serialize_audit_log(log)
                f.write(json.dumps(log_dict) + "\n")
        logging.warning(f"Wrote {len(logs)} logs to fallback file")
        return True
    except Exception as e:
        logging.error(f"Fallback write failed: {str(e)}")
        return False

def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
    """计算指数退避延迟时间"""
    return base_delay * (2 ** attempt)