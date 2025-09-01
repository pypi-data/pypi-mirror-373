# FIS MCP Server

AWS Fault Injection Simulator (FIS) MCP Server for managing chaos engineering experiments.

## Features

- Create and manage FIS experiment templates
- Start and stop chaos engineering experiments
- List and monitor experiment status
- Retrieve AWS resources for targeting

## Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:

```bash
aws configure
```

## Usage

### Running the server directly

```bash
python index.py
```

### Using with MCP CLI

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "fis-mcp-server": {
      "command": "python",
      "args": ["index.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

## Available Tools

- `create_experiment_template`: Create a new FIS experiment template
- `start_experiment`: Start a chaos engineering experiment
- `stop_experiment`: Stop a running experiment
- `list_experiment_templates`: List all experiment templates
- `get_experiment_template`: Get details of a specific template
- `list_experiments`: List all experiments
- `get_experiment`: Get details of a specific experiment
- `get_aws_resources`: Retrieve available AWS resources for targeting

## Requirements

- Python 3.10+
- AWS credentials configured
- Appropriate IAM permissions for FIS operations
