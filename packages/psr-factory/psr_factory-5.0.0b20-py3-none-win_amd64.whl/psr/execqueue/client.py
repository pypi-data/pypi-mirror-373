import os
import zipfile
import requests
from typing import List, Optional, Tuple


def zip_directory(directory_path, output_zip):
    """Compress a directory into a zip file."""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=directory_path)
                zipf.write(file_path, arcname=arcname)


def upload_case_file(zip_path, server_url):
    """Upload a zip file to the server."""
    with open(zip_path, 'rb') as f:
        files = {'file': (os.path.basename(zip_path), f)}
        response = requests.post(f"{server_url}/upload", files=files)

    if response.status_code == 200:
        print("Upload successful!")
        print("Case ID:", response.json().get('case_id'))
        return response.json().get('case_id')
    else:
        print("Upload failed:", response.text)
        return None


def run_case(case_id: str, server_url: str, cloud_execution: bool = False) -> Optional[str]:
    """Add a case to the execution queue. For server-local run,
    returns the execution id. For cloud run, returns the cloud upload id."""
    data = {"case_id": case_id,'cloud_execution': cloud_execution}
    response = requests.post(f"{server_url}/run",data=data)

    if response.status_code == 200:
        if not cloud_execution:
            print("Added to queue successfully!")
            print("Execution ID:", response.json().get('execution_id'))
            return response.json().get('execution_id')
        else:
            print("Cloud execution queued!")
            print("Cloud upload ID:", response.json().get('cloud_upload_id'))
            return response.json().get('cloud_upload_id')
    else:
        print("Upload failed:", response.text)
        return None


def upload_and_run_file(zip_path: str, server_url: str, cloud_execution: bool = False):
    """Upload a zip file to the server."""
    with open(zip_path, 'rb') as f:
        files = {'file': (os.path.basename(zip_path), f)}
        data = {'cloud_execution': cloud_execution}
        response = requests.post(f"{server_url}/upload_and_run", files=files, data=data)

    if response.status_code == 200:
        print("Upload successful! Waiting for execution.")

        if cloud_execution:
            print("Cloud upload ID:", response.json().get('cloud_upload_id'))
            return response.json().get('cloud_upload_id')
        else:
            print("Local execution ID:", response.json().get('execution_id'))
            return response.json().get('execution_id')
    else:
        print("Upload failed:", response.text)
        return None


def get_execution_status(execution_id: str, server_url: str, cloud_execution: bool = False) -> Optional[tuple[int, str]]:
    """Get the status of an execution."""
    print("Getting status for execution ID:", execution_id)
    data = {'cloud_execution': cloud_execution}
    response = requests.get(f"{server_url}/status/{execution_id}", data=data)
    result = response.status_code == 200
    return response.json().get('status_id'), response.json().get('status_msg') if result else None

def get_results(execution_id, server_url, cloud_execution=False) -> Optional[List[str]]:
    """Download the results of an execution."""
    response = requests.get(f"{server_url}/results/{execution_id}", data={'cloud_execution': cloud_execution})

    if response.status_code == 200:
        print("Results downloaded successfully!")
        files = response.json().get('files')
        print("Files:", files)
        return files
    else:
        print("Results download failed:", response.text)
        return None


def download_execution_file(execution_id: str, server_url: str, file: str, download_path: str, cloud_execution: bool = False):
    """Download the results of an execution."""
    data = {'cloud_execution': cloud_execution}
    response = requests.get(f"{server_url}/results/{execution_id}/{file}", data=data)

    # TODO: add validation for download_path existence.
    if response.status_code == 200:
        with open(os.path.join(download_path, file), 'wb') as f:
            f.write(response.content)
    else:
        print("Download failed:", response.text)