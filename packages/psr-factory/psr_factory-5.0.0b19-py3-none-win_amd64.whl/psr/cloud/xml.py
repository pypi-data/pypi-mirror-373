# PSR Cloud. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from typing import Any, Dict
from xml.etree import ElementTree as ET


def create_case_xml(parameters: Dict[str, Any]) -> str:
    root = ET.Element("ColecaoParametro")
    for name, value in parameters.items():
        if value is None:
            continue
        value = _handle_invalid_xml_chars(value)
        parameter = ET.SubElement(root, "Parametro", nome=name, tipo="System.String")
        parameter.text = value
    ET.indent(root, "  ")
    return ET.tostring(root, encoding="unicode", method="xml")


def create_desktop_xml(parameters: Dict[str, Any]) -> str:
    # use element tree to write the file contents instead
    node = ET.Element("Repositorio")
    case_node = ET.SubElement(node, "CasoOperacao")
    for key, value in parameters.items():
        value_escaped = _handle_invalid_xml_chars(value)
        case_node.set(key, value_escaped)
    tree = ET.ElementTree(node)
    return ET.tostring(
        tree.getroot(), encoding="unicode", method="xml", xml_declaration=False
    )


def _return_invalid_xml_chars(xml_content: str) -> str:
    special_chars = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&apos;": "'",
    }
    for char, replacement in special_chars.items():
        xml_content = xml_content.replace(char, replacement)
    return xml_content


def _handle_invalid_xml_chars(xml_content: str) -> str:
    special_chars = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&apos;",
    }
    for char, replacement in special_chars.items():
        xml_content = str(xml_content).replace(char, replacement)
    return xml_content
