import json
import base64
import boto3
import requests

from os import path, environ
from sys import exit
from outerbounds._vendor import click

from ..utils import metaflowconfig


@click.group()
def cli(**kwargs):
    pass


@click.group(help="Commands for interacting with Fast Bakery.")
def fast_bakery(**kwargs):
    pass


def get_aws_token(config_dir: str, profile: str):
    metaflow_token = metaflowconfig.get_metaflow_token_from_config(config_dir, profile)
    auth_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_AUTH_SERVER"
    )

    aws_response = requests.get(
        f"{auth_url}//generate/aws",
        headers={"x-api-key": metaflow_token},
    )

    if aws_response.status_code != 200:
        click.secho(
            "Failed to retrieve AWS credentials. Fast-Bakery is currently only supported in AWS Deployments. Please reach out to your Outerbounds support team if you need additional assistance.",
            fg="red",
            err=True,
        )
        exit(1)

    return aws_response.json()


def check_valid_registry_url(registry_url: str, config_dir: str, profile: str):
    auth_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_AUTH_SERVER"
    )

    # Extract the domain parts after the first section
    registry_domain = registry_url.split(".", 1)[1] if "." in registry_url else ""
    auth_domain = auth_url.split(".", 1)[1] if "." in auth_url else ""

    if registry_url.startswith(("http://", "https://")):
        click.secho(
            f"Invalid Fast Bakery Registry URL: {registry_url}. URL should not start with http:// or https://",
            fg="red",
            err=True,
        )
        exit(1)

    if not registry_domain:
        click.secho(
            f"Invalid Fast Bakery Registry URL: {registry_url}",
            fg="red",
            err=True,
        )
        exit(1)

    if registry_domain != auth_domain:
        click.secho(
            f"Invalid Fast Bakery Domain: {registry_domain}",
            fg="red",
            err=True,
        )
        exit(1)

    return True


def get_docker_auth_data(auth_token_response: dict):
    role_arn = auth_token_response.get("role_arn")
    token = auth_token_response.get("token")
    region = auth_token_response.get("region")

    sts_client = boto3.client("sts", region_name=region)
    response = sts_client.assume_role_with_web_identity(
        RoleArn=role_arn,
        RoleSessionName="FastBakerySession",
        WebIdentityToken=token,
        DurationSeconds=3600,
    )
    credentials = response["Credentials"]
    auth_data = {
        "AccessKeyId": credentials["AccessKeyId"],
        "SecretAccessKey": credentials["SecretAccessKey"],
        "SessionToken": credentials["SessionToken"],
        "Expiration": credentials["Expiration"].isoformat() + "Z",
        "Version": 1,
    }
    return auth_data


@fast_bakery.command(
    help="""
Get a docker login password for Fast Bakery. Example usage:
outerbounds fast-bakery get-login-password | docker login --username fastreg --password-stdin <fast-bakery-registry-url>

Note: The username must be set to 'fastreg'.
"""
)
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
def get_login_password(config_dir=None, profile=None):
    auth_token_response = get_aws_token(config_dir, profile)
    auth_data = get_docker_auth_data(auth_token_response)
    auth_base64 = base64.b64encode(json.dumps(auth_data).encode("utf-8")).decode(
        "utf-8"
    )
    # Output the password
    click.echo(auth_base64)


@fast_bakery.command(
    help="""
Configure docker login credentials for Fast Bakery. Example usage:
outerbounds fast-bakery configure-docker-login
"""
)
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "--registry-url",
    help="The fast-bakery registry url you would like to configured docker auth for",
)
@click.option(
    "--output",
    help="The output file you would like to save the docker config to. Defaults to $HOME/.docker/config.json",
)
def configure_docker_login(registry_url, output, config_dir=None, profile=None):
    if registry_url is None:
        click.secho(
            "Missing a required argument: --registry-url <fast-bakery-registry-url>",
            fg="red",
            err=True,
        )
        return

    check_valid_registry_url(registry_url, config_dir, profile)
    auth_token_response = get_aws_token(config_dir, profile)
    auth_data = get_docker_auth_data(auth_token_response)
    auth_json = json.dumps(auth_data, separators=(",", ":"))
    docker_config = {
        # "auth": base64.b64encode(
        #     f"fastreg:{base64.b64encode(auth_json.encode()).decode()}".encode()
        # ).decode(),
        "username": "fastreg",  # This is currently hardcoded in the Fast Bakery Registry implementation.
        "password": base64.b64encode(auth_json.encode()).decode(),
    }

    if output is None:
        home = path.expanduser("~")
        output = path.join(home, ".docker", "config.json")

    existing_docker_config = {"auths": {}}
    if path.exists(output):
        with open(output, "r") as f:
            existing_docker_config = json.load(f)

        if "auths" not in existing_docker_config:
            existing_docker_config["auths"] = {}

    existing_docker_config["auths"][registry_url] = docker_config
    with open(output, "w") as f:
        json.dump(existing_docker_config, f, indent=4)

    click.secho(f"Docker config saved to {output}", fg="green", err=True)


cli.add_command(fast_bakery, name="fast-bakery")
