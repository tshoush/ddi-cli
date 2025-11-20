# Architecture: DDI-CLI

## 1. Overview

This document describes the architecture of the DDI-CLI. The architecture is designed to be modular, scalable, and maintainable, allowing for the easy addition of new cloud providers and features.

## 2. High-Level Architecture

The tool is a Python-based command-line interface (CLI) application that follows a layered architecture.

```
+-------------------------------------------------+
|               Command-Line Interface            |
|                    (cli.py)                     |
+-------------------------------------------------+
|                Configuration Layer              |
|                    (config.py)                  |
+-------------------------------------------------+
|                  Core Logic Layer               |
|                                                 |
|  +-----------------+   +----------------------+ |
|  | Cloud Providers |   |  Infoblox Manager    | |
|  |  (providers/)   |   |   (infoblox.py)      | |
|  +-----------------+   +----------------------+ |
|                                                 |
+-------------------------------------------------+
```

### 2.1. Layers

*   **Command-Line Interface (CLI):** This is the entry point for the user. It is responsible for parsing command-line arguments, displaying help messages, and orchestrating the overall workflow. It is built using the `click` library.
*   **Configuration Layer:** This layer is responsible for loading and managing the application's configuration from the `config.json` file. It provides a centralized way to access configuration values.
*   **Core Logic Layer:** This layer contains the main business logic of the application. It is further divided into two main components:
    *   **Cloud Providers:** A collection of modules, each responsible for interacting with a specific cloud provider's API or data export format.
    *   **Infoblox Manager:** A dedicated module for handling all communication with the Infoblox WAPI.

## 3. Project Structure

The project is organized into the following directory structure:

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

## 4. Components

### 4.1. `ddi-cli.py`

The main entry point of the application. Its only role is to invoke the CLI.

### 4.2. `ddi/cli.py`

*   Uses the `click` library to define the CLI commands (e.g., `aws`, `azure`).
*   Acts as the controller, orchestrating the flow of data between the configuration, cloud providers, and the Infoblox manager.
*   Initializes the `InfobloxManager` and passes it to the relevant commands.

### 4.3. `ddi/config.py`

*   Responsible for loading the `config.json` file.
*   Provides helper functions to safely access nested configuration values.
*   Handles errors related to missing or malformed configuration files.

### 4.4. `ddi/infoblox.py`

*   Contains the `InfobloxManager` class, which encapsulates all the logic for interacting with the Infoblox WAPI.
*   Handles authentication, session management, and the construction of WAPI requests.
*   Provides methods for common Infoblox operations (e.g., `get_network_views`, `sync_network`).

### 4.5. `ddi/providers/`

This package contains modules for each supported cloud provider.

#### 4.5.1. `ddi/providers/aws.py`

*   Contains the logic for parsing the AWS VPC export file.
*   Transforms the AWS-specific data into a generic format that can be consumed by the `InfobloxManager`.
*   The `sync_aws_to_infoblox` function orchestrates the process of reading the AWS data and sending it to the `InfobloxManager`.

## 5. Data Flow (AWS Example)

1.  The user runs `python ddi-cli.py aws`.
2.  `ddi-cli.py` calls the `main` function in `ddi/cli.py`.
3.  The `main` function in `cli.py` loads the configuration and instantiates the `InfobloxManager`.
4.  The `aws` command in `cli.py` is invoked.
5.  The `aws` command calls the provider's `sync` method (defined in `ddi/providers/aws.py`), passing it the `InfobloxManager` instance.
6.  `sync_aws_to_infoblox` parses the VPC export file.
7.  For each network in the export file, `sync_aws_to_infoblox` calls the `sync_network` method on the `InfobloxManager` instance.
8.  The `InfobloxManager` sends the appropriate WAPI request to the Infoblox grid.

## 6. Extensibility

To add a new cloud provider (e.g., Azure):

1.  Create a new file: `ddi/providers/azure.py`.
2.  Implement the logic for interacting with Azure (e.g., parsing an export file or calling the Azure API).
3.  Add a new command to `ddi/cli.py` called `azure`.
4.  This new command will call the Azure-specific logic in `ddi/providers/azure.py`.
