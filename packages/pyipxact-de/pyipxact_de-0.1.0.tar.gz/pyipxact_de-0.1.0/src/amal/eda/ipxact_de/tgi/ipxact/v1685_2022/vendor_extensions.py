"""Vendor extensions category TGI functions (IEEE 1685-2022).

Implements the public TGI functions for Vendor Extensions:
* BASE (F.7.85) – traversal and retrieval of vendor extension elements.
* EXTENDED (F.7.86) – addition and removal of vendor extension fragments.

The IP-XACT schema models vendor extensions as a container element (usually
named ``vendorExtensions``) holding an arbitrary sequence of XML extension
elements (wildcards). In generated bindings this frequently appears as a
structure with an ``any`` or similarly named list of generic objects (often
``lxml.etree._Element`` or simple namespace objects).

Design choices:
* BASE getters are tolerant: invalid IDs yield neutral values (``None`` or
    empty lists) rather than raising faults.
* EXTENDED mutators raise :class:`TgiError` with
    ``TgiFaultCode.INVALID_ID`` for unknown handles and
    ``TgiFaultCode.INVALID_ARGUMENT`` for malformed XML fragments.
* Added fragments are stored as lightweight objects. If an lxml parser is
    available the fragment is parsed and the element stored; otherwise a
    fallback simple object capturing tag/text/attributes is produced.
"""
from types import SimpleNamespace  # ruff: noqa: I001
from xml.etree import ElementTree as ET  # ruff: noqa: I001
from typing import Any  # ruff: noqa: I001

from .core import (
    TgiError,
    TgiFaultCode,
    resolve_handle,
    get_handle,
    register_parent,
)

__all__: list[str] = [
        # BASE (F.7.85)
        "getVendorExtensionsIDs",
        "getVendorExtensionElementNames",
        "getVendorExtensionElementsRaw",
        "getVendorExtensionElementText",
        "getVendorExtensionElementAttributeNames",
        "getVendorExtensionElementAttributeValue",
        # EXTENDED (F.7.86)
        "addVendorExtensions",
        "removeVendorExtensionsElement",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve(parentID: str) -> Any | None:
    obj = resolve_handle(parentID)
    return obj


def _vendor_extensions_container(obj: Any) -> Any:
    # Many top-level objects have vendor_extensions attribute; container inside may
    # be vendor_extensions.any or vendor_extensions.vendor_extension etc.
    ve = getattr(obj, "vendor_extensions", None)
    return ve


def _iter_extensions(container: Any) -> list[Any]:
    if container is None:
        return []
    # Try common attribute names in preference order
    candidates = [
        "any",  # lxml / wildcard list
        "vendor_extension",  # hypothetical list name
        "items",  # generic
    ]
    for name in candidates:
        seq = getattr(container, name, None)
        if isinstance(seq, list):
            return seq
    # If container itself is list-like
    if isinstance(container, list):
        return container
    try:  # pragma: no cover
        return list(container)
    except Exception:  # pragma: no cover
        return []


def _ext_elems(parentID: str) -> list[Any]:
    parent = _resolve(parentID)
    if parent is None:
        return []
    container = _vendor_extensions_container(parent)
    return _iter_extensions(container)


# ---------------------------------------------------------------------------
# BASE (F.7.85)
# ---------------------------------------------------------------------------

def getVendorExtensionsIDs(parentID: str) -> list[str]:  # F.7.85.1
    elems = _ext_elems(parentID)
    return [get_handle(e) for e in elems]


def getVendorExtensionElementNames(parentID: str) -> list[str]:  # F.7.85.2
    names: list[str] = []
    for elem in _ext_elems(parentID):
        tag = getattr(elem, "tag", None)
        if isinstance(tag, str):
            local = tag.split("}")[-1] if "}" in tag else tag
            names.append(local)
    return names


def getVendorExtensionElementsRaw(parentID: str) -> list[Any]:  # F.7.85.3
    return list(_ext_elems(parentID))


def getVendorExtensionElementText(parentID: str, elementName: str) -> list[str]:  # F.7.85.4
    texts: list[str] = []
    for elem in _ext_elems(parentID):
        tag = getattr(elem, "tag", None)
        if isinstance(tag, str):
            local = tag.split("}")[-1] if "}" in tag else tag
            if local == elementName:
                text_val = getattr(elem, "text", None)
                if isinstance(text_val, str):
                    texts.append(text_val)
    return texts


def getVendorExtensionElementAttributeNames(parentID: str, elementName: str) -> list[str]:  # F.7.85.5
    names: list[str] = []
    for elem in _ext_elems(parentID):
        tag = getattr(elem, "tag", None)
        if isinstance(tag, str):
            local = tag.split("}")[-1] if "}" in tag else tag
            if local == elementName:
                attrib = getattr(elem, "attrib", None) or getattr(elem, "attributes", None)
                if isinstance(attrib, dict):
                    names.extend(attrib.keys())
    return names


def getVendorExtensionElementAttributeValue(
    parentID: str,
    elementName: str,
    attributeName: str,
) -> list[str]:  # F.7.85.6
    values: list[str] = []
    for elem in _ext_elems(parentID):
        tag = getattr(elem, "tag", None)
        if isinstance(tag, str):
            local = tag.split("}")[-1] if "}" in tag else tag
            if local == elementName:
                attrib = getattr(elem, "attrib", None) or getattr(elem, "attributes", None)
                if isinstance(attrib, dict) and attributeName in attrib:
                    val = attrib[attributeName]
                    if isinstance(val, str):
                        values.append(val)
    return values


# ---------------------------------------------------------------------------
# EXTENDED (F.7.86)
# ---------------------------------------------------------------------------

def _parse_fragment(xmlFragment: str) -> Any:
    try:
        elem = ET.fromstring(xmlFragment)
        return elem
    except Exception as exc:  # pragma: no cover
        raise TgiError(f"Malformed vendor extension XML: {exc}", TgiFaultCode.INVALID_ARGUMENT) from exc


def addVendorExtensions(
    vendorExtensionsContainerElementID: str, vendorExtensions: str
) -> bool:  # F.7.86.1 (bulk add by XML fragment string)
    parent = resolve_handle(vendorExtensionsContainerElementID)
    if parent is None:
        raise TgiError("Invalid ID", TgiFaultCode.INVALID_ID)
    container = _vendor_extensions_container(parent)
    if container is None:
        # create a container placeholder with an 'any' list
        container = SimpleNamespace(any=[])
        parent.vendor_extensions = container  # type: ignore[attr-defined]
    seq = None
    for attr in ("any", "vendor_extension", "items"):
        val = getattr(container, attr, None)
        if isinstance(val, list):
            seq = val
            break
    if seq is None:  # create default list under 'any'
        container.any = []  # type: ignore[attr-defined]
        seq = container.any  # type: ignore[attr-defined]
    # Parse input which might contain multiple top-level siblings => wrap
    xml_text = vendorExtensions.strip()
    if not xml_text:
        return True
    # Simple heuristic: if multiple top-level, wrap in root.
    if xml_text.count("<") > 1 and xml_text.lstrip().startswith("<") and xml_text.rstrip().endswith(">"):
        if xml_text.count("<") - xml_text.count("</") > 1 and not xml_text.startswith("<root>"):
            xml_text_wrapped = f"<root>{xml_text}</root>"
            try:
                root = ET.fromstring(xml_text_wrapped)
                elements = list(root)
            except Exception:
                elements = [ _parse_fragment(xml_text) ]
        else:
            elements = [ _parse_fragment(xml_text) ]
    else:
        elements = [ _parse_fragment(xml_text) ]
    for e in elements:
        seq.append(e)
        register_parent(e, parent, ("vendor_extensions",), "list")
    return True


def removeVendorExtensionsElement(extensionID: str) -> bool:  # F.7.86.2
    elem = resolve_handle(extensionID)
    if elem is None:
        raise TgiError("Invalid ID", TgiFaultCode.INVALID_ID)
    # Parent linkage maintained via register_parent; remove from its list
    # We cannot rely on generic detach helper (not imported) -> manual search
    # Attempt typical structure
    parent = getattr(elem, "__tgi_parent__", None)
    if parent is None:
        return True
    container = getattr(parent, "vendor_extensions", None)
    if container is None:
        return True
    for attr in ("any", "vendor_extension", "items"):
        seq = getattr(container, attr, None)
        if isinstance(seq, list) and elem in seq:
            seq.remove(elem)
            break
    return True


## End of file

