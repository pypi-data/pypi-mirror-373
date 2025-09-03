import hashlib
import queue
import shutil
import sys
import threading
import time
import zipfile
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    jsonify,
    send_file
)
import ulid


import psr.runner
import psr.cloud

from psr.execqueue.config import *
from psr.execqueue import db

_execution_queue = queue.Queue()
_cloud_upload_queue = queue.Queue()


os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(LOCAL_RESULTS_FOLDER, exist_ok=True)
os.makedirs(CLOUD_RESULTS_FOLDER, exist_ok=True)
os.makedirs(TEMPORARY_UPLOAD_FOLDER, exist_ok=True)


load_dotenv()


try:
    client = psr.cloud.Client(cluster=psrcloud_cluster, verbose=True)
except psr.cloud.CloudInputError as e:
    print(f"Error connecting to PSR Cloud. Check user credentials: {e}")
    exit(1)

_cloud_execution_case_map = {}

app = Flask(__name__, root_path=os.getcwd())
session = None


def get_file_checksum(file_path: str) -> str:
    with open(file_path, 'rb') as file:
        return hashlib.md5(file.read()).hexdigest()


def run_local_case(execution_id: str, case_path: str):
    global session
    success = False
    try:
        psr.runner.run_sddp(case_path, sddp_path, parallel_run=False)
        success = True
    except RuntimeError as e:
        print(f"Error running {execution_id}: {e}")

    status = db.LOCAL_EXECUTION_FINISHED if success else db.LOCAL_EXECUTION_ERROR
    db.update_local_execution_status(session, execution_id, status)


def initialize_db():
    session, engine = db.initialize()
    return session


def run_cloud_case(execution_id: str, case_path: str):
    global client
    # Run the case
    case = psr.cloud.Case(
        name="LSEG Server "+ execution_id,
        data_path=case_path,
        program="SDDP",
        program_version = "17.3.9",
        execution_type="Default",
        memory_per_process_ratio='2:1',
        price_optimized=False,
        number_of_processes=64,
        repository_duration=1,
    )
    case_id = client.run_case(case)

    return str(case_id)


def process_local_execution_queue():
    global session
    while True:
        execution_id, case_id = _execution_queue.get()
        try:
            print(f"Processing {execution_id}...")
            # Unzip the file
            execution_extraction_path = os.path.join(LOCAL_RESULTS_FOLDER, execution_id)
            os.makedirs(execution_extraction_path, exist_ok=True)

            zip_upload_path = os.path.join(UPLOADS_FOLDER, case_id + ".zip")

            with zipfile.ZipFile(zip_upload_path, 'r') as zip_ref:
                zip_ref.extractall(execution_extraction_path)
            # Run SDDP
            run_local_case(execution_id, execution_extraction_path)

        except Exception as e:
            print(f"Error processing {execution_id}: {e}")
        finally:
            _execution_queue.task_done()


threading.Thread(target=process_local_execution_queue, daemon=True).start()


def process_cloud_execution_queue():
    global client
    global session
    while True:
        cloud_upload_id, case_id = _cloud_upload_queue.get()
        try:
            print(f"Processing {cloud_upload_id}...")
            # Unzip the file
            zip_upload_path = os.path.join(UPLOADS_FOLDER, case_id + ".zip")
            tmp_extraction_path = os.path.join(TEMPORARY_UPLOAD_FOLDER, cloud_upload_id)

            os.makedirs(tmp_extraction_path, exist_ok=True)
            with zipfile.ZipFile(zip_upload_path, 'r') as zip_ref:
                zip_ref.extractall(tmp_extraction_path)

            # Run SDDP
            repository_id = run_cloud_case(cloud_upload_id, tmp_extraction_path)

            #delete the extraction path folder recursively
            shutil.rmtree(tmp_extraction_path)

            execution_extraction_path = os.path.join(CLOUD_RESULTS_FOLDER, repository_id)
            os.makedirs(execution_extraction_path, exist_ok=True)
            with zipfile.ZipFile(zip_upload_path, 'r') as zip_ref:
                zip_ref.extractall(execution_extraction_path)

            db.register_cloud_execution(session, repository_id, cloud_upload_id, case_id)

        except Exception as e:
            print(f"Error processing {cloud_upload_id}: {e}")
        finally:
            _cloud_upload_queue.task_done()


threading.Thread(target=process_cloud_execution_queue, daemon=True).start()


def monitor_cloud_runs():
    global client
    global session

    #wait for cloud upload queue to be empty
    while not _cloud_upload_queue.empty():
        time.sleep(10)

    while True:
        if session:
            #check running executions
            for cloud_execution in db.get_runing_cloud_executions(session):
                case_id = cloud_execution.repository_id
                print(f"Checking status of {case_id}...")
                status, status_msg = client.get_status(case_id)
                if status in psr.cloud.FAULTY_TERMINATION_STATUS:
                    print(f"Execution {case_id} finished with errors")
                    db.update_cloud_execution_status(session, case_id, db.CloudStatus.ERROR.value)
                elif status == psr.cloud.ExecutionStatus.SUCCESS:
                    print(f"Execution {case_id} finished successfully")
                    db.update_cloud_execution_status(session, case_id, db.CloudStatus.FINISHED.value)

            #download finished executions
            for cloud_execution in db.get_cloud_finished_executions(session):
                repository_id = cloud_execution.repository_id
                print(f"Downloading results for {repository_id}...")
                result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
                client.download_results(repository_id, result_path)
                db.update_cloud_execution_status(session, repository_id, db.CloudStatus.RESULTS_AVAILABLE.value)
            
            #download failed executions
            for cloud_execution in db.get_cloud_failed_executions(session):
                try:
                    repository_id = cloud_execution.repository_id
                    print(f"Downloading results for {repository_id}...")
                    result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
                    client.download_results(repository_id, result_path, extensions=['log'])
                    db.update_cloud_execution_status(session, repository_id, db.CloudStatus.LOGS_AVAILABLE_ERROR.value)
                except Exception as e:
                    print(f"Error downloading results for {repository_id}: {e}")
                    print("Forcing execution to Failed downloaded execution")
                    db.update_cloud_execution_status(session, repository_id, db.CloudStatus.LOGS_AVAILABLE_ERROR.value)
                    continue
        else:
            print("Database not initialized. Retrying in 30s...")
        time.sleep(30)

threading.Thread(target=monitor_cloud_runs, daemon=True).start()

@app.route('/upload', methods=['POST'])
def upload_file():
    global session
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    case_id = str(ulid.ULID())
    zip_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    file.save(zip_path)

    checksum = get_file_checksum(zip_path)
    db.register_case(session, case_id, checksum)

    return jsonify({'case_id': case_id}), 200


# route to run an uploaded file
@app.route('/run', methods=['POST'])
def run_endpoint():
    global session
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'
    case_id = request.form.get('case_id')

    if not case_id:
        return jsonify({'error': 'Case ID not provided'}), 400

    zip_case_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    if not os.path.exists(zip_case_path):
        return jsonify({'error': 'Upload file for this case ID not found'}), 404

    if cloud_execution:
        cloud_upload_id = str(ulid.ULID())
        _cloud_upload_queue.put((cloud_upload_id, case_id))

        db.register_cloud_upload(session, case_id, cloud_upload_id)

        return jsonify({'case_id': case_id, 'cloud_upload_id': cloud_upload_id}), 200
    else:
        execution_id = str(ulid.ULID())
        _execution_queue.put((execution_id, case_id))

        db.register_local_execution(session, case_id, execution_id)

        return jsonify({'case_id': case_id, 'execution_id': execution_id}), 200


@app.route('/upload_and_run', methods=['POST'])
def upload_and_run_file():
    global session
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'

    case_id = str(ulid.ULID())
    zip_path = os.path.join(UPLOADS_FOLDER, f"{case_id}.zip")
    file.save(zip_path)
    db.register_case(session, case_id, get_file_checksum(zip_path))

    if cloud_execution:
        cloud_upload_id = str(ulid.ULID())
        _cloud_upload_queue.put((cloud_upload_id, case_id))
        db.register_cloud_upload(session, case_id, cloud_upload_id)
        return jsonify({'case_id': case_id, 'cloud_upload_id': cloud_upload_id}), 200
    else:
        execution_id = str(ulid.ULID())
        _execution_queue.put((execution_id, case_id))
        db.register_local_execution(session, case_id, execution_id)
        return jsonify({'case_id': case_id, 'execution_id': execution_id}), 200


@app.route('/status/<execution_id>', methods=['GET'])
def get_status(execution_id):
    """
    Get the status of an execution
    ---
    tags:
      - Execution
    parameters:
      - name: execution_id
        in: path
        type: string
        required: true
        description: The ID of the execution
    responses:
      200:
        description: Execution status
        schema:
          type: object
      404:
        description: Execution ID not found
    """
    global client
    global session
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'

    if cloud_execution:
        repository_id = db.get_repository_id_from_cloud_upload_id(session, execution_id)
        if repository_id is None:
            return jsonify({'error': 'Execution ID not found in Cloud'}), 404
        status = db.get_cloud_execution_status(session, repository_id)
        if status == db.CloudStatus.ERROR.value:
            status_msg = 'Execution finished with errors. Only log files will be downloaded'
        elif status == db.CloudStatus.RUNNING.value:
            status_msg = 'Execution not finished yet'
        elif status == db.CloudStatus.FINISHED.value:
            status_msg = 'Execution finished, but download not yet started from Cloud server'
        elif status == db.CloudStatus.RESULTS_AVAILABLE.value:
            status_msg = 'Execution finished and results are available to download'
        elif status == db.CloudStatus.LOGS_AVAILABLE_ERROR.value:
            status_msg = 'Execution finished with errors and log files are avaialble to download'
        else:
            status_msg = 'Unknown status'
        print(f"Cloud execution status for {execution_id} ({repository_id}): {status_msg}")
        return jsonify({'status_id': status, 'status_msg': status_msg}), 200
    else:
        status = db.get_local_execution_status(session, execution_id)
        if status == db.LOCAL_EXECUTION_ERROR:
            status_msg = 'Execution finished with errors'
        elif status != db.LOCAL_EXECUTION_FINISHED:
            status_msg = 'Execution not finished yet'
        else:
            status_msg = 'Execution finished'
        return jsonify({'status_id': status, 'status_msg': status_msg}), 200


@app.route('/results/<execution_id>', methods=['GET'])
def get_results(execution_id: str):
    global session
    global client
    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'

    if cloud_execution:
        repository_id = db.get_repository_id_from_cloud_upload_id(session, execution_id)
        if repository_id is None:
            return jsonify({'error': 'Execution ID not found in Cloud'}),
        status = db.get_cloud_execution_status(session, execution_id)

        if status == db.CloudStatus.RUNNING:
            return jsonify({'error': f'{repository_id} execution not finished yet'}), 402
        elif status == db.CloudStatus.FINISHED:
            return jsonify({'error': f'{repository_id} results not available yet'}), 403
        else:
            #fazer download da pasta do resultado
            result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
            if not os.path.exists(result_path):
                return jsonify({'error': f'{repository_id} execution result folder not found'}), 404
            result_files = os.listdir(result_path)
            result_files = [f for f in result_files if os.path.isfile(os.path.join(result_path, f))]
            return jsonify({'execution_id': repository_id, 'files': result_files}), 200
    else:
        status = db.get_local_execution_status(session, execution_id)
        if status == db.LOCAL_EXECUTION_ERROR:
            return jsonify({'error': 'Execution finished with errors'}), 401
        if status != db.LOCAL_EXECUTION_FINISHED:
            return jsonify({'error': 'Execution not finished yet'}), 402
        result_path = os.path.join(LOCAL_RESULTS_FOLDER, execution_id)
        if not os.path.exists(result_path):
            return jsonify({'error': 'Execution result folder not found'}), 404
    result_files = os.listdir(result_path)
    return jsonify({'execution_id': execution_id, 'files': result_files}), 200


@app.route('/results/<execution_id>/<file>', methods=['GET'])
def download_file(execution_id: str, file):
    global session

    cloud_execution = request.form.get('cloud_execution', 'false').lower() == 'true'
    
    if cloud_execution:
        repository_id = db.get_repository_id_from_cloud_upload_id(session, execution_id)
        result_path = os.path.join(CLOUD_RESULTS_FOLDER, str(repository_id))
    else:
        result_path = os.path.join(LOCAL_RESULTS_FOLDER, execution_id)
    if not os.path.exists(result_path):
        if cloud_execution:
            msg = f'{repository_id} execution result folder not found'
        else:
            msg = f'Execution result folder not found'
        return jsonify({'error': msg}), 404

    file_path = os.path.normpath(os.path.join(result_path, file)).replace("\\", "/")
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
       return send_file(file_path, download_name=file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting server...")
    session = initialize_db()
    try:
        app.run(debug=FLASK_DEBUG,
                port=settings.get("port", DEFAULT_PORT),
                threaded=True,
                use_reloader=False,)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

