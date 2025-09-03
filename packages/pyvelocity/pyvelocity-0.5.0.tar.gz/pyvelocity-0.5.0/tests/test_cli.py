"""Tests for `pyvelocity` package."""

# Reason: Accept risk of using subprocess.
from subprocess import CalledProcessError  # nosec B404
from subprocess import run  # nosec B404

import pytest
from click.testing import CliRunner

from pyvelocity import cli


def test_echo_success() -> None:
    cli.echo_success()


def test_echo_success_in_subprocess() -> None:
    """Function echo_success() should fallback to no emoji.

    When echo emoji in subprocess on Windows, Following error raised:
      UnicodeEncodeError: 'charmap' codec can't encode characters in position 21-22
    Pyvelocity may be used in CI and it may be used in subprocess.
    see:
    - UnicodeEncodeError on Windows when there are Unicode chars in the help message
       · Issue #2121 · pallets/click
      https://github.com/pallets/click/issues/2121
    - UnicodeEncodeError in Windows agent CI pipelines
      https://gist.github.com/NodeJSmith/e7e37f2d3f162456869f015f842bcf15
    """
    # Reason: Accept risk of using subprocess.
    try:
        completed_process = run(  # nosec B603 B607
            "pyvelocity",  # noqa: S607
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except CalledProcessError as exc:
        pytest.fail(
            f"Command: {exc.cmd} failed with exit code ({exc.returncode}): {exc.output}{exc.stderr}",
        )
    expected = ["Looks high velocity! ⚡️ 🚄 ✨\n", "Looks high velocity!\n"]
    assert completed_process.stdout in expected


@pytest.mark.parametrize(
    ("files", "expect_exit_code", "expect_message"),
    [
        (["pyproject_success.toml", "setup_success.cfg"], 0, "Looks high velocity! ⚡️ 🚄 ✨\n"),
        (
            ["pyproject_error.toml", "setup_error.cfg"],
            3,
            (
                "Line length are not consistent.\n"
                "\tMost common = 119\n"
                "\tpyproject.toml tool.docformatter wrap-summaries = 118\n"
                "\tsetup.cfg flake8 max-line-length = 118 (B950 in flake8-bugbear detects: 130)\n"
                "\tpyproject.toml tool.ruff line-length = 118\n"
                "Python version classifiers don't match requires-python '>=3.5': missing classifiers: "
                "Programming Language :: Python :: 3.10, "
                "Programming Language :: Python :: 3.11, "
                "Programming Language :: Python :: 3.12, "
                "Programming Language :: Python :: 3.13\n"
                "Error: Looks there are some of improvements.\n"
            ),
        ),
    ],
)
def test_command_line_interface(configured_cli_runner: CliRunner, expect_exit_code: int, expect_message: str) -> None:
    """Test the CLI."""
    result = configured_cli_runner.invoke(cli.main)
    assert result.exit_code == expect_exit_code
    assert result.output == expect_message


def test_help() -> None:
    runner = CliRunner()
    help_result = runner.invoke(cli.main, ["--help"])
    assert help_result.exit_code == 0
    assert "--help  Show this message and exit." in help_result.output
