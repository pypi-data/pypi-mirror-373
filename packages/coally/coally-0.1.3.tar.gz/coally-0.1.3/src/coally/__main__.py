"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Coally."""


if __name__ == "__main__":
    main(prog_name="coally")  # pragma: no cover
