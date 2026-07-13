# RHEL 10 Zero-Touch Provisioning (ZTP) Pipeline

This repository contains the architecture and deployment configurations for an end-to-end Zero-Touch Provisioning (ZTP) pipeline. The system automates the generation of custom Red Hat Enterprise Linux (RHEL) 10 images in the cloud and orchestrates their deployment to bare-metal edge devices via a local PXE-boot environment.

> **Note:** For step-by-step deployment, credential configuration, and installation instructions, please refer to [`SETUP.md`](./SETUP.md).

---

## System Architecture

The pipeline bridges cloud infrastructure (Microsoft Azure, Red Hat Console) with local network hardware (OpenWRT) to achieve a fully automated installation loop. 

### High-Level Data Flow

1. **Code Commit:** Infrastructure and automation logic are committed to the `main` branch of this GitHub repository.
2. **CI/CD Sync:** GitHub Actions authenticates with Azure via Service Principal credentials and deploys the latest Python automation code to an Azure Function App.
3. **Image Compilation:** The Azure Function App interacts with the Red Hat Image Builder API to trigger or monitor the build of a specific RHEL 10 Blueprint.
4. **Cloud Storage:** Upon a successful build, Red Hat Image Builder pushes the generated system image (`.vhd` or raw file) directly to a designated Microsoft Azure Storage Account.
5. **Notification:** The Azure Function triggers an SMTP notification to alert administrators that a new image is staged and ready for edge deployment.
6. **Edge Network Preparation:** A local OpenWRT router is configured to serve the deployment environment. Its startup scripts (`rc.local`) initialize a local TFTP/HTTP server with an iPXE bootloader.
7. **Bare-Metal Provisioning:** The target hardware is connected to the OpenWRT router via Ethernet. It powers on, initiates a PXE boot request, pulls the iPXE configuration, and automatically pulls and installs the staged RHEL 10 image.

---

## Repository Structure

The repository is organized to separate cloud infrastructure orchestration, CI/CD deployment pipelines, and local edge hardware configurations.

```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD deployment pipeline for the Function App
├── azure-function/             # Serverless orchestration backend (Python 3.11)
│   ├── host.json               # Global configuration for the Azure Function host
│   ├── requirements.txt        # Python package dependencies
│   └── ztp_orchestrator/       # Function module for RHEL API & Azure Storage tracking
│       ├── __init__.py         # Core runtime logic and API integration
│       └── function.json       # Input/Output bindings configuration
├── edge/                       # Local provisioning and network configurations
│   ├── openwrt/
│   │   └── rc.local            # Router startup script for runtime synchronization
│   └── ipxe/
│       └── boot.ipxe           # iPXE script for orchestrating hardware boot targets
├── README.md                   # System architecture and directory overview
└── SETUP.md                    # Step-by-step infrastructure provisioning guide
```

Component Breakdown & File Explanations

1. Continuous Integration & Deployment [`/.github`](/.github)

[`workflows/deploy.yml`](workflows/deploy.yml)
This GitHub Actions workflow automates the continuous deployment of the serverless backend. Whenever changes are pushed to main, this action runs a runner environment, packages the azure-function/ directory, and deploys it directly to the Azure Linux Function App. It leverages the repository secrets AZURE_CREDENTIALS (Service Principal JSON) and AZURE_FUNC_PUBLISH_PROFILE to securely interface with the Azure SCM endpoint.

2. Serverless Orchestration Engine [`/azure-function`](/azure-function)

This directory contains the complete application code for the Azure Function App running on a serverless Linux Consumption plan with a Python 3.11 runtime.

    [`host.json`](host.json): Configures global settings affecting the Function App instance, such as extension bundles, function timeouts, and structured logging parameters (e.g., routing stdout to Application Insights).

    [`requirements.txt`](requirements.txt): Specifies dependencies, including azure-functions for execution contexts, requests for Red Hat Image Builder API calls, and azure-identity & azure-storage-blob for authenticated interactions with the Azure Storage data plane.

    [`ztp_orchestrator/function.json`](ztp_orchestrator/function.json): Defines the programmatic bindings, mapping how the function is triggered (HTTP or Timer) and ensuring it knows how to receive data and log execution metadata.

    [`ztp_orchestrator/__init__.py`](ztp_orchestrator/__init__.py): The primary execution engine. It resolves environment variables, exchanges the offline token for a short-lived Bearer token, polls the Red Hat API for build status, and queries the Azure storage bucket for the finalized .vhd. Finally, it triggers the SMTP alert notification.

3. Red Hat Image Builder (Cloud Configuration)

Defines the state and configuration of the operating system before it ever touches hardware.

    Configured via Blueprints for RHEL 10 (x86_64) targeting a Bare Metal Installer output.

    Kickstart: Injects a custom bash script that modifies `/etc/gdm/custom.conf` to force an automatic graphical login (Wayland) upon the first system boot, ensuring a zero-touch experience.

4. Edge Provisioning Environment [`/OpenWRT`](/OpenWRT) 

Configuration files destined for the local physical infrastructure layer responsible for bootstrapping target hardware.

    [`autoexec.ipxe`](autoexec.ipxe): Compatibility file that merely chains to `boot.ipxe```. Used for compatibility issues with certain manufacturers.

    [`boot.ipxe`](boot.ipxe): The foundational script interpreted by the target hardware during a network boot sequence. It bridges the gap between the hardware's native PXE ROM and modern network protocols, allowing the machine to fetch the massive OS image over HTTP(S) directly from Azure Storage.

    [`rc.local`](rc.local): The initialization script pushed to the local OpenWRT gateway router. Executed automatically at boot, it binds network interfaces and initializes local web/TFTP directory paths so the router can immediately serve installation components without manual administration.

Security & Credential Management

All components are designed to operate with least-privilege access to ensure credentials remain secure throughout the pipeline lifecycle:

    Azure RBAC: Roles such as Storage Blob Data Reader, Storage Blob Data Contributor, and Contributor are strictly scoped to the exact Azure resource group.

    API Authentication: Interaction with the Red Hat API is secured using Short-Lived Access Tokens, generated dynamically from an Offline Token during runtime.

    Repository Secrets: No UUIDs, tenant IDs, subscription IDs, or plain-text OS passwords are stored in the codebase. All sensitive environmental variables are exclusively injected via Azure Function App Settings and GitHub Secrets.