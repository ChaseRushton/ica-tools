# ICA Tools

A collection of Python scripts for interacting with Illumina Connected Analytics (ICA). These tools simplify common ICA operations like uploading data, running DRAGEN pipelines, and downloading results.

## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Available Scripts](#available-scripts)
- [Common Workflows](#common-workflows)
- [Configuration](#configuration)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [Contributing](#contributing)
- [FAQ](#faq)
- [Testing](#testing)
- [Pipeline Templates](#pipeline-templates)
- [Advanced Usage](#advanced-usage)
- [Development](#development)

## Features

- **Easy Data Management**
  - Upload folders with automatic session management
  - Download analysis results with progress tracking
  - Automatic retry and error handling

- **Pipeline Management**
  - Start DRAGEN pipelines with custom parameters
  - Monitor analysis progress
  - Real-time status updates

- **Flexible Interface**
  - Both API and CLI-based implementations
  - Project name resolution (no need to remember project IDs)
  - Comprehensive error messages and logging

- **Workflow Automation**
  - Combined upload-analyze-download workflow
  - Progress monitoring and status updates
  - Proper exit codes for automation

## Quick Start

### 1. Complete Workflow (Recommended)
Run an entire analysis pipeline in one command:
```bash
python ica_cli_workflow.py ./sequencing_data "My Project" "DRAGEN Pipeline" ./results \
    --params-file examples/dragen_params.json
```

### 2. Individual Steps
Or run each step separately:
```bash
# Upload data
python ica_cli_upload.py ./sequencing_data "My Project"

# Run pipeline
python ica_cli_pipeline.py "My Project" "DRAGEN Pipeline" "sequencing_data"

# Download results
python ica_cli_download.py "My Project" ANALYSIS_ID ./results
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ChaseRushton/ica-tools.git
cd ica-tools
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install ICA CLI:
   - Follow instructions at: https://help.ica.illumina.com/command-line/latest/install
   - Configure CLI: `ica configure`

4. For API-based scripts, set environment variables:
```bash
export ICA_API_KEY='your-api-key'
export ICA_BASE_URL='https://ica.illumina.com/ica/rest'  # Optional
```

## Available Scripts

### CLI-Based Tools (Recommended)

1. **Complete Workflow** (`ica_cli_workflow.py`)
   - Combines upload, pipeline execution, and download
   - Real-time progress monitoring
   - Automatic error handling
   ```bash
   python ica_cli_workflow.py INPUT_FOLDER PROJECT_NAME PIPELINE_NAME OUTPUT_DIR
   ```

2. **Folder Upload** (`ica_cli_upload.py`)
   - Upload data to ICA projects
   - Supports custom folder names
   ```bash
   python ica_cli_upload.py INPUT_FOLDER PROJECT_NAME [--folder-name NAME]
   ```

3. **Pipeline Runner** (`ica_cli_pipeline.py`)
   - Start and configure pipelines
   - Support for parameter files
   ```bash
   python ica_cli_pipeline.py PROJECT_NAME PIPELINE_NAME INPUT_FOLDER
   ```

4. **Results Download** (`ica_cli_download.py`)
   - Download analysis results
   - Progress monitoring
   ```bash
   python ica_cli_download.py PROJECT_NAME ANALYSIS_ID OUTPUT_DIR
   ```

### API-Based Tools

1. **Folder Upload & Pipeline** (`ica_folder_upload.py`)
   - Direct API integration
   - Requires project IDs
   ```bash
   python ica_folder_upload.py INPUT_FOLDER --project-id ID
   ```

2. **Results Download** (`ica_download_results.py`)
   - Direct API integration
   - Supports wait-for-completion
   ```bash
   python ica_download_results.py --project-id ID --analysis-id ID
   ```

## Common Workflows

### DRAGEN Pipeline Workflow

1. **Prepare Your Data**
   - Organize sequencing data in a folder
   - Create parameter file (see `examples/dragen_params.json`)

2. **Run Analysis**
   ```bash
   python ica_cli_workflow.py ./sequencing_data "My Project" "DRAGEN Pipeline" ./results \
       --folder-name "Sample_Jan2025" \
       --params-file examples/dragen_params.json \
       --analysis-name "DRAGEN Analysis Jan2025"
   ```

3. **Monitor Progress**
   - The workflow script provides real-time updates
   - Use `ica pipelines history` for additional details

### Custom Workflows

1. **Upload Only**
   ```bash
   python ica_cli_upload.py ./data "My Project" --folder-name "Custom_Name"
   ```

2. **Pipeline Only**
   ```bash
   python ica_cli_pipeline.py "My Project" "Pipeline Name" "Folder_Name" \
       --params-file params.json
   ```

3. **Download Only**
   ```bash
   python ica_cli_download.py "My Project" ANALYSIS_ID ./results
   ```

## Configuration

### Environment Variables

- **ICA_API_KEY** (Required for API scripts)
  - Your ICA API key
  - Keep this secure and never commit to version control

- **ICA_BASE_URL** (Optional)
  - Custom base URL for ICA API
  - Default: https://ica.illumina.com/ica/rest

### Pipeline Parameters

Create a JSON file with pipeline parameters:
```json
{
    "reference-tar": "/reference-data/hg38/hg38.fa",
    "output-directory": "/output",
    "enable-map-align": true,
    "enable-variant-caller": true
}
```

## Examples

Check the `examples/` directory for:
- Sample parameter files for different pipelines
- Example workflow scripts
- Common use case demonstrations

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure ICA CLI is configured: `ica configure`
   - Check API key for API-based scripts
   - Verify project permissions

2. **Upload Failures**
   - Check folder permissions
   - Verify project name/ID
   - Ensure sufficient storage quota

3. **Pipeline Errors**
   - Validate parameter file format
   - Check input data structure
   - Verify pipeline name and version

### Getting Help

1. Check the error message for specific details
2. Use `--help` with any script for usage information
3. Review ICA documentation for specific pipeline requirements

## Security

- Never commit API keys or credentials
- Use environment variables for sensitive data
- Keep parameter files separate from code
- Review access logs regularly

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For major changes:
1. Open an issue first
2. Discuss the proposed changes
3. Proceed with implementation after approval

## FAQ

### General Questions

1. **What's the difference between API and CLI tools?**
   - API tools use direct REST API calls
   - CLI tools use the ICA command-line interface
   - CLI tools are recommended for better stability

2. **How do I handle large datasets?**
   - Use the CLI tools for better reliability
   - Enable automatic retries
   - Consider parallel processing
   - Monitor system resources

3. **Can I use custom pipeline parameters?**
   - Yes, create a JSON file with parameters
   - Use templates from examples/
   - Parameters are pipeline-specific

### Common Issues

1. **Upload fails with timeout**
   - Check network connection
   - Try smaller batch sizes
   - Use CLI tools for better reliability
   - Enable automatic retries

2. **Pipeline fails to start**
   - Verify project permissions
   - Check parameter file format
   - Ensure input data is accessible
   - Verify pipeline name and version

3. **Download incomplete**
   - Check available disk space
   - Verify analysis completion
   - Use --retry-failed option
   - Check output permissions

### Best Practices

1. **Performance**
   - Use CLI tools for large datasets
   - Enable parallel processing
   - Monitor resource usage
   - Use appropriate batch sizes

2. **Security**
   - Rotate API keys regularly
   - Use environment variables
   - Never commit credentials
   - Review access logs

3. **Maintenance**
   - Update tools regularly
   - Monitor ICA CLI versions
   - Keep parameters updated
   - Review pipeline logs

## Testing

### Unit Tests
Run the test suite:
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest tests/ --cov=src/

# Generate coverage report
coverage html
```

### Integration Tests
Test the complete workflow:
```bash
# Run integration tests
pytest tests/integration/ --runintegration

# Test specific components
pytest tests/integration/test_upload.py
pytest tests/integration/test_pipeline.py
pytest tests/integration/test_download.py
```

### Mock Tests
Test without ICA access:
```bash
# Run mock tests
pytest tests/mock/ --mock-ica

# Generate mock data
python tests/mock/generate_mock_data.py
```

## Pipeline Templates

### DRAGEN Germline
```json
{
    "sample-id": "NA12878",
    "reference-tar": "/reference-data/hg38/hg38.fa",
    "output-directory": "/output",
    "enable-map-align": true,
    "enable-variant-caller": true,
    "vc-emit-ref-confidence": "GVCF",
    "qc-coverage-region-1": "/reference-data/hg38/coverage.bed"
}
```

### DRAGEN RNA
```json
{
    "sample-id": "RNA_sample1",
    "reference-tar": "/reference-data/hg38/hg38.fa",
    "output-directory": "/output",
    "enable-rna": true,
    "enable-rna-quantification": true,
    "annotation-file": "/reference-data/hg38/genes.gtf"
}
```

### DRAGEN Joint Calling
```json
{
    "sample-id": "cohort1",
    "reference-tar": "/reference-data/hg38/hg38.fa",
    "output-directory": "/output",
    "enable-joint-genotyping": true,
    "variant-caller-prefix": "joint_called",
    "gvcf-gq-bands": "10,20,30,40,50,60",
    "gvcf-file": "/input/sample.g.vcf.gz"
}
```

## Advanced Usage

### Parallel Processing
Run multiple analyses simultaneously:
```bash
# Start multiple analyses in parallel
for sample in sample1 sample2 sample3; do
    python ica_cli_workflow.py ./$sample "My Project" "DRAGEN Pipeline" ./results/$sample \
        --folder-name "${sample}_analysis" \
        --params-file params.json &
done
```

### Custom Pipeline Parameters
Generate pipeline parameters dynamically:
```python
import json

def create_dragen_params(sample_id, reference):
    return {
        "sample-id": sample_id,
        "reference-tar": reference,
        "output-directory": f"/output/{sample_id}",
        "enable-map-align": True,
        "enable-variant-caller": True
    }

# Save parameters
params = create_dragen_params("sample1", "/references/hg38.fa")
with open("params.json", "w") as f:
    json.dump(params, f, indent=4)
```

### Error Recovery
Resume failed analyses:
```bash
# Check analysis status
python ica_cli_download.py "My Project" ANALYSIS_ID ./results --status-only

# Download results from specific analysis step
python ica_cli_download.py "My Project" ANALYSIS_ID ./results \
    --step-name "variant_calling" \
    --retry-failed
```

### Batch Processing
Process multiple samples using a manifest:
```bash
# samples.txt
# sample_id,input_folder,params_file
# sample1,/data/sample1,params1.json
# sample2,/data/sample2,params2.json

while IFS=, read -r sample_id folder params; do
    python ica_cli_workflow.py "$folder" "My Project" "DRAGEN Pipeline" \
        ./results/$sample_id --params-file $params
done < samples.txt
```

## Development

### Setup Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt
```

### Code Style
```bash
# Install style checkers
pip install black flake8 isort

# Format code
black src/
isort src/

# Check style
flake8 src/
```

### Documentation
Generate documentation:
```bash
# Install documentation tools
pip install sphinx sphinx-rtd-theme

# Generate docs
cd docs
make html
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run hooks
pre-commit run --all-files
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
