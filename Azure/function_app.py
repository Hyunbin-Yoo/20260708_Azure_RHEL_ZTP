import logging
import os
import time
import requests
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, UserDelegationKey

app = func.FunctionApp()

# --- Configuration ---
RH_IB_API_URL = os.environ.get("RHEL_IB_API_URL", "https://console.redhat.com/api/image-builder/v1")
RH_API_TOKEN = os.environ.get("RH_API_TOKEN")
BLUEPRINT_ID = os.environ.get("RHEL_BLUEPRINT_ID")
RESOURCE_GROUP = "20260708_Azure_RHEL_ZTP"

MAIN_STORAGE_ACCOUNT = "20260708azurerhelztp"
MAIN_CONTAINER = "public"
TARGET_BLOB_NAME = "latest_rhel_ztp.vhd"

STAGING_STORAGE_ACCOUNT = os.environ.get("IB_STORAGE_ACCOUNT_NAME") 

# SMTP Configuration
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL")

def send_email(subject: str, body: str):
    """Sends an email notification."""
    if not all([SMTP_USER, SMTP_PASS, NOTIFICATION_EMAIL]):
        logging.warning("SMTP credentials missing. Skipping email notification.")
        return
    
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = NOTIFICATION_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        logging.info(f"Email sent: {subject}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def get_user_delegation_sas(blob_service_client: BlobServiceClient, container_name: str, blob_name: str) -> str:
    """Generates a short-lived User Delegation SAS token for server-side copying."""
    start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    expiry_time = start_time + timedelta(hours=1)

    user_delegation_key = blob_service_client.get_user_delegation_key(start_time, expiry_time)
    
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        user_delegation_key=user_delegation_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time,
        start=start_time
    )
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

# --- Trigger 1: The 1-Hour Orchestrator ---
@app.timer_trigger(schedule="0 0 * * * *", arg_name="timer", run_on_startup=False, use_monitor=True)
def rhel_ztp_composer_timer(timer: func.TimerRequest) -> None:
    logging.info("RHEL ZTP 1-hour compose cycle initiated.")
    send_email("ZTP Pipeline: Build Started", "The 1-hour RHEL ZTP build cycle has been triggered.")
    
    headers = {
        "Authorization": f"Bearer {RH_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "blueprint_id": BLUEPRINT_ID,
        "image_requests": [{
            "architecture": "x86_64",
            "image_type": "azure",
            "upload_request": {
                "type": "azure",
                "options": {
                    "tenant_id": os.environ.get("AZURE_TENANT_ID"),
                    "subscription_id": os.environ.get("AZURE_SUBSCRIPTION_ID"),
                    "resource_group": RESOURCE_GROUP,
                    "storage_account": STAGING_STORAGE_ACCOUNT,
                    "hyper_v_generation": "V2"
                }
            }
        }]
    }

    max_build_attempts = 3
    build_success = False
    compose_id = ""
    target_blob_source = ""

    for attempt in range(1, max_build_attempts + 1):
        logging.info(f"Initiating RHEL build attempt {attempt}/{max_build_attempts}...")
        response = requests.post(f"{RH_IB_API_URL}/composes", json=payload, headers=headers)
        
        if response.status_code not in [200, 201]:
            logging.error(f"Compose POST failed: {response.text}")
            time.sleep(60)
            continue
            
        compose_data = response.json()
        compose_id = compose_data.get("id")
        
        max_polls = 60
        poll_delay = 30
        
        for _ in range(max_polls):
            time.sleep(poll_delay)
            status_res = requests.get(f"{RH_IB_API_URL}/composes/{compose_id}", headers=headers)
            
            if status_res.status_code == 200:
                status_data = status_res.json()
                status = status_data.get("image_status", {}).get("status")
                
                logging.info(f"Compose {compose_id} status: {status}")
                
                if status == "success":
                    build_success = True
                    target_blob_source = status_data.get("image_status", {}).get("upload_status", {}).get("options", {}).get("image_name")
                    break
                elif status in ["failed", "cancelled"]:
                    logging.warning(f"Build failed on attempt {attempt}.")
                    break
                    
        if build_success:
            break

    if not build_success:
        msg = f"ZTP Pipeline aborted. RHEL Image Builder failed {max_build_attempts} consecutive times."
        logging.error(msg)
        send_email("ZTP Pipeline: Build FATAL ERROR", msg)
        return

    # --- Phase 2: Copy to Production Storage ---
    logging.info(f"Build {compose_id} successful. Promoting artifact {target_blob_source} to production...")
    
    try:
        credential = DefaultAzureCredential()
        
        staging_url = f"https://{STAGING_STORAGE_ACCOUNT}.blob.core.windows.net"
        staging_client = BlobServiceClient(account_url=staging_url, credential=credential)
        
        staging_containers = list(staging_client.list_containers())
        if not staging_containers:
            raise Exception("No containers found in the staging account.")
        staging_container_name = staging_containers[0].name
        
        source_sas_url = get_user_delegation_sas(staging_client, staging_container_name, f"{target_blob_source}.vhd")
        
        main_url = f"https://{MAIN_STORAGE_ACCOUNT}.blob.core.windows.net"
        main_client = BlobServiceClient(account_url=main_url, credential=credential)
        dest_blob_client = main_client.get_blob_client(container=MAIN_CONTAINER, blob=TARGET_BLOB_NAME)
        
        dest_blob_client.start_copy_from_url(source_sas_url)
        
        msg = f"ZTP Pipeline complete. Image {compose_id} is successfully promoted to {MAIN_CONTAINER}/{TARGET_BLOB_NAME}."
        logging.info(msg)
        send_email("ZTP Pipeline: Deployment Success", msg)
        
    except Exception as e:
        msg = f"ZTP Pipeline failed during storage promotion: {e}"
        logging.error(msg)
        send_email("ZTP Pipeline: Promotion ERROR", msg)

# --- Trigger 2: The 24-Hour Garbage Collector ---
@app.timer_trigger(schedule="0 0 */6 * * *", arg_name="timer", run_on_startup=False, use_monitor=True)
def rhel_ztp_cleaner_timer(timer: func.TimerRequest) -> None:
    logging.info("RHEL ZTP 24-hour staging cleanup initiated.")
    
    try:
        credential = DefaultAzureCredential()
        staging_url = f"https://{STAGING_STORAGE_ACCOUNT}.blob.core.windows.net"
        staging_client = BlobServiceClient(account_url=staging_url, credential=credential)
        
        deleted_count = 0
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=6)
        
        for container in staging_client.list_containers():
            container_client = staging_client.get_container_client(container.name)
            
            for blob in container_client.list_blobs():
                if blob.last_modified < cutoff_time:
                    container_client.delete_blob(blob.name)
                    deleted_count += 1
                    logging.info(f"Purged stale staging image: {blob.name}")
                    
        send_email("ZTP Pipeline: Cleanup Complete", f"Successfully purged {deleted_count} stale images from staging account {STAGING_STORAGE_ACCOUNT}.")
        
    except Exception as e:
        logging.error(f"Failed to execute cleanup: {e}")
        send_email("ZTP Pipeline: Cleanup ERROR", f"The 24-hour garbage collector failed: {e}")