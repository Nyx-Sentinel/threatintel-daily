"""Command-line interface for ThreatIntel Daily"""

import click
import json
from datetime import datetime, timedelta
from threatintel_daily.database import ThreatDatabase
from threatintel_daily.main import ThreatIntelDaily
from threatintel_daily import ThreatType, ThreatSeverity, AlertStatus

@click.group()
def cli():
    """ThreatIntel Daily - Personal threat intelligence aggregator"""
    pass

@cli.command()
@click.option('--config', default='config.yml', help='Configuration file path')
def run(config):
    """Run the threat intelligence aggregator"""
    app = ThreatIntelDaily(config)
    app.start()

@cli.command()
@click.option('--config', default='config.yml', help='Configuration file path')
def check_all(config):
    """Run a single fetch cycle from all feeds"""
    app = ThreatIntelDaily(config)
    app.fetch_threats()
    click.echo("✓ Threat fetch completed")

@cli.command()
@click.option('--config', default='config.yml', help='Configuration file path')
@click.option('--db', default='./data/threatintel.db', help='Database path')
@click.option('--type', 'threat_type', help='Filter by threat type (CVE, MALICIOUS_IP, etc.)')
@click.option('--severity', help='Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)')
@click.option('--source', help='Filter by source feed')
@click.option('--since', default='7d', help='Show threats since (e.g., 7d, 24h, 1w)')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json', 'csv']))
def list_threats(config, db, threat_type, severity, source, since, output_format):
    """List threats from database"""
    
    # Parse 'since' parameter
    since_dt = None
    if since.endswith('d'):
        days = int(since[:-1])
        since_dt = datetime.utcnow() - timedelta(days=days)
    elif since.endswith('h'):
        hours = int(since[:-1])
        since_dt = datetime.utcnow() - timedelta(hours=hours)
    elif since.endswith('w'):
        weeks = int(since[:-1])
        since_dt = datetime.utcnow() - timedelta(weeks=weeks)
    
    db_instance = ThreatDatabase(db)
    threats = db_instance.list_threats(
        threat_type=ThreatType(threat_type) if threat_type else None,
        severity=ThreatSeverity(severity) if severity else None,
        source=source,
        since=since_dt,
        limit=1000
    )
    
    if output_format == 'json':
        click.echo(json.dumps([t.to_dict() for t in threats], indent=2, default=str))
    elif output_format == 'csv':
        click.echo("ID,Type,Severity,Title,Source,Discovered,Confidence")
        for threat in threats:
            click.echo(f'"{threat.id}","{threat.threat_type.value}","{threat.severity.value}",'
                      f'"{threat.title}","{threat.source}","{threat.discovered_at.isoformat()}",'
                      f'"{int(threat.confidence_score * 100)}"')
    else:
        # Table format
        click.echo(f"\n{'ID':<40} {'Type':<20} {'Severity':<10} {'Source':<15}")
        click.echo("-" * 85)
        for threat in threats[:50]:
            click.echo(f"{threat.id:<40} {threat.threat_type.value:<20} "
                      f"{threat.severity.value:<10} {threat.source:<15}")
        click.echo(f"\nShowing {min(50, len(threats))} of {len(threats)} threats")

@cli.command()
@click.option('--config', default='config.yml', help='Configuration file path')
@click.option('--db', default='./data/threatintel.db', help='Database path')
@click.option('--threat-id', required=True, help='Threat ID to view')
@click.option('--format', 'output_format', default='pretty', type=click.Choice(['pretty', 'json']))
def show_threat(config, db, threat_id, output_format):
    """Show detailed information about a specific threat"""
    db_instance = ThreatDatabase(db)
    threat = db_instance.get_threat(threat_id)
    
    if not threat:
        click.echo(f"Threat not found: {threat_id}", err=True)
        return
    
    if output_format == 'json':
        click.echo(json.dumps(threat.to_dict(), indent=2, default=str))
    else:
        click.echo(f"\n{'═' * 80}")
        click.echo(f"ID: {threat.id}")
        click.echo(f"Type: {threat.threat_type.value}")
        click.echo(f"Severity: {threat.severity.value}")
        click.echo(f"Title: {threat.title}")
        click.echo(f"{'─' * 80}")
        click.echo(f"\nDescription:\n{threat.description}")
        click.echo(f"\nSource: {threat.source}")
        click.echo(f"Discovered: {threat.discovered_at.isoformat()}")
        click.echo(f"Confidence: {int(threat.confidence_score * 100)}%")
        
        if threat.affected_emails:
            click.echo(f"\nAffected Emails: {', '.join(threat.affected_emails)}")
        if threat.affected_domains:
            click.echo(f"Affected Domains: {', '.join(threat.affected_domains)}")
        if threat.affected_ips:
            click.echo(f"Affected IPs: {', '.join(threat.affected_ips)}")
        if threat.affected_urls:
            click.echo(f"\nAffected URLs:")
            for url in threat.affected_urls:
                click.echo(f"  - {url}")
        
        if threat.references:
            click.echo(f"\nReferences:")
            for ref in threat.references[:5]:
                click.echo(f"  - {ref}")
        
        click.echo(f"\n{'═' * 80}\n")

@cli.command()
@click.option('--db', default='./data/threatintel.db', help='Database path')
@click.option('--days', default=7, help='Number of days to analyze')
def stats(db, days):
    """Show threat statistics"""
    db_instance = ThreatDatabase(db)
    
    since_dt = datetime.utcnow() - timedelta(days=days)
    all_threats = db_instance.list_threats(since=since_dt, limit=10000)
    
    # Count by type
    by_type = {}
    by_severity = {}
    by_source = {}
    
    for threat in all_threats:
        threat_type_str = threat.threat_type.value
        severity_str = threat.severity.value
        source_str = threat.source
        
        by_type[threat_type_str] = by_type.get(threat_type_str, 0) + 1
        by_severity[severity_str] = by_severity.get(severity_str, 0) + 1
        by_source[source_str] = by_source.get(source_str, 0) + 1
    
    click.echo(f"\n📊 Threat Statistics (Last {days} days)\n")
    
    click.echo("By Type:")
    for threat_type in sorted(by_type.keys()):
        count = by_type[threat_type]
        click.echo(f"  {threat_type}: {count}")
    
    click.echo("\nBy Severity:")
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        if severity in by_severity:
            count = by_severity[severity]
            click.echo(f"  {severity}: {count}")
    
    click.echo("\nBy Source:")
    for source in sorted(by_source.keys()):
        count = by_source[source]
        click.echo(f"  {source}: {count}")
    
    click.echo(f"\nTotal: {len(all_threats)} threats\n")

@cli.command()
@click.option('--email', required=True, help='Email address to check')
@click.option('--db', default='./data/threatintel.db', help='Database path')
def check_email(email, db):
    """Check if an email appears in known breaches"""
    db_instance = ThreatDatabase(db)
    threats = db_instance.search_threats(email)
    
    if not threats:
        click.echo(f"✓ No breaches found for {email}")
        return
    
    click.echo(f"\n⚠️  Found {len(threats)} breach(es) for {email}\n")
    for threat in threats:
        click.echo(f"  {threat.title}")
        click.echo(f"    Source: {threat.source}")
        click.echo(f"    Date: {threat.discovered_at.isoformat()}\n")

@cli.command()
@click.option('--ip', required=True, help='IP address to check')
@click.option('--db', default='./data/threatintel.db', help='Database path')
def check_ip(ip, db):
    """Check reputation of an IP address"""
    db_instance = ThreatDatabase(db)
    threats = db_instance.search_threats(ip)
    
    if not threats:
        click.echo(f"✓ IP {ip} appears clean")
        return
    
    click.echo(f"\n⚠️  Found {len(threats)} threat(s) for IP {ip}\n")
    for threat in threats:
        click.echo(f"  {threat.title}")
        click.echo(f"    Severity: {threat.severity.value}")
        click.echo(f"    Confidence: {int(threat.confidence_score * 100)}%")
        click.echo(f"    Source: {threat.source}\n")

@cli.command()
@click.option('--db', default='./data/threatintel.db', help='Database path')
@click.option('--format', 'output_format', default='json', type=click.Choice(['json', 'csv']))
@click.option('--output', default=None, help='Output file (default: stdout)')
@click.option('--since', default='30d', help='Export threats since (e.g., 7d, 24h)')
def export_threats(db, output_format, output, since):
    """Export threats to file"""
    
    # Parse 'since'
    since_dt = None
    if since.endswith('d'):
        days = int(since[:-1])
        since_dt = datetime.utcnow() - timedelta(days=days)
    elif since.endswith('h'):
        hours = int(since[:-1])
        since_dt = datetime.utcnow() - timedelta(hours=hours)
    
    db_instance = ThreatDatabase(db)
    threats = db_instance.list_threats(since=since_dt, limit=10000)
    
    if output_format == 'json':
        data = json.dumps([t.to_dict() for t in threats], indent=2, default=str)
    else:  # csv
        lines = ["ID,Type,Severity,Title,Source,Discovered,Confidence"]
        for threat in threats:
            lines.append(f'"{threat.id}","{threat.threat_type.value}","{threat.severity.value}",'
                        f'"{threat.title}","{threat.source}","{threat.discovered_at.isoformat()}",'
                        f'"{int(threat.confidence_score * 100)}"')
        data = '\n'.join(lines)
    
    if output:
        with open(output, 'w') as f:
            f.write(data)
        click.echo(f"✓ Exported {len(threats)} threats to {output}")
    else:
        click.echo(data)

@cli.command()
@click.option('--db', default='./data/threatintel.db', help='Database path')
@click.option('--days', default=90, help='Delete threats older than N days')
def cleanup(db, days):
    """Clean up old threat records"""
    db_instance = ThreatDatabase(db)
    click.echo(f"Cleaning up threats older than {days} days...")
    db_instance.cleanup_old_records(days)
    click.echo("✓ Cleanup completed")

if __name__ == '__main__':
    cli()
