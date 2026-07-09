import os
import logging
import time
import requests
import smtplib
from email.message import EmailMessage
import azure.functions as func
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp()

# Configuration Constants
CONTAINER_NAME = "ztp-container"
FINAL_BLOB_NAME = "rhel-image.iso"
TEMP_BLOB_NAME = "rhel-image.tmp"
MAX_TRIES = 3
DELAY_BETWEEN_TRIES = 300  # 5 minutes
POLL_INTERVAL = 60         # Poll Red Hat API every 60 seconds

def send_alert_email(error_details: str):
    """Fires a critical alert email via SMTP if the pipeline permanently fails."""
    try:
        msg = EmailMessage()
        msg.set_content(f"The RHEL ZTP pipeline failed after {MAX_TRIES} attempts.\n\nFinal Error:\n{error_details}")
        msg['Subject'] = 'CRITICAL: ZTP Pipeline Build Failure'
        msg['From'] = os.environ["SMTP_USER"]
        msg['To'] = os.environ["NOTIFICATION_EMAIL"]
        
        server = smtplib.SMTP(os.environ["SMTP_SERVER"], int(os.environ["SMTP_PORT"]))
        server.starttls()
        server.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        server.send_message(msg)
        server.quit()
        logging.info("Critical failure email alert dispatched.")
    except Exception as e:
        logging.error(f"Failed to dispatch SMTP alert: {str(e)}")

@app.timer_trigger(schedule="0 0 * * * *", arg_name="timer", run_on_startup=False, use_monitor=False)
def cron_ztp_build_cycle(timer: func.TimerRequest) -> None:
    logging.info("Starting daily RHEL ZTP build cycle orchestration.")
    
    # Initialize Azure Storage Client
    connection_string = os.environ["AzureWebJobsStorage"]
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    # Fetch API Tokens and Config from App Settings
    rh_api_token = os.environ["RH_API_TOKEN"]
    blueprint_id = os.environ["RHEL_BLUEPRINT_ID"]
    api_base_url = os.environ["RHEL_IB_API_URL"]
    
    headers = {
        "Authorization": f"Bearer {rh_api_token}",
        "Content-Type": "application/json"
    }

    # Execute the 3-Try Build Loop
    success = False
    last_error = ""
    
    for attempt in range(1, MAX_TRIES + 1):
        try:
            logging.info(f"Attempt {attempt}/{MAX_TRIES}: Triggering Red Hat Compose...")
            
            # 1. POST Request to start the build
            compose_url = f"{api_base_url}/composes"
            compose_payload = {
                "blueprint_id": blueprint_id,
                "image_requests": [{
                    "architecture": "x86_64",
                    "image_type": "image-installer"
                }]
            }
            
            trigger_res = requests.post(compose_url, json=compose_payload, headers=headers, timeout=30)
            trigger_res.raise_for_status()
            compose_id = trigger_res.json()["id"]
            logging.info(f"Compose triggered successfully. ID: {compose_id}. Starting status polling...")

            # 2. Poll the Compose ID until completion
            status_url = f"{compose_url}/{compose_id}"
            while True:
                status_res = requests.get(status_url, headers=headers, timeout=30)
                status_res.raise_for_status()
                status_data = status_res.json()
                
                image_status = status_data.get("image_status", {}).get("status")
                logging.info(f"Current Image Builder status for {compose_id}: {image_status}")
                
                if image_status == "success":
                    s3_source_url = status_data["image_status"]["upload_status"]["options"]["url"]
                    break
                elif image_status in ["failure", "error"]:
                    raise Exception("Red Hat Image Builder failed to compile the ISO.")
                
                time.sleep(POLL_INTERVAL)

            # 3. Stream from S3 directly to Azure Temp Blob
            logging.info("S3 URL acquired. Streaming ISO to Azure staging layer...")
            with requests.get(s3_source_url, stream=True, timeout=900) as response:
                response.raise_for_status()
                
                temp_blob_client = container_client.get_blob_client(TEMP_BLOB_NAME)
                temp_blob_client.upload_blob(response.raw, overwrite=True)
            
            logging.info(f"Attempt {attempt} completed successfully. Data payload committed.")
            success = True
            break
            
        except Exception as e:
            last_error = str(e)
            logging.error(f"Attempt {attempt} failed with error: {last_error}")
            if attempt < MAX_TRIES:
                logging.info(f"Waiting {DELAY_BETWEEN_TRIES} seconds before next try...")
                time.sleep(DELAY_BETWEEN_TRIES)
            else:
                logging.critical("All 3 build tries exhausted. Abandoning cycle for today.")
                send_alert_email(last_error)
                return

    # 4. Asynchronous Client Polling & Atomic Swap
    if success:
        logging.info("Executing atomic swap to update the fixed production URL.")
        production_blob_client = container_client.get_blob_client(FINAL_BLOB_NAME)
        temp_blob_client = container_client.get_blob_client(TEMP_BLOB_NAME)
        
        production_blob_client.start_copy_from_url(temp_blob_client.url)
        
        props = production_blob_client.get_blob_properties()
        while props.copy.status == "pending":
            logging.info("Atomic swap copy pending... waiting 2 seconds.")
            time.sleep(2)
            props = production_blob_client.get_blob_properties()
            
        if props.copy.status == "success":
            logging.info("Copy verified. Executing automated cleanup of staging asset.")
            temp_blob_client.delete_blob()
            logging.info("Daily ZTP ISO rotation complete. Pipeline is stable.")
        else:
            msg = f"Atomic swap copy failed with internal status: {props.copy.status}"
            logging.error(msg)
            send_alert_email(msg)