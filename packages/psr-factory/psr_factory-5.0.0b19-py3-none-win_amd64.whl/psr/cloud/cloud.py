# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import copy
import functools
import gzip
import hashlib
import logging
import os
import re
import shutil
import subprocess
import sys
import warnings
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep, time
from typing import List, Optional, Union

import pefile
import zeep
from filelock import FileLock

from .aws import download_case_from_s3, upload_case_to_s3
from .data import Case, CloudError, CloudInputError
from .desktop import import_case
from .log import enable_log_timestamp, get_logger
from .status import FAULTY_TERMINATION_STATUS, STATUS_MAP_TEXT, ExecutionStatus
from .tempfile import CreateTempFile
from .version import __version__
from .xml import create_case_xml

INTERFACE_VERSION = "PyCloud " + __version__ + ", binding for " + sys.version


def thread_safe():
    """
    Decorator to make a function thread-safe using filelock.
    :param lock_file: Path to the lock file. If None, it will be automatically generated.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with FileLock("pycloud.lock"):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def _md5sum(value: str, enconding=True) -> str:
    if enconding:
        return hashlib.md5(value.encode("utf-8")).hexdigest()  # nosec
    else:
        # hash binary data
        return hashlib.md5(value).hexdigest()  # nosec


def hash_password(password: str) -> str:
    return _md5sum(password).upper()


def _check_for_errors(
    xml: ET.ElementTree, logger: Optional[logging.Logger] = None
) -> None:
    error = xml.find("./Parametro[@nome='erro']")
    if error is not None:
        if logger is not None:
            logger.error(error.text)
        raise CloudError(error.text)


def _hide_password(params: str) -> str:
    pattern = r'(<Parametro nome="senha"[^>]*>)(.*?)(</Parametro>)'
    result = re.sub(pattern, r"\1********\3", params)
    return result


def _xml_to_str(xml_content: ET.ElementTree) -> str:
    # Remove <Parametro nome="senha" ...> tag, if found in the xml_content
    xml_str = ET.tostring(
        xml_content.getroot(), encoding="utf-8", method="xml"
    ).decode()
    return _hide_password(xml_str)


def _handle_relative_path(path: str) -> str:
    if not os.path.isabs(path):
        return os.path.abspath(path)
    return path


_PSRCLOUD_PATH = r"C:\PSR\PSRCloud"

_CONSOLE_REL_PARENT_PATH = r"Oper\Console"

_CONSOLE_APP = r"FakeConsole.exe"

_ALLOWED_PROGRAMS = ["SDDP", "OPTGEN", "PSRIO", "GRAF", "MyModel", "GNoMo"]

if os.name == "nt":
    _PSRCLOUD_CREDENTIALS_PATH = os.path.expandvars(
        os.path.join("%appdata%", "PSR", "PSRCloud", "EPSRConfig.xml")
    )
else:
    _PSRCLOUD_CREDENTIALS_PATH = ""

_PSRCLOUD_USER_ENV_VAR = "PSR_CLOUD_USER"
_PSRCLOUD_PASSWORD_HASH_ENV_VAR = "PSR_CLOUD_PASSWORD_HASH"  # nosec
_PSRCLOUD_CONSOLE_ENV_VAR = "PSR_CLOUD_CONSOLE_PATH"

_auth_error_message = f"Please set {_PSRCLOUD_USER_ENV_VAR} and {_PSRCLOUD_PASSWORD_HASH_ENV_VAR} environment variables."

# FIXME uninspired name
_DEFAULT_GET_CASES_SINCE_DAYS = 7


_DEFAULT_CLUSTER = {
    "name": "PSR-US",
    "pretty_name": "External",
    "url": "https://psrcloud.psr-inc.com/CamadaGerenciadoraServicoWeb/DespachanteWS.asmx",
}


class Client:
    def __init__(self, **kwargs) -> None:
        self.cwd = Path.cwd()

        # Caches (avoiding multiple soap requests)
        self._cloud_version_xml_cache = None
        self._cloud_clusters_xml_cache = None
        self._instance_type_map = None

        # Options
        self._selected_cluster = kwargs.get("cluster", _DEFAULT_CLUSTER["pretty_name"])
        self._import_desktop = kwargs.get("import_desktop", True)
        self._debug_mode = kwargs.get("debug", False)
        self._timeout = kwargs.get("timeout", None)
        self._python_client = kwargs.get("python_client", False)

        # Client version
        self.application_version = kwargs.get("application_version", None)

        # Logging setup
        self._quiet = kwargs.get("quiet", False)
        self._verbose = kwargs.get("verbose", False)
        if self._debug_mode:
            self._quiet = False
            self._verbose = True
        log_id = id(self)
        self._logger = get_logger(
            log_id, quiet=self._quiet, debug_mode=self._debug_mode
        )

        self._logger.info(f"Client uid {log_id} initialized.")

        if self._python_client:
            self._logger.info(
                "Using Python client for PSR Cloud. Some features may not be available."
            )
        else:
            self._console_path_setup(**kwargs)

        self._credentials_setup(**kwargs)

        self._cluster_setup(self._selected_cluster)

    def _console_path_setup(self, **kwargs) -> None:
        # For common users - provide PSR Cloud install path
        if "psrcloud_path" in kwargs:
            psrcloud_path = Path(kwargs["psrcloud_path"])
            self._console_path = psrcloud_path / _CONSOLE_REL_PARENT_PATH / _CONSOLE_APP
            if not os.path.exists(self._console_path):
                err_msg = (
                    f"PSR Cloud application not found at {self._console_path} "
                    f"Make sure the path is correct and PSR Cloud is installed."
                )
                self._logger.error(err_msg)
                self._logger.info("Provided psrcloud_path: " + str(psrcloud_path))
                raise CloudError(err_msg)
        # For advanced users or tests - provide full FakeConsole.exe path.
        elif "fakeconsole_path" in kwargs:
            self._console_path = Path(kwargs["fakeconsole_path"])
            if not os.path.exists(self._console_path):
                err_msg = (
                    f"PSR Cloud application not found at {self._console_path} "
                    f"Make sure the path is correct and PSR Cloud is installed."
                )
                self._logger.error(err_msg)
                self._logger.info(
                    "Provided fakeconsole_path: " + str(self._console_path)
                )
                raise CloudError(err_msg)
        # For advanced users or tests - provide PSR Cloud console path as environment variable.
        elif _PSRCLOUD_CONSOLE_ENV_VAR in os.environ:
            self._console_path = Path(os.environ[_PSRCLOUD_CONSOLE_ENV_VAR]).resolve()
            if not os.path.exists(self._console_path):
                err_msg = (
                    f"PSR Cloud application not found at {self._console_path} "
                    f"Make sure the path is correct and PSR Cloud is installed."
                )
                self._logger.error(err_msg)
                self._logger.info("Provided console path: " + str(self._console_path))
                raise CloudError(err_msg)
        else:
            self._console_path = (
                Path(_PSRCLOUD_PATH) / _CONSOLE_REL_PARENT_PATH / _CONSOLE_APP
            )
            if not os.path.exists(self._console_path):
                err_msg = (
                    f"PSR Cloud application not found at {self._console_path} "
                    f"Make sure the path is correct and PSR Cloud is installed."
                )
                self._logger.error(err_msg)
                self._logger.info("Using default console path.")
                raise CloudError(err_msg)

        self._logger.info(f"PSR Cloud console path: {self._console_path}")
        self._logger.info(f"PSR Cloud console version: {self._get_console_version()}")

    def _credentials_setup(self, **kwargs) -> None:
        self.username = kwargs.get("username", None)
        self.__password = None
        if self.username is not None:
            self.username = kwargs["username"]
            self.__password = hash_password(kwargs["password"])
            self._logger.info(
                "Using provided credentials from PSR Cloud console arguments."
            )
            self._logger.warning(
                "For security reasons, it is highly recommended to use environment variables to store your credentials.\n"
                + f"({_PSRCLOUD_USER_ENV_VAR}, {_PSRCLOUD_PASSWORD_HASH_ENV_VAR})"
            )
        else:
            if (
                _PSRCLOUD_USER_ENV_VAR in os.environ
                and _PSRCLOUD_PASSWORD_HASH_ENV_VAR in os.environ
            ):
                self.username = os.environ[_PSRCLOUD_USER_ENV_VAR]
                self.__password = os.environ[_PSRCLOUD_PASSWORD_HASH_ENV_VAR].upper()
                self._logger.info("Using credentials from environment variables")
            elif os.path.exists(_PSRCLOUD_CREDENTIALS_PATH):
                self._logger.info(
                    "Environment variables for Cloud credentials not found"
                )
                xml = ET.parse(
                    _PSRCLOUD_CREDENTIALS_PATH, parser=ET.XMLParser(encoding="utf-16")
                )
                root = xml.getroot()
                username = None
                _password = None
                for elem in root.iter("Aplicacao"):
                    username = elem.attrib.get("SrvUsuario")
                    _password = elem.attrib.get("SrvSenha")
                    break
                if username is None or _password is None:
                    err_msg = "Credentials not provided. " + _auth_error_message
                    self._logger.info(
                        "Loading credentials from file: " + _PSRCLOUD_CREDENTIALS_PATH
                    )
                    self._logger.error(err_msg)
                    raise CloudInputError(err_msg)
                self.username = username
                self.__password = _password
                self._logger.info("Using credentials from PSR Cloud Desktop cache")
            else:
                err_msg = "Username and password not provided." + _auth_error_message
                self._logger.info(
                    "Trying to get credentials from environment variables."
                )
                self._logger.error(err_msg)
                raise CloudInputError(err_msg)
        self._logger.info(f"Logged as {self.username}")

    def _cluster_setup(self, cluster_str: str) -> None:
        """
        Get cluster object by name.
        If the cluster is the default one, select it directly. If not, check using default cluster to get
        the available clusters for this user and select the one that matches the provided name.
        """

        if (
            _DEFAULT_CLUSTER["name"].upper() == cluster_str.upper()
            or _DEFAULT_CLUSTER["pretty_name"].capitalize() == cluster_str.capitalize()
        ):
            self.cluster = _DEFAULT_CLUSTER
        else:
            self.cluster = None
            clusters = self._get_clusters_by_user()
            for cluster in clusters:
                if (
                    cluster["name"].upper() == cluster_str.upper()
                    or cluster["pretty_name"].capitalize() == cluster_str.capitalize()
                ):
                    self.cluster = cluster

        if self.cluster is not None:
            self._logger.info(
                f"Running on Cluster {self.cluster['name']} ({self.cluster['pretty_name']})"
            )
        else:
            raise CloudInputError(f"Cluster {cluster_str} not found")

    def set_cluster(self, cluster_str: str) -> None:
        self._cluster_setup(cluster_str)
        # Clear caches
        self._cloud_version_xml_cache = None
        self._cloud_clusters_xml_cache = None
        self._instance_type_map = None

    def _get_console_path(self) -> Path:
        return self._console_path

    def _get_console_parent_path(self) -> Path:
        return self._console_path.parent

    def _get_console_version(self) -> str:
        console_path = self._get_console_path()
        pe = pefile.PE(console_path)
        for file_info in getattr(pe, "FileInfo", []):
            for entry in file_info:
                for st in getattr(entry, "StringTable", []):
                    product_version = st.entries.get(b"ProductVersion")
                    if product_version:
                        return product_version.decode()

    @staticmethod
    def _check_xml(xml_content: str) -> None:
        try:
            ET.fromstring(xml_content)
        except ET.ParseError:
            _hide_password(xml_content)
            raise CloudInputError(
                f"Invalid XML content.\n"
                f"Contact PSR support at psrcloud@psr-inc.com with following data:\n\n{xml_content}\n\n"
            )

    def _get_clusters_by_user(self) -> list:
        try:
            previous_cluster = self.cluster
            self.cluster = _DEFAULT_CLUSTER
            xml = self._make_soap_request("listarCluster", "listaCluster")

            clusters = []
            for cluster in xml.findall("Cluster"):
                nome = cluster.attrib.get("nome")
                url = cluster.attrib.get("urlServico") + "/DespachanteWS.asmx"
                pretty_name = cluster.attrib.get("legenda", nome)
                clusters.append({"name": nome, "pretty_name": pretty_name, "url": url})

            self.cluster = previous_cluster
        except Exception as e:
            self.cluster = previous_cluster
            raise e
        return clusters

    def get_clusters(self) -> List[str]:
        clusters = self._get_clusters_by_user()
        return [cluster["pretty_name"] for cluster in clusters]

    def _run_console(self, xml_content: str) -> None:
        self._check_xml(xml_content)
        delete_xml = not self._debug_mode
        with CreateTempFile(
            str(self.cwd), "psr_cloud_", xml_content, delete_xml
        ) as xml_file:
            xml_file.close()
            command = [self._get_console_path(), xml_file.name]
            command_str = " ".join(map(str, command))
            self._logger.debug(f"Running console command {command_str}")
            quiet_goes_to_log = subprocess.PIPE if self._debug_mode else None
            if self._verbose:
                proc_stdout = subprocess.PIPE
                proc_stderr = subprocess.PIPE
            else:
                if self._quiet:
                    proc_stdout = quiet_goes_to_log
                    proc_stderr = quiet_goes_to_log
                else:
                    proc_stdout = subprocess.PIPE
                    proc_stderr = None
            try:
                process = subprocess.Popen(
                    command, stdout=proc_stdout, stderr=proc_stderr, shell=False
                )
                enable_log_timestamp(self._logger, False)
                if proc_stdout is not None:
                    with process.stdout:
                        for line in iter(process.stdout.readline, b""):
                            if self._verbose:
                                self._logger.info(line.decode().strip())
                            else:
                                self._logger.debug(line.decode().strip())
                if proc_stderr is not None:
                    with process.stderr:
                        for line in iter(process.stderr.readline, b""):
                            self._logger.error(line.decode().strip())
                enable_log_timestamp(self._logger, True)
                result = process.wait(timeout=self._timeout)

                if result != 0:
                    err_msg = (
                        f"PSR Cloud console command failed with return code {result}"
                    )
                    self._logger.error(err_msg)
                    raise CloudError(err_msg)
            except subprocess.CalledProcessError as e:
                err_msg = f"PSR Cloud console command failed with exception: {str(e)}"
                self._logger.error(err_msg)
                raise CloudError(err_msg)

    def _validate_case(self, case: "Case") -> "Case":
        if not case.program:
            raise CloudInputError("Program not provided")
        elif case.program not in self.get_programs():
            raise CloudInputError(
                f"Program {case.program} not found. Available programs are: {', '.join(self.get_programs())}"
            )

        if not case.memory_per_process_ratio:
            raise CloudInputError("Memory per process ratio not provided")
        elif case.memory_per_process_ratio not in self.get_memory_per_process_ratios():
            raise CloudInputError(
                f"Memory per process ratio {case.memory_per_process_ratio} not found. Available ratios are: {', '.join(self.get_memory_per_process_ratios())}"
            )

        if case.number_of_processes < 1 or case.number_of_processes > 512:
            raise CloudInputError("Number of processes must be between 1 and 512")

        if case.data_path and not Path(case.data_path).exists():
            raise CloudInputError("Data path does not exist")

        if case.parent_case_id is None:
            case.parent_case_id = 0

        def validate_selection(
            selection, available_options, selection_name, program_name
        ):
            if selection is None:
                raise CloudInputError(
                    f"{selection_name} of program {program_name} not provided"
                )
            elif isinstance(selection, str):
                if selection not in available_options.values():
                    raise CloudInputError(
                        f"{selection_name} {selection} of program {program_name} not found. Available {selection_name.lower()}s are: {', '.join(available_options.values())}"
                    )
                return next(
                    key
                    for key, value in available_options.items()
                    if value == selection
                )
            elif selection not in available_options:
                raise CloudInputError(
                    f"{selection_name} id {selection} of program {program_name} not found. Available {selection_name.lower()} ids are: {', '.join(map(str,available_options.keys()))}"
                )
            return selection

        program_versions = self.get_program_versions(case.program)
        case.program_version_name = case.program_version
        case.program_version = validate_selection(
            case.program_version, program_versions, "Version", case.program
        )

        execution_types = self.get_execution_types(case.program, case.program_version)
        case.execution_type = validate_selection(
            case.execution_type, execution_types, "Execution type", case.program
        )

        instance_type_map = self._get_instance_type_map()
        if all(value[1] == False for value in instance_type_map.values()):
            is_spot_disabled = True
        else:
            is_spot_disabled = False

        if case.price_optimized == True and is_spot_disabled == True:
            raise CloudError("Price Optimized is temporarily unavailable.")

        repository_durations = self.get_repository_durations()
        case.repository_duration = validate_selection(
            case.repository_duration,
            repository_durations,
            "Repository duration",
            case.program,
        )

        if case.budget:
            budgets = self.get_budgets()
            match_list = _budget_matches_list(case.budget, budgets)
            if len(match_list) == 0:
                raise CloudInputError(
                    f'Budget "{case.budget}" not found. Get a list of available budgets using Client().get_budgets().'
                )
            elif len(match_list) > 1:
                raise CloudInputError(
                    f'Multiple budgets found for "{case.budget}". Please use the budget id instead of the name.\n'
                    "\n".join([f' - "{budget}"' for budget in match_list])
                )
            else:
                # Replace partial with complete budget name
                case.budget = match_list[0]

        # MyModel
        if case.program == "MyModel":
            if case.mymodel_program_files is None:
                raise CloudInputError("MyModel program files not provided")

        if case.program != "MyModel" and case.mymodel_program_files is not None:
            msg = "Ignoring mymodel_program_files parameter for non MyModel case."
            warnings.warn(msg)
        return case

    def _pre_process_graph(self, path: str, case_id: int) -> None:
        # This method is only used for testing the graf cloud execution.
        # Error handling is already done on the tests module.
        parameters = {
            "urlServico": self.cluster["url"],
            "usuario": self.username,
            "senha": self.__password,
            "idioma": "3",
            "modelo": "Graf",
            "comando": "PreProcessamento",
            "cluster": self.cluster["name"],
            "repositorioId": str(case_id),
            "diretorioDestino": path,
            "tipoExecucao": "1",
        }

        xml_content = create_case_xml(parameters)
        self._run_console(xml_content)

    def _check_until_status(
        self, case_id: int, requested_status: "ExecutionStatus", timeout: int = 60 * 60
    ) -> bool:
        """
        Check the status of a case until the requested status is reached or timeout occurs.

        :param case_id: The ID of the case to check.
        :param requested_status: The status to wait for.
        :param timeout: The maximum time to wait in seconds (default is 3600 seconds or 1 hour).
        :return: True if the requested status is reached, False if timeout occurs.
        """
        status = None
        last_status = None
        start_time = time()
        original_quiet_flag = self._quiet
        original_verbose_flag = self._verbose
        original_debug_flag = self._debug_mode
        self._quiet, self._verbose, self._debug_mode = True, False, False
        try:
            while status not in FAULTY_TERMINATION_STATUS + [
                ExecutionStatus.SUCCESS,
                requested_status,
            ]:
                if time() - start_time > timeout:
                    self._logger.error(
                        f"Timeout reached while waiting for status {requested_status}"
                    )
                    return False
                status, _ = self.get_status(case_id, quiet=True)
                if last_status != status:
                    self._logger.info(f"Status: {STATUS_MAP_TEXT[status]}")
                last_status = status
                sleep(20)
        finally:
            self._quiet = original_quiet_flag
            self._verbose = original_verbose_flag
            self._debug_mode = original_debug_flag

        return status == requested_status

    def _clean_folder(self, folder):
        for root, dirs, files in os.walk(folder, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)

            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)

    @thread_safe()
    def run_case(self, case: "Case", dry_run=False, **kwargs) -> int:
        self._validate_case(case)
        instance_type_map = self._get_instance_type_map()
        instance_type_id = next(
            key
            for key, value in instance_type_map.items()
            if value[0] == case.memory_per_process_ratio
            and value[1] == case.price_optimized
        )
        case.data_path = _handle_relative_path(case.data_path)

        if case.program == "GRAF":
            wait = True
        else:
            wait = kwargs.get("wait", False)

        if self.application_version:
            interface_version = self.application_version + " - " + INTERFACE_VERSION
        else:
            interface_version = INTERFACE_VERSION
        parameters = {
            "urlServico": self.cluster["url"],
            "usuario": self.username,
            "senha": self.__password,
            "idioma": "3",
            "modelo": case.program,
            "comando": "executar",
            "cluster": self.cluster["name"],
            "diretorioDados": case.data_path,
            "origemDados": "LOCAL",
            "s3Dados": "",
            "nproc": case.number_of_processes,
            "repositorioId": "0",
            "instanciaTipo": instance_type_id,
            "validacaoModelo": "True",
            "validacaoUsuario": "False",
            "idVersao": case.program_version,
            "modeloVersao": case.program_version_name,
            "pathModelo": "C:\\PSR",
            "idTipoExecucao": case.execution_type,
            "nomeCaso": case.name,
            "tipoExecucao": str(int(not wait)),
            "deveAgendar": "False",
            "userTag": "(Untagged)",
            "lifecycle": case.repository_duration,
            "versaoInterface": interface_version,
            "pathPrograma": case.mymodel_program_files,
            "arquivoSaida": case.mymodel_output_file,
        }

        if isinstance(case.parent_case_id, list) and case.parent_case_id is not None:
            parameters["repositoriosPais"] = ",".join(map(str, case.parent_case_id))
        else:
            parameters["repositorioPai"] = case.parent_case_id

        if case.budget:
            parameters["budget"] = case.budget
        if case.upload_only is not None:
            parameters["saveInCloud"] = case.upload_only

        xml_content = create_case_xml(parameters)

        if dry_run:
            return xml_content

        if self._python_client:
            case_id = self._execute_case(parameters)
        else:
            self._run_console(xml_content)
            xml = ET.parse(
                f"{self._get_console_parent_path()}\\fake{case.program}_async.xml"
            )
            _check_for_errors(xml, self._logger)
            id_parameter = xml.find("./Parametro[@nome='repositorioId']")
            if id_parameter is None:
                xml_str = _xml_to_str(xml)
                raise CloudError(
                    f"Case id not found on returned XML response.\n"
                    f"Contact PSR support at psrcloud@psr-inc.com with following data:\n\n{xml_str}\n\n"
                )

            case_id = int(id_parameter.text)
        if not wait:
            self._logger.info(f"Case {case.name} started with id {case_id}")

        if self._import_desktop and case.program != "GRAF":
            try:
                case_copy = copy.deepcopy(case)
                case_copy.id = case_id
                replace_case_str_values(self, case_copy)
                import_case(case_copy, self.cluster["name"], instance_type_id)
            except Exception as e:
                msg = f"Failed to import case {case.name} to desktop:\n{str(e)}"
                self._logger.error(msg)
                warnings.warn(msg)

        return case_id

    def get_status(self, case_id: int, quiet=False) -> tuple["ExecutionStatus", str]:
        delete_xml = not self._debug_mode
        xml_content = ""
        with CreateTempFile(
            str(self.cwd), "psr_cloud_status_", xml_content, delete_xml
        ) as xml_file:
            status_xml_path = os.path.abspath(xml_file.name)

            parameters = {
                "urlServico": self.cluster["url"],
                "usuario": self.username,
                "senha": self.__password,
                "idioma": "3",
                "idFila": str(case_id),
                "modelo": "SDDP",
                "comando": "obterstatusresultados",
                "arquivoSaida": status_xml_path,
            }

            xml = None
            if self._python_client:
                xml = self._get_status_python(parameters)
            else:
                run_xml_content = create_case_xml(parameters)
                self._run_console(run_xml_content)
                xml = ET.parse(status_xml_path)
            parameter_status = xml.find("./Parametro[@nome='statusExecucao']")
            if parameter_status is None:
                xml_str = _xml_to_str(xml)
                raise CloudError(
                    f"Status not found on returned XML response.\n"
                    f"Contact PSR support at psrcloud@psr-inc.com with following data:\n\n{xml_str}\n\n"
                )
            try:
                status = ExecutionStatus(int(parameter_status.text))
            except CloudError:
                xml_str = _xml_to_str(xml)
                raise CloudError(
                    f"Unrecognized status on returned XML response.\n"
                    f"Contact PSR support at psrcloud@psr-inc.com with following data:\n\n{xml_str}\n\n"
                )

            if not quiet:
                self._logger.info(f"Status: {STATUS_MAP_TEXT[status]}")
            return status, STATUS_MAP_TEXT[status]

    def list_download_files(self, case_id: int) -> List[dict]:
        xml_files = self._make_soap_request(
            "prepararListaArquivosRemotaDownload",
            "listaArquivoRemota",
            additional_arguments={
                "cluster": self.cluster["name"],
                "filtro": "(.*)",
                "diretorioRemoto": str(case_id),
            },
        )

        files = []

        for file in xml_files.findall("Arquivo"):
            file_info = {
                "name": file.attrib.get("nome"),
                "filesize": file.attrib.get("filesize"),
                "filedate": file.attrib.get("filedate"),
            }
            files.append(file_info)

        return files

    def download_results(
        self,
        case_id: int,
        output_path: Union[str, Path],
        files: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
    ) -> None:
        filter = ""

        if not extensions and not files:
            extensions = ["csv", "log", "hdr", "bin", "out", "ok"]

        filter_elements = []

        if extensions:
            Client._validate_extensions(extensions)
            filter_elements.extend([f"*.{ext}" for ext in extensions])

        if files:
            filter_elements.extend(files)

        filter += "|".join(filter_elements)

        self._logger.info("Download filter: " + filter)
        case = self.get_case(case_id)
        output_path = _handle_relative_path(output_path)
        parameters = {
            "urlServico": self.cluster["url"],
            "usuario": self.username,
            "senha": self.__password,
            "idioma": "3",
            "_cluster": self.cluster["name"],
            "modelo": case.program,
            "comando": "download",
            "diretorioDestino": output_path,
            "repositorioId": str(case_id),
            "filtroDownloadPorMascara": filter,
        }

        os.makedirs(output_path, exist_ok=True)

        if self._python_client:
            self._download_results_python(parameters)  ## Not implemented yet
        else:
            # Download results using Console
            xml_content = create_case_xml(parameters)
            self._run_console(xml_content)
            self._logger.info(f"Results downloaded to {output_path}")

    def cancel_case(self, case_id: int, wait: bool = False) -> bool:
        parameters = {
            "urlServico": self.cluster["url"],
            "usuario": self.username,
            "senha": self.__password,
            "idioma": "3",
            "modelo": "SDDP",
            "comando": "cancelarfila",
            "cancelamentoForcado": "False",
            "idFila": str(case_id),
        }

        if self._python_client:
            self._cancel_case_python(case_id, parameters)
        else:
            # Cancel case using Console
            xml_content = create_case_xml(parameters)
            self._run_console(xml_content)
        self._logger.info(f"Request to cancel case {case_id} was sent")

        if wait:
            self._logger.info(f"Waiting for case {case_id} to be canceled")
            if self._check_until_status(
                case_id, ExecutionStatus.CANCELLED, timeout=60 * 10
            ):
                self._logger.info(f"Case {case_id} was successfully canceled")
                return True
            else:
                self._logger.error(f"Failed to cancel case {case_id}")
                return False
        else:
            return True

    def _cases_from_xml(self, xml: ET.Element) -> List["Case"]:
        instance_type_map = self._get_instance_type_map()
        cases = []
        for fila in xml.findall("Fila"):
            try:
                case = Case(
                    name=fila.attrib.get("nomeCaso"),
                    data_path=None,
                    program=fila.attrib.get("programa"),
                    program_version=int(fila.attrib.get("idVersao")),
                    execution_type=int(fila.attrib.get("idTipoExecucao")),
                    price_optimized=bool(fila.attrib.get("flagSpot")),
                    number_of_processes=int(fila.attrib.get("numeroProcesso")),
                    id=int(fila.attrib.get("repositorioId")),
                    user=fila.attrib.get("usuario"),
                    execution_date=datetime.strptime(
                        fila.attrib.get("dataInicio"), "%d/%m/%Y %H:%M"
                    ),
                    parent_case_id=int(fila.attrib.get("repositorioPai"))
                    if fila.attrib.get("repositorioPai")
                    else 0,
                    memory_per_process_ratio=(
                        instance_type_map[int(fila.attrib.get("instanciaTipo"))][0]
                        if fila.attrib.get("instanciaTipo") in instance_type_map
                        else min([value[0] for value in instance_type_map.values()])
                    ),
                    repository_duration=int(fila.attrib.get("duracaoRepositorio")),
                    budget=fila.attrib.get("budget"),
                )
                cases.append(case)
            except (TypeError, ValueError):
                pass
                # case_id = fila.attrib.get("repositorioId")
                # Optionally, log the error or handle it as needed
                # self._logger.error(f"Error processing case with ID {case_id}: {e}")

        # sort cases by execution date desc
        cases.sort(key=lambda x: x.execution_date, reverse=True)
        return cases

    def get_all_cases_since(
        self, since: Union[int, datetime] = _DEFAULT_GET_CASES_SINCE_DAYS
    ) -> List["Case"]:
        if isinstance(since, int):
            initial_date = datetime.now() - timedelta(days=since)
            initial_date_iso = initial_date.isoformat().replace("T", " ")[:-7]
        else:
            initial_date_iso = since.strftime("%Y-%m-%d %H:%M:%S")

        xml = self._make_soap_request(
            "listarFila",
            "dados",
            additional_arguments={"dataInicial": initial_date_iso},
        )

        return self._cases_from_xml(xml)

    def get_case(self, case_id: int) -> "Case":
        cases = self.get_cases([case_id])
        if cases and len(cases) > 0:
            return cases[0]
        raise CloudInputError(f"Case {case_id} not found")

    def get_cases(self, case_ids: List[int]) -> List["Case"]:
        case_ids_str = ",".join(map(str, case_ids))
        xml = self._make_soap_request(
            "listarFila",
            "dados",
            additional_arguments={"listaRepositorio": case_ids_str},
        )
        return self._cases_from_xml(xml)

    def get_budgets(self) -> list:
        xml = self._make_soap_request(
            "listarCluster",
            "listaCluster",
        )

        budgets = []
        for cluster in xml.findall("Cluster"):
            if cluster.attrib.get("nome").lower() == self.cluster["name"].lower():
                collection = cluster.findall("ColecaoBudget")[0]
                budgets = [
                    budget.attrib.get("nome") for budget in collection.findall("Budget")
                ]
                break
        budgets.sort()
        return budgets

    def get_number_of_processes(self, programa_nome):
        xml = self._get_cloud_versions_xml()

        programa = xml.find(f".//Programa[@nome='{programa_nome}']")
        if programa is None:
            raise CloudError(f"Programa '{programa_nome}' não encontrado.")

        cluster = programa.find(f".//Cluster[@nome='{self.cluster['name']}']")
        if cluster is None:
            raise CloudError(
                f"Cluster '{self.cluster['name']}' não encontrado no programa '{programa_nome}'."
            )

        maximo_processos = cluster.get("maximoProcessos")
        processos_por_maquina = cluster.get("processosPorMaquina")

        if maximo_processos and processos_por_maquina:
            maximo_processos = int(maximo_processos)
            processos_por_maquina = int(processos_por_maquina)

            lista_processos = list(
                range(
                    processos_por_maquina, maximo_processos + 1, processos_por_maquina
                )
            )

            return lista_processos

        raise CloudError(f"Invalid values for cluster '{self.cluster['name']}'.")

    def _make_soap_request(self, service: str, name: str = "", **kwargs) -> ET.Element:
        portal_ws = zeep.Client(self.cluster["url"] + "?WSDL")
        section = str(id(self))
        password_md5 = self.__password.upper()
        additional_arguments = kwargs.get("additional_arguments", None)
        parameters = {
            "sessao_id": section,
            "tipo_autenticacao": "bcrypt",
            "idioma": "3",
            "versao_cliente": self._get_console_version().split("-")[0]
            if not self._python_client
            else "5.4.0",
        }
        if additional_arguments:
            parameters.update(additional_arguments)

        xml_input = create_case_xml(parameters)

        try:
            xml_output_str = portal_ws.service.despacharServico(
                service, self.username, password_md5, xml_input
            )
        except zeep.exceptions.Fault as e:
            # Log the full exception details
            self._logger.error(f"Zeep Fault: {str(e)}")
            raise CloudError(
                "Failed to connect to PSR Cloud service. Contact PSR support: psrcloud@psr-inc.com"
            )
        # Remove control characters - this is a thing
        xml_output_str = xml_output_str.replace("&amp;#x1F;", "")

        xml_output = ET.fromstring(xml_output_str)

        if name:
            for child in xml_output:
                if child.attrib.get("nome") == name:
                    xml_output = ET.fromstring(child.text)
                    break
            else:
                raise ValueError(
                    f"Invalid XML response from PSR Cloud: {xml_output_str}. Please contact PSR support at psrcloud@psr-inc.com"
                )
        return xml_output

    def _get_cloud_versions_xml(self) -> ET.Element:
        if self._cloud_version_xml_cache is not None:
            return self._cloud_version_xml_cache
        self._cloud_version_xml_cache = self._make_soap_request("obterVersoes", "dados")
        return self._cloud_version_xml_cache

    def _get_cloud_clusters_xml(self) -> ET.Element:
        if self._cloud_clusters_xml_cache is not None:
            return self._cloud_clusters_xml_cache
        self._cloud_clusters_xml_cache = self._make_soap_request(
            "listarCluster", "listaCluster"
        )
        return self._cloud_clusters_xml_cache

    def _execute_case(self, case_dict) -> int:
        """
        Execute a case on the PSR Cloud.
        :param case_dict: Dictionary containing the case parameters.
        :return: Case ID of the executed case.
        """
        case_dict["programa"] = case_dict["modelo"]
        case_dict["numeroProcessos"] = case_dict["nproc"]
        case_dict["versao_cliente"] = "5.4.0"
        filter_request_result = self._make_soap_request(
            "obterFiltros", additional_arguments=case_dict
        )
        upload_filter = filter_request_result.find(
            "./Parametro[@nome='filtroUpload']"
        ).text
        upload_filter = "^[a-zA-Z0-9./_]*(" + upload_filter + ")$"

        # Create Repository
        self._logger.info("Creating remote repository")
        repository_request_result = self._make_soap_request(
            "criarRepositorio", additional_arguments=case_dict
        )

        # Add all parameters from the XML response to case_dict
        # Iterates over each <Parametro> element in the XML response,
        # extracts the 'nome' attribute for the key and the element's text for the value,
        # then adds this key-value pair to case_dict.
        for parametro_element in repository_request_result.findall("./Parametro"):
            param_name = parametro_element.get("nome")
            param_value = (
                parametro_element.text
            )  # This will be None if the element has no text.
            if param_name:  # Ensure the parameter has a name before adding.
                case_dict[param_name] = param_value

        repository_id = repository_request_result.find(
            "./Parametro[@nome='repositorioId']"
        )
        cloud_access = repository_request_result.find(
            "./Parametro[@nome='cloudAccess']"
        )
        cloud_secret = repository_request_result.find(
            "./Parametro[@nome='cloudSecret']"
        )
        cloud_session_token = repository_request_result.find(
            "./Parametro[@nome='cloudSessionToken']"
        )
        cloud_aws_url = repository_request_result.find("./Parametro[@nome='cloudUrl']")
        bucket_name = repository_request_result.find(
            "./Parametro[@nome='diretorioBase']"
        )

        self._logger.info(f"Remote repository created with ID {repository_id.text}")
        case_dict["repositorioId"] = repository_id.text

        # Filtering files to upload
        self._logger.info("Checking list of files to send")

        file_list = _filter_upload_files(case_dict["diretorioDados"], upload_filter)

        if not file_list:
            self._logger.warning(
                "No files found to upload. Please check the upload filter."
            )
            return

        # generating .metadata folder with checksum for each file
        checksum_dictionary = {}
        metadata_folder = Path(case_dict["diretorioDados"]) / ".metadata"
        metadata_folder.mkdir(parents=True, exist_ok=True)
        for file_path in file_list:
            file_path = Path(file_path)
            if not file_path.is_absolute():
                file_path = Path(case_dict["diretorioDados"]) / file_path
            if not file_path.exists():
                self._logger.warning(f"File {file_path} does not exist. Skipping.")
                continue
            with open(file_path, "rb") as f:
                checksum = _md5sum(f.read(), enconding=False).upper()
            checksum_dictionary[file_path.name] = checksum
            metadata_file = metadata_folder / (file_path.name)
            with open(metadata_file, "w") as f:
                f.write(checksum)

        self._logger.info(
            f"Uploading list of files to remote repository {repository_id.text}"
        )

        # Uploading files to S3
        upload_case_to_s3(
            files=file_list,
            repository_id=repository_id.text,
            cluster_name=self.cluster["name"],
            checksums=checksum_dictionary,
            access=cloud_access.text if cloud_access is not None else None,
            secret=cloud_secret.text if cloud_secret is not None else None,
            session_token=cloud_session_token.text
            if cloud_session_token is not None
            else None,
            bucket_name=bucket_name.text if bucket_name is not None else None,
            url=cloud_aws_url.text if cloud_aws_url is not None else None,
            zip_compress=True,
        )

        self._make_soap_request(
            "finalizarUpload",
            additional_arguments={"repositorioId": repository_id.text},
        )
        self._logger.info("Files uploaded successfully. Enqueuing case.")
        self._make_soap_request("enfileirarProcesso", additional_arguments=case_dict)

        return repository_id.text

    def _get_status_python(self, case_dict: dict) -> ET.Element:
        """
        Get the status of a case using the Python client.
        :param case_dict: Dictionary containing the case parameters.
        :return: XML Element with the status information.
        """
        try:
            response = self._make_soap_request(
                "obterStatusResultados", additional_arguments=case_dict
            )

            # change response "status" parameter to "statusExecucao", as it is with current PSR Cloud
            status_param = response.find("./Parametro[@nome='status']")
            if status_param is not None:
                status_param.attrib["nome"] = "statusExecucao"

            result_log = response.find("./Parametro[@nome='resultado']")
            if self._verbose and result_log is not None:
                self._logger.info(result_log.text)
            return response
        except Exception as e:
            self._logger.error(f"Error getting status: {str(e)}")
            raise CloudError(f"Failed to get status: {str(e)}")

    def _cancel_case_python(self, case_id: int, xml_content: str) -> None:
        """
        Cancel a case using the Python client.
        :param case_id: The ID of the case to cancel.
        :param xml_content: XML content for the cancel request.
        """
        try:
            self._make_soap_request(
                "cancelarFila", additional_arguments={"idFila": str(case_id)}
            )
        except Exception as e:
            self._logger.error(f"Error cancelling case: {str(e)}")
            raise CloudError(f"Failed to cancel case: {str(e)}")

    def _download_results_python(self, parameters: dict) -> None:
        """
        Download results using the Python client.
        :param parameters: Dictionary containing the download parameters.
        """

        repository_id = parameters.get("repositorioId")
        download_filter = parameters.get("filtroDownloadPorMascara")
        output_path = parameters.get("diretorioDestino")

        download_filter = (
            "^[a-zA-Z0-9./_]*(" + download_filter + ")$" if download_filter else None
        )
        self._logger.info("Obtaining credentials for download")
        credentials = self._make_soap_request(
            "buscaCredenciasDownload", additional_arguments=parameters
        )

        access = credentials.find("./Parametro[@nome='cloudAccess']").text
        secret = credentials.find("./Parametro[@nome='cloudSecret']").text
        session_token = credentials.find("./Parametro[@nome='cloudSessionToken']").text
        url = credentials.find("./Parametro[@nome='cloudUrl']").text
        bucket_name = credentials.find("./Parametro[@nome='diretorioBase']").text
        bucket_name = bucket_name.replace("repository", "repository-download")

        if access is None or secret is None or session_token is None or url is None:
            raise CloudError("Failed to retrieve credentials for downloading results.")

        file_list = self.list_download_files(repository_id)

        # filtering files to download
        if download_filter:
            filtered_file_list = [
                file["name"]
                for file in file_list
                if re.match(download_filter, file["name"])
            ]
        else:
            filtered_file_list = [file["name"] for file in file_list]

        self._logger.info("Downloading results")
        downloaded_list = download_case_from_s3(
            repository_id=parameters["repositorioId"],
            cluster_name=self.cluster["name"],
            access=access,
            secret=secret,
            session_token=session_token,
            bucket_name=bucket_name,
            url=url,
            output_path=output_path,
            file_list=filtered_file_list,
        )

        # Decompress gzipped files
        for file in filtered_file_list:
            if self._is_file_gzipped(os.path.join(output_path, file)):
                self._decompress_gzipped_file(os.path.join(output_path, file))

        # Check if all requested files were downloaded
        for file in filtered_file_list:
            if file not in downloaded_list:
                self._logger.warning(f"File {file} was not downloaded.")

        self._logger.info(f"Results downloaded to {output_path}")

    def _is_file_gzipped(self, file_path: str) -> bool:
        """
        Checks if a file is gzipped by inspecting its magic number.

        :param file_path: The path to the file.
        :return: True if the file is gzipped, False otherwise.
        """
        try:
            with open(file_path, "rb") as f_check:
                return f_check.read(2) == b"\x1f\x8b"
        except IOError:
            # TODO: Replace print with proper logging
            print(
                f"WARNING: Could not read {file_path} to check for gzip magic number."
            )
            return False

    def _decompress_gzipped_file(self, gzipped_file_path: str) -> str:
        """
        Decompresses a gzipped file.

        If the original filename ends with .gz, the .gz is removed for the
        decompressed filename. Otherwise, the file is decompressed in-place.
        The original gzipped file is removed upon successful decompression.

        :param gzipped_file_path: The path to the gzipped file.
        :return: The path to the decompressed file. If decompression fails,
                the original gzipped_file_path is returned.
        """
        decompressed_target_path = (
            gzipped_file_path[:-3]
            if gzipped_file_path.lower().endswith(".gz")
            else gzipped_file_path
        )
        # Use a temporary file for decompression to avoid data loss if issues occur
        temp_decompressed_path = decompressed_target_path + ".decompressing_tmp"

        try:
            with gzip.open(gzipped_file_path, "rb") as f_in, open(
                temp_decompressed_path, "wb"
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(gzipped_file_path)
            os.rename(temp_decompressed_path, decompressed_target_path)
            return decompressed_target_path
        except (gzip.BadGzipFile, EOFError, IOError) as e:
            print(
                f"ERROR: Failed to decompress {gzipped_file_path}: {e}. Original file kept."
            )
        except (
            Exception
        ) as e:  # Catch other errors like permission issues during rename/remove
            print(
                f"ERROR: Error during post-decompression file operations for {gzipped_file_path}: {e}. Original file kept."
            )
        finally:
            if os.path.exists(
                temp_decompressed_path
            ):  # Clean up temp file if it still exists
                os.remove(temp_decompressed_path)
        return gzipped_file_path  # Return original path if decompression failed

    def get_programs(self) -> List[str]:
        xml = self._get_cloud_versions_xml()
        programs = [model.attrib["nome"] for model in xml]
        return [program for program in programs if program in _ALLOWED_PROGRAMS]

    def get_program_versions(self, program: str) -> dict[int, str]:
        if not isinstance(program, str):
            raise CloudInputError("Program must be a string")
        elif program not in self.get_programs():
            raise CloudInputError(
                f"Program {program} not found. Available programs: {', '.join(self.get_programs())}"
            )
        xml = self._get_cloud_versions_xml()
        versions = {}

        for model in xml:
            if model.attrib["nome"] == program:
                for version_child in model.findall(".//Versao"):
                    version_id = int(version_child.attrib["id"])
                    version_name = version_child.attrib["versao"]
                    versions[version_id] = version_name

        return versions

    def get_execution_types(
        self, program: str, version: Union[str, int]
    ) -> dict[int, str]:
        if not isinstance(program, str):
            raise CloudInputError("Program must be a string")
        elif program not in self.get_programs():
            raise CloudInputError(
                f"Program {program} not found. Available programs: {', '.join(self.get_programs())}"
            )
        if isinstance(version, int):
            if version not in self.get_program_versions(program):
                raise CloudInputError(
                    f"Version id {version} of program {program} not found. Available version ids: {', '.join(map(str, list(self.get_program_versions(program).keys())))}"
                )
            version = next(
                v for k, v in self.get_program_versions(program).items() if k == version
            )
        elif version not in self.get_program_versions(program).values():
            raise CloudInputError(
                f"Version {version} of program {program} not found. Available versions: {', '.join(self.get_program_versions(program).values())}"
            )
        xml = self._get_cloud_versions_xml()
        return {
            int(execution_type.attrib["id"]): execution_type.attrib["nome"]
            for program_child in xml
            if program_child.attrib["nome"] == program
            for version_child in program_child[0][0][0]
            if version_child.attrib["versao"] == version
            for execution_type in version_child[0]
        }

    def get_memory_per_process_ratios(self) -> List[str]:
        xml = self._get_cloud_clusters_xml()
        return sorted(
            list(
                {
                    f"{instance_type.attrib['memoriaPorCore']}:1"
                    for cluster in xml
                    if cluster.attrib["nome"] == self.cluster["name"]
                    for colection in cluster
                    if colection.tag == "ColecaoInstanciaTipo"
                    for instance_type in colection
                }
            )
        )

    def get_repository_durations(self) -> dict[int, str]:
        if self.cluster == "PSR-US":
            return {
                2: "Normal (1 month)",
            }

        else:
            return {
                1: "Short (1 week)",
                2: "Normal (1 month)",
                3: "Extended (6 months)",
                4: "Long (2 years)",
            }

    def _get_instance_type_map(self) -> dict[int, tuple[str, bool]]:
        if self._instance_type_map is not None:
            return self._instance_type_map
        xml = self._get_cloud_clusters_xml()
        self._instance_type_map = {
            int(instance_type.attrib["id"]): (
                f'{instance_type.attrib["memoriaPorCore"]}:1',
                "Price Optimized" in instance_type.attrib["descricao"],
            )
            for cluster in xml
            if cluster.attrib["nome"] == self.cluster["name"]
            for collection in cluster
            if collection.tag == "ColecaoInstanciaTipo"
            for instance_type in collection
        }
        return self._instance_type_map

    @staticmethod
    def _validate_extensions(extensions: List[str]):
        for ext in extensions:
            if not ext.isalnum():
                raise CloudInputError(
                    f"Invalid extension '{ext}' detected. Extensions must be alphanumeric."
                )


def _budget_matches_list(budget_part: str, all_budgets: List[str]) -> List[str]:
    """Tests if a part of a budget name is in the list all_budgets and returns a list of matches."""
    lowered_budget_part = budget_part.lower()
    return [budget for budget in all_budgets if lowered_budget_part in budget.lower()]


def _filter_upload_files(directory: str, upload_filter: str) -> List[str]:
    """
    Filter files in a directory based on the upload filter.
    :param directory: Directory to filter files from.
    :param upload_filter: Regular expression filter for file names.
    :return: List of filtered file paths.
    """
    if not os.path.exists(directory):
        raise CloudInputError(f"Directory {directory} does not exist")

    regex = re.compile(upload_filter)
    filtered_files = []
    for file in os.listdir(directory):
        if regex.match(file):
            filtered_files.append(os.path.join(directory, file))
    return filtered_files


def replace_case_str_values(client: Client, case: Case) -> Case:
    """Create a new case object using internal integer IDs instead of string values."""
    # Model Version
    if isinstance(case.program_version, str):
        program_versions = client.get_program_versions(case.program)
        case.program_version = next(
            key
            for key, value in program_versions.items()
            if value == case.program_version
        )

    # Execution Type
    if isinstance(case.execution_type, str):
        execution_types = client.get_execution_types(case.program, case.program_version)
        case.execution_type = next(
            key
            for key, value in execution_types.items()
            if value == case.execution_type
        )
    return case
