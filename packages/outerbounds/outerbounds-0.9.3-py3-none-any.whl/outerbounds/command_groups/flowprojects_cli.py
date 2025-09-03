import json
import os
import sys
import requests

from ..utils import metaflowconfig
from outerbounds._vendor import click


@click.group()
def cli(**kwargs):
    pass


@cli.group(help="Commands for pushing Deployments metadata.", hidden=True)
def flowproject(**kwargs):
    pass


@flowproject.command()
@click.option(
    "-d",
    "--config-dir",
    default=os.path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option("--id", help="The ID for this deployment")
def get_metadata(config_dir, profile, id):
    api_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_API_SERVER"
    )
    perimeter = _get_perimeter()
    headers = _get_request_headers()

    project, branch = _parse_id(id)

    # GET the latest flowproject config in order to modify it
    # /v1/perimeters/:perimeter/:project/:branch/flowprojects/latest
    response = requests.get(
        url=f"{api_url}/v1/perimeters/{perimeter}/projects/{project}/branches/{branch}/latestflowproject",
        headers=headers,
    )
    if response.status_code >= 500:
        raise Exception("API request failed.")

    body = response.json()
    if response.status_code >= 400:
        raise Exception("request failed: %s" % body)

    out = json.dumps(body)

    print(out, file=sys.stdout)


@flowproject.command()
@click.option(
    "-d",
    "--config-dir",
    default=os.path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.argument("json_str")
def set_metadata(config_dir, profile, json_str):
    api_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_API_SERVER"
    )

    perimeter = _get_perimeter()
    headers = _get_request_headers()
    payload = json.loads(json_str)

    # POST the updated flowproject config
    # /v1/perimeters/:perimeter/flowprojects
    response = requests.post(
        url=f"{api_url}/v1/perimeters/{perimeter}/flowprojects",
        json=payload,
        headers=headers,
    )
    if response.status_code >= 500:
        raise Exception("API request failed. %s" % response.text)

    if response.status_code >= 400:
        raise Exception("request failed: %s" % response.text)
    body = response.json()

    print(body, file=sys.stdout)


def _get_request_headers():
    headers = {"Content-Type": "application/json", "Connection": "keep-alive"}
    try:
        from metaflow.metaflow_config import SERVICE_HEADERS

        headers = {**headers, **(SERVICE_HEADERS or {})}
    except ImportError:
        headers = headers

    return headers


def _get_perimeter():
    # Get current perimeter
    from metaflow_extensions.outerbounds.remote_config import init_config  # type: ignore

    conf = init_config()
    if "OBP_PERIMETER" in conf:
        perimeter = conf["OBP_PERIMETER"]
    else:
        # if the perimeter is not in metaflow config, try to get it from the environment
        perimeter = os.environ.get("OBP_PERIMETER", None)
    if perimeter is None:
        raise Exception("Perimeter not found in config, but is required.")

    return perimeter


def _parse_id(id: str):
    parts = id.split("/")
    if len(parts) != 2:
        raise Exception("ID should consist of two parts: project/branch")

    project, branch = parts
    return project, branch
