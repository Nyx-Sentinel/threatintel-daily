"""Local database operations using SQLite"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
from threatintel_daily import (
    Threat, Alert, ThreatType, ThreatSeverity, AlertStatus,
    DatabaseException
)

class ThreatDatabase:
    """SQLite database for threats and alerts"""
    
    def __init__(self, db_path: str = "./data/threatintel.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    def _get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to connect to database: {e}")
    
    def _init_schema(self):
        """Create tables if they don't exist"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # Threats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threats (
                    id TEXT PRIMARY KEY,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    source TEXT NOT NULL,
                    discovered_at TEXT NOT NULL,
                    published_at TEXT,
                    last_seen_at TEXT NOT NULL,
                    affected_emails TEXT,
                    affected_domains TEXT,
                    affected_ips TEXT,
                    affected_services TEXT,
                    affected_urls TEXT,
                    metadata TEXT,
                    references TEXT,
                    mitre_tactics TEXT,
                    confidence_score REAL DEFAULT 1.0,
                    relevance_score REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    threat_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    channels TEXT NOT NULL,
                    delivered_at TEXT,
                    delivery_failed INTEGER DEFAULT 0,
                    failure_reason TEXT,
                    user_feedback TEXT,
                    notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(threat_id) REFERENCES threats(id)
                )
            ''')
            
            # Feed sync tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feed_syncs (
                    feed_name TEXT PRIMARY KEY,
                    last_sync TEXT,
                    next_sync TEXT,
                    status TEXT,
                    threat_count INTEGER DEFAULT 0,
                    new_threats INTEGER DEFAULT 0,
                    error_message TEXT
                )
            ''')
            
            # Indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threats_severity ON threats(severity)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threats_type ON threats(threat_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_threats_source ON threats(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_threat ON alerts(threat_id)')
            
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to initialize database schema: {e}")
        finally:
            conn.close()
    
    def insert_threat(self, threat: Threat) -> bool:
        """Insert or update a threat"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO threats (
                    id, threat_type, severity, title, description, source,
                    discovered_at, published_at, last_seen_at,
                    affected_emails, affected_domains, affected_ips,
                    affected_services, affected_urls, metadata, references,
                    mitre_tactics, confidence_score, relevance_score,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                threat.id,
                threat.threat_type.value,
                threat.severity.value,
                threat.title,
                threat.description,
                threat.source,
                threat.discovered_at.isoformat(),
                threat.published_at.isoformat() if threat.published_at else None,
                threat.last_seen_at.isoformat(),
                json.dumps(threat.affected_emails or []),
                json.dumps(threat.affected_domains or []),
                json.dumps(threat.affected_ips or []),
                json.dumps(threat.affected_services or []),
                json.dumps(threat.affected_urls or []),
                json.dumps(threat.metadata or {}),
                json.dumps(threat.references or []),
                json.dumps(threat.mitre_tactics or []),
                threat.confidence_score,
                threat.relevance_score,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to insert threat: {e}")
        finally:
            conn.close()
    
    def get_threat(self, threat_id: str) -> Optional[Threat]:
        """Get a threat by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM threats WHERE id = ?', (threat_id,))
            row = cursor.fetchone()
            return self._row_to_threat(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to get threat: {e}")
        finally:
            conn.close()
    
    def list_threats(
        self,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[ThreatSeverity] = None,
        source: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Threat]:
        """List threats with optional filtering"""
        conn = self._get_connection()
        try:
            query = 'SELECT * FROM threats WHERE 1=1'
            params = []
            
            if threat_type:
                query += ' AND threat_type = ?'
                params.append(threat_type.value)
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity.value)
            
            if source:
                query += ' AND source = ?'
                params.append(source)
            
            if since:
                query += ' AND discovered_at >= ?'
                params.append(since.isoformat())
            
            query += ' ORDER BY discovered_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_threat(row) for row in rows if row]
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to list threats: {e}")
        finally:
            conn.close()
    
    def search_threats(self, query: str, limit: int = 50) -> List[Threat]:
        """Full-text search on threats"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM threats
                WHERE title LIKE ? OR description LIKE ? OR id LIKE ?
                ORDER BY discovered_at DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            rows = cursor.fetchall()
            return [self._row_to_threat(row) for row in rows if row]
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to search threats: {e}")
        finally:
            conn.close()
    
    def get_threat_count(
        self,
        threat_type: Optional[ThreatType] = None,
        severity: Optional[ThreatSeverity] = None
    ) -> int:
        """Get count of threats"""
        conn = self._get_connection()
        try:
            query = 'SELECT COUNT(*) as count FROM threats WHERE 1=1'
            params = []
            
            if threat_type:
                query += ' AND threat_type = ?'
                params.append(threat_type.value)
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity.value)
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()['count']
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to get threat count: {e}")
        finally:
            conn.close()
    
    def insert_alert(self, alert: Alert) -> bool:
        """Insert an alert"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO alerts (
                    id, threat_id, status, channels,
                    delivered_at, delivery_failed, failure_reason,
                    user_feedback, notes, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.id,
                alert.threat_id,
                alert.status.value,
                json.dumps(alert.channels),
                alert.delivered_at.isoformat() if alert.delivered_at else None,
                1 if alert.delivery_failed else 0,
                alert.failure_reason,
                alert.user_feedback,
                alert.notes,
                datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to insert alert: {e}")
        finally:
            conn.close()
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
            row = cursor.fetchone()
            return self._row_to_alert(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to get alert: {e}")
        finally:
            conn.close()
    
    def list_alerts(
        self,
        status: Optional[AlertStatus] = None,
        threat_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Alert]:
        """List alerts with optional filtering"""
        conn = self._get_connection()
        try:
            query = 'SELECT * FROM alerts WHERE 1=1'
            params = []
            
            if status:
                query += ' AND status = ?'
                params.append(status.value)
            
            if threat_id:
                query += ' AND threat_id = ?'
                params.append(threat_id)
            
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_alert(row) for row in rows if row]
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to list alerts: {e}")
        finally:
            conn.close()
    
    def cleanup_old_records(self, days: int = 90):
        """Delete threats and alerts older than specified days"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            cursor.execute('DELETE FROM alerts WHERE created_at < ?', (cutoff,))
            cursor.execute('DELETE FROM threats WHERE discovered_at < ?', (cutoff,))
            
            conn.commit()
        except sqlite3.Error as e:
            raise DatabaseException(f"Failed to cleanup old records: {e}")
        finally:
            conn.close()
    
    @staticmethod
    def _row_to_threat(row) -> Threat:
        """Convert database row to Threat object"""
        return Threat(
            id=row['id'],
            threat_type=ThreatType(row['threat_type']),
            severity=ThreatSeverity(row['severity']),
            title=row['title'],
            description=row['description'],
            source=row['source'],
            discovered_at=datetime.fromisoformat(row['discovered_at']),
            published_at=datetime.fromisoformat(row['published_at']) if row['published_at'] else None,
            last_seen_at=datetime.fromisoformat(row['last_seen_at']),
            affected_emails=json.loads(row['affected_emails'] or '[]'),
            affected_domains=json.loads(row['affected_domains'] or '[]'),
            affected_ips=json.loads(row['affected_ips'] or '[]'),
            affected_services=json.loads(row['affected_services'] or '[]'),
            affected_urls=json.loads(row['affected_urls'] or '[]'),
            metadata=json.loads(row['metadata'] or '{}'),
            references=json.loads(row['references'] or '[]'),
            mitre_tactics=json.loads(row['mitre_tactics'] or '[]'),
            confidence_score=row['confidence_score'],
            relevance_score=row['relevance_score']
        )
    
    @staticmethod
    def _row_to_alert(row) -> Alert:
        """Convert database row to Alert object"""
        return Alert(
            id=row['id'],
            threat_id=row['threat_id'],
            status=AlertStatus(row['status']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            channels=json.loads(row['channels']),
            delivered_at=datetime.fromisoformat(row['delivered_at']) if row['delivered_at'] else None,
            delivery_failed=bool(row['delivery_failed']),
            failure_reason=row['failure_reason'],
            user_feedback=row['user_feedback'],
            notes=row['notes']
        )
