#!/usr/bin/env python3

import os
import sys
import argparse
from pathlib import Path
from icasdk import ApiClient, ApiException, Configuration, ProjectsApi, FilesApi, PipelineApi
from icasdk.model.folder_upload_session import FolderUploadSession
from icasdk.model.create_pipeline_analysis import CreatePipelineAnalysis
from icasdk.model.analysis_input import AnalysisInput
from icasdk.model.analysis_input_data_mount import AnalysisInputDataMount
from icasdk.model.pipeline_configuration_parameter import PipelineConfigurationParameter

def authenticate_ica():
    """Authenticate with ICA using API key."""
    try:
        # You should store these securely, preferably as environment variables
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

def upload_folder(folder_path: str, project_id: str):
    """
    Upload a folder to ICA.
    
    Args:
        folder_path: Path to the local folder to upload
        project_id: The ICA project ID to upload to
    
    Returns:
        str: The ID of the uploaded folder
    """
    try:
        # Convert folder path to absolute path
        folder_path = os.path.abspath(folder_path)
        if not os.path.isdir(folder_path):
            raise ValueError(f"Folder not found: {folder_path}")

        # Initialize API client
        api_client = authenticate_ica()
        files_api = FilesApi(api_client)
        
        # Create folder upload session
        folder_name = os.path.basename(folder_path)
        session = files_api.create_folder_upload_session(
            project_id=project_id,
            folder_upload_session=FolderUploadSession(name=folder_name)
        )
        
        print(f"Created upload session for folder: {folder_name}")
        
        # Walk through the folder and upload all files
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                
                print(f"Uploading: {relative_path}")
                with open(file_path, 'rb') as f:
                    files_api.upload_folder_session_file(
                        session.id,
                        file=f,
                        relative_path=relative_path
                    )
        
        # Complete the upload session
        folder = files_api.complete_folder_upload_session(session.id)
        print(f"Successfully uploaded folder: {folder_name}")
        return folder.id
        
    except ApiException as e:
        print(f"API error occurred: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

def start_dragen_pipeline(project_id: str, folder_id: str, pipeline_id: str, params: dict):
    """
    Start a DRAGEN pipeline analysis on the uploaded folder.
    
    Args:
        project_id: The ICA project ID
        folder_id: The ID of the uploaded folder
        pipeline_id: The ID of the DRAGEN pipeline to run
        params: Dictionary of pipeline parameters
    """
    try:
        api_client = authenticate_ica()
        pipeline_api = PipelineApi(api_client)

        # Create pipeline parameters
        pipeline_params = [
            PipelineConfigurationParameter(
                code=code,
                value=value
            ) for code, value in params.items()
        ]

        # Create analysis input
        analysis_input = AnalysisInput(
            data_ids=[folder_id],
            mounts=[
                AnalysisInputDataMount(
                    data_id=folder_id,
                    mount_path="/data"
                )
            ]
        )

        # Create pipeline analysis
        create_analysis = CreatePipelineAnalysis(
            user_reference="DRAGEN_Analysis",
            pipeline_id=pipeline_id,
            input=analysis_input,
            parameters=pipeline_params
        )

        # Start the analysis
        analysis = pipeline_api.create_pipeline_analysis(
            project_id=project_id,
            create_pipeline_analysis=create_analysis
        )

        print(f"Started DRAGEN pipeline analysis. Analysis ID: {analysis.id}")
        return analysis.id

    except ApiException as e:
        print(f"API error occurred while starting pipeline: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while starting pipeline: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Upload a folder to Illumina Connected Analytics and optionally start a DRAGEN pipeline')
    parser.add_argument('folder_path', help='Path to the folder to upload')
    parser.add_argument('--project-id', required=True, help='ICA project ID')
    parser.add_argument('--pipeline-id', help='DRAGEN pipeline ID to run after upload')
    parser.add_argument('--pipeline-params', help='JSON string of pipeline parameters', default='{}')
    
    args = parser.parse_args()
    
    # Upload the folder
    folder_id = upload_folder(args.folder_path, args.project_id)
    
    # If pipeline ID is provided, start the pipeline
    if args.pipeline_id:
        import json
        params = json.loads(args.pipeline_params)
        analysis_id = start_dragen_pipeline(
            args.project_id,
            folder_id,
            args.pipeline_id,
            params
        )
        print(f"Pipeline started successfully. You can monitor the analysis using the analysis ID: {analysis_id}")

if __name__ == '__main__':
    main()
