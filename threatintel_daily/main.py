"""Main application orchestrator and scheduler"""

import yaml
import logging
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from threatintel_daily.database import ThreatDatabase
from threatintel_daily.feeds import (
    FeedAggregator, NVDFeed, HaveIBeenPwnedFeed, AbuseIPDBFeed, URLhausFeed
)
from threatintel_daily.alerts import AlertManager, EmailAlertDelivery, WebhookAlertDelivery
from threatintel_daily import is_severity_match

class ThreatIntelDaily:
    """Main application class"""
    
    def __init__(self, config_path: str = "config.yml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.db = ThreatDatabase(self.config.get('app', {}).get('database_path', './data/threatintel.db'))
        self.feed_aggregator = FeedAggregator()
        self.alert_manager = AlertManager()
        self.scheduler = BackgroundScheduler()
        
        self._initialize_feeds()
        self._initialize_alerts()
    
    def _load_config(self) -> dict:
        """Load configuration from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise Exception(f"Invalid YAML in config: {e}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger('threatintel-daily')
        level_str = self.config.get('app', {}).get('log_level', 'INFO')
        logger.setLevel(getattr(logging, level_str))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level_str))
        
        # File handler
        log_dir = Path(self.config.get('logging', {}).get('file', './logs/threatintel-daily.log')).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(self.config.get('logging', {}).get('file'))
        file_handler.setLevel(getattr(logging, level_str))
        
        # Formatter
        formatter = logging.Formatter(
            self.config.get('logging', {}).get('format',
                                               '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def _initialize_feeds(self):
        """Initialize threat feeds from config"""
        feeds_config = self.config.get('feeds', {})
        
        # NVD
        if feeds_config.get('nvd', {}).get('enabled'):
            feed = NVDFeed(
                api_key=feeds_config['nvd'].get('api_key'),
                min_severity=feeds_config['nvd'].get('min_severity', 'HIGH')
            )
            self.feed_aggregator.register_feed(feed)
            self.logger.info("Registered NVD feed")
        
        # HaveIBeenPwned
        if feeds_config.get('haveibeenpwned', {}).get('enabled'):
            monitored = self.config.get('monitored', {})
            feed = HaveIBeenPwnedFeed(
                api_key=feeds_config['haveibeenpwned'].get('api_key'),
                monitored_emails=monitored.get('emails', [])
            )
            self.feed_aggregator.register_feed(feed)
            self.logger.info("Registered HaveIBeenPwned feed")
        
        # AbuseIPDB
        if feeds_config.get('abuseipdb', {}).get('enabled'):
            monitored = self.config.get('monitored', {})
            feed = AbuseIPDBFeed(
                api_key=feeds_config['abuseipdb'].get('api_key'),
                monitored_ips=monitored.get('ips', []),
                min_confidence=feeds_config['abuseipdb'].get('min_confidence', 75)
            )
            self.feed_aggregator.register_feed(feed)
            self.logger.info("Registered AbuseIPDB feed")
        
        # URLhaus
        if feeds_config.get('urlhaus', {}).get('enabled'):
            feed = URLhausFeed()
            self.feed_aggregator.register_feed(feed)
            self.logger.info("Registered URLhaus feed")
    
    def _initialize_alerts(self):
        """Initialize alert delivery from config"""
        alerts_config = self.config.get('alerts', {})
        
        # Email
        if alerts_config.get('email', {}).get('enabled'):
            email_cfg = alerts_config['email']
            smtp_cfg = email_cfg.get('smtp', {})
            delivery = EmailAlertDelivery(
                smtp_server=smtp_cfg.get('server', 'smtp.gmail.com'),
                smtp_port=smtp_cfg.get('port', 587),
                username=smtp_cfg.get('username'),
                password=smtp_cfg.get('password'),
                sender_email=email_cfg.get('from'),
                recipient_emails=email_cfg.get('to', []),
                use_tls=smtp_cfg.get('use_tls', True)
            )
            self.alert_manager.register_delivery(delivery)
            self.logger.info("Registered email alert delivery")
        
        # Webhook
        if alerts_config.get('webhook', {}).get('enabled'):
            webhook_cfg = alerts_config['webhook']
            if webhook_cfg.get('slack', {}).get('enabled'):
                delivery = WebhookAlertDelivery(
                    webhook_url=webhook_cfg['slack'].get('webhook_url'),
                    service='slack'
                )
                self.alert_manager.register_delivery(delivery)
                self.logger.info("Registered Slack webhook alert delivery")
            
            if webhook_cfg.get('teams', {}).get('enabled'):
                delivery = WebhookAlertDelivery(
                    webhook_url=webhook_cfg['teams'].get('webhook_url'),
                    service='teams'
                )
                self.alert_manager.register_delivery(delivery)
                self.logger.info("Registered Teams webhook alert delivery")
            
            if webhook_cfg.get('discord', {}).get('enabled'):
                delivery = WebhookAlertDelivery(
                    webhook_url=webhook_cfg['discord'].get('webhook_url'),
                    service='discord'
                )
                self.alert_manager.register_delivery(delivery)
                self.logger.info("Registered Discord webhook alert delivery")
    
    def fetch_threats(self):
        """Fetch threats from all configured feeds"""
        self.logger.info("Starting threat fetch cycle")
        
        try:
            threats, errors = self.feed_aggregator.fetch_all()
            
            if errors:
                for feed_name, error in errors.items():
                    self.logger.error(f"Error fetching from {feed_name}: {error}")
            
            # Store threats and check for alerts
            alert_config = self.config.get('alerts', {})
            min_severity = alert_config.get('email', {}).get('min_severity', 'MEDIUM')
            
            for threat in threats:
                # Check if already in database
                existing = self.db.get_threat(threat.id)
                
                if not existing:
                    # New threat
                    self.db.insert_threat(threat)
                    
                    # Send alert if severity threshold met
                    if is_severity_match(threat.severity, min_severity):
                        self.logger.info(f"Sending alert for {threat.id}")
                        try:
                            self.alert_manager.send_alert(threat)
                        except Exception as e:
                            self.logger.error(f"Failed to send alert: {e}")
                else:
                    # Update last_seen
                    existing.last_seen_at = datetime.utcnow()
                    self.db.insert_threat(existing)
            
            self.logger.info(f"Fetched {len(threats)} threats, {len(errors)} feed errors")
        
        except Exception as e:
            self.logger.error(f"Fatal error during fetch: {e}")
    
    def start(self):
        """Start the scheduler"""
        self.logger.info("Starting ThreatIntel Daily scheduler")
        
        # Schedule periodic threat fetch
        fetch_interval = self.config.get('app', {}).get('fetch_interval', 3600)
        self.scheduler.add_job(
            self.fetch_threats,
            'interval',
            seconds=fetch_interval,
            id='threat-fetch',
            name='Fetch threats from all feeds',
            replace_existing=True
        )
        
        # Schedule database cleanup
        self.scheduler.add_job(
            self.cleanup_old_data,
            'interval',
            seconds=86400,  # Daily
            id='db-cleanup',
            name='Cleanup old threat records',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.logger.info("Scheduler started successfully")
        
        # Run initial fetch
        self.fetch_threats()
        
        # Keep running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def cleanup_old_data(self):
        """Clean up old threat records"""
        retention_days = self.config.get('retention', {}).get('threats_days', 90)
        self.logger.info(f"Cleaning up threats older than {retention_days} days")
        try:
            self.db.cleanup_old_records(retention_days)
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        self.logger.info("Stopping ThreatIntel Daily")
        self.scheduler.shutdown()

if __name__ == '__main__':
    app = ThreatIntelDaily()
    app.start()
