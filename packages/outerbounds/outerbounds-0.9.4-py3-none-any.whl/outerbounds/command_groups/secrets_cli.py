import json
import os
from os import path
from typing import Any, Dict
from outerbounds._vendor import click
from collections import OrderedDict
from ..utils.utils import safe_write_to_disk


def _get_ob_provider():
    from metaflow.plugins import SECRETS_PROVIDERS

    ob_provider = [i for i in SECRETS_PROVIDERS if i.TYPE == "outerbounds"][0]
    return ob_provider()


class SecretOutput:
    def __init__(self, type):
        self.type = type
        self._secrets = OrderedDict()

    def consume(self, secret_id, secret_dict):
        self._secrets[secret_id] = secret_dict

    def parse(self):
        if self.type == "text":
            return "\n".join(
                [
                    f"{k}={v}"
                    for _, secret in self._secrets.items()
                    for k, v in secret.items()
                ]
            )
        elif self.type == "json":
            return json.dumps(self._secrets)


@click.group()
def cli(**kwargs):
    pass


@click.group(help="Manage secrets")
def secrets(**kwargs):
    pass


FORMAT_HELP = """
Format of the output. When you specify:
    - `text`: The output will be in `key=value` format. Each key-value pair in each secret will in a new line.
    - `json`: The output will be in JSON format. The secrets will be in a dictionary with the structure `{<secret-id>: {<key>: <value>, ...}, ...}`.
"""


@secrets.command(
    help="Get secrets. The `secret_ids` correspond to the name of the integrations configured on the Outerbounds platform."
)
# command should be like :
# `outerbounds secrets get <secret-id-0> <secret-id-1> ... --output [text|json] --config-dir <config-dir> --profile <profile> --role <role> --output-file <output-file>`
@click.argument("secret_ids", type=str, nargs=-1)
@click.option(
    "--format",
    type=click.Choice(["text", "json", "shell"]),
    default="text",
    help=FORMAT_HELP,
)
@click.option(
    "--profile",
    type=str,
    default=None,
    help="The named metaflow profile to use.",
)
@click.option(
    "--role",
    type=str,
    default=None,
    help="Any additional IAM role required to access the secrets.",
)
@click.option(
    "--file",
    "-f",
    "output_file",
    type=str,
    default=None,
    help="The file to write the output to. If not specified, the output will be printed to standard out.",
)
def get(
    secret_ids,
    format,
    profile,
    role,
    output_file,
):

    if profile != "" and profile is not None:
        os.environ["METAFLOW_PROFILE"] = profile

    provider = _get_ob_provider()
    output = SecretOutput(format)
    for secret_id in secret_ids:
        secret = provider.get_secret_as_dict(secret_id, role=role)
        output.consume(secret_id, secret)
    output_str = output.parse()
    if output_file:
        output_file = os.path.abspath(output_file)
        safe_write_to_disk(output_file, output_str)
    else:
        print(output_str)


cli.add_command(secrets, name="secrets")
