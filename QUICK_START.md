# Quick Start Guide

This guide will help you get the DDI-CLI up and running in a few simple steps.

## Prerequisites

*   **Python 3.6+**: The tool requires Python version 3.6 or newer.
*   An Infoblox grid with WAPI access
*   An export of your cloud provider's network information (e.g., an AWS VPC export file)

## 1. Installation & Setup

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

## 2. Configuration

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

## 3. Running the Tool

You are now ready to sync your network data.

### Syncing AWS Data

To sync your AWS VPCs with Infoblox, run the following command:

```bash
python ddi-cli.py aws
```

The tool will then connect to your Infoblox grid and process the VPC export file.

## 4. Testing

The project includes a suite of unit and integration tests to verify its functionality.

### Running Unit Tests

Unit tests are designed to run without any external dependencies. You can run them using `pytest`:

```bash
pytest tests/
```

### Running Integration Tests

Integration tests are designed to run against a real Infoblox instance. To run these tests, you first need to create a `config.json` file in the project root with your Infoblox credentials. You can copy the `config.json.example` file to get started:

```bash
cp config.json.example config.json
```

Then, edit `config.json` with your Infoblox details.

Once the `config.json` file is configured, you can run the integration tests:

```bash
pytest tests/test_cli_integration.py
```

## What's Next?

For more detailed information about the project's architecture, features, and development, please refer to the following documents:

*   `README.md`
*   `PRD.md`
*   `Architecture.md`
