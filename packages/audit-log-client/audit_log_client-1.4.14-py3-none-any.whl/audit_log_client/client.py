# client.py
import time
import threading
import asyncio
import logging
import httpx
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import AuditLog
from .tools import (
    serialize_audit_log,
    deserialize_audit_log,
    prepare_logs_for_transport,
    write_logs_to_file,
    exponential_backoff
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("audit_log_client")

# ====================== 同步客户端 ======================
class SyncAuditLogClient:
    def __init__(
        self,
        base_url: str,
        app_id: str,
        secret_key: str,
        buffer_size: int = 100,
        flush_interval: float = 10.0,
        max_retries: int = 3,
        timeout: float = 10.0
    ):
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.secret_key = secret_key
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.timeout = timeout
        
        self.buffer = []
        self.lock = threading.Lock()
        self.client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-App-ID": self.app_id,
                "X-Secret-Key": self.secret_key,
                "Content-Type": "application/json"         
            }
        )
        
        # 启动后台刷新线程
        self.flush_thread = threading.Thread(target=self._periodic_flush, daemon=True)
        self.running = True
        self.flush_thread.start()
        logger.info("SyncAuditLogClient initialized and flush thread started")
    
    def log(self, log: AuditLog) -> bool:
        """同步记录审计日志（缓冲处理）"""
        with self.lock:
            self.buffer.append(log)
            if len(self.buffer) >= self.buffer_size:
                logger.debug("Buffer full, triggering flush")
                self._flush_buffer()
        return True
    
    def batch_log(self, logs: List[AuditLog]) -> bool:
        """同步批量记录审计日志"""
        with self.lock:
            self.buffer.extend(logs)
            if len(self.buffer) >= self.buffer_size:
                logger.debug("Buffer full after batch add, triggering flush")
                self._flush_buffer()
        return True
    
    def _periodic_flush(self):
        """定期刷新缓冲区"""
        while self.running:
            time.sleep(self.flush_interval)
            logger.debug("Periodic flush triggered")
            self._flush_buffer()
    
    def _flush_buffer(self):
        """刷新缓冲区到日志服务（分批次处理）"""
        if not self.buffer:
            logger.debug("Flush called but buffer is empty")
            return True
        
        with self.lock:
            logs_to_send = self.buffer.copy()
            self.buffer = []
        
        # 分批次处理（每批最大500条）
        max_batch_size = 500
        batches = [
            logs_to_send[i:i + max_batch_size] 
            for i in range(0, len(logs_to_send), max_batch_size)
        ]
        
        logger.info(f"Flushing {len(logs_to_send)} logs in {len(batches)} batches")
        
        all_success = True
        
        for batch in batches:
            # 准备日志数据用于传输
            logs_data = prepare_logs_for_transport(batch)
            
            # 重试逻辑
            batch_success = False
            for attempt in range(self.max_retries + 1):
                try:
                    response = self.client.post(
                        "/logs/batch",
                        json=logs_data,
                        headers={"Content-Type": "application/json"}
                    )
                    if response.status_code == 201:
                        logger.info(f"Batch of {len(batch)} logs sent successfully")
                        batch_success = True
                        break
                    elif response.status_code == 413:  # 处理批次过大错误
                        logger.warning("Batch too large, splitting further")
                        # 尝试拆分批次
                        self._fallback_write(batch)
                        break
                    else:
                        logger.error(
                            f"Failed to send logs: HTTP {response.status_code} - {response.text}"
                        )
                except Exception as e:
                    logger.error(f"Flush attempt {attempt+1} failed: {str(e)}")
                
                # 指数退避
                if attempt < self.max_retries:
                    delay = exponential_backoff(attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
            
            if not batch_success:
                all_success = False
                # 当前批次所有尝试失败后的降级处理
                logger.warning("All retries failed, writing to fallback file")
                self._fallback_write(batch)
        
        return all_success
    
    def _fallback_write(self, logs: List[AuditLog]):
        """降级策略：写入本地文件"""
        return write_logs_to_file(logs)
    
    def query_logs(
        self,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """查询审计日志（同步）"""
        params = {}
        if action: params["action"] = action
        if target_type: params["target_type"] = target_type
        if target_id: params["target_id"] = target_id
        if user_id: params["user_id"] = user_id
        if start_time: params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_time: params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        params["limit"] = limit
        
        logger.info(f"Querying logs with params: {params}")
        
        try:
            response = self.client.get("/logs", params=params)
            if response.status_code == 200:
                # 反序列化响应数据
                logs = [deserialize_audit_log(item) for item in response.json()]
                logger.info(f"Query returned {len(logs)} logs")
                return logs
            else:
                logger.error(f"Query failed with status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
        
        return []
    
    def close(self):
        """关闭客户端并清理资源"""
        logger.info("Closing SyncAuditLogClient")
        self.running = False
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5)
        self._flush_buffer()  # Final flush
        self.client.close()
        logger.info("SyncAuditLogClient closed")

# ====================== 异步客户端 ======================
class AsyncAuditLogClient:
    def __init__(
        self,
        base_url: str,
        app_id: str,
        secret_key: str,
        buffer_size: int = 100,
        flush_interval: float = 10.0,
        max_retries: int = 3,
        timeout: float = 10.0
    ):
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.secret_key = secret_key
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.max_retries = max_retries
        self.timeout = timeout
        
        self.buffer = []
        self.lock = asyncio.Lock()
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={
                "X-App-ID": self.app_id,
                "X-Secret-Key": self.secret_key,
                "Content-Type": "application/json"         
            }
        )
        self.flush_task = None
        self.running = False
        logger.info("AsyncAuditLogClient initialized")
    
    async def initialize(self):
        """异步初始化客户端"""
        self.running = True
        self.flush_task = asyncio.create_task(self._periodic_flush())
        logger.info("AsyncAuditLogClient flush task started")
    
    async def log(self, log: AuditLog) -> bool:
        """异步记录审计日志（缓冲处理）"""
        async with self.lock:
            self.buffer.append(log)
            if len(self.buffer) >= self.buffer_size:
                logger.debug("Buffer full, triggering flush")
                await self._flush_buffer()
        return True
    
    async def batch_log(self, logs: List[AuditLog]) -> bool:
        """异步批量记录审计日志"""
        async with self.lock:
            self.buffer.extend(logs)
            if len(self.buffer) >= self.buffer_size:
                logger.debug("Buffer full after batch add, triggering flush")
                await self._flush_buffer()
        return True
    
    async def _periodic_flush(self):
        """定期刷新缓冲区"""
        while self.running:
            await asyncio.sleep(self.flush_interval)
            logger.debug("Periodic flush triggered")
            await self._flush_buffer()
    
    async def _flush_buffer(self):
        """刷新缓冲区到日志服务"""
        if not self.buffer:
            logger.debug("Flush called but buffer is empty")
            return True
        
        async with self.lock:
            logs_to_send = self.buffer.copy()
            self.buffer = []
        
        logger.info(f"Flushing {len(logs_to_send)} logs")
        
        # 准备日志数据用于传输
        logs_data = prepare_logs_for_transport(logs_to_send)
        
        # 重试逻辑
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.post(
                    "/logs/batch",
                    json=logs_data,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 201:
                    logger.info(f"Successfully sent {len(logs_to_send)} logs")
                    return True
                elif response.status_code == 413:  # 处理批次过大错误
                    logger.warning("Batch too large, writing to fallback file")
                    # 降级处理
                    await self._fallback_write(logs_to_send)
                    return False
                else:
                    logger.error(
                        f"Failed to send logs: HTTP {response.status_code} - {response.text}"
                    )
            except Exception as e:
                logger.error(f"Flush attempt {attempt+1} failed: {str(e)}")
            
            # 指数退避
            if attempt < self.max_retries:
                delay = exponential_backoff(attempt)
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
        
        # 所有尝试失败后的降级处理
        logger.warning("All retries failed, writing to fallback file")
        await self._fallback_write(logs_to_send)
        return False
    
    async def _fallback_write(self, logs: List[AuditLog]):
        """降级策略：写入本地文件"""
        # 使用线程池执行文件写入，避免阻塞事件循环
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, write_logs_to_file, logs)
    
    async def query_logs(
        self,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """查询审计日志（异步）"""
        params = {}
        if action: params["action"] = action
        if target_type: params["target_type"] = target_type
        if target_id: params["target_id"] = target_id
        if user_id: params["user_id"] = user_id
        if start_time: params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_time: params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        params["limit"] = limit
        
        logger.info(f"Querying logs with params: {params}")
        
        try:
            response = await self.client.get("/logs", params=params)
            if response.status_code == 200:
                # 反序列化响应数据
                logs = [deserialize_audit_log(item) for item in response.json()]
                logger.info(f"Query returned {len(logs)} logs")
                return logs
            else:
                logger.error(f"Query failed with status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
        
        return []
    
    async def shutdown(self):
        """关闭客户端并清理资源"""
        logger.info("Shutting down AsyncAuditLogClient")
        self.running = False
        if self.flush_task:
            self.flush_task.cancel()
            try:
                await self.flush_task
            except asyncio.CancelledError:
                logger.debug("Flush task cancelled")
                pass
        await self._flush_buffer()  # Final flush
        await self.client.aclose()
        logger.info("AsyncAuditLogClient closed")