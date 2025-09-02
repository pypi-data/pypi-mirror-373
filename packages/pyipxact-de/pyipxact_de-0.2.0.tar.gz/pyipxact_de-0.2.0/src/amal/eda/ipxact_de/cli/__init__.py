import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from amal.utilities import ARROW, logger
from org.accellera.standard import STANDARDS

from .. import __description__, __version__
from .commands import convert_xml, identify_xml, validate_xml

# Global Rich console (single theme) reused for all help rendering.
console = Console(
    theme=Theme(
        {
            "heading": "bold bright_green",
            "command": "bright_cyan",
            "command.bold": "bold bright_cyan",
            "flag": "bold bright_cyan",
            "usage.label": "bold bright_green",
            "usage.prog": "bold bright_cyan",
            "usage.meta": "cyan",
            "footer": "dim",
        }
    ),
    highlight=False,
)


@dataclass(slots=True)
class HelpSection:
    """Runtime help section (built dynamically)."""
    title: str
    rows: list[tuple[str, str]]
    priority: int = 100


_COMMANDS_ORDER: list[str] = ["standards", "identify", "validate", "convert", "help", "version"]
_ACTION_METADATA: dict[int, tuple[str, int]] = {}


def _build_sections(
    parser: argparse.ArgumentParser, subparser_map: dict[str, argparse.ArgumentParser]
) -> list[HelpSection]:
    """Create ordered help sections from parser metadata."""
    sections: dict[str, HelpSection] = {}

    # Commands section
    cmd_entries: list[tuple[int, str, str]] = []  # (order, name, desc)
    for name, sp in subparser_map.items():
        order = _COMMANDS_ORDER.index(name) if name in _COMMANDS_ORDER else 1000
        desc = sp.description or name
        cmd_entries.append((order, name, desc))
    if cmd_entries:
        cmd_entries.sort(key=lambda t: (t[0], t[1]))
        sections["Commands:"] = HelpSection("Commands:", [(n, d) for _, n, d in cmd_entries], priority=10)

    # Options grouped by registered metadata
    for action in parser._actions:  # noqa: SLF001
        if not action.option_strings:
            continue
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            continue
        title, prio = _ACTION_METADATA.get(id(action), ("Global options:", 90))
        if title in sections:
            hs = sections[title]
        else:
            hs = HelpSection(title, [], priority=prio)
            sections[title] = hs
        flags = ", ".join(action.option_strings)
        hs.rows.append((flags, action.help or ""))

    return sorted(sections.values(), key=lambda s: (s.priority, s.title))


def _format_flags(flags: str) -> str:
    """Return flags (already provided in desired form)."""
    return flags


class _RichSubHelpAction(argparse.Action):
    """Custom help action for subcommands to show Rich-styled help and exit early.

    This avoids argparse enforcing required positionals before displaying help.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values=None,
        option_string: str | None = None,
    ) -> None:  # type: ignore[override]
        parts = parser.prog.split()
        parent_prog = parts[0] if parts else 'ipxact'
        subcmd = parts[-1] if len(parts) > 1 else parser.prog
        _print_subcommand_help(parent_prog, subcmd, parser)
        parser.exit()


def _print_top_level_help(parser: argparse.ArgumentParser) -> None:
    """Print top-level help building sections dynamically from parser state."""
    prog = parser.prog
    if parser.description:
        console.print(parser.description)
        console.print()
    usage_line = (
        Text("Usage:", style="usage.label")
        .append(" ")
        .append(prog, style="usage.prog")
        .append(" ")
        .append("[OPTIONS] <COMMAND>", style="usage.meta")
    )
    console.print(usage_line)
    console.print()

    # Discover subparsers to build command section
    subparser_map: dict[str, argparse.ArgumentParser] = {}
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            for name, sp in action._name_parser_map.items():  # type: ignore[attr-defined]
                subparser_map[name] = sp

    sections = _build_sections(parser, subparser_map)
    for section in sections:
        console.print(Text(section.title, style="heading"))
        table = Table(show_header=False, box=None, pad_edge=False)
        table.add_column(no_wrap=True)
        table.add_column()
        pad_width = max(len(flags) for flags, _ in section.rows) if section.rows else 0
        for left, help_text in section.rows:
            pad = f"{left:<{pad_width}}"
            style = "command.bold" if section.title.startswith("Commands") else "flag"
            table.add_row(f"  [{style}]{pad}[/]", help_text)
        console.print(table)
        console.print()

    console.print(Text("Use `ipxact-de help` for more details.", style="footer"))


def _print_subcommand_help(parent_prog: str, name: str, subparser: argparse.ArgumentParser) -> None:
    """Print Rich-styled help for a specific subcommand.

    Args:
        parent_prog: Top-level program name.
        name: Subcommand name.
        subparser: The argparse subparser instance.
    """
    usage = f"{parent_prog} {name}"
    # Collect actions
    positional: list[tuple[str, str]] = []
    options: list[tuple[str, str]] = []
    for action in subparser._actions:  # noqa: SLF001
        if isinstance(action, argparse._HelpAction):  # skip built-in help
            continue
        if isinstance(action, argparse._SubParsersAction):  # skip nested subparsers
            continue
        help_text = action.help or ""
        if action.option_strings:
            flags = ", ".join(action.option_strings)
            # Determine if value placeholder needed
            needs_value = getattr(action, "nargs", None) not in (0, None) or (
                getattr(action, "nargs", None) is None
                and not isinstance(
                    action, argparse._StoreTrueAction | argparse._StoreFalseAction
                )
            )
            if not action.option_strings or isinstance(
                action, argparse._StoreTrueAction | argparse._StoreFalseAction
            ):
                needs_value = False
            if needs_value:
                placeholder = action.metavar or action.dest.upper().replace('-', '_')
                flags_display = f"{flags} {placeholder}"
            else:
                flags_display = flags
            options.append((flags_display, help_text))
        else:
            # Positional argument; metavar can be a tuple for multiple values.
            raw_meta = action.metavar or action.dest.upper().replace('-', '_')
            placeholder = " ".join(str(m) for m in raw_meta) if isinstance(raw_meta, tuple) else str(raw_meta)
            positional.append((placeholder, help_text))

    # Header / description: print top-level description then subcommand description (if any) before usage
    desc = subparser.description or next(
        (
            a.help
            for a in getattr(subparser, "_actions", [])
            if isinstance(a, argparse._HelpAction)
        ),
        None,
    )
    printed_any = False
    if __description__:
        console.print(__description__)
        printed_any = True
    if desc:
        if printed_any:
            console.print()
        console.print(desc)
        printed_any = True
    if printed_any:
        console.print()

    usage_line = (
        Text("Usage:", style="usage.label")
        .append(" ")
        .append(usage, style="usage.prog")
        .append(" ")
        .append("[OPTIONS]" if options else "", style="usage.meta")
    )
    console.print(usage_line)
    console.print()

    if positional:
        console.print(Text("Arguments", style="heading"))
        arg_table = Table(show_header=False, box=None, pad_edge=False)
        arg_table.add_column(no_wrap=True)
        arg_table.add_column()
        width = max(len(n) for n, _ in positional)
        for name_col, help_col in positional:
            pad = f"{name_col:<{width}}"
            arg_table.add_row(f"  [command.bold]{pad}[/]", help_col)
        console.print(arg_table)
        console.print()

    if options:
        console.print(Text("Options", style="heading"))
        opt_table = Table(show_header=False, box=None, pad_edge=False)
        opt_table.add_column(no_wrap=True)
        opt_table.add_column()
        width = max(len(n) for n, _ in options)
        for flags, help_col in options:
            pad = f"{flags:<{width}}"
            opt_table.add_row(f"  [flag]{pad}[/]", help_col)
        console.print(opt_table)


@dataclass(slots=True)
class CommandSpec:
    """Specification for registering a subcommand.

    Attributes:
        name: Subcommand name.
        help: Short help/description.
        register: Callable that receives the subparsers object and returns the created subparser.
    """

    name: str
    help: str
    register: Callable[[argparse._SubParsersAction], argparse.ArgumentParser]


def _build_command_specs(all_versions: list[str]) -> list[CommandSpec]:
    """Create command specs for identify, validate, convert, version.

    Args:
        all_versions: Supported conversion targets.

    Returns:
        List of command specifications (excluding 'help').
    """

    def _register_identify(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Register the 'identify' subcommand.

        Args:
            subparsers: Subparsers action to register with.

        Returns:
            The configured subparser.
        """
        # Provide description once; argparse will surface short help (first line of description) automatically if needed
        parser_identity = subparsers.add_parser(
            "identify",
            description="Identify IP-XACT xml files",
            help="Identify IP-XACT xml files",
            add_help=False,
        )
        parser_identity.add_argument(
            "xml-files",
            type=argparse.FileType("r"),
            nargs="+",
            help="IP-XACT xml files to identify",
        )
        parser_identity.add_argument(
            "-h",
            "--help",
            action=_RichSubHelpAction,
            nargs=0,
            help="Show this message and exit",
        )
        parser_identity.set_defaults(func=identify_xml)
        return parser_identity

    def _register_validate(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Register the 'validate' subcommand.

        Args:
            subparsers: Subparsers action to register with.

        Returns:
            The configured subparser.
        """
        parser_validate = subparsers.add_parser(
            "validate",
            description="Validate IP-XACT xml files",
            help="Validate IP-XACT xml files",
            add_help=False,
        )
        parser_validate.add_argument(
            "xml-files",
            type=argparse.FileType("r"),
            nargs="+",
            help="IP-XACT xml files to validate",
        )
        parser_validate.add_argument(
            "-h",
            "--help",
            action=_RichSubHelpAction,
            nargs=0,
            help="Show this message and exit",
        )
        parser_validate.set_defaults(func=validate_xml)
        return parser_validate

    def _register_convert(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Register the 'convert' subcommand.

        Args:
            subparsers: Subparsers action to register with.

        Returns:
            The configured subparser.
        """
        parser_convert = subparsers.add_parser(
            "convert",
            description="Convert IP-XACT xml files",
            help="Convert IP-XACT xml files",
            add_help=False,
        )
        parser_convert.add_argument(
            "--to-version",
            type=str,
            choices=all_versions,
            help="Convert IP-XACT file to version (supported: [bright_cyan]"
            + ", ".join(all_versions)
            + "[/bright_cyan])",
        )
        parser_convert.add_argument(
            "xml-files",
            type=argparse.FileType("r"),
            nargs="+",
            help="IP-XACT XML file to convert",
        )
        parser_convert.add_argument(
            "--output-dir",
            "-o",
            type=str,
            default="converted",
            help="Output directory for the converted IP-XACT XML file",
        )
        # parser_convert.add_argument("output-file", type=str, help="Output IP-XACT XML file")
        parser_convert.add_argument(
            "--overwrite",
            action="store_true",
            help="Force overwrite of the output file if it exists"
        )
        parser_convert.add_argument(
            "-h",
            "--help",
            action=_RichSubHelpAction,
            nargs=0,
            help="Show this message and exit",
        )
        parser_convert.set_defaults(func=convert_xml)
        return parser_convert

    def _register_standards(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Register the 'standards' subcommand to list supported schema versions."""
        parser_standards = subparsers.add_parser(
            "standards",
            description="List supported SPIRIT/IP-XACT schema versions",
            help="List supported schema versions",
            add_help=False,
        )
        parser_standards.add_argument(
            "-h",
            "--help",
            action=_RichSubHelpAction,
            nargs=0,
            help="Show this message and exit",
        )
        parser_standards.set_defaults(func=_print_standards)
        return parser_standards

    def _register_version(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Register the 'version' subcommand (just program version)."""
        parser_version = subparsers.add_parser(
            "version",
            description="Show CLI version",
            help="Show CLI version",
            add_help=False,
        )
        parser_version.add_argument(
            "-h",
            "--help",
            action=_RichSubHelpAction,
            nargs=0,
            help="Show this message and exit",
        )
        parser_version.set_defaults(func=_print_version)
        return parser_version

    return [
        CommandSpec("identify", "Identify IP-XACT xml files", _register_identify),
        CommandSpec("validate", "Validate IP-XACT xml files", _register_validate),
        CommandSpec("convert", "Convert IP-XACT xml files", _register_convert),
        CommandSpec("standards", "List supported schema versions", _register_standards),
        CommandSpec("version", "Show CLI version", _register_version),
    ]


## Removed legacy _commands_help helper; dynamic argparse introspection supplies command help.


def _print_version(args: argparse.Namespace) -> None:
    """Print CLI version only."""
    console.print(f"ipxact v{__version__}")


def _print_standards(args: argparse.Namespace) -> None:
    """Print supported SPIRIT/IP-XACT schema versions."""
    preferred_order = ["spirit", "ipxact"]
    all_versions = [
        f"{std}/{ver}"
        for std in preferred_order
        if std in STANDARDS
        for ver in STANDARDS[std].versions
    ]
    console.print(Text("Supported standards:", style="heading"))
    for ver in all_versions:
        console.print(f"  {ARROW} [bright_cyan]{ver}[/bright_cyan]")


def main() -> None:
    """Main entry point for the IP-XACT CLI."""

    # logger.trace("TRACE")
    # logger.debug("DEBUG")
    # logger.info("INFO")
    # logger.success("SUCCESS")
    # logger.warning("WARNING")
    # logger.error("ERROR")
    # try:
    #     1 / 0
    # except ZeroDivisionError:
    #     logger.exception("EXCEPTION")
    # logger.critical("CRITICAL")

    parser = argparse.ArgumentParser(
        prog="ipxact",
        description=__description__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Text at the bottom of help",
        add_help=False,
    )
    # Add global & logging options (captured into sections immediately below)
    help_action = parser.add_argument("-h", "--help", action="store_true", help="Show this message and exit")
    verbose_action = parser.add_argument("-v", "--verbose", action="count", default=0, help="Enable verbose logging")
    quiet_action = parser.add_argument("-q", "--quiet", action="store_true", help="Print diagnostics, but nothing else")
    silent_action = parser.add_argument("-s", "--silent", action="store_true", help="Disable all logging")
    version_action = parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s v{__version__}",
        help="Show version and exit",
    )
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    # Build versions list (shared) once
    preferred_order = ["spirit", "ipxact"]
    all_versions = [
        f"{std}/{ver}"
        for std in preferred_order
        if std in STANDARDS
        for ver in STANDARDS[std].versions
    ]

    # Register primary command specs
    specs = _build_command_specs(all_versions)
    subparser_map: dict[str, argparse.ArgumentParser] = {}
    for spec in specs:
        subparser_map[spec.name] = spec.register(subparsers)

    def _help_handler(args: argparse.Namespace | None = None) -> None:  # noqa: D401 - short internal handler
        """Help handler for 'help' subcommand or top-level help."""
        subcmd = getattr(args, "subcommand_name", None) if args else None
        if not subcmd:
            _print_top_level_help(parser)
            return
        if subcmd in subparser_map:
            _print_subcommand_help(parser.prog, subcmd, subparser_map[subcmd])
        else:
            sys.stderr.write(f"Unknown command '{subcmd}'. Available: {', '.join(sorted(subparser_map))}.\n")
            _print_top_level_help(parser)

    # Help subcommand registration (after others so map is populated)
    # Help command (must be added before building command sections so it shows up)
    parser_help = subparsers.add_parser(
        "help",
        description="Print this message or get help for subcommand",
        help="Print this message or get help for subcommand",
        add_help=False,
    )
    parser_help.add_argument(
        "subcommand_name",
        nargs="?",
        help="Subcommand to show help for (identify, validate, convert, standards, version)",
    )
    parser_help.add_argument("-h", "--help", action=_RichSubHelpAction, nargs=0, help="Show this message and exit")
    parser_help.set_defaults(func=_help_handler)
    # Track help command for section population
    subparser_map["help"] = parser_help

    # Register metadata for global options (id-based registry to avoid mutating Action objects)
    _ACTION_METADATA[id(help_action)] = ("Global options:", 40)
    _ACTION_METADATA[id(version_action)] = ("Global options:", 40)
    _ACTION_METADATA[id(verbose_action)] = ("Log levels:", 20)
    _ACTION_METADATA[id(quiet_action)] = ("Log levels:", 20)
    _ACTION_METADATA[id(silent_action)] = ("Log levels:", 20)

    args = parser.parse_args()
    # print(vars(args))

    # Subcommand help via generic -h on parent (only when subcommand chosen and it's not 'help').
    if getattr(args, "help", False) and getattr(args, "subcommand", None) is not None:
        if args.subcommand == "help":
            # Emulate styled help for the help command itself
            _print_subcommand_help(parser.prog, "help", subparser_map["help"])  # type: ignore[index]
        else:
            _print_subcommand_help(parser.prog, args.subcommand, subparser_map[args.subcommand])  # type: ignore[index]
        return

    # Per-subcommand help flag (from subparser definitions)
    if getattr(args, "help_sub", False):  # type: ignore[attr-defined]
        _print_subcommand_help(parser.prog, args.subcommand, subparser_map[args.subcommand])  # type: ignore[index]
        return

    # Top-level help handling (matches Click styling)
    if getattr(args, "help", False) and getattr(args, "subcommand", None) is None:
        _print_top_level_help(parser)
        return

    # If no subcommand, print styled help instead of error
    if args.subcommand is None:
        _print_top_level_help(parser)
        return

    # (Legacy per-subcommand -h removed) show_help_sub no longer used.

    args.func(args)
