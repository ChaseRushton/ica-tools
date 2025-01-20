# API Reference

## Core Modules

### Upload Module
```python
from ica_tools import upload

# Upload a folder
upload.folder(
    folder_path: str,
    project_name: str,
    session_name: str = None,
    validate: bool = True
) -> str
```

### Download Module
```python
from ica_tools import download

# Download analysis results
download.results(
    project_name: str,
    analysis_id: str,
    output_path: str,
    verify: bool = True
) -> str
```

### Pipeline Module
```python
from ica_tools import pipeline

# Launch a pipeline
pipeline.launch(
    project_name: str,
    pipeline_name: str,
    params: dict,
    data_ids: List[str]
) -> str
```

## Utility Modules

### Project Manager
```python
from ica_tools import project

# List projects
project.list_all() -> List[Dict]

# Clean up old data
project.cleanup(
    project_name: str,
    older_than: int = 30,
    dry_run: bool = True
) -> None
```

### Monitor
```python
from ica_tools import monitor

# Monitor pipeline status
monitor.watch_pipeline(
    project_name: str,
    analysis_id: str,
    notify: List[str] = None
) -> None
```

### Batch Processor
```python
from ica_tools import batch

# Process multiple samples
batch.process_samples(
    config_file: str,
    parallel: bool = True,
    max_workers: int = 4
) -> Dict[str, str]
```

## Error Handling

All modules use a consistent error handling approach:

```python
from ica_tools.exceptions import (
    ICAError,
    AuthenticationError,
    ValidationError,
    NetworkError
)

try:
    result = upload.folder("./data", "My Project")
except AuthenticationError:
    # Handle authentication issues
except ValidationError:
    # Handle validation failures
except NetworkError:
    # Handle network issues
except ICAError:
    # Handle other ICA-related errors
```

## Events

Subscribe to events for real-time updates:

```python
from ica_tools.events import subscribe

# Subscribe to upload events
@subscribe("upload:progress")
def handle_progress(event):
    print(f"Upload progress: {event.progress}%")

# Subscribe to pipeline events
@subscribe("pipeline:status")
def handle_status(event):
    print(f"Pipeline status: {event.status}")
```

## Configuration

Load configuration from file or environment:

```python
from ica_tools.config import load_config

# Load from file
config = load_config("config.yaml")

# Load from environment
config = load_config(from_env=True)
```

## Middleware

PCD integration middleware:

```python
from ica_tools.middleware import PCDAdapter

# Create adapter
adapter = PCDAdapter(config_file="pcd_config.yaml")

# Transform data
transformed = adapter.transform_data(data)

# Handle events
adapter.handle_event(event)
```

For more examples, see our [Examples](examples.md) documentation.
