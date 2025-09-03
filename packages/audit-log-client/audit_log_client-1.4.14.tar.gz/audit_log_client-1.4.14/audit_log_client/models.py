import datetime
from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

class AuditAction(str, Enum):
    # 基础操作
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    ACCESS = "ACCESS"
    DOWNLOAD = "DOWNLOAD"
    UPLOAD = "UPLOAD"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    EXECUTE = "EXECUTE"
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    
    # 项目管理相关
    RESTORE = "RESTORE"
    CHANGE_STATUS = "CHANGE_STATUS"
    ADD_MEMBER = "ADD_MEMBER"
    UPDATE_MEMBER_ROLE = "UPDATE_MEMBER_ROLE"
    REMOVE_MEMBER = "REMOVE_MEMBER"
    
    # 应用管理相关
    CHANGE_OWNER = "CHANGE_OWNER"
    CHANGE_ENVIRONMENT = "CHANGE_ENVIRONMENT"
    
    # 文件管理相关
    RENAME_FILE = "RENAME_FILE"
    MOVE_FILE = "MOVE_FILE"
    SHARE_FILE = "SHARE_FILE"
    REVOKE_FILE_SHARE = "REVOKE_FILE_SHARE"
    
    # 任务管理相关
    CREATE_TASK = "CREATE_TASK"
    ASSIGN_TASK = "ASSIGN_TASK"
    COMPLETE_TASK = "COMPLETE_TASK"
    REOPEN_TASK = "REOPEN_TASK"
    CHANGE_TASK_PRIORITY = "CHANGE_TASK_PRIORITY"
    ADD_TASK_COMMENT = "ADD_TASK_COMMENT"
    
    # 通知管理相关
    SEND_NOTIFICATION = "SEND_NOTIFICATION"
    READ_NOTIFICATION = "READ_NOTIFICATION"
    ARCHIVE_NOTIFICATION = "ARCHIVE_NOTIFICATION"
    
    # 支付管理相关
    INITIATE_PAYMENT = "INITIATE_PAYMENT"
    PROCESS_PAYMENT = "PROCESS_PAYMENT"
    REFUND_PAYMENT = "REFUND_PAYMENT"
    CANCEL_PAYMENT = "CANCEL_PAYMENT"
    CREATE_INVOICE = "CREATE_INVOICE"
    VERIFY_PAYMENT = "VERIFY_PAYMENT"
    
    # 系统管理相关
    CHANGE_ROLE = "CHANGE_ROLE"
    UPDATE_PERMISSION = "UPDATE_PERMISSION"
    RESET_PASSWORD = "RESET_PASSWORD"
    LOCK_ACCOUNT = "LOCK_ACCOUNT"
    UNLOCK_ACCOUNT = "UNLOCK_ACCOUNT"
    
    # 数据分析相关
    GENERATE_REPORT = "GENERATE_REPORT"
    EXPORT_DATA = "EXPORT_DATA"

class AuditTarget(str, Enum):
    # 基础实体
    USER = "USER"
    FILE = "FILE"
    ROLE = "ROLE"
    PERMISSION = "PERMISSION"
    CONFIG = "CONFIG"
    SETTING = "SETTING"
    PRODUCT = "PRODUCT"
    ORDER = "ORDER"
    CUSTOMER = "CUSTOMER"
    SESSION = "SESSION"
    API_KEY = "API_KEY"
    DATABASE = "DATABASE"
    REPORT = "REPORT"
    PAYMENT = "PAYMENT"
    
    # 网关&全链路追踪    
    API = "API"  # API接口访问
    GATEWAY = "GATEWAY"  # 网关操作
    TRACE = "TRACE"  # 全链路追踪
    ENDPOINT = "ENDPOINT"  # API端点
    ROUTER = "ROUTER"  # 路由配置
    
    
    # 项目管理实体
    PROJECT = "PROJECT"
    PROJECT_MEMBER = "PROJECT_MEMBER"
    APPLICATION = "APPLICATION"
    
    # 文件管理实体
    FOLDER = "FOLDER"
    SHARED_FILE = "SHARED_FILE"
    
    # 任务管理实体
    TASK = "TASK"
    TASK_COMMENT = "TASK_COMMENT"
    
    # 通知管理实体
    NOTIFICATION = "NOTIFICATION"
    NOTIFICATION_TEMPLATE = "NOTIFICATION_TEMPLATE"
    
    # 支付管理实体
    INVOICE = "INVOICE"
    REFUND = "REFUND"
    PAYMENT_GATEWAY = "PAYMENT_GATEWAY"
    
    # 系统管理实体
    ACCOUNT = "ACCOUNT"
    SECURITY_POLICY = "SECURITY_POLICY"
    
    # 数据分析实体
    DATA_REPORT = "DATA_REPORT"
    DASHBOARD = "DASHBOARD"

class AuditLog(BaseModel):
    """审计日志数据模型 - 支持所有业务场景"""
    # 核心字段
    action: AuditAction
    target_type: AuditTarget
    user_id: str
    description: str
    
    # 可选核心字段
    target_id: Optional[str] = None
    ip_address: Optional[str] = None
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    
    # 时间戳 - 使用UTC时间
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    
    # Pydantic v2 配置语法
    model_config = ConfigDict(
        extra="allow",  # 允许任意额外字段
        arbitrary_types_allowed=True  # 允许自定义类型
    )