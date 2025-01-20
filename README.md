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

### 2. ICA Results Downloader (API-based)
`ica_download_results.py` - Download results from an ICA analysis using the API.

#### Usage
```bash
# Download completed analysis results
python ica_download_results.py --project-id YOUR_PROJECT_ID --analysis-id YOUR_ANALYSIS_ID --output-dir ./results

# Wait for completion and download
python ica_download_results.py --project-id YOUR_PROJECT_ID --analysis-id YOUR_ANALYSIS_ID --output-dir ./results --wait-for-completion
```

### 3. ICA CLI Folder Upload
`ica_cli_upload.py` - Upload a folder to ICA using the ICA Command Line Interface (CLI).

#### Usage
```bash
# Upload a folder using project name
python ica_cli_upload.py /path/to/folder "My Project Name"

# Upload with custom folder name in ICA
python ica_cli_upload.py /path/to/folder "My Project Name" --folder-name "Custom Folder Name"
```

### 4. ICA CLI Pipeline Runner
`ica_cli_pipeline.py` - Start a pipeline (e.g., DRAGEN) using the ICA Command Line Interface.

#### Usage
```bash
# Basic usage
python ica_cli_pipeline.py "My Project" "DRAGEN Pipeline" "input_folder_name"

# With parameters file and custom analysis name
python ica_cli_pipeline.py "My Project" "DRAGEN Pipeline" "input_folder_name" \
    --params-file params.json \
    --analysis-name "DRAGEN Analysis Jan 2025"
```

### 5. ICA CLI Results Downloader
`ica_cli_download.py` - Download analysis results using the ICA Command Line Interface.

#### Usage
```bash
# Wait for analysis to complete and download results
python ica_cli_download.py "My Project" ANALYSIS_ID ./results

# Download results from completed analysis
python ica_cli_download.py "My Project" ANALYSIS_ID ./results --no-wait

# Customize polling interval when waiting
python ica_cli_download.py "My Project" ANALYSIS_ID ./results --polling-interval 120
```

### 6. ICA CLI Complete Workflow
`ica_cli_workflow.py` - Run a complete workflow: upload data, start pipeline, and download results.

#### Usage
```bash
# Basic usage
python ica_cli_workflow.py ./input_data "My Project" "DRAGEN Pipeline" ./results

# Full example with all options
python ica_cli_workflow.py ./sequencing_data "My Project" "DRAGEN Pipeline" ./results \
    --folder-name "Sample_Jan2025" \
    --params-file examples/dragen_params.json \
    --analysis-name "DRAGEN Analysis Jan2025" \
    --polling-interval 120
```

The workflow script will:
1. Upload your input folder to ICA
2. Start the specified pipeline
3. Monitor the pipeline execution
4. Download results when complete
5. Provide real-time status updates

## Complete CLI Workflow Example

Here's a complete example of running a DRAGEN analysis using the CLI-based tools:

1. Upload your data:
```bash
python ica_cli_upload.py ./sequencing_data "My Project" --folder-name "Sample_Jan2025"
```

2. Start the DRAGEN pipeline:
```bash
python ica_cli_pipeline.py "My Project" "DRAGEN Pipeline" "Sample_Jan2025" \
    --params-file examples/dragen_params.json \
    --analysis-name "DRAGEN Analysis Jan 2025"
```

3. Download the results when complete:
```bash
python ica_cli_download.py "My Project" ANALYSIS_ID ./results
```

The download script will:
- Monitor the pipeline status
- Wait for completion
- Automatically download results to the specified directory
- Provide progress updates

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

## Examples
Check the `examples/` directory for:
- Sample parameter files for DRAGEN pipelines
- Example workflows and scripts

## Security Note
Never commit your API keys or sensitive credentials to the repository. Always use environment variables for sensitive information.
