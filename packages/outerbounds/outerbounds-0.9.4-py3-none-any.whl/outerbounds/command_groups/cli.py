from outerbounds._vendor import click
from . import (
    local_setup_cli,
    workstations_cli,
    perimeters_cli,
    apps_cli,
    tutorials_cli,
    fast_bakery_cli,
    secrets_cli,
    kubernetes_cli,
    flowprojects_cli,
)


@click.command(
    cls=click.CommandCollection,
    sources=[
        local_setup_cli.cli,
        workstations_cli.cli,
        perimeters_cli.cli,
        apps_cli.cli,
        tutorials_cli.cli,
        fast_bakery_cli.cli,
        secrets_cli.cli,
        kubernetes_cli.cli,
        flowprojects_cli.cli,
    ],
)
def cli(**kwargs):
    pass
