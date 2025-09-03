# PSR Factory. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from contextlib import contextmanager
import glob
import os
import pathlib
import shutil
import socket
import subprocess
from types import ModuleType
from typing import Dict, List, Optional, Tuple, Union
import warnings


from psr.psrfcommon import change_cwd, exec_cmd
import psr.psrfcommon.tempfile
import psr.factory

# Check whether psutil module is available.
_HAS_PSUTIL: Optional[bool] = None

psutil: Optional[ModuleType] = None

_DEBUG: bool = True


def _has_psutil() -> bool:
    """Check if psutil is available."""
    global _HAS_PSUTIL
    global psutil
    if _HAS_PSUTIL is None:
        try:
            import psutil
            _HAS_PSUTIL = True
        except ImportError:
            _HAS_PSUTIL = False
    return _HAS_PSUTIL


if os.name == "nt":
    __default_mpi_path = "C:\\Program Files\\MPICH2\\bin"
else:
    __default_mpi_path = "/usr/bin"


def _get_semver_version(version: str) -> Tuple[int, int, Union[int, str], Optional[str]]:
    def get_tag_from_part(part: str) -> Tuple[int, Optional[str]]:
        to_try = ("beta", "rc")
        part = part.lower()
        for tag_name in to_try:
            if tag_name in part:
                tag_pos = part.lower().index(tag_name)
                part_value = int(part[:tag_pos])
                tag = part[tag_pos:]
                return part_value, tag
        return int(part), None
    parts = version.split(".")
    major = int(parts[0])
    tag = None
    minor = 0
    patch = 0
    if len(parts) == 2:
        minor, tag = get_tag_from_part(parts[1])
        patch = 0
    elif len(parts) == 3:
        minor = int(parts[1])
        patch, tag = get_tag_from_part(parts[2])

    return major, minor, patch, tag


def _get_available_cpu() -> int:
    if not _has_psutil():
        raise ImportError("psutil module is required to get available CPU count")
    return psutil.cpu_count()


def _get_host_name() -> str:
    return socket.gethostname().upper()


def _get_nproc(specified: int, available: int) -> int:
    if available > specified:
        return specified
    elif available < specified:
        warnings.warn(f"Specified number of threads ({specified}) is greater than available ({available})")
        return available
    else:
        return available

def _write_mpi_settings(mpi_file_path: Union[str, pathlib.Path], cluster_settings: Optional[Union[int, bool, Dict[str, int]]]):
    if cluster_settings is not None:
        mpi_file_path = str(mpi_file_path)
        available_cpu = _get_available_cpu()
        if isinstance(cluster_settings, int):
            computer_name = _get_host_name()
            specified_cpu_number = cluster_settings
            nproc = _get_nproc(specified_cpu_number, available_cpu)
            cluster_settings = {computer_name: nproc}
        elif isinstance(cluster_settings, dict):
            pass
        elif isinstance(cluster_settings, bool):
            # Rewrite with default settings.
            if cluster_settings:
                computer_name = _get_host_name()
                nproc = available_cpu
                cluster_settings = {computer_name: nproc}
            else:
                cluster_settings = None
        else:
            raise ValueError("Invalid cluster settings type")
    else:
        computer_name = socket.gethostname()
        nproc = _get_available_cpu()
        cluster_settings = {computer_name: nproc}

    if isinstance(cluster_settings, dict):
        with open(mpi_file_path, 'w') as f:
            for computer, nproc in cluster_settings.items():
                f.write(f"{computer}:{nproc}\n")



def run_sddp(case_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    case_path = os.path.abspath(str(case_path))
    sddp_path = str(sddp_path)
    parallel_run = kwargs.get("parallel_run", True)
    cluster_settings: Optional[Union[int, bool, Dict[str, int]]] = kwargs.get("cluster_settings", False)
    dry_run = kwargs.get("dry_run", False)
    show_progress = kwargs.get("show_progress", False)
    extra_args = " ".join(kwargs.get("extra_args", ()))
    exec_mode = kwargs.get("_mode", None)
    mpi_path = kwargs.get("mpi_path", __default_mpi_path)

    sddp_path_full = _get_sddp_executable_parent_path(sddp_path)
    # Append last / if missing.
    case_path_last_slash = os.path.join(os.path.abspath(case_path), "")

    mode_arg = exec_mode if exec_mode is not None else ""
    # Disable parallel run in check mode.
    parallel_run = parallel_run if exec_mode is None else False

    major, minor, patch, tag = _get_semver_version(get_sddp_version(sddp_path))

    with change_cwd(sddp_path_full):
        # Write MPI settings if required
        if parallel_run and cluster_settings is not None:
            if major >= 18:
                mpi_file_path = os.path.join(sddp_path_full, "mpd_sddp.hosts")
            else:
                mpi_file_path = os.path.join(sddp_path_full, "mpd.hosts")
            _write_mpi_settings(mpi_file_path, cluster_settings)

        if parallel_run:
            if os.name == 'nt':
                if major <= 17:
                    cmd = f'sddpar.exe --path="{sddp_path_full}" --mpipath="{mpi_path}" --pathdata="{case_path_last_slash}" {extra_args}'
                else:
                    cmd = f'sddpar.exe --path="{sddp_path_full}" --mpipath="{mpi_path}" --pathdata="{case_path}" {extra_args}'
            else:
                # 17.3 and before uses one type of args, newer uses another
                if (major == 17 and minor <= 3) or major < 17:
                    cmd = f'./sddpar --path="{case_path_last_slash}" --mpipath="{mpi_path}" --habilitarhidra=1 {extra_args}'
                else:
                    cmd = f'./sddpar --path="{sddp_path}" --mpipath="{mpi_path}" --habilitarhidra=1 --pathdata="{case_path_last_slash}" {extra_args}'

        else:
            if os.name == 'nt':
                cmd = f'sddp.exe {mode_arg} -path "{case_path_last_slash}" {extra_args}'
            else:
                cmd = f'./sddp {mode_arg} -path "{case_path_last_slash}" {extra_args}'

        if os.name != "nt":
            os.environ["LD_LIBRARY_PATH"] = os.path.abspath(sddp_path_full)
        exec_cmd(cmd, **kwargs)


def run_sddp_check(case_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    kwargs["_mode"] = "check"
    run_sddp(case_path, sddp_path, **kwargs)


def run_sddp_cleanup(case_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    kwargs["_mode"] = "clean"
    run_sddp(case_path, sddp_path, **kwargs)


def run_sddp_convert_fcf(case_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    kwargs["_mode"] = "printfcf"
    # TODO: generated file use \t as separator, has an empty column and its name depends on study stage type.
    run_sddp(case_path, sddp_path, **kwargs)

def _get_sddp_executable_parent_path(sddp_path: Union[str, pathlib.Path]) -> str:
    if os.name == 'nt':
        model_path = os.path.join(sddp_path, "models", "sddp")
        if os.path.exists(model_path):
            return model_path
        else:
            return os.path.join(sddp_path, "Oper")
    return sddp_path

def _get_optgen_executable_parent_path(optgen_path: Union[str, pathlib.Path]) -> str:
    if os.name == 'nt':
        model_path = os.path.join(optgen_path, "models", "optgen", "Model")
        if os.path.exists(model_path):
            return model_path
        else:
            return os.path.join(optgen_path, "Model")
    return optgen_path


def get_sddp_version(sddp_path: Union[str, pathlib.Path]) -> str:
    sddp_path = str(sddp_path)
    sddp_path_full = _get_sddp_executable_parent_path(sddp_path)
    if os.name == 'nt':
        command = [os.path.join(sddp_path_full, "sddp.exe"), "ver"]
    else:
        command = [os.path.join(sddp_path_full, "sddp"), "ver"]

    if os.name != "nt":
        os.environ["LD_LIBRARY_PATH"] = os.path.abspath(sddp_path_full)
    sub = subprocess.run(command, stdout=subprocess.PIPE, check=False)
    output = sub.stdout.decode("utf-8").strip()
    return output.split()[2]


def run_ncp(case_path: Union[str, pathlib.Path], ncp_path: Union[str, pathlib.Path], **kwargs):
    if os.name != 'nt':
        raise NotImplementedError("Running NCP is only available on Windows")
    case_path = os.path.abspath(str(case_path))
    ncp_path = str(ncp_path)
    dry_run = kwargs.get("dry_run", False)
    show_progress = kwargs.get("show_progress", False)

    cnv_version = _ncp_determine_cnv_version(case_path)

    print("NCP cnv version is", cnv_version)

    ncp_path_full = os.path.join(ncp_path, "Oper")
    cnv_path_full = os.path.join(ncp_path, "Cnv", cnv_version)

    # Append last / if missing.
    case_path = os.path.join(os.path.abspath(case_path), "")

    coes_tmp_file_path = os.path.join(case_path, "coes.dat")
    coes_dat_file_path = os.path.join(case_path, "coes.tmp")

    with change_cwd(cnv_path_full):
        if os.path.exists(coes_dat_file_path):
            shutil.move(coes_dat_file_path, coes_tmp_file_path)
        exec_cmd(f"csvcnv csv -path {case_path}")

    with change_cwd(ncp_path_full):
        exec_cmd(f"sddprede -path {case_path}")
        if os.path.exists(coes_tmp_file_path):
            shutil.move(coes_tmp_file_path, coes_dat_file_path)

        exec_cmd(f"cpplus -path {case_path}")

        executed_successfully = os.path.exists(os.path.join(case_path, 'cpplus.ok'))
        if executed_successfully:
            if os.path.exists("post-run.bat"):
                exec_cmd(f'post-run.bat "{case_path}"')


def run_optgen(case_path: Union[str, pathlib.Path], optgen_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    case_path = os.path.abspath(str(case_path)).replace("\\", "/") + "/"
    optgen_path = str(optgen_path)
    sddp_path = str(sddp_path)
    sddp_path_full = _get_sddp_executable_parent_path(sddp_path)
    optgen_path_full = _get_optgen_executable_parent_path(optgen_path)
    exec_mode = kwargs.get("_mode", None)

    mode_arg = exec_mode if exec_mode is not None else ""

    with change_cwd(optgen_path_full):
        cmd = f'optgen {mode_arg} -optgdat="{case_path}" -sddpexe="{sddp_path_full}" -sddpmpi="{__default_mpi_path}"'
        exec_cmd(cmd, **kwargs)


def run_optgen_check(case_path: Union[str, pathlib.Path], optgen_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    kwargs["_mode"] = "check"
    run_optgen(case_path, optgen_path, sddp_path, **kwargs)


def run_optgen_cleanup(case_path: Union[str, pathlib.Path], optgen_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    kwargs["_mode"] = "clean"
    run_optgen(case_path, optgen_path, sddp_path, **kwargs)

def run_psrio(case_path, sddp_path: str, **kwargs):
    recipe_script = kwargs.get('r', kwargs.get('recipes', False))
    output_path = kwargs.get('o', kwargs.get('output', False))

    log_verbose = kwargs.get('v', kwargs.get('verbose', "0"))
    study_model = kwargs.get('model', "sddp")
    load_file_format = kwargs.get('load_format', "both")

    load_from_output_path = kwargs.get('load_from_output_path', False)
    save_only_in_csv = kwargs.get('csv', False)

    psrio_path_full = os.path.join(sddp_path, "Oper\\psrio\\")

    with change_cwd(psrio_path_full):

        cmd = psrio_path_full + 'psrio.exe --model ' + study_model + ' --load_format ' + load_file_format

        if recipe_script:
            cmd += '-v' + log_verbose

        if load_from_output_path:
            cmd += ' load_from_output_path'
        if save_only_in_csv:
            cmd += ' save_only_in_csv'
        
        if output_path:
            cmd += f' -o "{output_path}"'
        if recipe_script:
            cmd += f' -r "{recipe_script}"'

        if isinstance(case_path, str):
            cmd += f' "{case_path}"'
        else:
            case_paths = list(case_path)
            for path in case_paths:
                cmd += f' "{path}"'
                
        exec_cmd(cmd, **kwargs)

def run_nwsddp(input_case_path: Union[str, pathlib.Path], output_case_path: Union[str, pathlib.Path], nwsddp_app_path: Union[str, pathlib.Path], mdc_file_path: Optional[Union[str, pathlib.Path]] = None, **kwargs):
    if os.name != 'nt':
        raise NotImplementedError("Running NWSDDP is only available on Windows")

    input_case_path = os.path.abspath(str(input_case_path)).rstrip("\\")
    output_case_path = os.path.abspath(str(output_case_path)).rstrip("\\")
    nwsddp_app_path = str(nwsddp_app_path)
    mdc_file_path = str(mdc_file_path)

    if mdc_file_path is not None:
        mdc_file_path = os.path.abspath(mdc_file_path)
    nwsddp_path_full = os.path.join(nwsddp_app_path, "bin", "")

    with change_cwd(nwsddp_path_full):
        if mdc_file_path is not None:
            extra_args = "-MDC "
            # Copy mdc file to case directory.
            output_mdc_path = os.path.join(input_case_path, "nwsddp.mdc")
            # compare if input and output mdc path are equal
            if mdc_file_path.lower().strip() != output_mdc_path.lower().strip():
                shutil.copy(mdc_file_path, output_mdc_path)
        case_args = f"-NW:\"{os.path.join(input_case_path, '')}\" -SP:\"{os.path.join(output_case_path, '')}\""
        cmd1 = 'nwsddp.exe ' + extra_args + case_args
        return_code = exec_cmd(cmd1, **kwargs)
        if return_code == 0:
            cmd2_args = ["nwpatch.exe", "-nw", f"{input_case_path}", "-sp", f"{output_case_path}"]
            exec_cmd(cmd2_args, **kwargs)



__hydro_estimation_path_contents = """                          ------- PATH ---------------------------
Directorio Datos          {path}
Directorio Hidro          {path}
"""


def run_hydro_estimation(case_path: Union[str, pathlib.Path], sddp_path: Union[str, pathlib.Path], **kwargs):
    if os.name != 'nt':
        raise NotImplementedError("Running hydro estimation is only available on Windows")
    case_path = os.path.abspath(str(case_path))
    sddp_path = str(sddp_path)
    estima_path = os.path.join(sddp_path, "Hidro")
    estima_files = [
        os.path.join(estima_path, "estima.exe"),
        os.path.join(estima_path, "estimaen.fmt"),
        os.path.join(estima_path, "estimaes.fmt"),
        os.path.join(estima_path, "estimapo.fmt"),
    ]

    path_file = os.path.join(case_path, "path.dat")
    path_file_contents = __hydro_estimation_path_contents.format(path=case_path)
    with change_cwd(case_path), __temporary_copy_of_files(case_path, *estima_files), \
            __temporary_file(path_file, path_file_contents):
        # create temporary path.dat file
        exec_cmd(f"estima", **kwargs)


def run_graph(case_path: Union[str, pathlib.Path], graph_path: Union[str, pathlib.Path], **kwargs):
    if os.name != 'nt':
        raise NotImplementedError("Running graph tool is only available on Windows")
    case_path = os.path.abspath(str(case_path))
    graph_base_path = os.path.abspath(str(graph_path))
    graph_abs_path = os.path.join(graph_base_path, "PSRGraphInterface.exe")

    with change_cwd(case_path):
        exec_cmd(graph_abs_path, **kwargs)


def run_psrcloud(psrcloud_path: Union[str, pathlib.Path], **kwargs):
    if os.name != 'nt':
        raise NotImplementedError("Running PSRCloud Desktop tool is only available on Windows")
    psrcloud_base_path = os.path.abspath(str(psrcloud_path))

    with change_cwd(psrcloud_base_path):
        exec_cmd("PSRCloud.exe", **kwargs)


@contextmanager
def __temporary_copy_of_files(target_dir: str, *files: str):
    for file in files:
        shutil.copy(file, target_dir)
    try:
        yield
    finally:
        for file in files:
            os.remove(os.path.join(target_dir, os.path.basename(file)))


@contextmanager
def __temporary_file(file_path: Union[str, pathlib.Path], content: str):
    with open(file_path, 'w') as file:
        file.write(content)
    try:
        yield
    finally:
        os.remove(file_path)


def _ncp_determine_cnv_version(case_path: Union[str, pathlib.Path]) -> str:
    CURRENT_CNV_VERSION = "V14"
    LEGACY_CNV_VERSION = "V12"

    csumcirc_path = os.path.join(case_path, "csumcirc.dat")
    if os.path.exists(csumcirc_path):
        with open(csumcirc_path, 'r') as csumcirc_file:
            line = next(csumcirc_file)
            if line.strip().lower().find("$version") == -1:
                return LEGACY_CNV_VERSION

    all_ctermis = glob.glob(os.path.join(case_path, "ctermi*.dat"))
    for ctermi_path in all_ctermis:
        with open(ctermi_path, 'r') as ctermi_file:
            line = next(ctermi_file)
            if line.strip().lower().find("$version=") == -1:
                return LEGACY_CNV_VERSION

    all_cgnds = glob.glob(os.path.join(case_path, "cgnd*.dat"))
    for cgnd_path in all_cgnds:
        with open(cgnd_path, 'r') as cgnd_file:
            line = next(cgnd_file)
            if line.strip().lower().find("$version=") == -1:
                return LEGACY_CNV_VERSION

    return CURRENT_CNV_VERSION


def _tsl_filter_plants_with_coordinates(plant_list: List[psr.factory.DataObject]):
    filtered = []
    for plant in plant_list:
        lat = plant.get("Latitude")
        lon = plant.get("Longitude")
        if not((lat) and (lon)):
            filtered.append(plant)
    return filtered

def _tsl_get_renewable_plants_with_coordinates(study: psr.factory.Study, tech_type: int) -> List[psr.factory.DataObject]:
    plant_list = study.find("RenewablePlant.*")
    plant_list = [plant for plant in plant_list if plant.get("TechnologyType") == tech_type]
    return _tsl_filter_plants_with_coordinates(plant_list)

def _tsl_get_csp_plants_with_coordinates(study: psr.factory.Study) -> List[psr.factory.DataObject]:
    plant_list = study.find("CSP.*")
    return _tsl_filter_plants_with_coordinates(plant_list)

def _tsl_create_csol_dat_file(case_path: Union[str, pathlib.Path], plant_list: List[psr.factory.DataObject]):
    csol_dat_path = os.path.join(case_path, "csol.dat")
    with open(csol_dat_path, 'w') as csol_dat_file:
        csol_dat_file.write("ID,CODE,NAME,SYS,CLUSTER_ID,CLUSTER,POT_INST,LON,LAT,TRACKING,TILT,AZIMUTH,CFOBS_ID,PROFILE_TYPE,AC_DC_RATIO,SYSTEM_LOSSES,USE_AZIMUTH\n")
        for plant in plant_list:
            unique_id = "peteca"
            capacity_profile = plant.get("RefCapacityProfile")
            cluster_id = ""  # FIXME
            cluster = ""  # FIXME
            cfobs_id = "" if capacity_profile is None else capacity_profile.name
            profile_type = "" if capacity_profile is None else capacity_profile.get("Type")
            values = [
                unique_id,
                plant.code,
                plant.name,
                plant.get("RefSystem").id,
                cluster_id,
                cluster,
                plant.get("InstalledCapacity"),
                plant.get("Longitude"),
                plant.get("Latitude"),
                plant.get("Tracking"),
                plant.get("Tilt"),
                plant.get("Azimuth"),
                cfobs_id,
                profile_type,
                plant.get("DCACRatio"),
                plant.get("SystemLosses"),
                plant.get("UseAzimuth")
            ]
            csol_dat_file.write(",".join(map(str, values)) + "\n")

def _tsl_create_ceol_dat_file(case_path: Union[str, pathlib.Path], plant_list: List[psr.factory.DataObject]):
    ceol_dat_file = os.path.join(case_path, "ceol.dat")
    with (open(ceol_dat_file, 'w') as ceol_dat):
        ceol_dat.write("ID,PLANT_CODE,PLANT_NAME,PLANT_SYS,STATION_CODE,STATION_NAME,PLANT_POT_INST,LON,LAT,PROFILE_CODE,PLANT_HEIGHT,PLANT_TURBINE_MODEL,PROFILE_TYPE,DOWNS_FLAG,DENS_FLAG,DENS_SITE_HEIGHT\n")
        for plant in plant_list:
            unique_id = "peteca"
            system = plant.get("RefSystem")
            turbine = plant.get("RefTurbine")
            station = plant.get("RefStation")
            capacity_profile = plant.get("RefCapacityProfile")

            turbine_model = "" if turbine is None else turbine.name
            profile_code = "" if capacity_profile is None else capacity_profile.name
            profile_type = "" if capacity_profile is None else capacity_profile.get("Type")
            values = [
                unique_id,
                plant.code,
                plant.name,
                system.id,
                station.code,
                station.name,
                plant.get("InstalledCapacity"),
                plant.get("Longitude"),
                plant.get("Latitude"),
                plant.get("Tracking"),
                plant.get("Tilt"),
                plant.get("Azimuth"),
                profile_code,
                plant.get("Height"),
                turbine_model,
                profile_type,
                plant.get("DownscalingFlag"),
                plant.get("DensityCorrectionFlag"),
                plant.get("DensityCorrection"),
            ]
            ceol_dat.write(",".join(map(str, values)) + "\n")

def _tsl_create_ccsp_dat_file(case_path: Union[str, pathlib.Path], plant_list: List[psr.factory.DataObject]):
    ccsp_dat_file = os.path.join(case_path, "ccsp.dat")
    with (open(ccsp_dat_file, 'w') as ccsp_dat):
        ccsp_dat.write("ID,CODE,NAME,SYS,CLUSTER_ID,CLUSTER,POT_INST,LON,LAT,SM,EFF,CFOBS_ID,PROFILE_TYPE\n")
        for plant in plant_list:
            unique_id = "peteca"
            cluster_id = "" # FIXME
            cluster = "" # FIXME
            capacity_profile = plant.get("RefCapacityProfile")
            cfobs_id = "" if capacity_profile is None else capacity_profile.name
            profile_type = "" if capacity_profile is None else capacity_profile.get("Type")
            values = [
                unique_id,
                plant.code,
                plant.name,
                plant.get("RefSystem").id,
                cluster_id,
                cluster,
                plant.get("InstalledCapacity"),
                plant.get("Longitude"),
                plant.get("Latitude"),
                plant.get("SM"),
                plant.get("Efficiency"),
                cfobs_id,
                profile_type,
            ]
            ccsp_dat.write(",".join(map(str, values)) + "\n")


def run_rpsdata(tsl_path: Union[str, pathlib.Path], case_path: Union[str, pathlib.Path], file_name: str, base_type: str, **kwargs):
    rps_parentpath = os.path.join(str(tsl_path), "Extensions","Script")
    file_path = os.path.join(str(case_path), file_name)
    with change_cwd(rps_parentpath):
        cmd = f'RPSDataConsole.exe GET_POINTS "{file_path}" "{case_path}" {base_type}'
        exec_cmd(cmd, **kwargs)

def run_tsldata(tsl_path: Union[str, pathlib.Path], case_path: Union[str, pathlib.Path], db_type: str, **kwargs):
    tsldata_parentpath = os.path.join(str(tsl_path), "Extensions","tsldata-distribution")
    with change_cwd(tsldata_parentpath):
        cmd = f'TSLData.exe --path "{str(case_path)}" --{db_type}'
        exec_cmd(cmd, **kwargs)

def run_tslconsole(tsl_path: Union[str, pathlib.Path], script_path: Union[str, pathlib.Path], **kwargs):
    tsl_console = os.path.join(tsl_path, "Extensions", "TimeSeriesLab")
    with change_cwd(tsl_console):
        cmd = f'TimeSeriesConsole.exe "{str(script_path)}"'
        exec_cmd(cmd, **kwargs)

def run_tsl(case_path: Union[str, pathlib.Path], tsl_path: Union[str, pathlib.Path], base_type: str, **kwargs):
    if os.name != 'nt':
        raise NotImplementedError("Running TimeSeriesLab is only available on Windows")
    case_path = os.path.abspath(str(case_path))
    tsl_path = str(tsl_path)
    dry_run = kwargs.get("dry_run", False)
    show_progress = kwargs.get("show_progress", False)

    def _run_rpsdata(file_name):
        run_rpsdata(tsl_path, case_path, file_name, base_type, **kwargs)

    def _run_tsldata(db_type):
        run_tsldata(tsl_path, case_path, db_type, **kwargs)

    def _run_tslconsole(commands: List[str]):
        _run_tslconsole_command(tsl_path, case_path, commands, **kwargs)

    study = psr.factory.load_study(case_path, ["TSL"])

    wind_list = _tsl_get_renewable_plants_with_coordinates(study, 1)
    if len(wind_list) > 0:
        _tsl_create_ceol_dat_file(case_path, wind_list)
        _run_rpsdata("ceol.dat")
        _run_tsldata("wind")

    solar_list = _tsl_get_renewable_plants_with_coordinates(study, 2)
    if len(solar_list) > 0:
        _tsl_create_csol_dat_file(case_path, solar_list)
        _run_rpsdata("csol.dat")
        _run_tsldata("solar")

    csp_list = _tsl_get_csp_plants_with_coordinates(study)
    if len(csp_list) > 0:
        _tsl_create_ccsp_dat_file(case_path, csp_list)
        _run_rpsdata("ccsp.dat")
        _run_tsldata("csp")

    if len(solar_list) > 0 or len(csp_list) > 0:
        _run_tsldata("solar-correction")

    # todo: create cdlr.dat
    _run_rpsdata("cdlr.dat")
    _run_tsldata("dlr")

    _run_tsldata("merge")

    #todo: generate default script for parameters
    _run_tslconsole([])

    #todo: generate default script for scenarios
    _run_tslconsole([])


def _run_tslconsole_command(tsl_path: Union[str, pathlib.Path], case_path: Union[str, pathlib.Path], commands: list[str], script_prefix: str = "", **kwargs):
    tsl_console_path = os.path.join(tsl_path, "Extensions", "TimeSeriesLab")
    delete_xml = not _DEBUG
    full_path = os.path.join(os.path.abspath(case_path), "")
    with psr.psrfcommon.tempfile.CreateTempFile(
            "./", script_prefix, "", ".dat", delete_xml
    ) as script_file, change_cwd(tsl_console_path):
        with open(script_file.name, "w") as script_file:
            script_file.write(f"SET,PATHDATA,{full_path}\n")
            for command in commands:
                script_file.write(f"RUN,{command}\n")
        run_tslconsole(tsl_path, os.path.abspath(script_file.name), **kwargs)


def run_tsl_generate_external_scenarios(case_path: Union[str, pathlib.Path], tsl_path: Union[str, pathlib.Path], option: str, **kwargs):
    inflow_path = os.path.join(str(case_path), "inflow.dat")
    option_command_map = {
        "natural": "generate_inflow_from_external_natural",
        "incremental": "generate_inflow_from_external_incremental",
    }
    if option not in option_command_map.keys():
        raise ValueError(f"Invalid option. Should be one of {','.join(option_command_map.keys())}")

    commands = [option_command_map[option]]
    _run_tslconsole_command(tsl_path, case_path, commands)
