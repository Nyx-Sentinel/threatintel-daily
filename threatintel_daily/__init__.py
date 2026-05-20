"""Data models and utilities for ThreatIntel Daily"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
import json

class ThreatSeverity(str, Enum):
    """Threat severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class ThreatType(str, Enum):
    """Types of threats monitored"""
    CVE = "CVE"
    CREDENTIAL_BREACH = "CREDENTIAL_BREACH"
    MALICIOUS_IP = "MALICIOUS_IP"
    MALWARE_URL = "MALWARE_URL"
    EXPOSED_DOMAIN = "EXPOSED_DOMAIN"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    HONEYPOT_ATTACK = "HONEYPOT_ATTACK"
    FIREWALL_ALERT = "FIREWALL_ALERT"
    CUSTOM = "CUSTOM"

class AlertStatus(str, Enum):
    """Alert status"""
    NEW = "NEW"
    IN_REVIEW = "IN_REVIEW"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"

@dataclass
class Threat:
    """Core threat data model"""
    id: str  # Unique threat ID (e.g., CVE-2024-1234, HIBP-{email_hash})
    threat_type: ThreatType
    severity: ThreatSeverity
    title: str
    description: str
    source: str  # Which feed (nvd, hibp, abuseipdb, etc.)
    
    # Temporal
    discovered_at: datetime
    published_at: Optional[datetime]
    last_seen_at: datetime
    
    # Affected entities
    affected_emails: List[str] = None  # Emails from breaches
    affected_domains: List[str] = None  # Domains mentioned
    affected_ips: List[str] = None  # IPs involved
    affected_services: List[str] = None  # Software versions
    affected_urls: List[str] = None  # Malicious URLs
    
    # Details
    metadata: Dict[str, Any] = None  # Feed-specific fields
    references: List[str] = None  # Links to source material
    mitre_tactics: List[str] = None  # MITRE ATT&CK tactics
    
    # Scoring
    confidence_score: float = 1.0  # 0.0-1.0
    relevance_score: float = None  # 0.0-1.0, computed
    
    def to_dict(self):
        """Convert to dict for serialization"""
        data = asdict(self)
        data['threat_type'] = self.threat_type.value
        data['severity'] = self.severity.value
        data['discovered_at'] = self.discovered_at.isoformat()
        data['published_at'] = self.published_at.isoformat() if self.published_at else None
        data['last_seen_at'] = self.last_seen_at.isoformat()
        return data

@dataclass
class Alert:
    """Alert sent to user"""
    id: str
    threat_id: str
    status: AlertStatus
    created_at: datetime
    updated_at: datetime
    
    # Delivery
    channels: List[str]  # email, slack, webhook, etc.
    delivered_at: Optional[datetime] = None
    delivery_failed: bool = False
    failure_reason: Optional[str] = None
    
    # User feedback
    user_feedback: Optional[str] = None  # "false_positive", "acknowledged", etc.
    notes: Optional[str] = None
    
    def to_dict(self):
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        data['delivered_at'] = self.delivered_at.isoformat() if self.delivered_at else None
        return data

@dataclass
class FeedSync:
    """Track feed sync status"""
    feed_name: str
    last_sync: datetime
    next_sync: datetime
    status: str  # "success", "failed", "running"
    threat_count: int
    new_threats: int
    error_message: Optional[str] = None

class ThreatIntelenceException(Exception):
    """Base exception for ThreatIntel Daily"""
    pass

class FeedException(ThreatIntelenceException):
    """Exception from threat feed"""
    pass

class DatabaseException(ThreatIntelenceException):
    """Exception from database operations"""
    pass

class AlertException(ThreatIntelenceException):
    """Exception from alert delivery"""
    pass

def parse_severity(severity_str: str) -> ThreatSeverity:
    """Parse severity string to enum"""
    for s in ThreatSeverity:
        if s.value == severity_str.upper():
            return s
    return ThreatSeverity.MEDIUM

def severity_to_numeric(severity: ThreatSeverity) -> int:
    """Convert severity to numeric score for comparison"""
    scores = {
        ThreatSeverity.CRITICAL: 4,
        ThreatSeverity.HIGH: 3,
        ThreatSeverity.MEDIUM: 2,
        ThreatSeverity.LOW: 1,
        ThreatSeverity.INFO: 0,
    }
    return scores.get(severity, 0)

def is_severity_match(actual: ThreatSeverity, minimum: ThreatSeverity) -> bool:
    """Check if actual severity meets or exceeds minimum"""
    return severity_to_numeric(actual) >= severity_to_numeric(minimum)
