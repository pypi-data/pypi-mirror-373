"""Console script for pyvelocity."""

import click
from click import ClickException

from pyvelocity.checks.aggregation import Checks
from pyvelocity.checks.aggregation import Results
from pyvelocity.configurations.aggregation import Configurations
from pyvelocity.configurations.files.aggregation import ConfigurationFiles


def echo_success() -> None:
    """Echos success even if can't use emoji."""
    try:
        click.echo("Looks high velocity! ⚡️ 🚄 ✨")
    except UnicodeEncodeError:  # pragma: no cover
        # see:
        # - UnicodeEncodeError on Windows when there are Unicode chars in the help message
        #    · Issue #2121 · pallets/click
        #   https://github.com/pallets/click/issues/2121
        # - UnicodeEncodeError in Windows agent CI pipelines
        #   https://gist.github.com/NodeJSmith/e7e37f2d3f162456869f015f842bcf15
        click.echo("Looks high velocity!")


@click.command()
def main() -> None:
    """Console script for pyvelocity."""
    configuration_files = ConfigurationFiles()
    configurations = Configurations(configuration_files)
    results = Results(list(Checks(configuration_files, configurations).execute()))
    if results.message:
        click.echo(results.message)
    if not results.is_ok:
        exception = ClickException("Looks there are some of improvements.")
        exception.exit_code = 3
        raise exception
    echo_success()
