"""CLI smoke tests for the ipxact argparse implementation.

These tests focus on exercising the public command line surface and the Rich
custom help action. They don't validate full business logic (which is covered
by existing XML / version tests) but ensure:

* Each primary subcommand is exposed.
* Subcommand help (-h/--help) renders without raising and contains expected
  headings/keywords.
* Top-level help renders with sections in the expected order.
* The version command prints the package version and (optionally) standards list.

The tests intentionally avoid deep behavioral assertions to remain resilient to
formatting tweaks; they look for stable anchor substrings only.
"""
import subprocess
import sys

import pytest

PYTHON = sys.executable


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    """Run the CLI in a subprocess returning completed result.

    Args:
        *args: Argument tokens (excluding the program name).

    Returns:
        CompletedProcess with stdout/stderr captured as text.
    """
    # Execute module by path to ensure we test the current checkout without install.
    # Run the CLI package as a module so its relative imports resolve.
    cmd = [PYTHON, "-m", "amal.eda.ipxact_de.cli", *args]
    # Rich outputs to stdout; capture both.
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


@pytest.mark.parametrize("subcmd", ["identify", "validate", "convert", "version"])
def test_subcommand_help_smoke(subcmd: str) -> None:
    """Each subcommand's -h prints help with usage line and exits cleanly."""
    proc = _run_cli(subcmd, "-h")
    assert proc.returncode == 0, f"Help for {subcmd} failed: {proc.stderr or proc.stdout}"
    out = proc.stdout
    # Anchor strings
    assert "Usage:" in out
    assert f"ipxact {subcmd}" in out
    # Per design subcommand help should not show raw argparse error messages.
    assert "error:" not in out.lower()


def test_top_level_help_sections_order() -> None:
    """Top-level help lists sections in the declared order.

    Order: Commands:, Log levels:, Global options:
    """
    proc = _run_cli("-h")
    assert proc.returncode == 0
    out = proc.stdout
    first = out.find("Commands:")
    second = out.find("Log levels:")
    third = out.find("Global options:")
    assert -1 not in {first, second, third}, out
    assert first < second < third, "Sections not in expected order"


def test_version_and_standards_commands() -> None:
    """`ipxact version` prints version; `ipxact standards` lists standards."""
    proc_v = _run_cli("version")
    assert proc_v.returncode == 0
    assert proc_v.stdout.strip().startswith("ipxact v"), proc_v.stdout
    proc_s = _run_cli("standards")
    assert proc_s.returncode == 0
    assert "Supported standards:" in proc_s.stdout


@pytest.mark.parametrize("flag", ["-v", "-q", "-s"])  # smoke test they don't crash with --help
def test_global_flags_coexist_with_help(flag: str) -> None:
    """Global flags combined with -h should still show help (parser not failing)."""
    proc = _run_cli(flag, "-h")
    assert proc.returncode == 0
    assert "Usage:" in proc.stdout


def test_convert_help_shows_to_version_choices() -> None:
    """Convert help lists the --to-version option choices."""
    proc = _run_cli("convert", "-h")
    assert proc.returncode == 0
    out = proc.stdout
    assert "--to-version" in out
    # Ensure at least one known schema appears as a choice anchor (spirit/1.0)
    assert "spirit/1.0" in out
