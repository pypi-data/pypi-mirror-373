import os
import time
import shutil
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import psr.execqueue.client as execqueue

load_dotenv()
SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:5000")
WATCH_DIR = os.getenv("WATCH_DIR")
PROCESSED_DIR = os.getenv("PROCESSED_DIR")
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")
SLEEP_SECONDS = int(os.getenv("WATCHER_SLEEP", "1"))
DB_PATH = os.getenv("WATCHER_DB_PATH", "watcher.sqlite")


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            cloud_upload_id TEXT NOT NULL,
            processed_at TEXT NOT NULL,
            downloaded INTEGER NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def _log_to_db(filename, cloud_upload_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO processed_files (filename, cloud_upload_id, processed_at, downloaded) VALUES (?, ?, ?, ?)",
        (filename, cloud_upload_id, datetime.now().isoformat(), 0)
    )
    conn.commit()
    conn.close()

def _is_file_locked(filepath):
    """Returns True if the file is locked by another process (e.g., still being copied)."""
    if not os.path.exists(filepath):
        return True
    try:
        # Try to open for exclusive writing
        with open(filepath, 'rb+') as f:
            pass
        return False
    except (OSError, PermissionError):
        return True
    
def _process_zip_files():
    for filename in os.listdir(WATCH_DIR):
        if filename.lower().endswith('.zip'):
            zip_path = os.path.join(WATCH_DIR, filename)

            # Check if the file is locked
            if _is_file_locked(zip_path):
                logging.info(f"Skipping {zip_path}: file is locked or being copied.")
                continue

            logging.info(f"zip file found: {zip_path}")

            #case_id = execqueue.upload_case_file(zip_path, SERVER_URL)
            case_id = 1
            if not case_id:
                logging.error(f"Failed uploading file {zip_path}")
                continue

            cloud_upload_id = execqueue.run_case(case_id, SERVER_URL, cloud_execution=True)
            if not cloud_upload_id:
                logging.error(f"Failed executing case {case_id} with {zip_path}")
                continue

            logging.info(f"File {filename} uploaded and execution started. Cloud Upload ID: {cloud_upload_id}")
            _log_to_db(filename, cloud_upload_id)
            dest_path = os.path.join(PROCESSED_DIR, filename)
            shutil.move(zip_path, dest_path)
            logging.info(f"File {filename} moved to {PROCESSED_DIR}")


def _check_and_download_results():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, cloud_upload_id FROM processed_files WHERE downloaded=0")
    rows = cursor.fetchall()
    for row in rows:
        record_id, filename, cloud_upload_id = row
        status_id, status_msg = execqueue.get_execution_status(cloud_upload_id, SERVER_URL, cloud_execution=True)
        logging.info(f"Execution status for {cloud_upload_id}: {status_id} - {status_msg}")
        if status_id is None:
            logging.error(f"Failed to get status for {cloud_upload_id}. Skipping download.")
            continue
        if status_id == 5 or status_id == 6:
            files = execqueue.get_results(cloud_upload_id, SERVER_URL, cloud_execution=True)
            if files:
                base_filename = os.path.splitext(filename)[0]
                download_folder_name = f"{base_filename}-{cloud_upload_id}"
                download_path = os.path.join(RESULTS_DIR, download_folder_name)
                os.makedirs(download_path, exist_ok=True)
                for file in files:
                    execqueue.download_execution_file(cloud_upload_id, SERVER_URL, file, download_path,
                                                   cloud_execution=True)
                # Update downloaded flag
                cursor.execute("UPDATE processed_files SET downloaded=1 WHERE id=?", (record_id,))
                conn.commit()
                logging.info(f"Results of {cloud_upload_id} downloaded to {download_path}")

    conn.close()


if __name__ == "__main__":
    if not WATCH_DIR or not PROCESSED_DIR:
        print("WATCH_DIR and PROCESSED_DIR must be set as environment variables or in a .env file")
        exit(1)

    LOG_FILE = os.path.join(os.getcwd(), "watcher.log")
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # log to standard output as well
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    _init_db()
    logging.info(f"Case watcher started. Monitoring directory for SDDP cases: {WATCH_DIR}")

    while True:
        try:
            _check_and_download_results()
            _process_zip_files()

        except Exception as e:
            logging.error(f"Watcher error: {e}", exc_info=True)
        time.sleep(SLEEP_SECONDS)
