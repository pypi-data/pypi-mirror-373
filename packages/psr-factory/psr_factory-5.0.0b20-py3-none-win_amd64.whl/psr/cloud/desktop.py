# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

from .data import Case
from .xml import create_desktop_xml


def import_case(case: Case, console_cluster: str, instance_type_id: int) -> None:
    case_counter = _get_last_case_id()
    filepath = os.path.expandvars(
        os.path.join(r"%appdata%\PSR\PSRCloud\Dados", f"Caso{case_counter}.xml")
    )
    now = datetime.now()
    case_datetime = now.strftime("%d/%m/%Y %H:%M")
    case_date = now.strftime("%d/%m/%Y")
    case_lifetime = ""
    case_budget = "" if case.budget is None else case.budget
    repositorio_template = (
        case.parent_case_id
        if case.parent_case_id is not None and case.parent_case_id != 0
        else ""
    )

    parameters = {
        "Id": str(case_counter),
        "IdRepositorio": str(case.id),
        "IdFila": str(case.id),
        "Modelo": case.program.upper(),
        "RepositorioTemplate": repositorio_template,
        "DirDados": case.data_path,
        "TipoExecucao": str(case.execution_type),
        "InstanciaTipo": str(instance_type_id),
        "Cluster": console_cluster,
        "ClusterSrv": console_cluster,
        "DtX": case_datetime,
        "NProc": str(case.number_of_processes),
        "Versao": str(case.program_version),
        "Status": "2",
        "StatusX": "Executando",
        "Budget": case_budget,
        "PodeListarFila": "True",
        "IdX": case.name,
        "Nom": case.name,
        "Tag": f"PyCloud\\{case_date.replace('/', '-')}",
        "DuracaoRepositorio": case_lifetime,
        "FlagMaqNormalS": "False",
    }

    with open(filepath, "w", encoding="utf-8") as f:
        xml_contents = create_desktop_xml(parameters)
        f.write(xml_contents)


def _get_last_case_id() -> Optional[int]:
    config_path = os.path.expandvars(r"%appdata%\PSR\PSRCloud\ePSRConfig.xml")
    data_path = os.path.expandvars(r"%appdata%\PSR\PSRCloud\Dados")

    if os.path.isfile(config_path):
        xml = ET.parse(config_path, parser=ET.XMLParser(encoding="utf-16"))
        root = xml.getroot()
        last_case_id = None
        for child in root.iter("Aplicacao"):
            last_case_id = int(child.get("idUltimoCaso"))
            break
        if last_case_id is not None:
            # Check for existing files with the same
            # last_case_id. Increment it if necessary.
            last_case_id = int(last_case_id)
            files = os.listdir(data_path)
            while f"Caso{last_case_id}.xml" in files:
                last_case_id += 1
            return last_case_id
        # No case has been run yet
        return None
    else:
        raise Exception("ERROR: PSR Cloud Desktop is not installed.")
