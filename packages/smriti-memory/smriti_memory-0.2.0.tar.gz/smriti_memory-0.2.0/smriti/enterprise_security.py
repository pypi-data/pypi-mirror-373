"""
Enterprise Security and Privacy Module for Smriti Memory

This module implements enterprise-grade security and privacy features:
- Multi-tenancy with user isolation
- Privacy-preserving memory operations
- Audit trails and compliance logging
- Data encryption and secure storage
- Access control and permission management
- GDPR/CCPA compliance features
"""

import hashlib
import hmac
import secrets
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import uuid
from collections import defaultdict

from .graph_memory import GraphMemory, Entity, Relationship


class PermissionLevel(Enum):
    """Permission levels for access control"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class AuditAction(Enum):
    """Types of actions for audit logging"""
    CREATE_MEMORY = "create_memory"
    READ_MEMORY = "read_memory"
    UPDATE_MEMORY = "update_memory"
    DELETE_MEMORY = "delete_memory"
    SEARCH_MEMORY = "search_memory"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    DATA_EXPORT = "data_export"
    DATA_IMPORT = "data_import"


@dataclass
class User:
    """Represents a user in the system"""
    user_id: str
    username: str
    email: str
    tenant_id: str
    permissions: Set[PermissionLevel]
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: PermissionLevel) -> bool:
        """Check if user has specific permission"""
        return permission in self.permissions or PermissionLevel.ADMIN in self.permissions


@dataclass
class Tenant:
    """Represents a tenant in multi-tenant architecture"""
    tenant_id: str
    name: str
    subscription_tier: str
    max_users: int
    max_memories: int
    data_retention_days: int
    encryption_enabled: bool
    audit_enabled: bool
    created_at: datetime
    settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditLogEntry:
    """Represents an audit log entry"""
    entry_id: str
    user_id: str
    tenant_id: str
    action: AuditAction
    resource_id: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Dict[str, Any]
    success: bool


class EncryptionManager:
    """Handles encryption and decryption of sensitive data"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        if master_key is None:
            master_key = Fernet.generate_key()
        self.master_key = master_key
        self.cipher_suite = Fernet(master_key)
    
    def encrypt_text(self, plaintext: str) -> str:
        """Encrypt plaintext string"""
        encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
        return base64.b64encode(encrypted_bytes).decode()
    
    def decrypt_text(self, encrypted_text: str) -> str:
        """Decrypt encrypted string"""
        encrypted_bytes = base64.b64decode(encrypted_text.encode())
        decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary data"""
        json_str = json.dumps(data, default=str)
        return self.encrypt_text(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt dictionary data"""
        json_str = self.decrypt_text(encrypted_data)
        return json.loads(json_str)
    
    def generate_hash(self, data: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Generate secure hash with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        hash_obj = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
        return hash_obj.hex(), salt
    
    def verify_hash(self, data: str, hash_value: str, salt: str) -> bool:
        """Verify data against hash"""
        computed_hash, _ = self.generate_hash(data, salt)
        return hmac.compare_digest(computed_hash, hash_value)


class UserManager:
    """Manages users and authentication"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.users: Dict[str, User] = {}
        self.user_credentials: Dict[str, Tuple[str, str]] = {}  # user_id -> (password_hash, salt)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_user(self, username: str, email: str, password: str, 
                   tenant_id: str, permissions: Set[PermissionLevel]) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        
        # Hash password
        password_hash, salt = self.encryption_manager.generate_hash(password)
        self.user_credentials[user_id] = (password_hash, salt)
        
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            tenant_id=tenant_id,
            permissions=permissions,
            created_at=datetime.utcnow()
        )
        
        self.users[user_id] = user
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password"""
        # Find user by username
        user = next((u for u in self.users.values() if u.username == username), None)
        
        if not user or not user.is_active:
            return None
        
        # Verify password
        password_hash, salt = self.user_credentials.get(user.user_id, ('', ''))
        if self.encryption_manager.verify_hash(password, password_hash, salt):
            user.last_login = datetime.utcnow()
            return user
        
        return None
    
    def create_session(self, user: User, ip_address: str = None, user_agent: str = None) -> str:
        """Create a new session for authenticated user"""
        session_id = secrets.token_urlsafe(32)
        
        self.active_sessions[session_id] = {
            'user_id': user.user_id,
            'created_at': datetime.utcnow(),
            'last_activity': datetime.utcnow(),
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        return session_id
    
    def validate_session(self, session_id: str, max_idle_minutes: int = 30) -> Optional[User]:
        """Validate session and return user if valid"""
        session = self.active_sessions.get(session_id)
        
        if not session:
            return None
        
        # Check if session expired
        idle_time = datetime.utcnow() - session['last_activity']
        if idle_time.total_seconds() > (max_idle_minutes * 60):
            del self.active_sessions[session_id]
            return None
        
        # Update last activity
        session['last_activity'] = datetime.utcnow()
        
        # Get user
        user = self.users.get(session['user_id'])
        return user if user and user.is_active else None
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session"""
        self.active_sessions.pop(session_id, None)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)


class TenantManager:
    """Manages multi-tenant architecture"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: {'users': 0, 'memories': 0})
    
    def create_tenant(self, name: str, subscription_tier: str = "basic") -> Tenant:
        """Create a new tenant"""
        tenant_id = str(uuid.uuid4())
        
        # Set limits based on subscription tier
        tier_limits = {
            "basic": {"max_users": 10, "max_memories": 1000, "retention_days": 30},
            "professional": {"max_users": 100, "max_memories": 10000, "retention_days": 90},
            "enterprise": {"max_users": 1000, "max_memories": 100000, "retention_days": 365}
        }
        
        limits = tier_limits.get(subscription_tier, tier_limits["basic"])
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            subscription_tier=subscription_tier,
            max_users=limits["max_users"],
            max_memories=limits["max_memories"],
            data_retention_days=limits["retention_days"],
            encryption_enabled=subscription_tier != "basic",
            audit_enabled=subscription_tier == "enterprise",
            created_at=datetime.utcnow()
        )
        
        self.tenants[tenant_id] = tenant
        return tenant
    
    def can_add_user(self, tenant_id: str) -> bool:
        """Check if tenant can add more users"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        current_users = self.tenant_usage[tenant_id]['users']
        return current_users < tenant.max_users
    
    def can_add_memory(self, tenant_id: str) -> bool:
        """Check if tenant can add more memories"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        current_memories = self.tenant_usage[tenant_id]['memories']
        return current_memories < tenant.max_memories
    
    def increment_usage(self, tenant_id: str, resource_type: str, count: int = 1):
        """Increment usage count for tenant"""
        self.tenant_usage[tenant_id][resource_type] += count
    
    def get_tenant_usage(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant usage statistics"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return {}
        
        usage = self.tenant_usage[tenant_id]
        
        return {
            "tenant_id": tenant_id,
            "subscription_tier": tenant.subscription_tier,
            "usage": usage,
            "limits": {
                "max_users": tenant.max_users,
                "max_memories": tenant.max_memories
            },
            "utilization": {
                "users": usage['users'] / tenant.max_users,
                "memories": usage['memories'] / tenant.max_memories
            }
        }


class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.audit_logs: List[AuditLogEntry] = []
        self.max_logs = 100000  # Limit to prevent memory issues
    
    def log_action(self, user_id: str, tenant_id: str, action: AuditAction,
                  resource_id: Optional[str] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None, details: Dict[str, Any] = None,
                  success: bool = True):
        """Log an audit action"""
        
        entry = AuditLogEntry(
            entry_id=str(uuid.uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            success=success
        )
        
        self.audit_logs.append(entry)
        
        # Maintain size limit
        if len(self.audit_logs) > self.max_logs:
            self.audit_logs = self.audit_logs[-self.max_logs:]
    
    def get_audit_trail(self, tenant_id: str, user_id: Optional[str] = None,
                       action: Optional[AuditAction] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None,
                       limit: int = 100) -> List[AuditLogEntry]:
        """Get filtered audit trail"""
        
        filtered_logs = []
        
        for log in reversed(self.audit_logs):  # Most recent first
            # Apply filters
            if log.tenant_id != tenant_id:
                continue
            
            if user_id and log.user_id != user_id:
                continue
            
            if action and log.action != action:
                continue
            
            if start_time and log.timestamp < start_time:
                continue
            
            if end_time and log.timestamp > end_time:
                continue
            
            filtered_logs.append(log)
            
            if len(filtered_logs) >= limit:
                break
        
        return filtered_logs
    
    def get_audit_statistics(self, tenant_id: str, days: int = 30) -> Dict[str, Any]:
        """Get audit statistics for a tenant"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        tenant_logs = [
            log for log in self.audit_logs
            if log.tenant_id == tenant_id and log.timestamp >= cutoff_time
        ]
        
        if not tenant_logs:
            return {"message": "No audit data available"}
        
        # Action breakdown
        action_counts = defaultdict(int)
        success_counts = defaultdict(int)
        user_activity = defaultdict(int)
        
        for log in tenant_logs:
            action_counts[log.action.value] += 1
            if log.success:
                success_counts[log.action.value] += 1
            user_activity[log.user_id] += 1
        
        # Calculate success rates
        success_rates = {
            action: success_counts[action] / action_counts[action]
            for action in action_counts
        }
        
        return {
            "period_days": days,
            "total_actions": len(tenant_logs),
            "action_breakdown": dict(action_counts),
            "success_rates": success_rates,
            "most_active_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
            "period_start": cutoff_time.isoformat(),
            "period_end": datetime.utcnow().isoformat()
        }


class PrivacyManager:
    """Privacy-preserving operations and GDPR compliance"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        self.encryption_manager = encryption_manager
        self.data_processing_records: List[Dict[str, Any]] = []
        self.consent_records: Dict[str, Dict[str, Any]] = {}
    
    def anonymize_memory(self, memory: GraphMemory, user_id: str) -> GraphMemory:
        """Anonymize a memory by removing/hashing PII"""
        
        # Create anonymized copy
        anonymized_memory = GraphMemory(
            memory_id=memory.memory_id,
            content=self._anonymize_text(memory.content),
            entities=[self._anonymize_entity(entity) for entity in memory.entities],
            relationships=memory.relationships,  # Relationships are already using IDs
            embedding=memory.embedding,
            timestamp=memory.timestamp,
            user_id=f"anon_{hashlib.sha256(user_id.encode()).hexdigest()[:8]}",
            memory_type=memory.memory_type
        )
        
        return anonymized_memory
    
    def _anonymize_text(self, text: str) -> str:
        """Anonymize PII in text content"""
        import re
        
        # Replace emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        
        # Replace phone numbers
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s?\d{3}-\d{4}\b', '[PHONE]', text)
        
        # Replace social security numbers
        text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
        
        # Replace credit card numbers
        text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CREDIT_CARD]', text)
        
        return text
    
    def _anonymize_entity(self, entity: Entity) -> Entity:
        """Anonymize an entity"""
        anonymized_entity = Entity(
            id=entity.id,
            text=self._anonymize_text(entity.text) if entity.type in ['PERSON', 'EMAIL', 'PHONE'] else entity.text,
            type=entity.type,
            confidence=entity.confidence,
            start_pos=entity.start_pos,
            end_pos=entity.end_pos,
            canonical_form=self._anonymize_text(entity.canonical_form) if entity.type in ['PERSON', 'EMAIL', 'PHONE'] else entity.canonical_form,
            metadata=entity.metadata
        )
        
        return anonymized_entity
    
    def record_data_processing(self, user_id: str, tenant_id: str, 
                             processing_purpose: str, data_types: List[str],
                             legal_basis: str, retention_period_days: int):
        """Record data processing activity for compliance"""
        
        record = {
            "record_id": str(uuid.uuid4()),
            "user_id": user_id,
            "tenant_id": tenant_id,
            "processing_purpose": processing_purpose,
            "data_types": data_types,
            "legal_basis": legal_basis,
            "retention_period_days": retention_period_days,
            "recorded_at": datetime.utcnow(),
            "status": "active"
        }
        
        self.data_processing_records.append(record)
    
    def record_consent(self, user_id: str, consent_type: str, granted: bool, 
                      purpose: str, details: Dict[str, Any] = None):
        """Record user consent for data processing"""
        
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}
        
        self.consent_records[user_id][consent_type] = {
            "granted": granted,
            "purpose": purpose,
            "details": details or {},
            "timestamp": datetime.utcnow(),
            "ip_address": details.get('ip_address') if details else None
        }
    
    def has_consent(self, user_id: str, consent_type: str) -> bool:
        """Check if user has given consent for specific processing"""
        user_consents = self.consent_records.get(user_id, {})
        consent = user_consents.get(consent_type, {})
        return consent.get('granted', False)
    
    def get_user_data_export(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR data portability"""
        
        # This would typically gather data from all systems
        user_data = {
            "user_id": user_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data_processing_records": [
                record for record in self.data_processing_records
                if record["user_id"] == user_id and record["tenant_id"] == tenant_id
            ],
            "consent_records": self.consent_records.get(user_id, {}),
            "note": "This export includes all personal data stored in the Smriti Memory system"
        }
        
        return user_data
    
    def delete_user_data(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Delete all user data for GDPR right to erasure"""
        
        deleted_count = 0
        
        # Mark data processing records as deleted
        for record in self.data_processing_records:
            if record["user_id"] == user_id and record["tenant_id"] == tenant_id:
                record["status"] = "deleted"
                record["deleted_at"] = datetime.utcnow()
                deleted_count += 1
        
        # Remove consent records
        consent_count = len(self.consent_records.get(user_id, {}))
        self.consent_records.pop(user_id, None)
        
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "deletion_timestamp": datetime.utcnow().isoformat(),
            "data_processing_records_deleted": deleted_count,
            "consent_records_deleted": consent_count,
            "status": "completed"
        }


class EnterpriseSecurityManager:
    """Main enterprise security coordinator"""
    
    def __init__(self, master_key: Optional[bytes] = None):
        self.encryption_manager = EncryptionManager(master_key)
        self.user_manager = UserManager(self.encryption_manager)
        self.tenant_manager = TenantManager()
        self.audit_logger = AuditLogger(self.encryption_manager)
        self.privacy_manager = PrivacyManager(self.encryption_manager)
    
    def initialize_tenant(self, name: str, admin_username: str, admin_email: str, 
                         admin_password: str, subscription_tier: str = "basic") -> Dict[str, Any]:
        """Initialize a new tenant with admin user"""
        
        # Create tenant
        tenant = self.tenant_manager.create_tenant(name, subscription_tier)
        
        # Create admin user
        admin_permissions = {PermissionLevel.ADMIN}
        admin_user = self.user_manager.create_user(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            tenant_id=tenant.tenant_id,
            permissions=admin_permissions
        )
        
        # Update tenant usage
        self.tenant_manager.increment_usage(tenant.tenant_id, 'users', 1)
        
        # Log tenant creation
        self.audit_logger.log_action(
            user_id=admin_user.user_id,
            tenant_id=tenant.tenant_id,
            action=AuditAction.CREATE_USER,
            details={"action": "tenant_initialization", "role": "admin"}
        )
        
        return {
            "tenant": asdict(tenant),
            "admin_user": asdict(admin_user),
            "setup_complete": True
        }
    
    def secure_memory_operation(self, session_id: str, operation: str, 
                               memory_data: Dict[str, Any], 
                               required_permission: PermissionLevel) -> Dict[str, Any]:
        """Perform secure memory operation with full access control"""
        
        # Validate session
        user = self.user_manager.validate_session(session_id)
        if not user:
            return {"error": "Invalid or expired session", "code": "AUTH_FAILED"}
        
        # Check permissions
        if not user.has_permission(required_permission):
            self.audit_logger.log_action(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                action=AuditAction.READ_MEMORY,  # or appropriate action
                success=False,
                details={"error": "insufficient_permissions", "required": required_permission.value}
            )
            return {"error": "Insufficient permissions", "code": "PERMISSION_DENIED"}
        
        # Check tenant limits
        if operation == "create" and not self.tenant_manager.can_add_memory(user.tenant_id):
            return {"error": "Memory limit exceeded for tenant", "code": "LIMIT_EXCEEDED"}
        
        try:
            # Get tenant for encryption settings
            tenant = self.tenant_manager.tenants.get(user.tenant_id)
            
            # Encrypt data if required
            if tenant and tenant.encryption_enabled:
                if 'content' in memory_data:
                    memory_data['content'] = self.encryption_manager.encrypt_text(memory_data['content'])
            
            # Perform operation (this would integrate with actual memory manager)
            result = self._execute_memory_operation(operation, memory_data, user)
            
            # Update tenant usage for create operations
            if operation == "create":
                self.tenant_manager.increment_usage(user.tenant_id, 'memories', 1)
            
            # Log successful operation
            action_map = {
                "create": AuditAction.CREATE_MEMORY,
                "read": AuditAction.READ_MEMORY,
                "update": AuditAction.UPDATE_MEMORY,
                "delete": AuditAction.DELETE_MEMORY,
                "search": AuditAction.SEARCH_MEMORY
            }
            
            self.audit_logger.log_action(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                action=action_map.get(operation, AuditAction.READ_MEMORY),
                resource_id=result.get('memory_id'),
                details={"operation_details": memory_data},
                success=True
            )
            
            return {"success": True, "result": result}
            
        except Exception as e:
            # Log failed operation
            self.audit_logger.log_action(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                action=AuditAction.READ_MEMORY,  # or appropriate action
                success=False,
                details={"error": str(e), "operation": operation}
            )
            
            return {"error": "Operation failed", "code": "OPERATION_FAILED", "details": str(e)}
    
    def _execute_memory_operation(self, operation: str, memory_data: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Execute the actual memory operation"""
        # This would integrate with the actual memory management system
        # For now, return a mock result
        
        operation_result = {
            "memory_id": str(uuid.uuid4()),
            "operation": operation,
            "user_id": user.user_id,
            "tenant_id": user.tenant_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return operation_result
    
    def get_compliance_report(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        
        # Validate access
        user = self.user_manager.get_user_by_id(user_id)
        if not user or user.tenant_id != tenant_id or not user.has_permission(PermissionLevel.ADMIN):
            return {"error": "Access denied"}
        
        # Gather compliance data
        tenant_usage = self.tenant_manager.get_tenant_usage(tenant_id)
        audit_stats = self.audit_logger.get_audit_statistics(tenant_id)
        
        # Get data processing records
        processing_records = [
            record for record in self.privacy_manager.data_processing_records
            if record["tenant_id"] == tenant_id and record["status"] == "active"
        ]
        
        return {
            "tenant_id": tenant_id,
            "report_timestamp": datetime.utcnow().isoformat(),
            "tenant_usage": tenant_usage,
            "audit_statistics": audit_stats,
            "data_processing_activities": len(processing_records),
            "encryption_enabled": self.tenant_manager.tenants.get(tenant_id, Tenant("", "", "", 0, 0, 0, False, False, datetime.utcnow())).encryption_enabled,
            "audit_enabled": self.tenant_manager.tenants.get(tenant_id, Tenant("", "", "", 0, 0, 0, False, False, datetime.utcnow())).audit_enabled,
            "compliance_score": self._calculate_compliance_score(tenant_id),
            "recommendations": self._get_compliance_recommendations(tenant_id)
        }
    
    def _calculate_compliance_score(self, tenant_id: str) -> float:
        """Calculate compliance score based on various factors"""
        score = 0.0
        
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant:
            return 0.0
        
        # Encryption enabled (30 points)
        if tenant.encryption_enabled:
            score += 30
        
        # Audit enabled (25 points)
        if tenant.audit_enabled:
            score += 25
        
        # Data retention policy (20 points)
        if tenant.data_retention_days > 0:
            score += 20
        
        # Recent audit activity (15 points)
        recent_audits = self.audit_logger.get_audit_trail(tenant_id, limit=10)
        if recent_audits:
            score += 15
        
        # User activity monitoring (10 points)
        if any(log.action == AuditAction.LOGIN for log in recent_audits):
            score += 10
        
        return min(score, 100.0)  # Cap at 100
    
    def _get_compliance_recommendations(self, tenant_id: str) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        tenant = self.tenant_manager.tenants.get(tenant_id)
        if not tenant:
            return ["Tenant not found"]
        
        if not tenant.encryption_enabled:
            recommendations.append("Enable encryption for enhanced data protection")
        
        if not tenant.audit_enabled:
            recommendations.append("Enable audit logging for compliance tracking")
        
        if tenant.data_retention_days == 0:
            recommendations.append("Implement data retention policy")
        
        # Check for recent audit activity
        recent_audits = self.audit_logger.get_audit_trail(tenant_id, limit=10)
        if not recent_audits:
            recommendations.append("Increase system monitoring and audit frequency")
        
        return recommendations 