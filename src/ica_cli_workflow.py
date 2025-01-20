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

def run_upload(input_folder: str, project_name: str, folder_name: Optional[str] = None) -> Optional[str]:
    """
    Upload a folder using ica_cli_upload.py
    
    Returns:
        str: Name of the uploaded folder if successful, None otherwise
    """
    try:
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'ica_cli_upload.py'),
            input_folder,
            project_name
        ]
        
        if folder_name:
            cmd.extend(['--folder-name', folder_name])
            
        print("\n=== Step 1: Uploading Data ===")
        print(f"Uploading {input_folder} to project '{project_name}'...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Use the specified folder name or extract from input path
            return folder_name or os.path.basename(input_folder.rstrip('/\\'))
        else:
            print(f"Error during upload: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error running upload script: {str(e)}")
        return None

def run_pipeline(project_name: str, 
                pipeline_name: str, 
                input_folder: str,
                params_file: Optional[str] = None,
                analysis_name: Optional[str] = None) -> Optional[str]:
    """
    Start pipeline using ica_cli_pipeline.py
    
    Returns:
        str: Analysis ID if successful, None otherwise
    """
    try:
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'ica_cli_pipeline.py'),
            project_name,
            pipeline_name,
            input_folder
        ]
        
        if params_file:
            cmd.extend(['--params-file', params_file])
        if analysis_name:
            cmd.extend(['--analysis-name', analysis_name])
            
        print("\n=== Step 2: Starting Pipeline ===")
        print(f"Starting pipeline '{pipeline_name}' on folder '{input_folder}'...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Extract analysis ID from output
            try:
                output = result.stdout
                # Look for analysis ID in the output
                for line in output.splitlines():
                    if "Analysis ID:" in line:
                        return line.split("Analysis ID:", 1)[1].strip()
            except Exception:
                pass
            print("Warning: Could not extract analysis ID from output")
            return None
        else:
            print(f"Error starting pipeline: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"Error running pipeline script: {str(e)}")
        return None

def run_download(project_name: str, 
                analysis_id: str, 
                output_dir: str,
                polling_interval: int = 60) -> bool:
    """
    Download results using ica_cli_download.py
    
    Returns:
        bool: True if download was successful
    """
    try:
        cmd = [
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'ica_cli_download.py'),
            project_name,
            analysis_id,
            output_dir,
            '--polling-interval', str(polling_interval)
        ]
        
        print("\n=== Step 3: Downloading Results ===")
        print(f"Monitoring analysis {analysis_id} and downloading results...")
        
        # Run the download script and stream its output
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 universal_newlines=True,
                                 bufsize=1)
        
        # Stream the output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                
        # Get the return code
        return_code = process.poll()
        
        if return_code == 0:
            print("\nWorkflow completed successfully!")
            print(f"Results downloaded to: {output_dir}")
            return True
        else:
            error = process.stderr.read()
            print(f"Error downloading results: {error}")
            return False
            
    except Exception as e:
        print(f"Error running download script: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Run a complete ICA workflow: upload data, run pipeline, and download results'
    )
    parser.add_argument('input_folder', help='Local folder to upload')
    parser.add_argument('project_name', help='Name of the ICA project')
    parser.add_argument('pipeline_name', help='Name of the pipeline to run')
    parser.add_argument('output_dir', help='Local directory to save results')
    parser.add_argument('--folder-name', help='Optional name for the uploaded folder')
    parser.add_argument('--params-file', help='JSON file containing pipeline parameters')
    parser.add_argument('--analysis-name', help='Optional name for the analysis')
    parser.add_argument('--polling-interval', type=int, default=60,
                       help='Seconds between status checks (default: 60)')
    
    args = parser.parse_args()
    
    # Check if ICA CLI is installed
    if not check_ica_cli():
        print("Error: ICA CLI not found. Please install and configure the ICA CLI first.")
        print("Installation instructions: https://help.ica.illumina.com/command-line/latest/install")
        sys.exit(1)
    
    # Step 1: Upload data
    folder_name = run_upload(args.input_folder, args.project_name, args.folder_name)
    if not folder_name:
        print("Upload failed. Stopping workflow.")
        sys.exit(1)
    
    # Step 2: Start pipeline
    analysis_id = run_pipeline(
        args.project_name,
        args.pipeline_name,
        folder_name,
        args.params_file,
        args.analysis_name
    )
    if not analysis_id:
        print("Pipeline start failed. Stopping workflow.")
        sys.exit(1)
    
    # Step 3: Download results
    success = run_download(
        args.project_name,
        analysis_id,
        args.output_dir,
        args.polling_interval
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
