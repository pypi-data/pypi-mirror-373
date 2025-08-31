"""File set category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.47) and EXTENDED (F.7.48) *File set* functions.
Only the exact public API defined by Annex F is exported.  These functions
cover traversal of fileSets, files, default file builders, functions (SW
functions inside a fileSet), and their subordinate argument / sourceFile
elements; plus mutation helpers for the EXTENDED section.

Design notes:
* Absent optional children return ``None`` (or empty list) – invalid handles
  raise ``TgiError`` with ``INVALID_ID``.
* Newly created child objects are registered with their parent via
  ``register_parent`` allowing later detach via remove* functions.
* The 2022 schema expresses many list-valued fields as ``Iterable`` but
  uses ``list`` factories; we treat them as mutable lists (adding a
  ``# type: ignore`` where static checkers complain).
* Some spec functions reference *fileSetRef* / *fileSetRefGroup* elements
  that are not present in the 2022 FileSet schema. They are stubbed to
  return empty results (BASE) or raise ``INVALID_ARGUMENT`` (EXTENDED) so
  callers can detect unsupported constructs. This is documented in each
  affected docstring.
"""

from collections.abc import Iterable
from typing import Any

from org.accellera.ipxact.v1685_2022 import (
    Dependency,
    File,
    FileBuilderType,
    FileSet,
    FileType,
    IpxactUri,
    NameValuePairType,
)
from org.accellera.ipxact.v1685_2022.file_set_type import FileSetType
from org.accellera.ipxact.v1685_2022.return_type_type import ReturnTypeType
from org.accellera.ipxact.v1685_2022.simple_file_type import SimpleFileType
from org.accellera.ipxact.v1685_2022.unsigned_bit_expression import UnsignedBitExpression

from .core import (
    TgiError,
    TgiFaultCode,
    get_handle,
    resolve_handle,
    register_parent,
    detach_child_by_handle,
)

__all__ = [
    # BASE (F.7.47.x)
    "getBuildCommandReplaceDefaultFlagsExpression",
    "getFileDefineIDs",
    "getFileDefineSymbolValue",
    "getFileDependencyIDs",
    "getFileExportedNameIDs",
    "getFileExportedNames",
    "getFileFileTypeIDs",
    "getFileFileTypes",
    "getFileImageTypeIDs",
    "getFileImageTypes",
    "getFileIsIncludeFile",
    "getFileIsIncludeFileID",
    "getFileIsStructural",
    "getFileLogicalName",
    "getFileLogicalNameID",
    "getFileName",
    "getFileSetDefaultFileBuilderIDs",
    "getFileSetDependencyIDs",
    "getFileSetFileIDs",
    "getFileSetFunctionIDs",
    "getFileSetGroupFileSetRefIDs",
    "getFileSetGroupIDs",
    "getFileSetGroups",
    "getFileSetRefByID",
    "getFileSetRefGroupFileSetRefIDs",
    "getFileSetRefLocalNameRefByID",
    "getFunctionArgumentDataType",
    "getFunctionArgumentIDs",
    "getFunctionDisabled",
    "getFunctionDisabledExpression",
    "getFunctionDisabledID",
    "getFunctionEntryPoint",
    "getFunctionFileID",
    "getFunctionFileRefByID",
    "getFunctionFileRefByName",
    "getFunctionReplicate",
    "getFunctionReturnType",
    "getFunctionSourceFileIDs",
    "getFunctionSourceFileName",
    "getFunctionSourceFileType",
    "getSourceFileFileType",
    "getSourceFileFileTypeID",
    "getSourceFileSourceName",
    # EXTENDED (F.7.48.x)
    "addFileDefine",
    "addFileDependency",
    "addFileExportedName",
    "addFileFileType",
    "addFileImageType",
    "addFileSetDefaultFileBuilder",
    "addFileSetDependency",
    "addFileSetFile",
    "addFileSetFunction",
    "addFileSetGroup",
    "addFileSetRefGroupFileSetRef",
    "addFunctionArgument",
    "addFunctionSourceFile",
    "removeFileBuildCommand",
    "removeFileDefine",
    "removeFileDependency",
    "removeFileExportedName",
    "removeFileFileType",
    "removeFileImageType",
    "removeFileIsIncludeFile",
    "removeFileIsStructural",
    "removeFileLogicalName",
    "removeFileSetDefaultFileBuilder",
    "removeFileSetDependency",
    "removeFileSetFile",
    "removeFileSetFunction",
    "removeFileSetGroup",
    "removeFunctionArgument",
    "removeFunctionDisabled",
    "removeFunctionEntryPoint",
    "removeFunctionReturnType",
    "removeFunctionSourceFile",
    "setFileIsIncludeFile",
    "setFileIsStructural",
    "setFileLogicalName",
    "setFileName",
    "setFunctionArgumentDataType",
    "setFunctionDisabled",
    "setFunctionEntryPoint",
    "setFunctionFileRef",
    "setFunctionReplicate",
    "setFunctionReturnType",
    "setFunctionSourceFileName",
    "setSourceFileFileType",
    "setSourceFileSourceName",
]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_fileset(fileSetID: str) -> FileSet:
    fs = resolve_handle(fileSetID)
    if not isinstance(fs, FileSet):
        raise TgiError("Invalid fileSet handle", TgiFaultCode.INVALID_ID)
    return fs


def _resolve_file(fileID: str) -> File:
    f = resolve_handle(fileID)
    if not isinstance(f, File):
        raise TgiError("Invalid file handle", TgiFaultCode.INVALID_ID)
    return f


def _resolve_function(functionID: str) -> FileSetType.Function:
    fn = resolve_handle(functionID)
    if not isinstance(fn, FileSetType.Function):
        raise TgiError("Invalid function handle", TgiFaultCode.INVALID_ID)
    return fn


def _resolve_argument(argumentID: str) -> FileSetType.Function.Argument:
    arg = resolve_handle(argumentID)
    if not isinstance(arg, FileSetType.Function.Argument):
        raise TgiError("Invalid argument handle", TgiFaultCode.INVALID_ID)
    return arg


def _resolve_source_file(sourceFileID: str) -> FileSetType.Function.SourceFile:
    sf = resolve_handle(sourceFileID)
    if not isinstance(sf, FileSetType.Function.SourceFile):
        raise TgiError("Invalid sourceFile handle", TgiFaultCode.INVALID_ID)
    return sf


def _resolve_define(defineID: str) -> NameValuePairType:
    dv = resolve_handle(defineID)
    if not isinstance(dv, NameValuePairType):
        raise TgiError("Invalid fileDefine handle", TgiFaultCode.INVALID_ID)
    return dv


def _resolve_dependency(dependencyID: str) -> Dependency:
    dep = resolve_handle(dependencyID)
    if not isinstance(dep, Dependency):
        raise TgiError("Invalid dependency handle", TgiFaultCode.INVALID_ID)
    return dep


def _ids(items: Iterable[Any]) -> list[str]:
    return [get_handle(x) for x in items]


def _enum_file_type(value: str) -> FileType:
    try:
        simple = SimpleFileType(value)
    except ValueError as exc:  # invalid enum literal
        raise TgiError("Unknown FileType", TgiFaultCode.INVALID_ARGUMENT) from exc
    return FileType(value=simple)


# ---------------------------------------------------------------------------
# BASE (F.7.47)
# ---------------------------------------------------------------------------

def getBuildCommandReplaceDefaultFlagsExpression(fileID: str) -> str | None:  # F.7.47.1
    """Return replaceDefaultFlags expression (Section: F.7.47.1)."""
    f = _resolve_file(fileID)
    bc = f.build_command
    if bc is None or bc.replace_default_flags is None:
        return None
    return getattr(bc.replace_default_flags, "value", None)


def getFileDefineIDs(fileID: str) -> list[str]:  # F.7.47.2
    """Return handles of define symbols (Section: F.7.47.2)."""
    return _ids(_resolve_file(fileID).define)  # type: ignore[arg-type]


def getFileDefineSymbolValue(fileDefineID: str) -> str | None:  # F.7.47.3
    """Return value of a fileDefine (Section: F.7.47.3)."""
    d = _resolve_define(fileDefineID)
    return getattr(d, "value", None)


def getFileDependencyIDs(fileID: str) -> list[str]:  # F.7.47.4
    """Return dependency handles for a file (Section: F.7.47.4)."""
    return _ids(_resolve_file(fileID).dependency)  # type: ignore[arg-type]


def getFileExportedNameIDs(fileID: str) -> list[str]:  # F.7.47.5
    """Return exportedName handles (Section: F.7.47.5)."""
    return _ids(_resolve_file(fileID).exported_name)  # type: ignore[arg-type]


def getFileExportedNames(fileID: str) -> list[str]:  # F.7.47.6
    """Return exported names (Section: F.7.47.6)."""
    return [getattr(en, "value", "") for en in _resolve_file(fileID).exported_name]


def getFileFileTypeIDs(fileID: str) -> list[str]:  # F.7.47.7
    """Return fileType handles (Section: F.7.47.7)."""
    return _ids(_resolve_file(fileID).file_type)  # type: ignore[arg-type]


def getFileFileTypes(fileID: str) -> list[str]:  # F.7.47.8
    """Return fileType enumeration literals (Section: F.7.47.8)."""
    names: list[str] = []
    for ft in _resolve_file(fileID).file_type:
        val = getattr(ft, "value", None)
        if val is None:
            continue
        lit = getattr(val, "value", None)
        names.append(lit if lit is not None else str(val))
    return names


def getFileImageTypeIDs(fileID: str) -> list[str]:  # F.7.47.9
    """Return imageType handles (Section: F.7.47.9)."""
    return _ids(_resolve_file(fileID).image_type)  # type: ignore[arg-type]


def getFileImageTypes(fileID: str) -> list[str]:  # F.7.47.10
    """Return image type values (Section: F.7.47.10)."""
    return [getattr(it, "value", "") for it in _resolve_file(fileID).image_type]


def getFileIsIncludeFile(fileID: str) -> bool:  # F.7.47.11
    """Return isIncludeFile boolean (Section: F.7.47.11)."""
    inc = _resolve_file(fileID).is_include_file
    return bool(getattr(inc, "value", False)) if inc is not None else False


def getFileIsIncludeFileID(fileID: str) -> str | None:  # F.7.47.12
    """Return handle to isIncludeFile element (Section: F.7.47.12)."""
    f = _resolve_file(fileID)
    return get_handle(f.is_include_file) if f.is_include_file is not None else None


def getFileIsStructural(fileID: str) -> bool:  # F.7.47.13
    """Return isStructural value (Section: F.7.47.13)."""
    return bool(_resolve_file(fileID).is_structural)


def getFileLogicalName(fileID: str) -> str | None:  # F.7.47.14
    """Return logicalName value (Section: F.7.47.14)."""
    ln = _resolve_file(fileID).logical_name
    return getattr(ln, "value", None) if ln is not None else None


def getFileLogicalNameID(fileID: str) -> str | None:  # F.7.47.15
    """Return handle to logicalName element (Section: F.7.47.15)."""
    f = _resolve_file(fileID)
    return get_handle(f.logical_name) if f.logical_name is not None else None


def getFileName(fileID: str) -> str | None:  # F.7.47.16
    """Return file name path value (Section: F.7.47.16)."""
    n = _resolve_file(fileID).name
    return getattr(n, "value", None) if n is not None else None


def getFileSetDefaultFileBuilderIDs(fileSetID: str) -> list[str]:  # F.7.47.17
    """Return handles of defaultFileBuilder elements (Section: F.7.47.17)."""
    return _ids(_resolve_fileset(fileSetID).default_file_builder)  # type: ignore[arg-type]


def getFileSetDependencyIDs(fileSetID: str) -> list[str]:  # F.7.47.18
    """Return fileSet dependency handles (Section: F.7.47.18)."""
    return _ids(_resolve_fileset(fileSetID).dependency)  # type: ignore[arg-type]


def getFileSetFileIDs(fileSetID: str) -> list[str]:  # F.7.47.19
    """Return file handles (Section: F.7.47.19)."""
    return _ids(_resolve_fileset(fileSetID).file)  # type: ignore[arg-type]


def getFileSetFunctionIDs(fileSetID: str) -> list[str]:  # F.7.47.20
    """Return function handles (Section: F.7.47.20)."""
    return _ids(_resolve_fileset(fileSetID).function)  # type: ignore[arg-type]


def getFileSetGroupFileSetRefIDs(fileSetGroupID: str) -> list[str]:  # F.7.47.21
    """Return fileSetRef handles (Section: F.7.47.21).

    Not supported by current schema – returns empty list if group exists else
    raises INVALID_ID.
    """
    grp = resolve_handle(fileSetGroupID)
    if isinstance(grp, FileSetType.Group):  # group has no refs
        return []
    raise TgiError("Invalid fileSetGroup handle", TgiFaultCode.INVALID_ID)


def getFileSetGroupIDs(fileSetID: str) -> list[str]:  # F.7.47.22
    """Return group handles (Section: F.7.47.22)."""
    return _ids(_resolve_fileset(fileSetID).group)  # type: ignore[arg-type]


def getFileSetGroups(fileSetID: str) -> list[str]:  # F.7.47.23
    """Return group string values (Section: F.7.47.23)."""
    return [getattr(g, "value", "") for g in _resolve_fileset(fileSetID).group]


def getFileSetRefByID(fileSetRefID: str) -> str | None:  # F.7.47.24
    """Return referenced fileSet handle (Section: F.7.47.24).

    Unsupported (no fileSetRef element in schema) – always returns None or
    raises INVALID_ID if handle does not refer to a placeholder type.
    """
    obj = resolve_handle(fileSetRefID)
    if obj is None:
        raise TgiError("Invalid fileSetRef handle", TgiFaultCode.INVALID_ID)
    return None


def getFileSetRefGroupFileSetRefIDs(fileSetRefGroupID: str) -> list[str]:  # F.7.47.25
    """Return fileSetRef handles (Section: F.7.47.25 – unsupported)."""
    grp = resolve_handle(fileSetRefGroupID)
    if grp is None:
        raise TgiError("Invalid fileSetRefGroup handle", TgiFaultCode.INVALID_ID)
    return []


def getFileSetRefLocalNameRefByID(fileSetRefID: str) -> str | None:  # F.7.47.26
    """Return referenced fileSet handle (Section: F.7.47.26 – unsupported)."""
    obj = resolve_handle(fileSetRefID)
    if obj is None:
        raise TgiError("Invalid fileSetRef handle", TgiFaultCode.INVALID_ID)
    return None


def getFunctionArgumentDataType(argumentID: str) -> str | None:  # F.7.47.27
    """Return argument dataType (Section: F.7.47.27)."""
    arg = _resolve_argument(argumentID)
    return getattr(arg, "data_type", None)


def getFunctionArgumentIDs(functionID: str) -> list[str]:  # F.7.47.28
    """Return function argument handles (Section: F.7.47.28)."""
    return _ids(_resolve_function(functionID).argument)  # type: ignore[arg-type]


def getFunctionDisabled(functionID: str) -> bool:  # F.7.47.29
    """Return disabled boolean (Section: F.7.47.29)."""
    fn = _resolve_function(functionID)
    dis = fn.disabled
    if dis is None:
        return False
    v = getattr(dis, "value", None)
    if v is None:
        return False
    # UnsignedBitExpression holds numeric string
    return v in ("1", 1, True)


def getFunctionDisabledExpression(functionID: str) -> str | None:  # F.7.47.30
    """Return disabled expression (Section: F.7.47.30)."""
    fn = _resolve_function(functionID)
    return getattr(fn.disabled, "value", None) if fn.disabled is not None else None


def getFunctionDisabledID(functionID: str) -> str | None:  # F.7.47.31
    """Return disabled element handle (Section: F.7.47.31)."""
    fn = _resolve_function(functionID)
    return get_handle(fn.disabled) if fn.disabled is not None else None


def getFunctionEntryPoint(functionID: str) -> str | None:  # F.7.47.32
    """Return entryPoint (Section: F.7.47.32)."""
    return getattr(_resolve_function(functionID).entry_point, "value", None)


def getFunctionFileID(functionID: str) -> str | None:  # F.7.47.33
    """Return file handle referenced by function (Section: F.7.47.33)."""
    fn = _resolve_function(functionID)
    # file_ref is stored as string (fileId) – return as-is
    return getattr(fn, "file_ref", None)


def getFunctionFileRefByID(functionID: str) -> str | None:  # F.7.47.34
    """Alias of getFunctionFileID (Section: F.7.47.34)."""
    return getFunctionFileID(functionID)


def getFunctionFileRefByName(functionID: str) -> str | None:  # F.7.47.35
    """Return fileRef name (Section: F.7.47.35).

    The schema encodes fileRef as string (the referenced fileId); no separate
    local name – we return the same value.
    """
    return getFunctionFileID(functionID)


def getFunctionReplicate(functionID: str) -> bool:  # F.7.47.36
    """Return replicate boolean (Section: F.7.47.36)."""
    return bool(_resolve_function(functionID).replicate)


def getFunctionReturnType(functionID: str) -> str | None:  # F.7.47.37
    """Return returnType literal (Section: F.7.47.37)."""
    rt = _resolve_function(functionID).return_type
    if rt is None:
        return None
    val = getattr(rt, "value", None)
    return getattr(val, "value", None) if val is not None else None


def getFunctionSourceFileIDs(functionID: str) -> list[str]:  # F.7.47.38
    """Return sourceFile handles (Section: F.7.47.38)."""
    return _ids(_resolve_function(functionID).source_file)  # type: ignore[arg-type]


def getFunctionSourceFileName(functionSourceFileID: str) -> str | None:  # F.7.47.39
    """Return sourceFile sourceName (Section: F.7.47.39)."""
    sf = _resolve_source_file(functionSourceFileID)
    sn = sf.source_name
    return getattr(sn, "value", None) if sn is not None else None


def getFunctionSourceFileType(functionSourceFileID: str) -> str | None:  # F.7.47.40
    """Return sourceFile fileType literal (Section: F.7.47.40)."""
    sf = _resolve_source_file(functionSourceFileID)
    ft = sf.file_type
    if ft is None:
        return None
    val = getattr(ft, "value", None)
    return getattr(val, "value", None) if val is not None else None


def getSourceFileFileType(sourceFileID: str) -> str | None:  # F.7.47.41
    """Return fileType value (Section: F.7.47.41)."""
    return getFunctionSourceFileType(sourceFileID)


def getSourceFileFileTypeID(sourceFileID: str) -> str | None:  # F.7.47.42
    """Return fileType element handle (Section: F.7.47.42)."""
    sf = _resolve_source_file(sourceFileID)
    return get_handle(sf.file_type) if sf.file_type is not None else None


def getSourceFileSourceName(sourceFileID: str) -> str | None:  # F.7.47.43
    """Return sourceName value (Section: F.7.47.43)."""
    return getFunctionSourceFileName(sourceFileID)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.48)
# ---------------------------------------------------------------------------

def addFileDefine(fileID: str, name: str, value: str) -> str:  # F.7.48.1
    """Add a define symbol (Section: F.7.48.1).

    The schema's NameValuePairType may expect wrapped value object; we assign
    plain string which aligns with other usage sites in the codebase.
    """
    f = _resolve_file(fileID)
    new = NameValuePairType(name=name, value=value)  # type: ignore[arg-type]
    f.define.append(new)  # type: ignore[attr-defined]
    register_parent(new, f, ("define",), "list")
    return get_handle(new)


def addFileDependency(fileID: str, dependency: str) -> str:  # F.7.48.2
    """Add a dependency string (Section: F.7.48.2)."""
    f = _resolve_file(fileID)
    dep = Dependency(value=dependency)
    f.dependency.append(dep)  # type: ignore[attr-defined]
    register_parent(dep, f, ("dependency",), "list")
    return get_handle(dep)


def addFileExportedName(fileID: str, value: str) -> str:  # F.7.48.3
    """Add exportedName (Section: F.7.48.3)."""
    from org.accellera.ipxact.v1685_2022.file import File as _File
    f = _resolve_file(fileID)
    en = _File.ExportedName(value=value)
    f.exported_name.append(en)  # type: ignore[attr-defined]
    register_parent(en, f, ("exported_name",), "list")
    return get_handle(en)


def addFileFileType(fileID: str, fileType: str) -> str:  # F.7.48.4
    """Add an additional fileType (Section: F.7.48.4)."""
    f = _resolve_file(fileID)
    ft = _enum_file_type(fileType)
    f.file_type.append(ft)  # type: ignore[attr-defined]
    register_parent(ft, f, ("file_type",), "list")
    return get_handle(ft)


def addFileImageType(fileID: str, value: str) -> str:  # F.7.48.5
    """Add imageType (Section: F.7.48.5)."""
    from org.accellera.ipxact.v1685_2022.file import File as _File
    f = _resolve_file(fileID)
    it = _File.ImageType(value=value)
    f.image_type.append(it)  # type: ignore[attr-defined]
    register_parent(it, f, ("image_type",), "list")
    return get_handle(it)


def addFileSetDefaultFileBuilder(fileSetID: str, fileType: str) -> str:  # F.7.48.6
    """Add defaultFileBuilder to fileSet (Section: F.7.48.6).

    Note: Spec text lists fileID; schema associates defaultFileBuilder with
    fileSet. We adopt fileSetID here.
    """
    fs = _resolve_fileset(fileSetID)
    ft = _enum_file_type(fileType)
    b = FileBuilderType(file_type=ft)
    fs.default_file_builder.append(b)  # type: ignore[attr-defined]
    register_parent(b, fs, ("default_file_builder",), "list")
    return get_handle(b)


def addFileSetDependency(fileSetID: str, dependency: str) -> str:  # F.7.48.7
    """Add dependency to fileSet (Section: F.7.48.7)."""
    fs = _resolve_fileset(fileSetID)
    dep = Dependency(value=dependency)
    fs.dependency.append(dep)  # type: ignore[attr-defined]
    register_parent(dep, fs, ("dependency",), "list")
    return get_handle(dep)


def addFileSetFile(fileSetID: str, name: str, fileTypes: list[str]) -> str:  # F.7.48.8
    """Add file to fileSet (Section: F.7.48.8)."""
    if not fileTypes:
        raise TgiError("fileTypes must be non-empty", TgiFaultCode.INVALID_ARGUMENT)
    fs = _resolve_fileset(fileSetID)
    ft_list = [_enum_file_type(ft) for ft in fileTypes]
    new_file = File(name=IpxactUri(value=name), file_type=ft_list)
    fs.file.append(new_file)  # type: ignore[attr-defined]
    register_parent(new_file, fs, ("file",), "list")
    return get_handle(new_file)


def addFileSetFunction(fileSetID: str, fileRef: str) -> str:  # F.7.48.9
    """Add function referencing fileRef (Section: F.7.48.9)."""
    fs = _resolve_fileset(fileSetID)
    fn = FileSetType.Function(file_ref=fileRef)
    fs.function.append(fn)  # type: ignore[attr-defined]
    register_parent(fn, fs, ("function",), "list")
    return get_handle(fn)


def addFileSetGroup(fileSetID: str, group: str) -> str:  # F.7.48.10
    """Add group value (Section: F.7.48.10)."""
    fs = _resolve_fileset(fileSetID)
    g = FileSetType.Group(value=group)
    fs.group.append(g)  # type: ignore[attr-defined]
    register_parent(g, fs, ("group",), "list")
    return get_handle(g)


def addFileSetRefGroupFileSetRef(fileSetRefGroupID: str, localName: str) -> str:  # F.7.48.11
    """Add fileSetRef (Section: F.7.48.11 – unsupported).

    Raises INVALID_ARGUMENT because schema lacks fileSetRefGroup.
    """
    raise TgiError("fileSetRefGroup unsupported in schema", TgiFaultCode.INVALID_ARGUMENT)


def addFunctionArgument(functionID: str, name: str, value: str, dataType: str) -> str:  # F.7.48.12
    """Add function argument (Section: F.7.48.12)."""
    fn = _resolve_function(functionID)
    arg = FileSetType.Function.Argument(name=name, value=value, data_type=dataType)  # type: ignore[arg-type]
    fn.argument.append(arg)  # type: ignore[attr-defined]
    register_parent(arg, fn, ("argument",), "list")
    return get_handle(arg)


def addFunctionSourceFile(functionID: str, sourceFileName: str, fileType: str) -> str:  # F.7.48.13
    """Add sourceFile (Section: F.7.48.13)."""
    fn = _resolve_function(functionID)
    sf = FileSetType.Function.SourceFile(
        source_name=IpxactUri(value=sourceFileName),
        file_type=_enum_file_type(fileType),
    )
    fn.source_file.append(sf)  # type: ignore[attr-defined]
    register_parent(sf, fn, ("source_file",), "list")
    return get_handle(sf)


def removeFileBuildCommand(fileID: str) -> bool:  # F.7.48.14
    """Remove buildCommand (Section: F.7.48.14)."""
    f = _resolve_file(fileID)
    if f.build_command is None:
        return False
    f.build_command = None  # type: ignore[assignment]
    return True


def removeFileDefine(defineID: str) -> bool:  # F.7.48.15
    """Remove define (Section: F.7.48.15)."""
    return detach_child_by_handle(defineID)


def removeFileDependency(dependencyID: str) -> bool:  # F.7.48.16
    """Remove dependency (Section: F.7.48.16)."""
    return detach_child_by_handle(dependencyID)


def removeFileExportedName(exportedNameID: str) -> bool:  # F.7.48.17
    """Remove exportedName (Section: F.7.48.17)."""
    return detach_child_by_handle(exportedNameID)


def removeFileFileType(fileTypeID: str) -> bool:  # F.7.48.18
    """Remove fileType (Section: F.7.48.18)."""
    return detach_child_by_handle(fileTypeID)


def removeFileImageType(imageTypeID: str) -> bool:  # F.7.48.19
    """Remove imageType (Section: F.7.48.19)."""
    return detach_child_by_handle(imageTypeID)


def removeFileIsIncludeFile(fileID: str) -> bool:  # F.7.48.20
    """Remove isIncludeFile (Section: F.7.48.20)."""
    f = _resolve_file(fileID)
    if f.is_include_file is None:
        return False
    f.is_include_file = None  # type: ignore[assignment]
    return True


def removeFileIsStructural(fileID: str) -> bool:  # F.7.48.21
    """Remove isStructural (Section: F.7.48.21)."""
    f = _resolve_file(fileID)
    if f.is_structural is None:
        return False
    f.is_structural = None  # type: ignore[assignment]
    return True


def removeFileLogicalName(fileID: str) -> bool:  # F.7.48.22
    """Remove logicalName (Section: F.7.48.22)."""
    f = _resolve_file(fileID)
    if f.logical_name is None:
        return False
    f.logical_name = None  # type: ignore[assignment]
    return True


def removeFileSetDefaultFileBuilder(fileBuilderID: str) -> bool:  # F.7.48.23
    """Remove defaultFileBuilder (Section: F.7.48.23)."""
    return detach_child_by_handle(fileBuilderID)


def removeFileSetDependency(dependencyID: str) -> bool:  # F.7.48.24
    """Remove fileSet dependency (Section: F.7.48.24)."""
    return detach_child_by_handle(dependencyID)


def removeFileSetFile(fileID: str) -> bool:  # F.7.48.25
    """Remove file from fileSet (Section: F.7.48.25)."""
    return detach_child_by_handle(fileID)


def removeFileSetFunction(functionID: str) -> bool:  # F.7.48.26
    """Remove function (Section: F.7.48.26)."""
    return detach_child_by_handle(functionID)


def removeFileSetGroup(groupID: str) -> bool:  # F.7.48.27
    """Remove group (Section: F.7.48.27)."""
    return detach_child_by_handle(groupID)


def removeFunctionArgument(argumentID: str) -> bool:  # F.7.48.28
    """Remove function argument (Section: F.7.48.28)."""
    return detach_child_by_handle(argumentID)


def removeFunctionDisabled(functionID: str) -> bool:  # F.7.48.29
    """Remove disabled element (Section: F.7.48.29)."""
    fn = _resolve_function(functionID)
    if fn.disabled is None:
        return False
    fn.disabled = None  # type: ignore[assignment]
    return True


def removeFunctionEntryPoint(functionID: str) -> bool:  # F.7.48.30
    """Remove entryPoint (Section: F.7.48.30)."""
    fn = _resolve_function(functionID)
    if fn.entry_point is None:
        return False
    fn.entry_point = None  # type: ignore[assignment]
    return True


def removeFunctionReturnType(functionID: str) -> bool:  # F.7.48.31
    """Remove returnType (Section: F.7.48.31)."""
    fn = _resolve_function(functionID)
    if fn.return_type is None:
        return False
    fn.return_type = None  # type: ignore[assignment]
    return True


def removeFunctionSourceFile(functionSourceFileID: str) -> bool:  # F.7.48.32
    """Remove sourceFile (Section: F.7.48.32)."""
    return detach_child_by_handle(functionSourceFileID)


def setFileIsIncludeFile(fileID: str, value: bool) -> bool:  # F.7.48.33
    """Set isIncludeFile (Section: F.7.48.33)."""
    from org.accellera.ipxact.v1685_2022.file import File as _File
    f = _resolve_file(fileID)
    f.is_include_file = _File.IsIncludeFile(value=value)  # type: ignore[assignment]
    return True


def setFileIsStructural(fileID: str, value: bool) -> bool:  # F.7.48.34
    """Set isStructural (Section: F.7.48.34)."""
    f = _resolve_file(fileID)
    f.is_structural = value  # type: ignore[assignment]
    return True


def setFileLogicalName(fileID: str, logicalName: str) -> bool:  # F.7.48.35
    """Set logicalName (Section: F.7.48.35)."""
    from org.accellera.ipxact.v1685_2022.file import File as _File
    f = _resolve_file(fileID)
    f.logical_name = _File.LogicalName(value=logicalName)  # type: ignore[assignment]
    return True


def setFileName(fileID: str, name: str) -> bool:  # F.7.48.36
    """Set file name path (Section: F.7.48.36)."""
    f = _resolve_file(fileID)
    f.name = IpxactUri(value=name)  # type: ignore[assignment]
    return True


def setFunctionArgumentDataType(argumentID: str, dataType: str) -> bool:  # F.7.48.37
    """Set argument dataType (Section: F.7.48.37)."""
    arg = _resolve_argument(argumentID)
    arg.data_type = dataType  # type: ignore[assignment]
    return True


def setFunctionDisabled(functionID: str, disabledExpression: str) -> bool:  # F.7.48.38
    """Set disabled expression (Section: F.7.48.38)."""
    fn = _resolve_function(functionID)
    fn.disabled = UnsignedBitExpression(value=disabledExpression)  # type: ignore[assignment]
    return True


def setFunctionEntryPoint(functionID: str, entryPoint: str) -> bool:  # F.7.48.39
    """Set entryPoint (Section: F.7.48.39)."""
    fn = _resolve_function(functionID)
    fn.entry_point = entryPoint  # type: ignore[assignment]
    return True


def setFunctionFileRef(functionID: str, fileRef: str) -> bool:  # F.7.48.40
    """Set fileRef (Section: F.7.48.40)."""
    fn = _resolve_function(functionID)
    fn.file_ref = fileRef  # type: ignore[assignment]
    return True


def setFunctionReplicate(functionID: str, replicate: bool) -> bool:  # F.7.48.41
    """Set replicate (Section: F.7.48.41)."""
    fn = _resolve_function(functionID)
    fn.replicate = replicate  # type: ignore[assignment]
    return True


def setFunctionReturnType(functionID: str, returnType: str) -> bool:  # F.7.48.42
    """Set returnType (Section: F.7.48.42)."""
    fn = _resolve_function(functionID)
    try:
        enum_val = ReturnTypeType(returnType)
    except ValueError as exc:
        raise TgiError("Unknown returnType", TgiFaultCode.INVALID_ARGUMENT) from exc
    fn.return_type = enum_val  # type: ignore[assignment]
    return True


def setFunctionSourceFileName(functionID: str, value: str) -> bool:  # F.7.48.43
    """Set first sourceFile's sourceName (Section: F.7.48.43).

    If no sourceFile exists a new one (without fileType) is created.
    """
    fn = _resolve_function(functionID)
    sf: FileSetType.Function.SourceFile | None = None
    if fn.source_file:  # type: ignore[truthy-bool]
        sf = list(fn.source_file)[0]  # type: ignore[index]
    if sf is None:
        sf = FileSetType.Function.SourceFile(source_name=IpxactUri(value=value))
        fn.source_file.append(sf)  # type: ignore[attr-defined]
        register_parent(sf, fn, ("source_file",), "list")
    else:
        sf.source_name = IpxactUri(value=value)  # type: ignore[assignment]
    return True


def setSourceFileFileType(sourceFileID: str, value: str) -> bool:  # F.7.48.44
    """Set sourceFile fileType (Section: F.7.48.44)."""
    sf = _resolve_source_file(sourceFileID)
    sf.file_type = _enum_file_type(value)  # type: ignore[assignment]
    return True


def setSourceFileSourceName(sourceFileID: str, sourceName: str) -> bool:  # F.7.48.45
    """Set sourceName (Section: F.7.48.45)."""
    sf = _resolve_source_file(sourceFileID)
    sf.source_name = IpxactUri(value=sourceName)  # type: ignore[assignment]
    return True

