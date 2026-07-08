# RHEL Zero-Touch Provisioning (ZTP) Orchestrator

An automated cloud-to-edge pipeline leveraging **RHEL Image Builder**, **Azure Functions (Python)**, and **OpenWRT iPXE** to provision bare-metal systems with immutable golden images.

## Repository Layout
- `/Azure`: Contains the serverless Azure Function cron trigger and Red Hat API watcher.
- `/OpenWRT`: Contains the iPXE boot configuration for edge hardware consumption.

## Workflow Architecture
1. **Azure Timer Trigger** fires every 2 hours via cron (`0 0 */2 * * *`).
2. **Azure Function** issues a `POST` request to Red Hat Image Builder using a static Blueprint UUID.
3. **Red Hat Image Builder** compiles the image and securely exports the final VHD artifact directly into **Azure Blob Storage** via pre-configured Contributor permissions.
4. **Target Hardware (OpenWRT/iPXE)** boots over the network, pulling the clean build directly from public storage.