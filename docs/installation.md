# Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/ChaseRushton/ica-tools.git
cd ica-tools
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:
```bash
ICA_API_KEY=your-api-key
ICA_BASE_URL=your-base-url
```

Or set them in your environment:
```bash
export ICA_API_KEY="your-api-key"
export ICA_BASE_URL="your-base-url"
```

### 4. Verify Installation
```bash
python -m pytest tests/
```

## Configuration

### API Configuration
1. Obtain your ICA API key from the ICA web interface
2. Set the base URL for your ICA instance

### Email Notifications (Optional)
To enable email notifications:
```bash
export SMTP_SERVER="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="your-username"
export SMTP_PASSWORD="your-password"
```

### Slack Notifications (Optional)
To enable Slack notifications:
```bash
export SLACK_WEBHOOK_URL="your-webhook-url"
```

## Troubleshooting

### Common Issues

1. **API Authentication Failed**
   - Verify your API key is correct
   - Check if your API key has expired
   - Ensure your base URL is correct

2. **Dependencies Installation Failed**
   - Update pip: `pip install --upgrade pip`
   - Install wheel: `pip install wheel`
   - Try installing dependencies one by one

3. **Permission Issues**
   - Check file permissions
   - Verify environment variable access
   - Ensure write permissions in output directories

For more help, see our [Troubleshooting Guide](troubleshooting.md)
