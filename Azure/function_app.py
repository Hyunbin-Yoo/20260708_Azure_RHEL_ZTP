import logging
import os
import time
import requests
import azure.functions as func

app = func.FunctionApp()

# Configuration from Environment Variables
RH_IB_API_URL = os.environ.get("RHEL_IB_API_URL")
RH_API_TOKEN = os.environ.get("RH_API_TOKEN")
BLUEPRINT_ID = os.environ.get("RHEL_BLUEPRINT_ID")
STORAGE_ACCOUNT = "20260708azurerhelztp"
RESOURCE_GROUP = "20260708_Azure_RHEL_ZTP"

@app.timer_trigger(schedule="0 0 */2 * * *", arg_name="timer", run_on_startup=False, use_monitor=True)
def rhel_ztp_composer_timer(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.info("The timer is past due!")

    logging.info("RHEL ZTP 2-hour compose timer triggered.")
    
    headers = {
        "Authorization": f"Bearer {RH_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "blueprint_id": BLUEPRINT_ID,
        "image_requests": [{
            "architecture": "x86_64",
            "image_type": "image-installer",
            "upload_request": {
                "type": "azure",
                "options": {
                    "resource_group": RESOURCE_GROUP,
                    "storage_account": STORAGE_ACCOUNT
                }
            }
        }]
    }

    response = requests.post(f"{RH_IB_API_URL}/composes", json=payload, headers=headers)
    if response.status_code not in [200, 201]:
        logging.error(f"Failed to trigger compose: {response.text}")
        return

    compose_data = response.json()
    compose_id = compose_data.get("id")
    logging.info(f"Successfully initiated compose ID: {compose_id}. Polling for completion...")

    max_retries = 40  
    delay_seconds = 30

    for attempt in range(max_retries):
        time.sleep(delay_seconds)
        status_res = requests.get(f"{RH_IB_API_URL}/composes/{compose_id}", headers=headers)
        
        if status_res.status_code != 200:
            continue
            
        status_data = status_res.json()
        status = status_data.get("image_status", {}).get("status")
        
        logging.info(f"Compose {compose_id} status: {status} (Attempt {attempt+1}/{max_retries})")

        if status == "success":
            logging.info("Compose completed successfully and exported to Azure!")
            break
        elif status in ["failed", "cancelled"]:
            logging.error(f"Compose failed with status data: {status_data}")
            break
    else:
        logging.warning("Compose polling timed out before reaching a final state.")