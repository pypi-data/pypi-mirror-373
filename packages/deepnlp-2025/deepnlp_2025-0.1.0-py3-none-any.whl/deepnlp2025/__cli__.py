"""Command line interface for deepnlp2025"""

# Importing the libraries

import os
import webbrowser
from typing import Union

import click
import yaml

from deepnlp2025._version import __version__

__package_path__ = os.path.abspath(os.path.dirname(__file__))
__package_name__ = os.path.basename(__package_path__)


def load_about() -> dict[str, Union[str, int, bool, None]]:
    """
    Load the about.yml file.
    """

    about_path = os.path.join(__package_path__, f"conf/about/{__package_name__}.yaml")
    if not os.path.isfile(about_path):
        click.echo(f"The `{about_path}` was not found.")
        raise click.Abort()
    with open(about_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


__about__ = load_about()


@click.command()
@click.version_option(__version__)
def main() -> None:
    """
    This is the cli function of the package.
    It opens the book in the browser.
    """
    open_book()


def open_book() -> None:
    """
    Open the book in the browser.
    """
    click.echo("Opening the book...")
    homepage = __about__.get("homepage", "")
    if isinstance(homepage, str):
        webbrowser.open_new_tab(homepage)
    else:
        click.echo("Homepage URL not found in configuration.")


# main function for the main module
if __name__ == "__main__":
    main()
