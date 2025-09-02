"""File builder category TGI functions (IEEE 1685-2022).

Implements BASE (F.7.45) and EXTENDED (F.7.46) *File builder* functions.
Only the exact public API defined by Annex F is exported (no legacy helper
aliases). The functions provide access to buildCommand and fileBuilder
structures contained within higher-level elements (e.g., executableImage,
languageTools, fileSet entries). Where an element (command/flags/...) is not
present, getters return ``None`` (or empty lists) consistent with other
categories.

NOTE: The underlying 2022 schema classes are imported from
``org.accellera.ipxact.v1685_2022``. We interact with them via attribute
access and simple container list manipulations. We purposefully keep the
implementation conservative—if an expected container is missing we raise
``INVALID_ID`` for invalid handles; absence of a specific optional child just
returns ``None`` / False.
"""

from __future__ import annotations

from typing import Any

from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage
from org.accellera.ipxact.v1685_2022.linker_command_file import LinkerCommandFile

from .core import TgiError, TgiFaultCode, resolve_handle, get_handle, register_parent, detach_child_by_handle

__all__ = [
    # BASE (F.7.45.x)
    "getBuildCommandCommand",
    "getBuildCommandCommandExpression",
    "getBuildCommandCommandID",
    "getBuildCommandFlags",
    "getBuildCommandFlagsExpression",
    "getBuildCommandFlagsID",
    "getBuildCommandReplaceDefaultFlags",
    "getBuildCommandReplaceDefaultFlagsID",
    "getBuildCommandTargetName",
    "getBuildCommandTargetNameExpression",
    "getExecutableImageFileBuilderIDs",
    "getExecutableImageFileSetRefIDs",
    "getExecutableImageLanguageToolsID",
    "getExecutableImageLinker",
    "getExecutableImageLinkerCommandFileID",
    "getExecutableImageLinkerExpression",
    "getExecutableImageLinkerFlags",
    "getExecutableImageLinkerFlagsExpression",
    "getFileBuildCommandID",
    "getFileBuilderCommand",
    # EXTENDED (F.7.46.x)
    "addExecutableImageFileBuilderID",
    "addExecutableImageLinkerCommandFile",
    "addLanguageToolsFileBuilder",
    "addLinkerCommandFileGeneratorRef",
    "removeBuildCommandCommand",
    "removeBuildCommandFlags",
    "removeBuildCommandReplaceDefaultFlags",
    "removeBuildCommandTargetName",
    "removeDefaultFileBuilderCommand",
    "removeExecutableImageFileBuilderID",
    "removeExecutableImageLanguageTools",
    "removeExecutableImageLinkerCommandFile",
    "removeFileBuilderCommand",
    "removeFileBuilderFlags",
    "removeFileBuilderReplaceDefaultFlags",
    "removeLanguageToolsFileBuilder",
    "removeLanguageToolsLinkerCommandFile",
    "removeLanguageToolsLinkerFlags",
    "removeLinkerCommandFileGeneratorRef",
    "setBuildCommandCommand",
    "setBuildCommandFlags",
    "setBuildCommandReplaceDefaultFlags",
    "setBuildCommandTargetName",
    "setExecutableImageLanguageTools",
    "setExecutableImageLinker",
    "setExecutableImageLinkerFlags",
    "setFileBuildCommand",
    "setFileBuilderCommand",
    "setFileBuilderFileType",
    "setFileBuilderFlags",
    "setFileBuilderReplaceDefaultFlags",
    "setLanguageToolsLinker",
    "setLanguageToolsLinkerCommandFile",
    "setLanguageToolsLinkerFlags",
    "setLinkerCommandFileCommandLineSwitch",
    "setLinkerCommandFileEnable",
]


def _resolve(handle: str) -> Any:
    obj = resolve_handle(handle)
    if obj is None:
        raise TgiError("Invalid handle", TgiFaultCode.INVALID_ID)
    return obj


def _get_value(node: Any) -> Any:
    if node is None:
        return None
    v = getattr(node, "value", node)
    return getattr(v, "value", v)


# ---------------------------------------------------------------------------
# BASE (F.7.45)
# ---------------------------------------------------------------------------

def _resolve_build_command(fileHandle: str) -> Any:
    f = _resolve(fileHandle)
    # buildCommand is an optional child of a File element
    bc = getattr(f, "build_command", None)
    return bc


def getBuildCommandCommand(fileID: str) -> str | None:  # F.7.45.1
    """Return textual build command value.

    Section: F.7.45.1.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.command is None:
        return None
    return _get_value(bc.command)


def getBuildCommandCommandExpression(fileID: str) -> str | None:  # F.7.45.2
    """Return expression (if any) for build command.

    Section: F.7.45.2.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.command is None:
        return None
    return getattr(bc.command, "value", None)


def getBuildCommandCommandID(fileID: str) -> str | None:  # F.7.45.3
    """Return handle of build command value element.

    Section: F.7.45.3.
    """
    bc = _resolve_build_command(fileID)
    return None if bc is None or bc.command is None else get_handle(bc.command)


def getBuildCommandFlags(fileID: str) -> str | None:  # F.7.45.4
    """Return textual flags value.

    Section: F.7.45.4.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.flags is None:
        return None
    return _get_value(bc.flags)


def getBuildCommandFlagsExpression(fileID: str) -> str | None:  # F.7.45.5
    """Return expression (if any) for flags.

    Section: F.7.45.5.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.flags is None:
        return None
    return getattr(bc.flags, "value", None)


def getBuildCommandFlagsID(fileID: str) -> str | None:  # F.7.45.6
    """Return handle of flags element.

    Section: F.7.45.6.
    """
    bc = _resolve_build_command(fileID)
    return None if bc is None or bc.flags is None else get_handle(bc.flags)


def getBuildCommandReplaceDefaultFlags(fileID: str) -> bool | None:  # F.7.45.7
    """Return boolean value of replaceDefaultFlags (converted to bool).

    Section: F.7.45.7.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.replace_default_flags is None:
        return None
    val = _get_value(bc.replace_default_flags)
    if isinstance(val, bool):
        return val
    return str(val).lower() in {"1", "true", "yes", "on"}


def getBuildCommandReplaceDefaultFlagsID(fileID: str) -> str | None:  # F.7.45.8
    """Return handle of replaceDefaultFlags element.

    Section: F.7.45.8.
    """
    bc = _resolve_build_command(fileID)
    return None if bc is None or bc.replace_default_flags is None else get_handle(bc.replace_default_flags)


def getBuildCommandTargetName(fileID: str) -> str | None:  # F.7.45.9
    """Return targetName value (derived file path).

    Section: F.7.45.9.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.target_name is None:
        return None
    return _get_value(bc.target_name)


def getBuildCommandTargetNameExpression(fileID: str) -> str | None:  # F.7.45.10
    """Return expression for targetName.

    Section: F.7.45.10.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.target_name is None:
        return None
    return getattr(bc.target_name, "value", None)


def getExecutableImageFileBuilderIDs(executableImageID: str) -> list[str]:  # F.7.45.11
    """Return handles of all fileBuilder children of languageTools.

    Section: F.7.45.11.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        return []
    return [get_handle(fb) for fb in img.language_tools.file_builder]


def getExecutableImageFileSetRefIDs(executableImageID: str) -> list[str]:  # F.7.45.12
    """Return handles of all fileSetRef children.

    Section: F.7.45.12.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.file_set_ref_group is None:
        return []
    return [get_handle(r) for r in img.file_set_ref_group.file_set_ref]


def getExecutableImageLanguageToolsID(executableImageID: str) -> str | None:  # F.7.45.13
    """Return handle of languageTools or None.

    Section: F.7.45.13.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    return None if img.language_tools is None else get_handle(img.language_tools)


def getExecutableImageLinker(executableImageID: str) -> str | None:  # F.7.45.14
    """Return linker command text.

    Section: F.7.45.14.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None or img.language_tools.linker is None:
        return None
    return _get_value(img.language_tools.linker)


def getExecutableImageLinkerCommandFileID(executableImageID: str) -> str | None:  # F.7.45.15
    """Return handle of first linkerCommandFile (if any).

    Section: F.7.45.15.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        return None
    # Spec returns first? F.7.45.15 singular; choose first if present
    for lcf in img.language_tools.linker_command_file:
        return get_handle(lcf)
    return None


def getExecutableImageLinkerExpression(executableImageID: str) -> str | None:  # F.7.45.16
    """Return expression for linker element.

    Section: F.7.45.16.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None or img.language_tools.linker is None:
        return None
    return getattr(img.language_tools.linker, "value", None)


def getExecutableImageLinkerFlags(executableImageID: str) -> str | None:  # F.7.45.17
    """Return textual linker flags.

    Section: F.7.45.17.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None or img.language_tools.linker_flags is None:
        return None
    return _get_value(img.language_tools.linker_flags)


def getExecutableImageLinkerFlagsExpression(executableImageID: str) -> str | None:  # F.7.45.18
    """Return expression for linker flags.

    Section: F.7.45.18.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None or img.language_tools.linker_flags is None:
        return None
    return getattr(img.language_tools.linker_flags, "value", None)


def getFileBuildCommandID(fileID: str) -> str | None:  # F.7.45.19
    """Return handle of buildCommand element for a File.

    Section: F.7.45.19.
    """
    bc = _resolve_build_command(fileID)
    return None if bc is None else get_handle(bc)


def getFileBuilderCommand(fileBuilderID: str) -> str | None:  # F.7.45.20
    """Return command text of a fileBuilder.

    Section: F.7.45.20.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not a FileBuilder", TgiFaultCode.INVALID_ID)
    if fb.command is None:
        return None
    return _get_value(fb.command)


# ---------------------------------------------------------------------------
# EXTENDED (F.7.46)
# ---------------------------------------------------------------------------

def addExecutableImageFileBuilderID(executableImageID: str, fileType: str) -> str:  # F.7.46.1
    """Create a new fileBuilder under executableImage.languageTools.

    Section: F.7.46.1.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        img.language_tools = ExecutableImage.LanguageTools()
        register_parent(img.language_tools, img, (), "single")
    fb = ExecutableImage.LanguageTools.FileBuilder()
    fb.file_type = fileType  # type: ignore[attr-defined]
    img.language_tools.file_builder.append(fb)  # type: ignore[attr-defined]
    register_parent(fb, img.language_tools, ("file_builder",), "list")
    return get_handle(fb)


def addExecutableImageLinkerCommandFile(executableImageID: str, enable: bool | None = None) -> str:  # F.7.46.2
    """Append a new linkerCommandFile (optionally setting enable flag).

    Section: F.7.46.2.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not an ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        img.language_tools = ExecutableImage.LanguageTools()
        register_parent(img.language_tools, img, (), "single")
    lcf = LinkerCommandFile()
    if enable is not None:
        lcf.enable = bool(enable)  # type: ignore[attr-defined]
    img.language_tools.linker_command_file.append(lcf)  # type: ignore[attr-defined]
    register_parent(lcf, img.language_tools, ("linker_command_file",), "list")
    return get_handle(lcf)


def addLanguageToolsFileBuilder(languageToolsID: str, fileType: str) -> str:  # F.7.46.3
    """Add fileBuilder to existing languageTools element.

    Section: F.7.46.3.
    """
    lt = _resolve(languageToolsID)
    from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage as _EI
    if not isinstance(lt, _EI.LanguageTools):
        raise TgiError("Handle is not LanguageTools", TgiFaultCode.INVALID_ID)
    fb = _EI.LanguageTools.FileBuilder()
    fb.file_type = fileType  # type: ignore[attr-defined]
    lt.file_builder.append(fb)  # type: ignore[attr-defined]
    register_parent(fb, lt, ("file_builder",), "list")
    return get_handle(fb)


def addLinkerCommandFileGeneratorRef(linkerCommandFileID: str, generatorRef: str) -> bool:  # F.7.46.4
    """Append a generatorRef to a linkerCommandFile.

    Section: F.7.46.4.
    """
    lcf = _resolve(linkerCommandFileID)
    if not isinstance(lcf, LinkerCommandFile):
        raise TgiError("Handle is not LinkerCommandFile", TgiFaultCode.INVALID_ID)
    # Append a new generatorRef simple structure (assuming class exists in list)
    from org.accellera.ipxact.v1685_2022.generator_ref import GeneratorRef
    gr = GeneratorRef(value=generatorRef)  # type: ignore[arg-type]
    lcf.generator_ref.append(gr)  # type: ignore[attr-defined]
    return True


def removeBuildCommandCommand(fileID: str) -> bool:  # F.7.46.5
    """Remove buildCommand.command element.

    Section: F.7.46.5.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.command is None:
        return False
    bc.command = None
    return True


def removeBuildCommandFlags(fileID: str) -> bool:  # F.7.46.6
    """Remove buildCommand.flags element.

    Section: F.7.46.6.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.flags is None:
        return False
    bc.flags = None
    return True


def removeBuildCommandReplaceDefaultFlags(fileID: str) -> bool:  # F.7.46.7
    """Remove replaceDefaultFlags element.

    Section: F.7.46.7.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.replace_default_flags is None:
        return False
    bc.replace_default_flags = None
    return True


def removeBuildCommandTargetName(fileID: str) -> bool:  # F.7.46.8
    """Remove targetName element.

    Section: F.7.46.8.
    """
    bc = _resolve_build_command(fileID)
    if bc is None or bc.target_name is None:
        return False
    bc.target_name = None
    return True


def removeDefaultFileBuilderCommand(fileBuilderID: str) -> bool:  # F.7.46.9
    """Remove command child from fileBuilder.

    Section: F.7.46.9.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    if fb.command is None:
        return False
    fb.command = None
    return True


def removeExecutableImageFileBuilderID(fileBuilderID: str) -> bool:  # F.7.46.10
    """Detach a fileBuilder from its parent list.

    Section: F.7.46.10.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(get_handle(fb))


def removeExecutableImageLanguageTools(executableImageID: str) -> bool:  # F.7.46.11
    """Remove the entire languageTools element.

    Section: F.7.46.11.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        return False
    img.language_tools = None
    return True


def removeExecutableImageLinkerCommandFile(executableImageID: str) -> bool:  # F.7.46.12
    """Remove first linkerCommandFile under languageTools.

    Section: F.7.46.12.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        return False
    if not img.language_tools.linker_command_file:  # type: ignore[attr-defined]
        return False
    seq = list(img.language_tools.linker_command_file)  # type: ignore[attr-defined]
    seq.pop(0)
    img.language_tools.linker_command_file = seq  # type: ignore[attr-defined]
    return True


def removeFileBuilderCommand(fileBuilderID: str) -> bool:  # F.7.46.13
    """Remove command element of fileBuilder.

    Section: F.7.46.13.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    if fb.command is None:
        return False
    fb.command = None
    return True


def removeFileBuilderFlags(fileBuilderID: str) -> bool:  # F.7.46.14
    """Remove flags element of fileBuilder.

    Section: F.7.46.14.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    if fb.flags is None:
        return False
    fb.flags = None
    return True


def removeFileBuilderReplaceDefaultFlags(fileBuilderID: str) -> bool:  # F.7.46.15
    """Remove replaceDefaultFlags element of fileBuilder.

    Section: F.7.46.15.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    if fb.replace_default_flags is None:
        return False
    fb.replace_default_flags = None
    return True


def removeLanguageToolsFileBuilder(fileBuilderID: str) -> bool:  # F.7.46.16
    """Remove fileBuilder from languageTools (alias context).

    Section: F.7.46.16.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    return detach_child_by_handle(get_handle(fb))


def removeLanguageToolsLinkerCommandFile(languageToolsID: str) -> bool:  # F.7.46.17
    """Remove first linkerCommandFile of languageTools.

    Section: F.7.46.17.
    """
    lt = _resolve(languageToolsID)
    from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage as _EI
    if not isinstance(lt, _EI.LanguageTools):
        raise TgiError("Handle is not LanguageTools", TgiFaultCode.INVALID_ID)
    if not lt.linker_command_file:  # type: ignore[attr-defined]
        return False
    seq = list(lt.linker_command_file)  # type: ignore[attr-defined]
    seq.pop(0)
    lt.linker_command_file = seq  # type: ignore[attr-defined]
    return True


def removeLanguageToolsLinkerFlags(languageToolsID: str) -> bool:  # F.7.46.18
    """Remove linkerFlags element.

    Section: F.7.46.18.
    """
    lt = _resolve(languageToolsID)
    from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage as _EI
    if not isinstance(lt, _EI.LanguageTools):
        raise TgiError("Handle is not LanguageTools", TgiFaultCode.INVALID_ID)
    if lt.linker_flags is None:
        return False
    lt.linker_flags = None
    return True


def removeLinkerCommandFileGeneratorRef(linkerCommandFileID: str) -> bool:  # F.7.46.19
    """Clear all generatorRef entries from linkerCommandFile.

    Section: F.7.46.19.
    """
    lcf = _resolve(linkerCommandFileID)
    if not isinstance(lcf, LinkerCommandFile):
        raise TgiError("Handle is not LinkerCommandFile", TgiFaultCode.INVALID_ID)
    if not lcf.generator_ref:  # type: ignore[attr-defined]
        return False
    lcf.generator_ref = []  # type: ignore[attr-defined]
    return True


def setBuildCommandCommand(fileID: str, command: str) -> bool:  # F.7.46.20
    """Set buildCommand.command value (creates buildCommand if absent).

    Section: F.7.46.20.
    """
    f = _resolve(fileID)
    bc = getattr(f, "build_command", None)
    if bc is None:
        from org.accellera.ipxact.v1685_2022.file import File as _File
        bc = _File.BuildCommand()
        f.build_command = bc
    bc.command = command  # type: ignore[attr-defined]
    return True


def setBuildCommandFlags(fileID: str, flags: str) -> bool:  # F.7.46.21
    """Set buildCommand.flags value.

    Section: F.7.46.21.
    """
    f = _resolve(fileID)
    bc = getattr(f, "build_command", None)
    if bc is None:
        from org.accellera.ipxact.v1685_2022.file import File as _File
        bc = _File.BuildCommand()
        f.build_command = bc
    bc.flags = flags  # type: ignore[attr-defined]
    return True


def setBuildCommandReplaceDefaultFlags(fileID: str, replace: bool) -> bool:  # F.7.46.22
    """Set replaceDefaultFlags boolean.

    Section: F.7.46.22.
    """
    f = _resolve(fileID)
    bc = getattr(f, "build_command", None)
    if bc is None:
        from org.accellera.ipxact.v1685_2022.file import File as _File
        bc = _File.BuildCommand()
        f.build_command = bc
    bc.replace_default_flags = bool(replace)  # type: ignore[attr-defined]
    return True


def setBuildCommandTargetName(fileID: str, targetName: str) -> bool:  # F.7.46.23
    """Set targetName value.

    Section: F.7.46.23.
    """
    f = _resolve(fileID)
    bc = getattr(f, "build_command", None)
    if bc is None:
        from org.accellera.ipxact.v1685_2022.file import File as _File
        bc = _File.BuildCommand()
        f.build_command = bc
    bc.target_name = targetName  # type: ignore[attr-defined]
    return True


def setExecutableImageLanguageTools(executableImageID: str) -> str:  # F.7.46.24
    """Create (if absent) and return handle of languageTools.

    Section: F.7.46.24.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        img.language_tools = ExecutableImage.LanguageTools()
        register_parent(img.language_tools, img, (), "single")
    return get_handle(img.language_tools)


def setExecutableImageLinker(executableImageID: str, linker: str) -> bool:  # F.7.46.25
    """Set linker text inside languageTools.

    Section: F.7.46.25.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        img.language_tools = ExecutableImage.LanguageTools()
        register_parent(img.language_tools, img, (), "single")
    img.language_tools.linker = linker  # type: ignore[attr-defined]
    return True


def setExecutableImageLinkerFlags(executableImageID: str, flags: str) -> bool:  # F.7.46.26
    """Set linkerFlags text inside languageTools.

    Section: F.7.46.26.
    """
    img = _resolve(executableImageID)
    if not isinstance(img, ExecutableImage):
        raise TgiError("Handle is not ExecutableImage", TgiFaultCode.INVALID_ID)
    if img.language_tools is None:
        img.language_tools = ExecutableImage.LanguageTools()
        register_parent(img.language_tools, img, (), "single")
    img.language_tools.linker_flags = flags  # type: ignore[attr-defined]
    return True


def setFileBuildCommand(fileID: str) -> str:  # F.7.46.27
    """Ensure buildCommand exists and return its handle.

    Section: F.7.46.27.
    """
    f = _resolve(fileID)
    bc = getattr(f, "build_command", None)
    if bc is None:
        # create new build command
        from org.accellera.ipxact.v1685_2022.file import File as _File
        bc = _File.BuildCommand()
        f.build_command = bc
        register_parent(bc, f, (), "single")
    return get_handle(bc)


def setFileBuilderCommand(fileBuilderID: str, command: str) -> bool:  # F.7.46.28
    """Set fileBuilder.command.

    Section: F.7.46.28.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    fb.command = command  # type: ignore[attr-defined]
    return True


def setFileBuilderFileType(fileBuilderID: str, fileType: str) -> bool:  # F.7.46.29
    """Set fileBuilder.fileType.

    Section: F.7.46.29.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    fb.file_type = fileType  # type: ignore[attr-defined]
    return True


def setFileBuilderFlags(fileBuilderID: str, flags: str) -> bool:  # F.7.46.30
    """Set fileBuilder.flags.

    Section: F.7.46.30.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    fb.flags = flags  # type: ignore[attr-defined]
    return True


def setFileBuilderReplaceDefaultFlags(fileBuilderID: str, replace: bool) -> bool:  # F.7.46.31
    """Set fileBuilder.replaceDefaultFlags.

    Section: F.7.46.31.
    """
    fb = _resolve(fileBuilderID)
    if not hasattr(fb, "file_type") or not hasattr(fb, "command"):
        raise TgiError("Handle is not FileBuilder", TgiFaultCode.INVALID_ID)
    fb.replace_default_flags = bool(replace)  # type: ignore[attr-defined]
    return True


def setLanguageToolsLinker(languageToolsID: str, linker: str) -> bool:  # F.7.46.32
    """Set linker value under languageTools.

    Section: F.7.46.32.
    """
    lt = _resolve(languageToolsID)
    from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage as _EI
    if not isinstance(lt, _EI.LanguageTools):
        raise TgiError("Handle is not LanguageTools", TgiFaultCode.INVALID_ID)
    lt.linker = linker  # type: ignore[attr-defined]
    return True


def setLanguageToolsLinkerCommandFile(languageToolsID: str) -> str:  # F.7.46.33
    """Append new linkerCommandFile under languageTools.

    Section: F.7.46.33.
    """
    lt = _resolve(languageToolsID)
    from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage as _EI
    if not isinstance(lt, _EI.LanguageTools):
        raise TgiError("Handle is not LanguageTools", TgiFaultCode.INVALID_ID)
    lcf = LinkerCommandFile()
    lt.linker_command_file.append(lcf)  # type: ignore[attr-defined]
    register_parent(lcf, lt, ("linker_command_file",), "list")
    return get_handle(lcf)


def setLanguageToolsLinkerFlags(languageToolsID: str, flags: str) -> bool:  # F.7.46.34
    """Set linkerFlags for languageTools.

    Section: F.7.46.34.
    """
    lt = _resolve(languageToolsID)
    from org.accellera.ipxact.v1685_2022.executable_image import ExecutableImage as _EI
    if not isinstance(lt, _EI.LanguageTools):
        raise TgiError("Handle is not LanguageTools", TgiFaultCode.INVALID_ID)
    lt.linker_flags = flags  # type: ignore[attr-defined]
    return True


def setLinkerCommandFileCommandLineSwitch(linkerCommandFileID: str, switch: str) -> bool:  # F.7.46.35
    """Set commandLineSwitch of linkerCommandFile.

    Section: F.7.46.35.
    """
    lcf = _resolve(linkerCommandFileID)
    if not isinstance(lcf, LinkerCommandFile):
        raise TgiError("Handle is not LinkerCommandFile", TgiFaultCode.INVALID_ID)
    lcf.command_line_switch = switch  # type: ignore[attr-defined]
    return True


def setLinkerCommandFileEnable(linkerCommandFileID: str, enable: bool) -> bool:  # F.7.46.36
    """Set enable flag of linkerCommandFile.

    Section: F.7.46.36.
    """
    lcf = _resolve(linkerCommandFileID)
    if not isinstance(lcf, LinkerCommandFile):
        raise TgiError("Handle is not LinkerCommandFile", TgiFaultCode.INVALID_ID)
    lcf.enable = bool(enable)  # type: ignore[attr-defined]
    return True

