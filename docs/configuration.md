# Configuration Guide

## Environment Variables

### Required Variables
```bash
# ICA API Configuration
ICA_API_KEY="your-api-key"
ICA_BASE_URL="your-base-url"

# Optional Debug Mode
ICA_LOG_LEVEL="DEBUG"  # Default: INFO
```

### Optional Variables
```bash
# Email Notifications
SMTP_SERVER="smtp.example.com"
SMTP_PORT="587"
SMTP_USERNAME="your-username"
SMTP_PASSWORD="your-password"

# Slack Notifications
SLACK_WEBHOOK_URL="your-webhook-url"

# PCD Integration
PCD_API_URL="pcd-api-url"
PCD_API_KEY="pcd-api-key"
```

## Configuration Files

### Main Configuration
```yaml
# config.yaml
api:
  key: ${ICA_API_KEY}
  base_url: ${ICA_BASE_URL}
  timeout: 300
  retries: 3

logging:
  level: INFO
  file: ~/.ica/logs/ica.log
  format: "%(asctime)s [%(levelname)s] %(message)s"

upload:
  chunk_size: 1048576  # 1MB
  max_retries: 3
  validate: true

download:
  chunk_size: 1048576  # 1MB
  verify: true
  resume: true

pipeline:
  max_concurrent: 4
  monitor_interval: 60
```

### Email Configuration
```yaml
# email_config.yaml
smtp:
  server: ${SMTP_SERVER}
  port: ${SMTP_PORT}
  username: ${SMTP_USERNAME}
  password: ${SMTP_PASSWORD}
  use_tls: true

notifications:
  on_start: true
  on_complete: true
  on_error: true
  recipients:
    - admin@example.com
    - team@example.com

templates:
  start: templates/email/start.html
  complete: templates/email/complete.html
  error: templates/email/error.html
```

### Slack Configuration
```yaml
# slack_config.yaml
webhook_url: ${SLACK_WEBHOOK_URL}

channels:
  default: "#pipeline-alerts"
  errors: "#pipeline-errors"
  success: "#pipeline-success"

notifications:
  on_start: false
  on_complete: true
  on_error: true

templates:
  start: templates/slack/start.json
  complete: templates/slack/complete.json
  error: templates/slack/error.json
```

### PCD Configuration
```yaml
# pcd_config.yaml
api:
  url: ${PCD_API_URL}
  key: ${PCD_API_KEY}
  timeout: 300

data_mapping:
  input:
    - source: "metadata.json"
      target: "pcd_metadata.json"
      transform: "transform_metadata"
    
    - source: "sample_sheet.csv"
      target: "pcd_samples.csv"
      transform: "transform_samples"

  output:
    - source: "results.json"
      target: "pcd_results.json"
      transform: "transform_results"

validation:
  input:
    - validate_structure
    - check_metadata
    - verify_samples
  
  output:
    - validate_results
    - check_completeness
    - verify_format

transformations:
  metadata:
    - map_fields
    - validate_required
    - format_dates
  
  samples:
    - standardize_ids
    - validate_types
    - check_duplicates
  
  results:
    - extract_metrics
    - format_output
    - generate_summary
```

## Templates

### Email Templates
```html
<!-- templates/email/complete.html -->
<html>
<body>
  <h1>Pipeline Complete</h1>
  <p>Project: {{project_name}}</p>
  <p>Analysis ID: {{analysis_id}}</p>
  <p>Status: {{status}}</p>
  <p>Duration: {{duration}}</p>
  <p>Results: <a href="{{results_url}}">Download</a></p>
</body>
</html>
```

### Slack Templates
```json
// templates/slack/complete.json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "Pipeline Complete"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Project:*\n{{project_name}}"
        },
        {
          "type": "mrkdwn",
          "text": "*Status:*\n{{status}}"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Results:* <{{results_url}}|Download>"
      }
    }
  ]
}
```

## Usage

### Loading Configuration
```python
from ica_tools.config import load_config

# Load main config
config = load_config("config.yaml")

# Load email config
email_config = load_config("email_config.yaml")

# Load slack config
slack_config = load_config("slack_config.yaml")

# Load PCD config
pcd_config = load_config("pcd_config.yaml")
```

### Using Configuration
```python
from ica_tools import pipeline, notifications

# Start pipeline with notifications
analysis_id = pipeline.launch(
    "My Project",
    "DRAGEN Pipeline",
    params={...},
    notify={
        "email": ["team@example.com"],
        "slack": ["#pipeline-alerts"]
    }
)

# Monitor with custom configuration
pipeline.monitor(
    analysis_id,
    config=config,
    email_config=email_config,
    slack_config=slack_config
)
```

For more examples, see our [Examples](examples.md) documentation.
