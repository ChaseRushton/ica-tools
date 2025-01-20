#!/usr/bin/env python3

import os
import sys
import time
import argparse
from pathlib import Path
from icasdk import ApiClient, ApiException, Configuration, ProjectsApi, FilesApi, AnalysisApi
from icasdk.model.download_session import DownloadSession

def authenticate_ica():
    """Authenticate with ICA using API key."""
    try:
        api_key = os.getenv('ICA_API_KEY')
        base_url = os.getenv('ICA_BASE_URL', 'https://ica.illumina.com/ica/rest')
        
        if not api_key:
            raise ValueError("ICA_API_KEY environment variable is not set")
        
        configuration = Configuration(
            host=base_url,
            api_key={'ApiKeyAuth': api_key}
        )
        return ApiClient(configuration)
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        sys.exit(1)

def wait_for_analysis_completion(analysis_api, project_id: str, analysis_id: str, polling_interval: int = 60):
    """
    Wait for the analysis to complete.
    
    Args:
        analysis_api: The AnalysisApi instance
        project_id: The project ID
        analysis_id: The analysis ID to monitor
        polling_interval: Time in seconds between status checks
    
    Returns:
        bool: True if analysis completed successfully, False if failed
    """
    print(f"Monitoring analysis {analysis_id}...")
    while True:
        try:
            analysis = analysis_api.get_analysis(project_id, analysis_id)
            status = analysis.status
            
            print(f"Current status: {status}")
            
            if status == "SUCCEEDED":
                return True
            elif status in ["FAILED", "CANCELLED", "TERMINATED"]:
                print(f"Analysis ended with status: {status}")
                return False
            
            time.sleep(polling_interval)
            
        except ApiException as e:
            print(f"Error checking analysis status: {str(e)}")
            return False

def get_analysis_output_folder(analysis_api, project_id: str, analysis_id: str):
    """
    Get the output folder ID from the analysis.
    
    Args:
        analysis_api: The AnalysisApi instance
        project_id: The project ID
        analysis_id: The analysis ID
    
    Returns:
        str: The output folder ID
    """
    try:
        analysis = analysis_api.get_analysis(project_id, analysis_id)
        return analysis.output.folder.id
    except ApiException as e:
        print(f"Error getting output folder: {str(e)}")
        sys.exit(1)

def download_folder(files_api, project_id: str, folder_id: str, local_path: str):
    """
    Download a folder from ICA.
    
    Args:
        files_api: The FilesApi instance
        project_id: The project ID
        folder_id: The folder ID to download
        local_path: Local path to save the folder
    """
    try:
        # Create download session
        session = files_api.create_download_session(
            project_id=project_id,
            data_ids=[folder_id],
            download_session=DownloadSession()
        )
        
        # Create local directory if it doesn't exist
        os.makedirs(local_path, exist_ok=True)
        
        # Get all files in the folder
        files = files_api.list_files_in_folder(project_id, folder_id)
        
        # Download each file
        for file in files:
            relative_path = file.path
            local_file_path = os.path.join(local_path, relative_path)
            
            # Create directory structure if needed
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            
            print(f"Downloading: {relative_path}")
            
            # Download the file
            with open(local_file_path, 'wb') as f:
                files_api.download_file_content(
                    project_id,
                    file.id,
                    _preload_content=False,
                    callback=lambda response: f.write(response.read())
                )
        
        print(f"Successfully downloaded all files to: {local_path}")
        
    except ApiException as e:
        print(f"API error occurred: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download DRAGEN pipeline results from ICA')
    parser.add_argument('--project-id', required=True, help='ICA project ID')
    parser.add_argument('--analysis-id', required=True, help='Analysis ID to download results from')
    parser.add_argument('--output-dir', required=True, help='Local directory to save results')
    parser.add_argument('--wait-for-completion', action='store_true', 
                       help='Wait for analysis to complete before downloading')
    parser.add_argument('--polling-interval', type=int, default=60,
                       help='Polling interval in seconds when waiting for completion')
    
    args = parser.parse_args()
    
    # Initialize API clients
    api_client = authenticate_ica()
    analysis_api = AnalysisApi(api_client)
    files_api = FilesApi(api_client)
    
    # Wait for completion if requested
    if args.wait_for_completion:
        success = wait_for_analysis_completion(
            analysis_api,
            args.project_id,
            args.analysis_id,
            args.polling_interval
        )
        if not success:
            print("Analysis did not complete successfully")
            sys.exit(1)
    
    # Get the output folder ID
    folder_id = get_analysis_output_folder(analysis_api, args.project_id, args.analysis_id)
    
    # Download the results
    download_folder(files_api, args.project_id, folder_id, args.output_dir)

if __name__ == '__main__':
    main()
