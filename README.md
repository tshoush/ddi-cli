# DDI CLI

A CLI tool to sync network data from cloud providers to Infoblox.

## Project Structure

```
ddi-cli/
├── ddi/
│   ├── __init__.py
│   ├── cli.py          # Core CLI logic (using Click)
│   ├── config.py       # Configuration management
│   ├── infoblox.py     # Infoblox WAPI interaction
│   └── providers/
│       ├── __init__.py
│       └── aws.py      # AWS-specific logic
├── tests/
│   ├── __init__.py
│   └── test_config.py
├── .gitignore
├── config.json.example # Example configuration file
├── ddi-cli.py          # Main entry point
└── requirements.txt    # Project dependencies
```

## Setup

### Prerequisites

*   **Python 3.6+**: The tool requires Python version 3.6 or newer.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd ddi-cli
    ```

2.  **Run the setup script:**

    The `setup.sh` script will create a virtual environment and install all dependencies.

    ```bash
    ./setup.sh
    ```
    *   You will be prompted to provide the path to your Python 3 executable (default: `python3`).
    *   The script will create a `venv` directory and install requirements.

3.  **Activate the environment:**

    ```bash
    source venv/bin/activate
    ```

### Configuration

The tool uses a `config.json` file to store your Infoblox and cloud provider settings. If `config.json` does not exist, it will be automatically created from `config.json.example` the first time you run the tool.

You can edit `config.json` manually or use the interactive configuration dashboard when running the tool.

```json
{
    "infoblox": {
        "grid_master_ip": "YOUR_INFOBLOX_IP",
        "wapi_version": "2.13.1",
        "admin_name": "YOUR_INFOBLOX_USERNAME",
        "password": "YOUR_INFOBLOX_PASSWORD"
    },
    "aws": {
        "vpc_export_file": "/path/to/your/aws_vpc_export.json"
    }
}
```

## Usage

The main entry point is `ddi-cli.py`.

### Interactive Mode (Recommended)

Simply run the script without arguments to enter the interactive mode:

```bash
python ddi-cli.py
```

1.  **Configuration Dashboard**: You will be presented with a dashboard to view and update your Infoblox settings.
2.  **Network View Selection**: You can choose to operate on a specific Network View (fetched from Infoblox) or the default 'All'.
3.  **Main Menu**: Navigate through the available commands (Audit, AWS, Search, etc.) using the numbered menu.

### Command Line Arguments

You can also run specific commands directly:

```bash
# Sync AWS data
python ddi-cli.py aws sync

# Search for a resource
python ddi-cli.py search "my-resource"
```

## Development

This project uses `click` for the CLI, `requests` for API calls, and is structured to be easily extendable. To add a new cloud provider, you can create a new module in the `ddi/providers/` directory and add a new command to `ddi/cli.py`.
