#!/usr/bin/env python3

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, List

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

def get_pipeline_id(project_id: str, pipeline_name: str) -> Optional[str]:
    """Get pipeline ID from pipeline name."""
    try:
        result = subprocess.run([
            'ica', 'pipelines', 'list',
            '--project-id', project_id,
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error listing pipelines: {result.stderr}")
            return None
            
        pipelines = json.loads(result.stdout)
        for pipeline in pipelines:
            if pipeline['name'].lower() == pipeline_name.lower():
                return pipeline['id']
                
        print(f"Pipeline '{pipeline_name}' not found in project")
        return None
        
    except Exception as e:
        print(f"Error getting pipeline ID: {str(e)}")
        return None

def get_data_id(project_id: str, folder_path: str) -> Optional[str]:
    """Get data ID for a folder path in ICA."""
    try:
        # List files in project
        result = subprocess.run([
            'ica', 'files', 'list',
            '--project-id', project_id,
            '--output', 'json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error listing files: {result.stderr}")
            return None
            
        files = json.loads(result.stdout)
        folder_name = os.path.basename(folder_path.rstrip('/'))
        
        # Find the folder
        for file in files:
            if file['name'] == folder_name and file['type'] == 'FOLDER':
                return file['id']
                
        print(f"Folder '{folder_name}' not found in project")
        return None
        
    except Exception as e:
        print(f"Error getting data ID: {str(e)}")
        return None

def start_pipeline(project_name: str, 
                  pipeline_name: str, 
                  input_folder: str,
                  params_file: Optional[str] = None,
                  analysis_name: Optional[str] = None) -> bool:
    """
    Start a pipeline run using the ICA CLI.
    
    Args:
        project_name: Name of the ICA project
        pipeline_name: Name of the pipeline to run
        input_folder: Path of the input folder in ICA
        params_file: Optional JSON file containing pipeline parameters
        analysis_name: Optional name for the analysis
    
    Returns:
        bool: True if pipeline started successfully
    """
    try:
        # Get project ID
        project_id = get_project_id(project_name)
        if not project_id:
            return False
            
        # Get pipeline ID
        pipeline_id = get_pipeline_id(project_id, pipeline_name)
        if not pipeline_id:
            return False
            
        # Get input folder ID
        data_id = get_data_id(project_id, input_folder)
        if not data_id:
            return False
            
        # Build command
        cmd = [
            'ica', 'pipelines', 'start',
            '--project-id', project_id,
            '--pipeline-id', pipeline_id,
            '--input', f"folder_id={data_id}"
        ]
        
        # Add optional parameters
        if params_file:
            if not os.path.isfile(params_file):
                print(f"Error: Parameters file not found: {params_file}")
                return False
            cmd.extend(['--params-file', params_file])
            
        if analysis_name:
            cmd.extend(['--name', analysis_name])
            
        print(f"Starting pipeline '{pipeline_name}' in project '{project_name}'...")
        print(f"Using input folder: {input_folder}")
        
        # Start the pipeline
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                response = json.loads(result.stdout)
                analysis_id = response.get('id')
                print(f"Successfully started pipeline analysis")
                print(f"Analysis ID: {analysis_id}")
                print(f"Monitor progress with: ica pipelines history --analysis-id {analysis_id}")
                return True
            except json.JSONDecodeError:
                print("Error parsing pipeline response")
                return False
        else:
            print(f"Error starting pipeline: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during pipeline execution: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Start a DRAGEN pipeline using ICA CLI')
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('pipeline_name', help='Name of the pipeline to run')
    parser.add_argument('input_folder', help='Path of the input folder in ICA')
    parser.add_argument('--params-file', help='JSON file containing pipeline parameters')
    parser.add_argument('--analysis-name', help='Optional name for the analysis')
    
    args = parser.parse_args()
    
    # Check if ICA CLI is installed
    if not check_ica_cli():
        print("Error: ICA CLI not found. Please install and configure the ICA CLI first.")
        print("Installation instructions: https://help.ica.illumina.com/command-line/latest/install")
        sys.exit(1)
    
    # Start the pipeline
    success = start_pipeline(
        args.project_name,
        args.pipeline_name,
        args.input_folder,
        args.params_file,
        args.analysis_name
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
