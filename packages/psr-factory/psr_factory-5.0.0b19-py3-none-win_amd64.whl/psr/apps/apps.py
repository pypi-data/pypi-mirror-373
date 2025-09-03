# PSR Factory. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import glob
import os
import pathlib
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

if os.name == "nt":
    import winreg


from psr.runner import (
    run_sddp,
    run_sddp_check,
    run_hydro_estimation,
    run_sddp_cleanup,
    get_sddp_version,
    run_optgen,
    run_optgen_check,
    run_optgen_cleanup,
    run_ncp,
    run_graph,
    run_psrcloud,
    run_tsl,
)


class ModelNotFound(Exception):
    pass


def _get_versions_from_base_path(base_path: Union[str, pathlib.Path], program_name: str) -> Dict[str, str]:
    program_path = os.path.join(base_path, program_name)
    if not os.path.exists(program_path):
        return dict()
    versions = dict()
    for entry in os.scandir(program_path):
        if entry.is_dir():
            versions[entry.name] = entry.path
    return versions

def get_program_versions_paths(program_name: str) -> Dict[str, str]:
    if os.name == "nt":
        return _get_registry_versions(program_name)
    else:
        return _get_versions_from_base_path("/opt/psr/", program_name)


def get_latest_version_and_path(program_name: str) -> Tuple[str, str]:
    versions = get_program_versions_paths(program_name)
    if not versions:
        raise ModelNotFound(f"Model {program_name} not found")
    # sort keys
    versions_keys = dict(sorted(versions.items()))
    latest = list(versions_keys.keys())[-1]
    return latest, versions[latest]


def get_latest_version(program_name: str) -> "AppRunner":
    program_name_lower = program_name.lower()
    version, path = get_latest_version_and_path(program_name)
    if program_name_lower == "sddp":
        return SDDP(path)

    if program_name_lower == "optgen":
        _, sddp_path = get_latest_version_and_path("sddp")
        return OptGen(path, sddp_path, version)

    if program_name_lower == "ncp":
        return NCP(path, version)

    if program_name_lower == "graph":
        return Graph(path, version)

    if program_name_lower == "psrcloud":
        return PSRCloud(path, version)

    if program_name_lower == "tsl" or program_name_lower == "timeserieslab":
        return TSL(path, version)

    raise ModelNotFound(f"Model {program_name} not found")


class AppRunner:
    def __init__(self):
        pass
    def run(self, case_path: str, **kwargs):
        pass
    def version(self) -> str:
        pass
    def install_path(self) -> str:
        pass


class SDDP(AppRunner):
    def __init__(self, sddp_path: str):
        super().__init__()
        self._sddp_path = sddp_path

    def run(self, case_path: str, **kwargs):
        run_sddp(case_path, self._sddp_path, **kwargs)

    def run_check(self, case_path: str, **kwargs):
        run_sddp_check(case_path, self._sddp_path, **kwargs)

    def run_cleanup(self, case_path: str, **kwargs):
        run_sddp_cleanup(case_path, self._sddp_path, **kwargs)

    def run_hydro_estimation(self, case_path: str, **kwargs):
        run_hydro_estimation(case_path, self._sddp_path, **kwargs)

    def version(self) -> str:
        return get_sddp_version(self._sddp_path)

    def install_path(self) -> str:
        return self._sddp_path


class OptGen(AppRunner):
    def __init__(self, optgen_path: str, sddp_path: str, version: str):
        super().__init__()
        self._optgen_path = optgen_path
        self._sddp_path = sddp_path
        self._version = version

    def run(self, case_path: str, **kwargs):
        run_optgen(case_path, self._optgen_path, self._sddp_path, **kwargs)

    def run_check(self, case_path: str, **kwargs):
        run_optgen_check(case_path, self._optgen_path, self._sddp_path, **kwargs)

    def run_cleanup(self, case_path: str, **kwargs):
        run_optgen_cleanup(case_path, self._optgen_path, self._sddp_path, **kwargs)

    def version(self) -> str:
        return self._version


class NCP(AppRunner):
    def __init__(self, ncp_path: str, version: str):
        super().__init__()
        self._ncp_path = ncp_path
        self._version = version

    def run(self, case_path: str, **kwargs):
        run_ncp(case_path, self._ncp_path, **kwargs)

    def version(self) -> str:
        return self._version

class Graph(AppRunner):
    def __init__(self, graph_path: str, version: str):
        super().__init__()
        self._graph_path = graph_path
        self._version = version

    def run(self, case_path: str, **kwargs):
        run_graph(case_path, self._graph_path, **kwargs)

    def version(self) -> str:
        return self._version

class TSL(AppRunner):
    def __init__(self, tsl_path: str, version: str):
        super().__init__()
        self._tsl_path = tsl_path
        self._version = version

    def run(self, **kwargs):
        run_tsl(self._tsl_path, **kwargs)

    def version(self) -> str:
        return self._version


class PSRCloud(AppRunner):
    def __init__(self, psrcloud_path: str, version: str):
        super().__init__()
        self._psrcloud_path = psrcloud_path
        self._version = version

    def run(self, **kwargs):
        run_psrcloud(self._psrcloud_path, **kwargs)

    def version(self) -> str:
        return self._version



if os.name == "nt":
    def _get_registry_versions(program_name: str) -> Dict[str, str]:
        base_key = winreg.HKEY_LOCAL_MACHINE
        subkey_path = rf"SOFTWARE\PSR\{program_name}"
        version_paths: Dict[str, str] = dict()
        try:
            with winreg.OpenKey(base_key, subkey_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_full_path = f"{subkey_path}\\{subkey_name}"

                        with winreg.OpenKey(base_key, subkey_full_path) as subkey:
                            try:
                                path_value, _ = winreg.QueryValueEx(subkey, "Path")
                                # if subkey ends with .x, replace with blank
                                subkey_name = subkey_name.replace(".x", "")
                                version_paths[subkey_name] = path_value
                            except FileNotFoundError:
                                pass
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass
        return version_paths

