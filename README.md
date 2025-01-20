# ICA Tools

A collection of Python scripts for interacting with Illumina Connected Analytics (ICA).

## Scripts

### 1. ICA Folder Upload & DRAGEN Pipeline
`ica_folder_upload.py` - Upload a folder to ICA and optionally start a DRAGEN pipeline.

#### Usage
```bash
# Just upload a folder
python ica_folder_upload.py /path/to/folder --project-id YOUR_PROJECT_ID

# Upload and start DRAGEN pipeline
python ica_folder_upload.py /path/to/folder --project-id YOUR_PROJECT_ID --pipeline-id YOUR_PIPELINE_ID --pipeline-params '{"param1": "value1"}'
```

### 2. ICA Results Downloader
`ica_download_results.py` - Download results from an ICA analysis (e.g., DRAGEN pipeline results).

#### Usage
```bash
# Download completed analysis results
python ica_download_results.py --project-id YOUR_PROJECT_ID --analysis-id YOUR_ANALYSIS_ID --output-dir ./results

# Wait for completion and download
python ica_download_results.py --project-id YOUR_PROJECT_ID --analysis-id YOUR_ANALYSIS_ID --output-dir ./results --wait-for-completion
```

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
# Set your ICA API key
export ICA_API_KEY='your-api-key'

# Optional: Set custom base URL if needed
export ICA_BASE_URL='https://ica.illumina.com/ica/rest'
```

## Requirements
- Python 3.7+
- ICA SDK
- Valid ICA API credentials

## Security Note
Never commit your API keys or sensitive credentials to the repository. Always use environment variables for sensitive information.
