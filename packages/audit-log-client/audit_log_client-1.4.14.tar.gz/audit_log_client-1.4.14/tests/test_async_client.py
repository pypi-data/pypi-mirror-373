import pytest
import asyncio
from audit_log_client import AsyncAuditLogClient, AuditLog, AuditAction, AuditTarget

class TestAsyncClient:
    @pytest.fixture
    async def client(self):
        client = AsyncAuditLogClient(
            base_url="http://localhost:8080",
            api_key="test-key",
            buffer_size=5,
            flush_interval=0.1
        )
        await client.initialize()
        yield client
        await client.shutdown()
    
    @pytest.mark.asyncio
    async def test_single_log(self, client):
        log = AuditLog(
            action=AuditAction.LOGIN,
            target_type=AuditTarget.USER,
            user_id="test-user",
            description="User login"
        )
        assert await client.log(log) is True
    
    @pytest.mark.asyncio
    async def test_batch_log(self, client):
        logs = [
            AuditLog(
                action=AuditAction.LOGIN,
                target_type=AuditTarget.USER,
                user_id=f"user-{i}",
                description=f"Login {i}"
            )
            for i in range(10)
        ]
        assert await client.batch_log(logs) is True