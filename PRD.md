# Product Requirements Document: DDI-CLI

## 1. Overview

This document outlines the requirements for the DDI-CLI, a command-line interface (CLI) application designed to synchronize network information from various public cloud providers with an on-premises Infoblox DDI solution.

## 2. Goals

*   **Primary Goal:** To automate the process of updating Infoblox with network data from public clouds, ensuring that the Infoblox database is an accurate and up-to-date source of truth for all network allocations.
*   **Secondary Goal:** To create a flexible and extensible tool that can be easily adapted to support new cloud providers and customized to different environments.

## 3. Target Audience

*   Network Administrators
*   Cloud Administrators
*   DevOps Engineers

## 4. Features

### 4.1. Core Functionality

*   **Configuration:** The tool will be configured via a JSON file (`config.json`) that stores credentials and settings for Infoblox and cloud providers.
*   **CLI Interface:** The tool will provide a clear and consistent CLI for initiating synchronization tasks.
*   **Extensibility:** The architecture will be modular, allowing for the addition of new cloud providers with minimal effort.

### 4.2. Infoblox Integration

*   **WAPI Support:** The tool will communicate with Infoblox using the WAPI (Web API), with a default version of 2.13.1.
*   **Network Views:** The tool will support specifying an Infoblox network view for all operations.
*   **Network Creation/Update:** The tool will be able to create and update network containers and IP ranges within Infoblox based on the data from cloud providers.

### 4.3. Cloud Provider Support

The tool will be designed to support multiple cloud providers, with an initial focus on AWS.

#### 4.3.1. Amazon Web Services (AWS)

*   **Data Source:** The tool will consume an AWS VPC export file (in JSON format) as the source of network information.
*   **Synchronization:** The tool will parse the VPC export file and synchronize the VPC CIDR blocks with Infoblox.

#### 4.3.2. Future Cloud Providers

The following cloud providers are planned for future implementation:

*   Microsoft Azure (`-az`)
*   Google Cloud Platform (`-gc`)
*   Alibaba Cloud (`-alibab`)
*   Oracle Cloud Infrastructure (`-or`)

## 5. User Stories

*   As a Network Administrator, I want to be able to run a single command to update Infoblox with all the VPCs from my AWS account, so that I can save time and reduce manual errors.
*   As a Cloud Administrator, I want to be able to easily configure the tool with my cloud credentials, so that I can get up and running quickly.
*   As a DevOps Engineer, I want to be able to integrate this tool into my automation pipelines, so that I can ensure that our Infoblox data is always in sync with our dynamic cloud environments.

## 6. Non-Functional Requirements

*   **Performance:** The tool should be able to handle large cloud environments with thousands of networks.
*   **Security:** The tool must securely handle all credentials and sensitive information. Passwords should not be stored in plain text in the configuration file where possible (future enhancement: support for environment variables or a secrets management system).
*   **Usability:** The CLI should be intuitive and provide clear feedback to the user.
*   **Reliability:** The tool should be robust and handle errors gracefully.

## 7. Assumptions and Dependencies

*   The user will have the necessary permissions to access the Infoblox WAPI.
*   The user will be able to generate the required network export files from their cloud provider.
*   The initial version will focus on AWS, with other providers to be added later.
