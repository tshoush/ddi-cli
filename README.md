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

### Installation & Virtual Environment

The tool automatically manages its own Python virtual environment. You just need to run the `ddi-cli.py` script with your system's Python 3.6+ interpreter.

1.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd ddi-cli
    ```

2.  **Run the tool for the first time:**

    Execute the `ddi-cli.py` script. It will prompt you to create a virtual environment and install dependencies.

    ```bash
    python ddi-cli.py aws
    ```
    *   You will be prompted for the location to create the virtual environment (default: `~/DDI-Apps/ddi-cli`). Press Enter to accept the default or provide a custom path.
    *   The script will create the virtual environment and install all necessary dependencies from `requirements.txt`.
    *   It will then relaunch itself within this new virtual environment.

### Configuration

The tool uses a `config.json` file to store your Infoblox and cloud provider settings. If `config.json` does not exist, it will be automatically created from `config.json.example` the first time you run the tool.

1.  **Review and Edit your configuration:**

    Open `config.json` (which will be created automatically if missing) in a text editor and fill in the details for your environment.

    ```json
    {
        "infoblox": {
            "grid_master_ip": "YOUR_INFOBLOX_IP",
            "wapi_version": "2.13.1",
            "username": "YOUR_INFOBLOX_USERNAME",
            "password": "YOUR_INFOBLOX_PASSWORD",
            "network_view": "default"
        },
        "aws": {
            "vpc_export_file": "/path/to/your/aws_vpc_export.json"
        }
    }
    ```
    *   **`grid_master_ip`**: The IP address of your Infoblox Grid Master.
    *   **`username` / `password`**: Your Infoblox WAPI credentials. If these are missing, the tool will prompt you for them and offer to save them to `config.json`.
    *   **`vpc_export_file`**: The full path to your AWS VPC export file. If you leave this empty, the tool will prompt you for the path when you run it.

## Usage

The main entry point is `ddi-cli.py`. You can use it with different subcommands for each cloud provider.

### AWS

To sync AWS VPC data, use the `aws` subcommand:

```bash
python ddi-cli.py aws
```

The tool will then connect to your Infoblox grid and process the VPC export file.

## Development

This project uses `click` for the CLI, `requests` for API calls, and is structured to be easily extendable. To add a new cloud provider, you can create a new module in the `ddi/providers/` directory and add a new command to `ddi/cli.py`.
