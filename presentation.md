# DDI CLI Tool
## Cloud to Infoblox Synchronization

---

# Overview

**DDI CLI** is a command-line tool designed to synchronize network data from cloud providers (like AWS) to Infoblox DDI.

**Key Features:**
*   **Automated Sync**: Keep Infoblox up-to-date with cloud network changes.
*   **Extensible**: Modular design allows adding new providers (Azure, GCP).
*   **Interactive**: User-friendly menu system for easy navigation.
*   **Audit & Search**: Tools to find and verify resources across platforms.

---

# Architecture

The tool follows a layered architecture for flexibility and maintainability:

*   **CLI Layer (`ddi/cli.py`)**: Handles user interaction, menus, and command dispatch. Built with `click`.
*   **Configuration (`ddi/config.py`)**: Manages settings via `config.json`.
*   **Core Logic (`ddi/infoblox.py`)**: Abstraction layer for Infoblox WAPI interactions.
*   **Providers (`ddi/providers/`)**:
    *   `base.py`: Abstract base class for all providers.
    *   `aws.py`: AWS implementation (VPC export, tagging).

---

# Installation & Setup

Getting started is simple:

1.  **Clone the Repo**:
    ```bash
    git clone https://github.com/tshoush/ddi-cli.git
    ```
2.  **Run Setup**:
    ```bash
    ./setup.sh
    ```
    *   Creates a virtual environment.
    *   Installs dependencies.
3.  **Activate**:
    ```bash
    source venv/bin/activate
    ```

---

# Interactive Workflow

The tool features a robust interactive mode:

1.  **Configuration Dashboard**:
    *   View and edit Grid Master IP, Admin Name, and Password.
    *   Visual "box" UI for clarity.

2.  **Network View Selection**:
    *   Choose to operate on 'All' views or a specific one.
    *   Dynamically fetches available views from Infoblox.

3.  **Main Menu**:
    *   Easy navigation to Audit, Search, and Provider commands.

---

# Key Commands

*   **`audit`**: Scan all configured providers and report on resources.
*   **`search <term>`**: Find a resource (IP, name, ID) across all clouds.
*   **`aws sync`**: Synchronize AWS VPC data to Infoblox.
*   **`aws attributes analyze`**: Compare AWS tags with Infoblox Extensible Attributes.

---

# Future Roadmap

*   **Azure Support**: Implement `AzureProvider` for Microsoft Azure integration.
*   **GCP Support**: Add Google Cloud Platform support.
*   **Automated Scheduling**: Built-in cron/scheduler for periodic syncs.
*   **Enhanced Reporting**: HTML or PDF report generation for audits.

---

# Thank You!

**Questions?**

Repository: https://github.com/tshoush/ddi-cli
