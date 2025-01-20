# ICA Tools

A collection of Python scripts for interacting with Illumina Connected Analytics (ICA).

## Scripts

### 1. ICA Folder Upload & DRAGEN Pipeline (API-based)
`ica_folder_upload.py` - Upload a folder to ICA and optionally start a DRAGEN pipeline using the ICA API.

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

### 3. ICA CLI Folder Upload
`ica_cli_upload.py` - Upload a folder to ICA using the ICA Command Line Interface (CLI).

#### Prerequisites
- ICA CLI must be installed and configured
- Installation instructions: https://help.ica.illumina.com/command-line/latest/install

#### Usage
```bash
# Upload a folder using project name
python ica_cli_upload.py /path/to/folder "My Project Name"

# Upload with custom folder name in ICA
python ica_cli_upload.py /path/to/folder "My Project Name" --folder-name "Custom Folder Name"
```

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set environment variables for API-based scripts:
```bash
# Set your ICA API key
export ICA_API_KEY='your-api-key'

# Optional: Set custom base URL if needed
export ICA_BASE_URL='https://ica.illumina.com/ica/rest'
```

3. For CLI-based scripts:
- Install and configure the ICA CLI following the official documentation
- Run `ica configure` to set up your credentials

## Requirements
- Python 3.7+
- ICA SDK (for API-based scripts)
- ICA CLI (for CLI-based scripts)
- Valid ICA credentials

## Security Note
Never commit your API keys or sensitive credentials to the repository. Always use environment variables for sensitive information.
