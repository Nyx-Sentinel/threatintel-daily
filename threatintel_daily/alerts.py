"""Alert delivery via email, webhooks, and dashboard"""

import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional
from threatintel_daily import Threat, Alert, AlertStatus, AlertException

class AlertDelivery:
    """Base class for alert delivery"""
    
    def send(self, threat: Threat) -> bool:
        """Send alert for a threat"""
        raise NotImplementedError

class EmailAlertDelivery(AlertDelivery):
    """Send alerts via SMTP email"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        sender_email: str,
        recipient_emails: List[str],
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email
        self.recipient_emails = recipient_emails
        self.use_tls = use_tls
    
    def send(self, threat: Threat) -> bool:
        """Send email alert"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{threat.severity.value}] ThreatIntel Alert: {threat.title}"
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipient_emails)
            
            # HTML body
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px;">
                  <h2 style="color: {self._severity_color(threat.severity)};">
                    {threat.severity.value} - {threat.threat_type.value}
                  </h2>
                  
                  <h3>{threat.title}</h3>
                  
                  <p><strong>Description:</strong><br/>{threat.description}</p>
                  
                  <div style="background-color: #fff; padding: 15px; border-left: 4px solid {self._severity_color(threat.severity)}; margin: 15px 0;">
                    <p><strong>Source:</strong> {threat.source}</p>
                    <p><strong>Confidence:</strong> {int(threat.confidence_score * 100)}%</p>
                    <p><strong>Discovered:</strong> {threat.discovered_at.isoformat()}</p>
                    
                    {self._format_affected(threat)}
                  </div>
                  
                  {self._format_references(threat)}
                  
                  <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    This is an automated alert from ThreatIntel Daily
                  </p>
                </div>
              </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send
            if self.use_tls:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            
            return True
        
        except Exception as e:
            raise AlertException(f"Failed to send email alert: {e}")
    
    @staticmethod
    def _severity_color(severity) -> str:
        """Get color for severity level"""
        colors = {
            'CRITICAL': '#d32f2f',
            'HIGH': '#f57c00',
            'MEDIUM': '#fbc02d',
            'LOW': '#388e3c',
            'INFO': '#1976d2'
        }
        return colors.get(severity.value, '#666')
    
    @staticmethod
    def _format_affected(threat: Threat) -> str:
        """Format affected entities"""
        html = ""
        if threat.affected_emails:
            html += f"<p><strong>Affected Emails:</strong> {', '.join(threat.affected_emails)}</p>"
        if threat.affected_domains:
            html += f"<p><strong>Affected Domains:</strong> {', '.join(threat.affected_domains)}</p>"
        if threat.affected_ips:
            html += f"<p><strong>Affected IPs:</strong> {', '.join(threat.affected_ips)}</p>"
        if threat.affected_services:
            html += f"<p><strong>Affected Services:</strong> {', '.join(threat.affected_services)}</p>"
        if threat.affected_urls:
            html += f"<p><strong>Affected URLs:</strong><br/>"
            for url in threat.affected_urls[:5]:
                html += f"{url}<br/>"
            html += "</p>"
        return html
    
    @staticmethod
    def _format_references(threat: Threat) -> str:
        """Format reference links"""
        if not threat.references:
            return ""
        
        html = "<p><strong>References:</strong></p><ul>"
        for ref in threat.references[:5]:
            html += f"<li><a href='{ref}' style='color: #1976d2;'>{ref[:80]}</a></li>"
        html += "</ul>"
        return html

class WebhookAlertDelivery(AlertDelivery):
    """Send alerts via webhook (Slack, Teams, Discord, custom)"""
    
    def __init__(self, webhook_url: str, service: str = 'custom'):
        self.webhook_url = webhook_url
        self.service = service  # slack, teams, discord, custom
    
    def send(self, threat: Threat) -> bool:
        """Send webhook alert"""
        try:
            if self.service == 'slack':
                payload = self._slack_payload(threat)
            elif self.service == 'teams':
                payload = self._teams_payload(threat)
            elif self.service == 'discord':
                payload = self._discord_payload(threat)
            else:
                payload = self._custom_payload(threat)
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        
        except Exception as e:
            raise AlertException(f"Failed to send webhook alert: {e}")
    
    @staticmethod
    def _slack_payload(threat: Threat) -> dict:
        """Format payload for Slack"""
        color_map = {
            'CRITICAL': '#d32f2f',
            'HIGH': '#f57c00',
            'MEDIUM': '#fbc02d',
            'LOW': '#388e3c',
            'INFO': '#1976d2'
        }
        
        fields = [
            {"title": "Type", "value": threat.threat_type.value, "short": True},
            {"title": "Source", "value": threat.source, "short": True},
            {"title": "Confidence", "value": f"{int(threat.confidence_score * 100)}%", "short": True},
        ]
        
        if threat.affected_emails:
            fields.append({"title": "Emails", "value": ', '.join(threat.affected_emails), "short": False})
        if threat.affected_domains:
            fields.append({"title": "Domains", "value": ', '.join(threat.affected_domains), "short": False})
        if threat.affected_ips:
            fields.append({"title": "IPs", "value": ', '.join(threat.affected_ips), "short": False})
        
        return {
            "attachments": [{
                "color": color_map.get(threat.severity.value, "#666"),
                "title": threat.title,
                "text": threat.description,
                "fields": fields,
                "footer": "ThreatIntel Daily",
                "ts": int(datetime.utcnow().timestamp())
            }]
        }
    
    @staticmethod
    def _teams_payload(threat: Threat) -> dict:
        """Format payload for Microsoft Teams"""
        color_map = {
            'CRITICAL': 'e81828',
            'HIGH': 'ff8c00',
            'MEDIUM': 'ffd700',
            'LOW': '4caf50',
            'INFO': '2196f3'
        }
        
        facts = [
            {"name": "Type", "value": threat.threat_type.value},
            {"name": "Source", "value": threat.source},
            {"name": "Confidence", "value": f"{int(threat.confidence_score * 100)}%"},
            {"name": "Discovered", "value": threat.discovered_at.isoformat()},
        ]
        
        if threat.affected_emails:
            facts.append({"name": "Emails", "value": ', '.join(threat.affected_emails)})
        if threat.affected_domains:
            facts.append({"name": "Domains", "value": ', '.join(threat.affected_domains)})
        
        return {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": threat.title,
            "themeColor": color_map.get(threat.severity.value, "666666"),
            "sections": [{
                "activityTitle": threat.title,
                "activitySubtitle": threat.severity.value,
                "text": threat.description,
                "facts": facts
            }]
        }
    
    @staticmethod
    def _discord_payload(threat: Threat) -> dict:
        """Format payload for Discord"""
        color_map = {
            'CRITICAL': 0xd32f2f,
            'HIGH': 0xf57c00,
            'MEDIUM': 0xfbc02d,
            'LOW': 0x388e3c,
            'INFO': 0x1976d2
        }
        
        fields = [
            {"name": "Type", "value": threat.threat_type.value, "inline": True},
            {"name": "Source", "value": threat.source, "inline": True},
            {"name": "Confidence", "value": f"{int(threat.confidence_score * 100)}%", "inline": True},
        ]
        
        if threat.affected_emails:
            fields.append({"name": "Emails", "value": ', '.join(threat.affected_emails), "inline": False})
        if threat.affected_domains:
            fields.append({"name": "Domains", "value": ', '.join(threat.affected_domains), "inline": False})
        if threat.affected_ips:
            fields.append({"name": "IPs", "value": ', '.join(threat.affected_ips), "inline": False})
        
        return {
            "embeds": [{
                "title": threat.title,
                "description": threat.description,
                "color": color_map.get(threat.severity.value, 0x666666),
                "fields": fields,
                "footer": {"text": "ThreatIntel Daily"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
    
    @staticmethod
    def _custom_payload(threat: Threat) -> dict:
        """Generic JSON payload"""
        return threat.to_dict()

class AlertManager:
    """Manages alert delivery across multiple channels"""
    
    def __init__(self):
        self.deliveries: List[AlertDelivery] = []
    
    def register_delivery(self, delivery: AlertDelivery):
        """Register an alert delivery method"""
        self.deliveries.append(delivery)
    
    def send_alert(self, threat: Threat) -> bool:
        """Send alert through all registered channels"""
        success_count = 0
        
        for delivery in self.deliveries:
            try:
                if delivery.send(threat):
                    success_count += 1
            except Exception as e:
                print(f"Alert delivery failed: {e}")
        
        return success_count > 0
