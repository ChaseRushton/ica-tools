#!/usr/bin/env python3

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import smtplib
from email.message import EmailMessage
import logging
from dataclasses import dataclass
import yaml

@dataclass
class NotificationConfig:
    email_to: str
    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    slack_webhook: Optional[str] = None

class ICAMonitor:
    def __init__(self, project_name: str, config_file: str):
        self.project_name = project_name
        self.config = self._load_config(config_file)
        self.logger = self._setup_logging()

    def _load_config(self, config_file: str) -> NotificationConfig:
        """Load notification configuration from YAML"""
        with open(config_file) as f:
            config = yaml.safe_load(f)
        return NotificationConfig(**config)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger('ica_monitor')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('ica_monitor.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger

    def _send_email(self, subject: str, body: str):
        """Send email notification"""
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.config.smtp_user or "ica-monitor@localhost"
        msg['To'] = self.config.email_to
        
        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            if self.config.smtp_user and self.config.smtp_pass:
                server.login(self.config.smtp_user, self.config.smtp_pass)
            server.send_message(msg)

    def _send_slack(self, message: str):
        """Send Slack notification"""
        if not self.config.slack_webhook:
            return
            
        import requests
        payload = {'text': message}
        try:
            requests.post(self.config.slack_webhook, json=payload)
        except Exception as e:
            self.logger.error(f"Failed to send Slack notification: {e}")

    def monitor_pipeline(self, analysis_id: str,
                        check_interval: int = 300) -> Dict:
        """Monitor pipeline progress and send notifications"""
        self.logger.info(f"Starting monitoring of analysis {analysis_id}")
        
        while True:
            cmd = ['ica', 'projects', 'analyses', 'get',
                   self.project_name, analysis_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Failed to get analysis status: {result.stderr}"
                self.logger.error(error_msg)
                self._send_email("Pipeline Monitoring Error", error_msg)
                self._send_slack(error_msg)
                return {'status': 'error', 'message': error_msg}
            
            status_data = json.loads(result.stdout)
            current_status = status_data['status']
            
            if current_status in ['Completed', 'Failed']:
                msg = f"Pipeline {analysis_id} {current_status.lower()}"
                self.logger.info(msg)
                self._send_email(f"Pipeline {current_status}", msg)
                self._send_slack(msg)
                return status_data
            
            time.sleep(check_interval)

    def monitor_storage(self, threshold_percent: float = 90.0,
                       check_interval: int = 3600) -> None:
        """Monitor storage usage and send alerts when threshold exceeded"""
        self.logger.info(f"Starting storage monitoring (threshold: {threshold_percent}%)")
        
        while True:
            cmd = ['ica', 'projects', 'storage', self.project_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Failed to get storage info: {result.stderr}"
                self.logger.error(error_msg)
                self._send_email("Storage Monitoring Error", error_msg)
                self._send_slack(error_msg)
                continue
            
            # Parse storage info
            lines = result.stdout.splitlines()
            for line in lines:
                if 'Used:' in line:
                    used_gb = float(line.split()[1].replace('GB', ''))
                elif 'Total:' in line:
                    total_gb = float(line.split()[1].replace('GB', ''))
            
            usage_percent = (used_gb / total_gb) * 100
            if usage_percent >= threshold_percent:
                msg = (f"Storage usage alert: {usage_percent:.1f}% "
                      f"({used_gb:.1f}GB of {total_gb:.1f}GB)")
                self.logger.warning(msg)
                self._send_email("Storage Usage Alert", msg)
                self._send_slack(msg)
            
            time.sleep(check_interval)

    def monitor_costs(self, budget_threshold: float,
                     check_interval: int = 86400) -> None:
        """Monitor project costs and send alerts when exceeding budget"""
        self.logger.info(f"Starting cost monitoring (threshold: ${budget_threshold})")
        
        while True:
            cmd = ['ica', 'projects', 'costs', self.project_name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                error_msg = f"Failed to get cost info: {result.stderr}"
                self.logger.error(error_msg)
                self._send_email("Cost Monitoring Error", error_msg)
                self._send_slack(error_msg)
                continue
            
            cost_data = json.loads(result.stdout)
            current_cost = float(cost_data['total_cost'])
            
            if current_cost >= budget_threshold:
                msg = (f"Cost alert: Current cost ${current_cost:.2f} "
                      f"exceeds budget threshold ${budget_threshold:.2f}")
                self.logger.warning(msg)
                self._send_email("Cost Alert", msg)
                self._send_slack(msg)
            
            time.sleep(check_interval)

def main():
    parser = argparse.ArgumentParser(
        description='Monitor ICA pipelines, storage, and costs'
    )
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('--config', required=True,
                       help='Path to notification config YAML file')
    parser.add_argument('--action', required=True,
                       choices=['pipeline', 'storage', 'costs'],
                       help='What to monitor')
    parser.add_argument('--analysis-id',
                       help='Analysis ID for pipeline monitoring')
    parser.add_argument('--threshold',
                       help='Threshold for storage (%) or costs ($)')
    parser.add_argument('--check-interval', type=int,
                       help='Check interval in seconds')
    
    args = parser.parse_args()
    monitor = ICAMonitor(args.project_name, args.config)
    
    if args.action == 'pipeline':
        if not args.analysis_id:
            parser.error("--analysis-id is required for pipeline monitoring")
        monitor.monitor_pipeline(
            args.analysis_id,
            check_interval=args.check_interval or 300
        )
        
    elif args.action == 'storage':
        monitor.monitor_storage(
            threshold_percent=float(args.threshold or 90),
            check_interval=args.check_interval or 3600
        )
        
    elif args.action == 'costs':
        if not args.threshold:
            parser.error("--threshold is required for cost monitoring")
        monitor.monitor_costs(
            budget_threshold=float(args.threshold),
            check_interval=args.check_interval or 86400
        )

if __name__ == '__main__':
    main()
