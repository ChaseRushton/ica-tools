#!/usr/bin/env python3

import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class ICAProjectManager:
    def __init__(self, project_name: str):
        self.project_name = project_name

    def list_data(self, days: Optional[int] = None, pattern: Optional[str] = None) -> List[Dict]:
        """List all data in the project, optionally filtered by age and pattern"""
        cmd = ['ica', 'projects', 'data', 'ls', self.project_name]
        if pattern:
            cmd.extend(['--filter', pattern])
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to list data: {result.stderr}")
            
        data_list = []
        for line in result.stdout.splitlines()[1:]:  # Skip header
            parts = line.split()
            if not parts:
                continue
                
            created = datetime.strptime(parts[1], '%Y-%m-%d')
            if days and (datetime.now() - created) > timedelta(days=days):
                continue
                
            data_list.append({
                'name': parts[0],
                'created': parts[1],
                'size': parts[2],
                'type': parts[3]
            })
            
        return data_list

    def cleanup_old_data(self, days: int, dry_run: bool = True) -> List[str]:
        """Remove data older than specified days"""
        old_data = self.list_data(days=days)
        to_delete = []
        
        for item in old_data:
            if dry_run:
                print(f"Would delete: {item['name']} ({item['size']})")
            else:
                cmd = ['ica', 'projects', 'data', 'delete', 
                       self.project_name, item['name']]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    to_delete.append(item['name'])
                else:
                    print(f"Failed to delete {item['name']}: {result.stderr}")
                    
        return to_delete

    def get_storage_usage(self) -> Dict[str, float]:
        """Get storage usage statistics"""
        cmd = ['ica', 'projects', 'storage', self.project_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to get storage info: {result.stderr}")
            
        # Parse storage info
        lines = result.stdout.splitlines()
        usage = {}
        for line in lines:
            if 'Used:' in line:
                usage['used_gb'] = float(line.split()[1].replace('GB', ''))
            elif 'Available:' in line:
                usage['available_gb'] = float(line.split()[1].replace('GB', ''))
            elif 'Total:' in line:
                usage['total_gb'] = float(line.split()[1].replace('GB', ''))
                
        usage['usage_percent'] = (usage['used_gb'] / usage['total_gb']) * 100
        return usage

    def archive_old_data(self, days: int, archive_dir: str) -> List[str]:
        """Archive data older than specified days to local storage"""
        old_data = self.list_data(days=days)
        archived = []
        
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        
        for item in old_data:
            # Download to archive
            output_path = archive_path / item['name']
            cmd = ['ica', 'projects', 'data', 'download',
                   self.project_name, item['name'],
                   '--output-file', str(output_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                archived.append(item['name'])
                # Delete from ICA if download successful
                self.cleanup_old_data(days=days, dry_run=False)
            else:
                print(f"Failed to archive {item['name']}: {result.stderr}")
                
        return archived

def main():
    parser = argparse.ArgumentParser(
        description='Manage ICA project data and storage'
    )
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('--action', required=True,
                       choices=['list', 'cleanup', 'archive', 'storage'],
                       help='Action to perform')
    parser.add_argument('--days', type=int,
                       help='Process data older than this many days')
    parser.add_argument('--pattern', help='Filter data by pattern')
    parser.add_argument('--archive-dir',
                       help='Local directory for archiving data')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without doing it')
    
    args = parser.parse_args()
    manager = ICAProjectManager(args.project_name)
    
    if args.action == 'list':
        data = manager.list_data(days=args.days, pattern=args.pattern)
        print(json.dumps(data, indent=2))
        
    elif args.action == 'cleanup':
        if not args.days:
            parser.error("--days is required for cleanup")
        deleted = manager.cleanup_old_data(args.days, args.dry_run)
        print(f"Deleted {len(deleted)} items")
        
    elif args.action == 'archive':
        if not args.days or not args.archive_dir:
            parser.error("--days and --archive-dir are required for archive")
        archived = manager.archive_old_data(args.days, args.archive_dir)
        print(f"Archived {len(archived)} items to {args.archive_dir}")
        
    elif args.action == 'storage':
        usage = manager.get_storage_usage()
        print(json.dumps(usage, indent=2))

if __name__ == '__main__':
    main()
