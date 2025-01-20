#!/usr/bin/env python3

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple

def check_ica_cli() -> bool:
    """Check if ICA CLI is installed and configured."""
    try:
        result = subprocess.run(['ica', '--version'], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_project_id(project_name: str) -> Optional[str]:
    """Get project ID from project name."""
    try:
        result = subprocess.run(['ica', 'projects', 'list', '--output', 'json'],
                              capture_output=True,
                              text=True)
        
        if result.returncode != 0:
            print(f"Error listing projects: {result.stderr}")
            return None
            
        projects = json.loads(result.stdout)
        for project in projects:
            if project['name'].lower() == project_name.lower():
                return project['id']
                
        print(f"Project '{project_name}' not found")
        return None
        
    except Exception as e:
        print(f"Error getting project ID: {str(e)}")
        return None

def get_analysis_status(analysis_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the status and output folder ID of an analysis.
    
    Returns:
        Tuple[str, str]: (status, output_folder_id) or (None, None) if error
    """
    try:
        result = subprocess.run([
            'ica', 'pipelines', 'history',
            '--analysis-id', analysis_id,
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting analysis status: {result.stderr}")
            return None, None
            
        analysis = json.loads(result.stdout)
        status = analysis.get('status')
        
        # Get output folder ID if analysis is complete
        output_folder_id = None
        if status == 'COMPLETED':
            try:
                output = analysis.get('output', {})
                output_folder_id = output.get('folder', {}).get('id')
            except (KeyError, AttributeError):
                print("Warning: Could not find output folder ID in completed analysis")
                
        return status, output_folder_id
        
    except Exception as e:
        print(f"Error checking analysis status: {str(e)}")
        return None, None

def wait_for_analysis(analysis_id: str, polling_interval: int = 60) -> Optional[str]:
    """
    Wait for analysis to complete and return output folder ID.
    
    Args:
        analysis_id: The analysis ID to monitor
        polling_interval: Time in seconds between status checks
    
    Returns:
        str: Output folder ID if successful, None otherwise
    """
    print(f"Monitoring analysis {analysis_id}...")
    while True:
        status, folder_id = get_analysis_status(analysis_id)
        
        if status is None:
            return None
            
        print(f"Current status: {status}")
        
        if status == 'COMPLETED':
            print("Analysis completed successfully!")
            return folder_id
        elif status in ['FAILED', 'ABORTED', 'TERMINATED']:
            print(f"Analysis ended with status: {status}")
            return None
            
        time.sleep(polling_interval)

def download_folder(project_id: str, folder_id: str, output_dir: str) -> bool:
    """
    Download a folder from ICA.
    
    Args:
        project_id: The project ID
        folder_id: The folder ID to download
        output_dir: Local directory to save files
    
    Returns:
        bool: True if download was successful
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Download the folder
        cmd = [
            'ica', 'files', 'download',
            '--project-id', project_id,
            '--data-ids', folder_id,
            '--output-folder', output_dir
        ]
        
        print(f"Downloading results to: {output_dir}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Successfully downloaded results")
            return True
        else:
            print(f"Error downloading results: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during download: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Download analysis results using ICA CLI')
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('analysis_id', help='ID of the analysis to download results from')
    parser.add_argument('output_dir', help='Local directory to save results')
    parser.add_argument('--no-wait', action='store_true',
                       help='Download immediately without waiting for completion')
    parser.add_argument('--polling-interval', type=int, default=60,
                       help='Seconds between status checks when waiting (default: 60)')
    
    args = parser.parse_args()
    
    # Check if ICA CLI is installed
    if not check_ica_cli():
        print("Error: ICA CLI not found. Please install and configure the ICA CLI first.")
        print("Installation instructions: https://help.ica.illumina.com/command-line/latest/install")
        sys.exit(1)
    
    # Get project ID
    project_id = get_project_id(args.project_name)
    if not project_id:
        sys.exit(1)
    
    # Get output folder ID
    folder_id = None
    if args.no_wait:
        # Just get current status
        status, folder_id = get_analysis_status(args.analysis_id)
        if status != 'COMPLETED':
            print(f"Analysis is not complete (status: {status})")
            print("Use --no-wait flag only when analysis is already complete")
            sys.exit(1)
    else:
        # Wait for completion
        folder_id = wait_for_analysis(args.analysis_id, args.polling_interval)
    
    if not folder_id:
        print("Could not get output folder ID")
        sys.exit(1)
    
    # Download the results
    success = download_folder(project_id, folder_id, args.output_dir)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
