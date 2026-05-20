"""Threat intelligence feed integrations"""

import requests
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from threatintel_daily import (
    Threat, ThreatType, ThreatSeverity, FeedException, parse_severity
)

class ThreatFeed:
    """Base class for threat feeds"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.name = self.__class__.__name__
    
    def fetch(self) -> List[Threat]:
        """Fetch threats from this feed. Override in subclasses."""
        raise NotImplementedError
    
    def _make_request(self, url: str, headers: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with error handling"""
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise FeedException(f"{self.name} request failed: {e}")

class NVDFeed(ThreatFeed):
    """National Vulnerability Database (CVE) feed"""
    
    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    
    def __init__(self, api_key: str = None, min_severity: str = "HIGH"):
        super().__init__(api_key)
        self.min_severity = parse_severity(min_severity)
    
    def fetch(self) -> List[Threat]:
        """Fetch recent CVEs from NVD"""
        threats = []
        try:
            # Fetch last 100 modified CVEs
            headers = {}
            if self.api_key:
                headers['apiKey'] = self.api_key
            
            # This is simplified - real implementation would paginate
            params = {
                'resultsPerPage': 100,
                'sortBy': 'LAST_UPDATE'
            }
            
            data = self._make_request(self.BASE_URL, headers=headers, params=params)
            
            for vuln in data.get('vulnerabilities', []):
                cve = vuln.get('cve', {})
                metrics = vuln.get('cve', {}).get('metrics', {})
                
                # Extract CVSS severity
                severity_str = 'MEDIUM'
                if 'cvssV31' in metrics:
                    score = metrics['cvssV31'].get('baseScore', 5.0)
                    severity_str = self._score_to_severity(score)
                
                threat = Threat(
                    id=cve.get('id', 'unknown'),
                    threat_type=ThreatType.CVE,
                    severity=parse_severity(severity_str),
                    title=cve.get('descriptions', [{}])[0].get('value', 'CVE'),
                    description=cve.get('descriptions', [{}])[0].get('value', ''),
                    source='nvd',
                    discovered_at=datetime.utcnow(),
                    published_at=datetime.fromisoformat(
                        cve.get('published', '2024-01-01').replace('Z', '+00:00')
                    ) if cve.get('published') else None,
                    last_seen_at=datetime.utcnow(),
                    affected_services=[],
                    references=cve.get('references', []),
                    metadata=cve,
                    confidence_score=1.0
                )
                
                threats.append(threat)
        
        except Exception as e:
            raise FeedException(f"Failed to fetch NVD data: {e}")
        
        return threats
    
    @staticmethod
    def _score_to_severity(score: float) -> str:
        """Convert CVSS score to severity"""
        if score >= 9.0:
            return 'CRITICAL'
        elif score >= 7.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        else:
            return 'LOW'

class HaveIBeenPwnedFeed(ThreatFeed):
    """HaveIBeenPwned breach database feed"""
    
    BASE_URL = "https://haveibeenpwned.com/api/v3"
    
    def __init__(self, api_key: str, monitored_emails: List[str] = None):
        super().__init__(api_key)
        self.monitored_emails = monitored_emails or []
    
    def fetch(self) -> List[Threat]:
        """Check if monitored emails appear in breaches"""
        threats = []
        
        if not self.monitored_emails:
            return threats
        
        headers = {
            'User-Agent': 'ThreatIntel-Daily',
            'Accept': 'application/json'
        }
        
        for email in self.monitored_emails:
            try:
                # Check if email was in a breach
                url = f"{self.BASE_URL}/breachedaccount/{email}"
                response = requests.get(url, headers=headers, timeout=2)
                
                if response.status_code == 404:
                    continue  # Not in any breach
                
                elif response.status_code == 200:
                    breaches = response.json()
                    for breach in breaches:
                        threat = Threat(
                            id=f"HIBP-{breach['Name']}-{email}",
                            threat_type=ThreatType.CREDENTIAL_BREACH,
                            severity=ThreatSeverity.HIGH,
                            title=f"Email found in {breach['Name']} breach",
                            description=f"{email} was exposed in the {breach['Name']} breach. "
                                       f"{breach.get('Title', '')}",
                            source='haveibeenpwned',
                            discovered_at=datetime.fromisoformat(
                                breach['BreachDate'] + 'T00:00:00'
                            ),
                            published_at=None,
                            last_seen_at=datetime.utcnow(),
                            affected_emails=[email],
                            references=[f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"],
                            metadata=breach,
                            confidence_score=1.0
                        )
                        threats.append(threat)
                
                elif response.status_code == 401:
                    raise FeedException("HaveIBeenPwned API key invalid")
            
            except Exception as e:
                raise FeedException(f"Failed to check {email} in HaveIBeenPwned: {e}")
        
        return threats

class AbuseIPDBFeed(ThreatFeed):
    """AbuseIPDB malicious IP reputation feed"""
    
    BASE_URL = "https://api.abuseipdb.com/api/v2/check"
    
    def __init__(self, api_key: str, monitored_ips: List[str] = None, min_confidence: int = 75):
        super().__init__(api_key)
        self.monitored_ips = monitored_ips or []
        self.min_confidence = min_confidence
    
    def fetch(self) -> List[Threat]:
        """Check reputation of monitored IPs"""
        threats = []
        
        if not self.monitored_ips or not self.api_key:
            return threats
        
        headers = {
            'Key': self.api_key,
            'Accept': 'application/json'
        }
        
        for ip in self.monitored_ips:
            try:
                params = {'ipAddress': ip, 'maxAgeInDays': 90}
                response = requests.get(self.BASE_URL, headers=headers, params=params, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                abuse_data = data.get('data', {})
                confidence = abuse_data.get('abuseConfidenceScore', 0)
                
                if confidence >= self.min_confidence:
                    threat = Threat(
                        id=f"ABUSEIPDB-{ip}",
                        threat_type=ThreatType.MALICIOUS_IP,
                        severity=self._confidence_to_severity(confidence),
                        title=f"Malicious IP detected: {ip}",
                        description=f"IP {ip} has a confidence score of {confidence}%. "
                                   f"Total reports: {abuse_data.get('totalReports', 0)}",
                        source='abuseipdb',
                        discovered_at=datetime.utcnow(),
                        published_at=None,
                        last_seen_at=datetime.utcnow(),
                        affected_ips=[ip],
                        metadata=abuse_data,
                        references=[f"https://www.abuseipdb.com/check/{ip}"],
                        confidence_score=confidence / 100.0
                    )
                    threats.append(threat)
            
            except Exception as e:
                raise FeedException(f"Failed to check {ip} in AbuseIPDB: {e}")
        
        return threats
    
    @staticmethod
    def _confidence_to_severity(confidence: int) -> ThreatSeverity:
        """Convert confidence score to severity"""
        if confidence >= 90:
            return ThreatSeverity.CRITICAL
        elif confidence >= 75:
            return ThreatSeverity.HIGH
        elif confidence >= 50:
            return ThreatSeverity.MEDIUM
        else:
            return ThreatSeverity.LOW

class URLhausFeed(ThreatFeed):
    """URLhaus malware URL feed"""
    
    BASE_URL = "https://urlhaus-api.abuse.ch/v1/urls/recent/"
    
    def fetch(self) -> List[Threat]:
        """Fetch recent malware URLs"""
        threats = []
        
        try:
            data = self._make_request(self.BASE_URL)
            
            for url_record in data.get('urls', [])[:50]:  # Last 50 URLs
                threat = Threat(
                    id=f"URLhaus-{url_record['id']}",
                    threat_type=ThreatType.MALWARE_URL,
                    severity=ThreatSeverity.HIGH,
                    title=f"Malware URL detected: {url_record['url'][:60]}",
                    description=f"Hosting malware: {', '.join(url_record.get('tags', []))}. "
                               f"Status: {url_record.get('url_status', 'unknown')}",
                    source='urlhaus',
                    discovered_at=datetime.fromisoformat(
                        url_record.get('date_submitted', '2024-01-01')
                    ),
                    published_at=None,
                    last_seen_at=datetime.utcnow(),
                    affected_urls=[url_record['url']],
                    metadata=url_record,
                    references=[f"https://urlhaus.abuse.ch/url/{url_record['id']}/"],
                    confidence_score=1.0
                )
                threats.append(threat)
        
        except Exception as e:
            raise FeedException(f"Failed to fetch URLhaus data: {e}")
        
        return threats

class FeedAggregator:
    """Aggregates multiple threat feeds"""
    
    def __init__(self):
        self.feeds: Dict[str, ThreatFeed] = {}
    
    def register_feed(self, feed: ThreatFeed):
        """Register a feed"""
        self.feeds[feed.name] = feed
    
    def fetch_all(self) -> tuple[List[Threat], Dict[str, Exception]]:
        """Fetch from all registered feeds"""
        threats = []
        errors = {}
        
        for feed_name, feed in self.feeds.items():
            try:
                feed_threats = feed.fetch()
                threats.extend(feed_threats)
            except Exception as e:
                errors[feed_name] = e
        
        return threats, errors
