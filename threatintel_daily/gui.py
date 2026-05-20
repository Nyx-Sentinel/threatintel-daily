"""
ThreatIntel Daily - Windows GUI Application
A desktop application for personal threat intelligence monitoring
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QTableWidget,
    QTableWidgetItem, QComboBox, QSpinBox, QCheckBox, QMessageBox,
    QSystemTrayIcon, QMenu, QDialog, QFormLayout, QFileDialog, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon, QFont, QColor

from threatintel_daily.database import ThreatDatabase
from threatintel_daily.main import ThreatIntelDaily
from threatintel_daily import ThreatType, ThreatSeverity


class ThreatFetchWorker(QThread):
    """Background thread for fetching threats"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(int, int)  # new_threats, errors
    
    def __init__(self, app: ThreatIntelDaily):
        super().__init__()
        self.app = app
    
    def run(self):
        try:
            self.progress.emit("Fetching threats...")
            threats, errors = self.app.feed_aggregator.fetch_all()
            new_count = len(threats)
            error_count = len(errors)
            self.progress.emit(f"Fetched {new_count} threats")
            self.finished.emit(new_count, error_count)
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(0, 1)


class SettingsDialog(QDialog):
    """Configuration dialog"""
    
    def __init__(self, config_path: str, parent=None):
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.init_ui()
    
    def _load_config(self) -> dict:
        try:
            import yaml
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f) or {}
        except:
            pass
        return {}
    
    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 600, 500)
        
        layout = QFormLayout()
        
        # API Keys
        layout.addRow(QLabel("<b>API Keys</b>"))
        
        self.nvd_key = QLineEdit()
        self.nvd_key.setText(self.config.get('feeds', {}).get('nvd', {}).get('api_key', ''))
        self.nvd_key.setEchoMode(QLineEdit.Password)
        layout.addRow("NVD API Key:", self.nvd_key)
        
        self.hibp_key = QLineEdit()
        self.hibp_key.setText(self.config.get('feeds', {}).get('haveibeenpwned', {}).get('api_key', ''))
        self.hibp_key.setEchoMode(QLineEdit.Password)
        layout.addRow("HaveIBeenPwned Key:", self.hibp_key)
        
        self.abuseipdb_key = QLineEdit()
        self.abuseipdb_key.setText(self.config.get('feeds', {}).get('abuseipdb', {}).get('api_key', ''))
        self.abuseipdb_key.setEchoMode(QLineEdit.Password)
        layout.addRow("AbuseIPDB Key:", self.abuseipdb_key)
        
        # Monitored emails
        layout.addRow(QLabel("<b>Monitoring</b>"))
        
        self.monitored_emails = QTextEdit()
        emails = self.config.get('monitored', {}).get('emails', [])
        self.monitored_emails.setPlainText('\n'.join(emails))
        self.monitored_emails.setMaximumHeight(80)
        layout.addRow("Emails to monitor:", self.monitored_emails)
        
        self.monitored_domains = QTextEdit()
        domains = self.config.get('monitored', {}).get('domains', [])
        self.monitored_domains.setPlainText('\n'.join(domains))
        self.monitored_domains.setMaximumHeight(80)
        layout.addRow("Domains to monitor:", self.monitored_domains)
        
        # Alert settings
        layout.addRow(QLabel("<b>Alerts</b>"))
        
        self.alert_severity = QComboBox()
        self.alert_severity.addItems(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'])
        severity = self.config.get('alerts', {}).get('email', {}).get('min_severity', 'MEDIUM')
        self.alert_severity.setCurrentText(severity)
        layout.addRow("Alert severity level:", self.alert_severity)
        
        self.enable_email = QCheckBox("Enable email alerts")
        self.enable_email.setChecked(self.config.get('alerts', {}).get('email', {}).get('enabled', False))
        layout.addRow("Email Alerts:", self.enable_email)
        
        self.email_to = QLineEdit()
        self.email_to.setText(', '.join(self.config.get('alerts', {}).get('email', {}).get('to', [])))
        layout.addRow("Email address:", self.email_to)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addRow(button_layout)
        self.setLayout(layout)
    
    def save_settings(self):
        # Update config
        if not self.config.get('feeds'):
            self.config['feeds'] = {}
        
        self.config['feeds']['nvd'] = {'api_key': self.nvd_key.text(), 'enabled': True}
        self.config['feeds']['haveibeenpwned'] = {'api_key': self.hibp_key.text(), 'enabled': True}
        self.config['feeds']['abuseipdb'] = {'api_key': self.abuseipdb_key.text(), 'enabled': True}
        
        self.config['monitored'] = {
            'emails': [e.strip() for e in self.monitored_emails.toPlainText().split('\n') if e.strip()],
            'domains': [d.strip() for d in self.monitored_domains.toPlainText().split('\n') if d.strip()]
        }
        
        if not self.config.get('alerts'):
            self.config['alerts'] = {}
        self.config['alerts']['email'] = {
            'enabled': self.enable_email.isChecked(),
            'min_severity': self.alert_severity.currentText(),
            'to': [e.strip() for e in self.email_to.text().split(',')]
        }
        
        # Save to file
        try:
            import yaml
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f)
            QMessageBox.information(self, "Success", "Settings saved!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")


class ThreatIntelDailyGUI(QMainWindow):
    """Main GUI window for ThreatIntel Daily"""
    
    def __init__(self, config_path: str = "config.yml"):
        super().__init__()
        self.config_path = Path(config_path)
        self.db = ThreatDatabase()
        self.app = None
        self.fetch_worker = None
        self.fetch_timer = QTimer()
        self.fetch_timer.timeout.connect(self.start_fetch)
        
        self.init_ui()
        self.setup_tray()
        self.setWindowTitle("ThreatIntel Daily")
        self.setGeometry(100, 100, 1200, 700)
    
    def init_ui(self):
        """Initialize the UI"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Top bar
        top_layout = QHBoxLayout()
        
        status_label = QLabel("Status: Ready")
        self.status_label = status_label
        top_layout.addWidget(status_label)
        
        fetch_btn = QPushButton("🔄 Fetch Now")
        fetch_btn.clicked.connect(self.start_fetch)
        top_layout.addWidget(fetch_btn)
        
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(settings_btn)
        
        about_btn = QPushButton("ℹ️ About")
        about_btn.clicked.connect(self.show_about)
        top_layout.addWidget(about_btn)
        
        layout.addLayout(top_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Tabs
        tabs = QTabWidget()
        
        # Dashboard tab
        tabs.addTab(self.create_dashboard_tab(), "📊 Dashboard")
        
        # Threats tab
        tabs.addTab(self.create_threats_tab(), "⚠️ Threats")
        
        # Statistics tab
        tabs.addTab(self.create_stats_tab(), "📈 Statistics")
        
        layout.addWidget(tabs)
    
    def create_dashboard_tab(self) -> QWidget:
        """Create dashboard tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Stats boxes
        stats_layout = QHBoxLayout()
        
        # Total threats
        self.threats_label = QLabel("Total Threats: 0")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.threats_label.setFont(font)
        stats_layout.addWidget(self.threats_label)
        
        # Critical threats
        self.critical_label = QLabel("Critical: 0")
        self.critical_label.setFont(font)
        self.critical_label.setStyleSheet("color: red;")
        stats_layout.addWidget(self.critical_label)
        
        # High threats
        self.high_label = QLabel("High: 0")
        self.high_label.setFont(font)
        self.high_label.setStyleSheet("color: orange;")
        stats_layout.addWidget(self.high_label)
        
        layout.addLayout(stats_layout)
        
        # Recent threats
        layout.addWidget(QLabel("Recent Threats:"))
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(5)
        self.recent_table.setHorizontalHeaderLabels(['ID', 'Type', 'Severity', 'Source', 'Time'])
        self.recent_table.setColumnWidth(0, 250)
        self.recent_table.setColumnWidth(1, 150)
        self.recent_table.setColumnWidth(2, 100)
        self.recent_table.setColumnWidth(3, 100)
        layout.addWidget(self.recent_table)
        
        self.refresh_dashboard()
        
        return widget
    
    def create_threats_tab(self) -> QWidget:
        """Create threats list tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(['All', 'CVE', 'CREDENTIAL_BREACH', 'MALICIOUS_IP', 'MALWARE_URL'])
        self.type_filter.currentTextChanged.connect(self.refresh_threats)
        filter_layout.addWidget(self.type_filter)
        
        filter_layout.addWidget(QLabel("Severity:"))
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(['All', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'])
        self.severity_filter.currentTextChanged.connect(self.refresh_threats)
        filter_layout.addWidget(self.severity_filter)
        
        filter_layout.addWidget(QLabel("Days:"))
        self.days_filter = QSpinBox()
        self.days_filter.setValue(7)
        self.days_filter.setMinimum(1)
        self.days_filter.setMaximum(365)
        self.days_filter.valueChanged.connect(self.refresh_threats)
        filter_layout.addWidget(self.days_filter)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Threats table
        self.threats_table = QTableWidget()
        self.threats_table.setColumnCount(6)
        self.threats_table.setHorizontalHeaderLabels(['ID', 'Type', 'Severity', 'Title', 'Source', 'Date'])
        self.threats_table.setColumnWidth(0, 200)
        self.threats_table.setColumnWidth(1, 150)
        self.threats_table.setColumnWidth(2, 100)
        self.threats_table.setColumnWidth(3, 300)
        self.threats_table.itemDoubleClicked.connect(self.show_threat_details)
        layout.addWidget(self.threats_table)
        
        self.refresh_threats()
        
        return widget
    
    def create_stats_tab(self) -> QWidget:
        """Create statistics tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)
        
        self.refresh_stats()
        
        return widget
    
    def refresh_dashboard(self):
        """Refresh dashboard stats"""
        threats = self.db.list_threats(limit=100)
        
        total = len(threats)
        critical = sum(1 for t in threats if t.severity == ThreatSeverity.CRITICAL)
        high = sum(1 for t in threats if t.severity == ThreatSeverity.HIGH)
        
        self.threats_label.setText(f"Total Threats: {total}")
        self.critical_label.setText(f"Critical: {critical}")
        self.high_label.setText(f"High: {high}")
        
        # Recent threats
        self.recent_table.setRowCount(0)
        for i, threat in enumerate(threats[:10]):
            self.recent_table.insertRow(i)
            self.recent_table.setItem(i, 0, QTableWidgetItem(threat.id))
            self.recent_table.setItem(i, 1, QTableWidgetItem(threat.threat_type.value))
            self.recent_table.setItem(i, 2, QTableWidgetItem(threat.severity.value))
            self.recent_table.setItem(i, 3, QTableWidgetItem(threat.source))
            self.recent_table.setItem(i, 4, QTableWidgetItem(threat.discovered_at.strftime('%Y-%m-%d')))
    
    def refresh_threats(self):
        """Refresh threats list based on filters"""
        threat_type = self.type_filter.currentText()
        severity = self.severity_filter.currentText()
        days = self.days_filter.value()
        
        threat_type_enum = None if threat_type == 'All' else ThreatType(threat_type)
        severity_enum = None if severity == 'All' else ThreatSeverity(severity)
        
        since = datetime.utcnow() - timedelta(days=days)
        
        threats = self.db.list_threats(
            threat_type=threat_type_enum,
            severity=severity_enum,
            since=since,
            limit=1000
        )
        
        self.threats_table.setRowCount(0)
        for i, threat in enumerate(threats):
            self.threats_table.insertRow(i)
            self.threats_table.setItem(i, 0, QTableWidgetItem(threat.id))
            self.threats_table.setItem(i, 1, QTableWidgetItem(threat.threat_type.value))
            self.threats_table.setItem(i, 2, QTableWidgetItem(threat.severity.value))
            self.threats_table.setItem(i, 3, QTableWidgetItem(threat.title[:80]))
            self.threats_table.setItem(i, 4, QTableWidgetItem(threat.source))
            self.threats_table.setItem(i, 5, QTableWidgetItem(threat.discovered_at.strftime('%Y-%m-%d')))
    
    def refresh_stats(self):
        """Refresh statistics"""
        threats = self.db.list_threats(limit=10000)
        
        stats = "📊 Threat Statistics (All Time)\n\n"
        
        # By type
        by_type = {}
        by_severity = {}
        by_source = {}
        
        for threat in threats:
            by_type[threat.threat_type.value] = by_type.get(threat.threat_type.value, 0) + 1
            by_severity[threat.severity.value] = by_severity.get(threat.severity.value, 0) + 1
            by_source[threat.source] = by_source.get(threat.source, 0) + 1
        
        stats += "By Type:\n"
        for t_type in sorted(by_type.keys()):
            stats += f"  {t_type}: {by_type[t_type]}\n"
        
        stats += "\nBy Severity:\n"
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if severity in by_severity:
                stats += f"  {severity}: {by_severity[severity]}\n"
        
        stats += "\nBy Source:\n"
        for source in sorted(by_source.keys()):
            stats += f"  {source}: {by_source[source]}\n"
        
        stats += f"\nTotal: {len(threats)} threats\n"
        
        self.stats_text.setText(stats)
    
    def show_threat_details(self, item):
        """Show detailed threat information"""
        row = self.threats_table.row(item)
        threat_id = self.threats_table.item(row, 0).text()
        
        threat = self.db.get_threat(threat_id)
        if not threat:
            return
        
        details = f"""
        ID: {threat.id}
        Type: {threat.threat_type.value}
        Severity: {threat.severity.value}
        Title: {threat.title}
        
        Description:
        {threat.description}
        
        Source: {threat.source}
        Confidence: {int(threat.confidence_score * 100)}%
        Discovered: {threat.discovered_at.isoformat()}
        
        Affected:
        - Emails: {', '.join(threat.affected_emails) if threat.affected_emails else 'None'}
        - Domains: {', '.join(threat.affected_domains) if threat.affected_domains else 'None'}
        - IPs: {', '.join(threat.affected_ips) if threat.affected_ips else 'None'}
        
        References:
        {chr(10).join(threat.references[:5]) if threat.references else 'None'}
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle(f"Threat Details: {threat_id}")
        msg.setText(details)
        msg.setFont(QFont("Courier", 9))
        msg.exec_()
    
    def start_fetch(self):
        """Start fetching threats in background"""
        self.status_label.setText("Status: Fetching...")
        self.progress.setVisible(True)
        
        self.fetch_worker = ThreatFetchWorker(self.app)
        self.fetch_worker.progress.connect(self.update_status)
        self.fetch_worker.finished.connect(self.fetch_finished)
        self.fetch_worker.start()
    
    def update_status(self, message: str):
        """Update status message"""
        self.status_label.setText(f"Status: {message}")
    
    def fetch_finished(self, new_threats: int, errors: int):
        """Handle fetch completion"""
        self.progress.setVisible(False)
        if errors > 0:
            self.status_label.setText(f"Status: Fetched {new_threats} threats ({errors} errors)")
        else:
            self.status_label.setText(f"Status: Fetched {new_threats} threats ✓")
        
        self.refresh_dashboard()
        self.refresh_threats()
        self.refresh_stats()
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(str(self.config_path), self)
        dialog.exec_()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About ThreatIntel Daily",
            """
            ThreatIntel Daily v0.1.0
            
            Personal threat intelligence aggregator
            for security professionals
            
            Monitors multiple threat intelligence feeds:
            - CVE Database (NVD)
            - Breach Database (HaveIBeenPwned)
            - Malicious IPs (AbuseIPDB)
            - Malware URLs (URLhaus)
            
            © 2024 Alphonse
            MIT License
            """
        )
    
    def setup_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        tray_menu.addSeparator()
        
        fetch_action = tray_menu.addAction("Fetch Threats")
        fetch_action.triggered.connect(self.start_fetch)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def closeEvent(self, event):
        """Handle window close - minimize to tray instead"""
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Create window
    window = ThreatIntelDailyGUI()
    
    # Initialize threat intel app (without scheduler)
    try:
        window.app = ThreatIntelDaily()
    except Exception as e:
        print(f"Warning: Could not initialize threat feeds: {e}")
    
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
