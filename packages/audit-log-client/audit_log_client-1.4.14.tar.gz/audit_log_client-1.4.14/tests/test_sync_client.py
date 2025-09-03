import pytest
from audit_log_client import SyncAuditLogClient, AuditLog, AuditAction, AuditTarget

class TestSyncClient:
    @pytest.fixture
    def client(self):
        return SyncAuditLogClient(
            base_url="http://localhost:8080",
            api_key="test-key",
            buffer_size=5,
            flush_interval=0.1
        )
    
    def test_single_log(self, client):
        log = AuditLog(
            action=AuditAction.LOGIN,
            target_type=AuditTarget.USER,
            user_id="test-user",
            description="User login"
        )
        assert client.log(log) is True
    
    def test_batch_log(self, client):
        logs = [
            AuditLog(
                action=AuditAction.LOGIN,
                target_type=AuditTarget.USER,
                user_id=f"user-{i}",
                description=f"Login {i}"
            )
            for i in range(10)
        ]
        assert client.batch_log(logs) is True
    
    def test_close(self, client):
        client.close()
        assert client.running is False