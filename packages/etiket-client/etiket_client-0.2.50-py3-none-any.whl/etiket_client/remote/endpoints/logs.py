from etiket_client.remote.client import client

def get_user_logs(username : str, offset : int = 0, limit : int = 30):
    client.get("/logs/", params={"username" : username, "offset" : offset, "limit" : limit})

def get_current_user_logs(offset : int = 0, limit : int = 30):
    client.get("/logs/me/", params={"offset" : offset, "limit" : limit})

def create_log_deposit(file_name  : str, reason : str):
    response = client.post("/logs/deposit/create/", params={"file_name" : file_name, "reason" : reason})
    key = response["key"]
    upload_url = response["url"]
    return key, upload_url

def confirm_log_upload(key : str):
    client.post("/logs/deposit/confirm/", params={"key" : key})



if __name__ == "__main__":
    import os
    from etiket_client.remote.client import client # Ensure client is accessible
    import logging # For logging errors

    # Basic logging configuration for testing
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    file_name = "stephan_logs.zip"
    reason = "test upload"
    key = None
    upload_url = None
    success = False

    try:
        # 1. Create a dummy file to upload
        dummy_content = b"This is dummy log content." * 100 # Create some content
        with open(file_name, 'wb') as f:
            f.write(dummy_content)
        logger.info(f"Created dummy file: {file_name}")

        # 2. Get the upload URL and key
        key, upload_url = create_log_deposit(file_name, reason)
        logger.info(f"Obtained upload key: {key}")
        logger.info(f"Obtained upload URL: {upload_url[:50]}...")

        # 3. Prepare for upload
        file_size = os.stat(file_name).st_size
        timeout = max(10, min(file_size / 100_000, 1800))
        header = {
            'x-ms-blob-type': 'BlockBlob',
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(file_size)
        }

        # 4. Upload the file
        with open(file_name, 'rb') as file_to_upload:
            logger.info(f"Uploading {file_name} ({file_size} bytes) with timeout {timeout}s")
            response = client.session.put(upload_url, data=file_to_upload, timeout=timeout, headers=header)
            response.raise_for_status() # Still good to check for HTTP errors
            logger.info(f"Upload successful with status code: {response.status_code}")
            success = True

        # 5. Confirm upload if successful
        if success:
            logger.info(f"Confirming upload for key: {key}")
            confirm_log_upload(key)
            logger.info("Upload confirmed.")
        else:
            logger.warning("Upload did not succeed, skipping confirmation.")

    except Exception as e:
        logger.exception(f"An error occurred during the test log upload process: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response text: {e.response.text}")

    finally:
        # Clean up the dummy file
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"Cleaned up dummy file: {file_name}")
    