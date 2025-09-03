


# 审计日志客户端

用于审计日志服务的Python客户端，支持同步和异步两种使用模式。

## 主要功能

- **双模式支持**：同步和异步API
- **缓冲处理**：可配置的内存缓冲区
- **重试机制**：指数退避重试策略
- **降级策略**：失败时自动写入本地文件
- **查询支持**：灵活的日志查询功能

## 安装

```bash
pip install audit-log-client
```

## 快速入门

### 同步客户端

```python
from audit_log_client import SyncAuditLogClient, AuditLog, AuditAction, AuditTarget

# 初始化客户端
client = SyncAuditLogClient(
    base_url="http://audit.service/api",
    app_id="your-app-id",  # 应用ID
    secret_key="your-secret-key"  # 应用密钥
)

# 创建审计日志
log = AuditLog(
    action=AuditAction.UPDATE,
    target_type=AuditTarget.USER,
    user_id="admin",
    description="用户资料更新",
    before={"name": "张三"},
    after={"name": "张三丰"}
)

# 记录日志
client.log(log)

# 关闭客户端
client.close()
```

### 异步客户端

```python
import asyncio
from audit_log_client import AsyncAuditLogClient, AuditLog, AuditAction, AuditTarget

async def main():
    # 初始化客户端
    client = AsyncAuditLogClient(
        base_url="http://audit.service/api",
        app_id="your-app-id",  # 应用ID
        secret_key="your-secret-key"  # 应用密钥
    )
    
    # 创建审计日志
    log = AuditLog(
        action=AuditAction.CREATE,
        target_type=AuditTarget.ORDER,
        user_id="sales",
        description="新建订单"
    )
    
    # 记录日志
    await client.log(log)
    
    # 关闭客户端
    await client.shutdown()

asyncio.run(main())
```

## 认证方式

新版本已升级认证机制，使用应用ID和应用密钥进行身份验证：

1. 在请求头中添加：
   - `X-App-ID`: 您的应用ID
   - `X-Secret-Key`: 您的应用密钥

2. 初始化客户端时提供：
   ```python
   client = SyncAuditLogClient(
       base_url="...",
       app_id="your-app-id",
       secret_key="your-secret-key"
   )
   ```

## 查询示例

```python
from datetime import datetime, timedelta

# 查询最近1小时的用户更新日志
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

logs = client.query_logs(
    action="UPDATE",
    target_type="USER",
    user_id="admin",
    start_time=start_time,
    end_time=end_time
)

for log in logs:
    print(f"{log.timestamp}: {log.description}")
```

## 主要更新内容：

1. 将文档语言切换为中文
2. 更新了认证方式的说明，强调使用AppID和SecretKey
3. 修改了示例代码中的描述文本为中文
4. 添加了专门的认证方式说明章节
5. 新增了查询示例
6. 保留了必要的英文术语（如MIT许可证）
7. 更新了初始化客户端的参数说明
