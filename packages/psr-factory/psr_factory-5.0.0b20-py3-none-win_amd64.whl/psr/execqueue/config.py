import os
import tomllib

__version__ = "0.3.0"
_app_name = "PSR Factory ExecQueue"
DEFAULT_PORT = 5000
FLASK_DEBUG = False
_SETTINGS_FILE_PATH = "server_settings.toml"

if os.name == 'nt':
    _DEFAULT_SDDP_PATH = r"C:/PSR/Sddp17.3"
else:
    _DEFAULT_SDDP_PATH = "/opt/psr/sddp"
DEFAULT_CLUSTER_NAME = "server"
DEFAULT_PSRCLOUD_CLUSTER = "external"
DEFAULT_PSRCLOUD_CLUSTER_URL = ""


# read toml settings file
with open(os.path.join(os.getcwd(), _SETTINGS_FILE_PATH), 'rb') as f:
    settings = tomllib.load(f)


sddp_path = settings.get("sddp_path", _DEFAULT_SDDP_PATH)

cluster_name = settings.get("cluster_name", DEFAULT_CLUSTER_NAME)
psrcloud_cluster = settings.get("psrcloud_cluster", DEFAULT_PSRCLOUD_CLUSTER)
psrcloud_cluster_url = settings.get("psrcloud_cluster", DEFAULT_PSRCLOUD_CLUSTER_URL)

# Base server data storage path.
STORAGE_PATH = settings.get("storage_path", os.path.join(os.getcwd(), 'serverdata'))

# Where uploaded (received) cases will be stored.
UPLOADS_FOLDER = os.path.join(STORAGE_PATH, 'uploads')

# Where results of local runs will be stored.
LOCAL_RESULTS_FOLDER = os.path.join(STORAGE_PATH, 'local_results')

# Where results of cloud runs will be stored.
CLOUD_RESULTS_FOLDER = os.path.join(STORAGE_PATH, 'cloud_results')

# Where temporary extracted case files will be stored
TEMPORARY_UPLOAD_FOLDER = os.path.join(STORAGE_PATH, 'tmp')

