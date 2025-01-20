#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List

def check_ica_cli() -> bool:
    """
    Check if ICA CLI is installed and configured.
    """
    try:
        result = subprocess.run(['ica', '--version'], 
                              capture_output=True, 
                              text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_project_id(project_name: str) -> Optional[str]:
    """
    Get project ID from project name using ICA CLI.
    """
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

def upload_folder(folder_path: str, project_name: str, folder_name: Optional[str] = None) -> bool:
    """
    Upload a folder to ICA using the CLI.
    
    Args:
        folder_path: Path to the folder to upload
        project_name: Name of the ICA project
        folder_name: Optional name for the uploaded folder (default: use local folder name)
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    try:
        # Convert to absolute path and check if folder exists
        folder_path = os.path.abspath(folder_path)
        if not os.path.isdir(folder_path):
            print(f"Error: Folder not found: {folder_path}")
            return False
            
        # Get project ID
        project_id = get_project_id(project_name)
        if not project_id:
            return False
            
        # Use provided folder name or local folder name
        if not folder_name:
            folder_name = os.path.basename(folder_path)
            
        # Create upload command
        cmd = [
            'ica',
            'files',
            'upload',
            '--project-id', project_id,
            '--recursive',
            folder_path,
            folder_name
        ]
        
        print(f"Uploading folder '{folder_path}' to project '{project_name}'...")
        
        # Execute upload command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully uploaded folder to ICA")
            print(f"Upload location: {folder_name}")
            return True
        else:
            print(f"Error uploading folder: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during upload: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Upload a folder to ICA using the CLI')
    parser.add_argument('folder_path', help='Path to the folder to upload')
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('--folder-name', help='Optional name for the uploaded folder')
    
    args = parser.parse_args()
    
    # Check if ICA CLI is installed
    if not check_ica_cli():
        print("Error: ICA CLI not found. Please install and configure the ICA CLI first.")
        print("Installation instructions: https://help.ica.illumina.com/command-line/latest/install")
        sys.exit(1)
    
    # Upload the folder
    success = upload_folder(args.folder_path, args.project_name, args.folder_name)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
