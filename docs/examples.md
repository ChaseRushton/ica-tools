# Examples

## Basic Usage

### Upload Data and Run Pipeline
```python
from ica_tools import upload, pipeline, download

# Upload data
data_id = upload.folder(
    "./sequencing_data",
    "My Project",
    validate=True
)

# Run pipeline
analysis_id = pipeline.launch(
    "My Project",
    "DRAGEN Pipeline",
    params={
        "ref_genome": "hg38",
        "output_format": "CRAM"
    },
    data_ids=[data_id]
)

# Download results
download.results(
    "My Project",
    analysis_id,
    "./results"
)
```

### Monitor Pipeline with Notifications
```python
from ica_tools import monitor

# Watch pipeline with email notifications
monitor.watch_pipeline(
    "My Project",
    "analysis-123",
    notify=["email@example.com"]
)

# Watch pipeline with Slack notifications
monitor.watch_pipeline(
    "My Project",
    "analysis-123",
    notify=["#pipeline-alerts"]
)
```

## Advanced Usage

### Batch Processing
```python
from ica_tools import batch

# Process multiple samples in parallel
results = batch.process_samples(
    "batch_config.yaml",
    parallel=True,
    max_workers=4
)

# Sample batch_config.yaml:
samples:
  - id: sample1
    data: ./sample1
    params:
      ref_genome: hg38
      output_format: CRAM
  - id: sample2
    data: ./sample2
    params:
      ref_genome: hg38
      output_format: BAM
```

### Project Management
```python
from ica_tools import project

# List all projects
projects = project.list_all()

# Clean up old data
project.cleanup(
    "My Project",
    older_than=30,  # days
    dry_run=True    # preview changes
)

# Archive project data
project.archive(
    "My Project",
    destination="s3://my-bucket/archives"
)
```

### Custom Event Handling
```python
from ica_tools.events import subscribe

# Track upload progress
@subscribe("upload:progress")
def handle_progress(event):
    print(f"Upload progress: {event.progress}%")
    if event.progress == 100:
        print("Upload complete!")

# Monitor pipeline status
@subscribe("pipeline:status")
def handle_status(event):
    if event.status == "COMPLETED":
        print(f"Pipeline {event.id} completed successfully!")
    elif event.status == "FAILED":
        print(f"Pipeline {event.id} failed: {event.error}")
```

### PCD Integration
```python
from ica_tools.middleware import PCDAdapter

# Initialize adapter
adapter = PCDAdapter("pcd_config.yaml")

# Transform and upload data
data_id = adapter.upload_data(
    "./data",
    transform=True
)

# Run pipeline with PCD parameters
analysis_id = adapter.run_pipeline(
    data_id,
    pipeline="DRAGEN_PCD"
)

# Download and transform results
adapter.download_results(
    analysis_id,
    "./results",
    transform=True
)
```

## Configuration Examples

### Email Configuration
```yaml
# email_config.yaml
smtp:
  server: smtp.example.com
  port: 587
  username: your-username
  password: ${SMTP_PASSWORD}  # from environment

notifications:
  on_start: true
  on_complete: true
  on_error: true
  recipients:
    - admin@example.com
    - team@example.com
```

### Slack Configuration
```yaml
# slack_config.yaml
webhook_url: ${SLACK_WEBHOOK_URL}  # from environment

channels:
  default: "#pipeline-alerts"
  errors: "#pipeline-errors"

notifications:
  on_start: false
  on_complete: true
  on_error: true
```

### PCD Configuration
```yaml
# pcd_config.yaml
pcd:
  api_url: ${PCD_API_URL}
  api_key: ${PCD_API_KEY}

transformations:
  input:
    - validate_structure
    - convert_metadata
    - check_requirements
  
  output:
    - format_results
    - generate_reports
    - validate_output
```

For more detailed examples, see our [API Reference](api.md).
