import json
import os
import sys
from io import StringIO
from os import path
from typing import Any, Dict
from outerbounds._vendor import click
import requests
import configparser

from ..utils import metaflowconfig
from ..utils.utils import safe_write_to_disk
from ..utils.schema import (
    CommandStatus,
    OuterboundsCommandResponse,
    OuterboundsCommandStatus,
)

from .local_setup_cli import PERIMETER_CONFIG_URL_KEY


@click.group()
def cli(**kwargs):
    pass


@click.group(help="Manage perimeters")
def perimeter(**kwargs):
    pass


@perimeter.command(help="Switch current perimeter")
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
@click.option("--id", default="", type=str, help="Perimeter name to switch to")
@click.option(
    "-f",
    "--force",
    is_flag=True,
    help="Force change the existing perimeter",
    default=False,
)
def switch(config_dir=None, profile=None, output="", id=None, force=False):
    switch_perimeter_response = OuterboundsCommandResponse()

    switch_perimeter_step = CommandStatus(
        "SwitchPerimeter",
        OuterboundsCommandStatus.OK,
        "Perimeter was successfully switched!",
    )

    perimeters = get_perimeters_from_api_or_fail_command(
        config_dir, profile, output, switch_perimeter_response, switch_perimeter_step
    )
    confirm_user_has_access_to_perimeter_or_fail(
        id, perimeters, output, switch_perimeter_response, switch_perimeter_step
    )

    path_to_config = metaflowconfig.get_ob_config_file_path(config_dir, profile)

    import fcntl

    try:
        if os.path.exists(path_to_config):
            if not force:
                fd = os.open(path_to_config, os.O_WRONLY)
                # Try to acquire an exclusive lock
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            else:
                click.secho(
                    "Force flag is set. Perimeter will be switched, but can have unintended consequences on other running processes.",
                    fg="yellow",
                    err=True,
                )

        ob_config_dict = {
            "OB_CURRENT_PERIMETER": str(id),
            PERIMETER_CONFIG_URL_KEY: perimeters[id]["remote_config_url"],
        }

        # Now that we have the lock, we can safely write to the file
        with open(path_to_config, "w") as file:
            json.dump(ob_config_dict, file, indent=4)

        click.secho("Perimeter switched to {}".format(id), fg="green", err=True)
    except BlockingIOError:
        # This exception is raised if the file is already locked (non-blocking mode)
        # Note that its the metaflow package (the extension actually) that acquires a shared read lock
        # on the file whenever a process imports metaflow.
        # In the future we might want to get smarter about it and show which process is holding the lock.
        click.secho(
            "Can't switch perimeter while Metaflow is in use. Please make sure there are no running python processes or notebooks using metaflow.",
            fg="red",
            err=True,
        )
        switch_perimeter_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason="Can't switch perimeter while Metaflow is in use.",
            mitigation="Please make sure there are no running python processes or notebooks using metaflow.",
        )

    switch_perimeter_response.add_step(switch_perimeter_step)

    ensure_cloud_creds_step = CommandStatus(
        "EnsureCloudCredentials",
        OuterboundsCommandStatus.OK,
        "Cloud credentials were successfully updated.",
    )

    try:
        ensure_cloud_credentials_for_shell(config_dir, profile, "")
    except:
        click.secho(
            "Failed to update cloud credentials.",
            fg="red",
            err=True,
        )
        ensure_cloud_creds_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason="Failed to update cloud credentials.",
            mitigation="",
        )

    switch_perimeter_response.add_step(ensure_cloud_creds_step)

    if output == "json":
        click.echo(json.dumps(switch_perimeter_response.as_dict(), indent=4))


@perimeter.command(help="Show current perimeter")
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="Configure a named profile. Activate the profile by setting "
    "`METAFLOW_PROFILE` environment variable.",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def show_current(config_dir=None, profile=None, output=""):
    show_current_perimeter_response = OuterboundsCommandResponse()

    show_current_perimeter_step = CommandStatus(
        "ShowCurrentPerimeter",
        OuterboundsCommandStatus.OK,
        "Current Perimeter Fetch Successful.",
    )

    ob_config_dict = get_ob_config_or_fail_command(
        config_dir,
        profile,
        output,
        show_current_perimeter_response,
        show_current_perimeter_step,
    )

    perimeters = get_perimeters_from_api_or_fail_command(
        config_dir,
        profile,
        output,
        show_current_perimeter_response,
        show_current_perimeter_step,
    )
    confirm_user_has_access_to_perimeter_or_fail(
        ob_config_dict["OB_CURRENT_PERIMETER"],
        perimeters,
        output,
        show_current_perimeter_response,
        show_current_perimeter_step,
    )

    click.secho(
        "Current Perimeter: {}".format(ob_config_dict["OB_CURRENT_PERIMETER"]),
        fg="green",
        err=True,
    )

    show_current_perimeter_response.add_or_update_data(
        "current_perimeter", ob_config_dict["OB_CURRENT_PERIMETER"]
    )

    if output == "json":
        click.echo(json.dumps(show_current_perimeter_response.as_dict(), indent=4))


@perimeter.command(help="List all available perimeters")
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def list(config_dir=None, profile=None, output=""):
    list_perimeters_response = OuterboundsCommandResponse()

    list_perimeters_step = CommandStatus(
        "ListPerimeters", OuterboundsCommandStatus.OK, "Perimeter Fetch Successful."
    )

    if "WORKSTATION_ID" in os.environ and (
        "OBP_DEFAULT_PERIMETER" not in os.environ
        or "OBP_DEFAULT_PERIMETER_URL" not in os.environ
    ):
        list_perimeters_response.update(
            OuterboundsCommandStatus.NOT_SUPPORTED,
            500,
            "Perimeters are not supported on old workstations.",
        )
        click.secho(
            "Perimeters are not supported on old workstations.", err=True, fg="red"
        )
        if output == "json":
            click.echo(json.dumps(list_perimeters_response.as_dict(), indent=4))
        return

    ob_config_dict = get_ob_config_or_fail_command(
        config_dir, profile, output, list_perimeters_response, list_perimeters_step
    )
    active_perimeter = ob_config_dict["OB_CURRENT_PERIMETER"]

    perimeters = get_perimeters_from_api_or_fail_command(
        config_dir, profile, output, list_perimeters_response, list_perimeters_step
    )

    perimeter_list = []
    for perimeter in perimeters.values():
        status = "OK"
        perimeter_list.append(
            {
                "id": perimeter["perimeter"],
                "active": perimeter["perimeter"] == active_perimeter,
                "status": status,
            }
        )
        if perimeter["perimeter"] != active_perimeter:
            click.secho("Perimeter: {}".format(perimeter["perimeter"]), err=True)
        else:
            click.secho(
                "Perimeter: {} (active)".format(perimeter["perimeter"]),
                fg="green",
                err=True,
            )

    list_perimeters_response.add_or_update_data("perimeters", perimeter_list)

    if output == "json":
        click.echo(json.dumps(list_perimeters_response.as_dict(), indent=4))


@perimeter.command(
    help="Ensure credentials for cloud are synced with perimeter", hidden=True
)
@click.option(
    "-d",
    "--config-dir",
    default=path.expanduser(os.environ.get("METAFLOW_HOME", "~/.metaflowconfig")),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-p",
    "--profile",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
@click.option(
    "-c",
    "--cspr-override",
    default="",
    help="Override the CSPR role ARN to use for AWS credentials.",
)
def ensure_cloud_creds(config_dir=None, profile=None, output="", cspr_override=""):
    ensure_cloud_creds_step = CommandStatus(
        "EnsureCloudCredentials",
        OuterboundsCommandStatus.OK,
        "Cloud credentials were successfully updated.",
    )

    ensure_cloud_creds_response = OuterboundsCommandResponse()

    try:
        ensure_cloud_credentials_for_shell(config_dir, profile, cspr_override)
        click.secho("Cloud credentials updated successfully.", fg="green", err=True)
    except:
        click.secho(
            "Failed to update cloud credentials.",
            fg="red",
            err=True,
        )
        ensure_cloud_creds_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason="Failed to update cloud credentials.",
            mitigation="",
        )

    ensure_cloud_creds_response.add_step(ensure_cloud_creds_step)
    if output == "json":
        click.echo(json.dumps(ensure_cloud_creds_response.as_dict(), indent=4))


def get_list_perimeters_api_response(config_dir, profile):
    metaflow_token = metaflowconfig.get_metaflow_token_from_config(config_dir, profile)
    api_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_API_SERVER"
    )
    perimeters_response = requests.get(
        f"{api_url}/v1/me/perimeters?privilege=Execute",
        headers={"x-api-key": metaflow_token},
    )
    perimeters_response.raise_for_status()
    return perimeters_response.json()["perimeters"]


def get_perimeters_from_api_or_fail_command(
    config_dir: str,
    profile: str,
    output: str,
    command_response: OuterboundsCommandResponse,
    command_step: CommandStatus,
) -> Dict[str, Dict[str, str]]:
    try:
        perimeters = get_list_perimeters_api_response(config_dir, profile)
    except:
        click.secho(
            "Failed to fetch perimeters from API.",
            fg="red",
            err=True,
        )
        command_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason="Failed to fetch perimeters from API",
            mitigation="",
        )
        command_response.add_step(command_step)
        if output == "json":
            click.echo(json.dumps(command_response.as_dict(), indent=4))
        sys.exit(1)
    return {p["perimeter"]: p for p in perimeters}


def get_ob_config_or_fail_command(
    config_dir: str,
    profile: str,
    output: str,
    command_response: OuterboundsCommandResponse,
    command_step: CommandStatus,
) -> Dict[str, str]:
    path_to_config = metaflowconfig.get_ob_config_file_path(config_dir, profile)

    if not os.path.exists(path_to_config):
        click.secho(
            "Config file not found at {}".format(path_to_config), fg="red", err=True
        )
        command_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason="Config file not found",
            mitigation="Please make sure the config file exists at {}".format(
                path_to_config
            ),
        )
        command_response.add_step(command_step)
        if output == "json":
            click.echo(json.dumps(command_response.as_dict(), indent=4))
        sys.exit(1)

    with open(path_to_config, "r") as file:
        ob_config_dict = json.load(file)

    if "OB_CURRENT_PERIMETER" not in ob_config_dict:
        click.secho(
            "OB_CURRENT_PERIMETER not found in Config file: {}".format(path_to_config),
            fg="red",
            err=True,
        )
        command_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason="OB_CURRENT_PERIMETER not found in Config file: {}",
            mitigation="",
        )
        command_response.add_step(command_step)
        if output == "json":
            click.echo(json.dumps(command_response.as_dict(), indent=4))
        sys.exit(1)

    return ob_config_dict


def ensure_cloud_credentials_for_shell(config_dir, profile, cspr_override):
    if "WORKSTATION_ID" not in os.environ:
        # Naive check to see if we're running in workstation. No need to ensure anything
        # if this is not a workstation.
        return

    mf_config = metaflowconfig.init_config(config_dir, profile)

    # Currently we only support GCP. TODO: utkarsh to add support for AWS and Azure
    if "METAFLOW_DEFAULT_GCP_CLIENT_PROVIDER" in mf_config:
        # This is a GCP deployment.
        ensure_gcp_cloud_creds(config_dir, profile)
    elif "METAFLOW_DEFAULT_AWS_CLIENT_PROVIDER" in mf_config:
        # This is an AWS deployment.
        ensure_aws_cloud_creds(config_dir, profile, cspr_override)


def confirm_user_has_access_to_perimeter_or_fail(
    perimeter_id: str,
    perimeters: Dict[str, Any],
    output: str,
    command_response: OuterboundsCommandResponse,
    command_step: CommandStatus,
):
    if perimeter_id not in perimeters:
        click.secho(
            f"You do not have access to perimeter {perimeter_id} or it does not exist.",
            fg="red",
            err=True,
        )
        command_step.update(
            status=OuterboundsCommandStatus.FAIL,
            reason=f"You do not have access to perimeter {perimeter_id} or it does not exist.",
            mitigation="",
        )
        command_response.add_step(command_step)
        if output == "json":
            click.echo(json.dumps(command_response.as_dict(), indent=4))
        sys.exit(1)


def ensure_gcp_cloud_creds(config_dir, profile):
    token_info = get_gcp_auth_credentials(config_dir, profile)
    auth_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_AUTH_SERVER"
    )
    metaflow_token = metaflowconfig.get_metaflow_token_from_config(config_dir, profile)

    try:
        # GOOGLE_APPLICATION_CREDENTIALS is a well known gcloud environment variable
        credentials_file_loc = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    except KeyError:
        # This is most likely an old workstation when these params weren't set. Do nothing.
        # Alternatively, user might have deliberately unset it to use their own auth.
        return

    credentials_json = {
        "type": "external_account",
        "audience": f"//iam.googleapis.com/projects/{token_info['gcpProjectNumber']}/locations/global/workloadIdentityPools/{token_info['gcpWorkloadIdentityPool']}/providers/{token_info['gcpWorkloadIdentityPoolProvider']}",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "token_url": "https://sts.googleapis.com/v1/token",
        "service_account_impersonation_url": f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{token_info['gcpServiceAccountEmail']}:generateAccessToken",
        "credential_source": {
            "url": f"{auth_url}/generate/gcp",
            "headers": {"x-api-key": metaflow_token},
            "format": {"type": "json", "subject_token_field_name": "token"},
        },
    }

    safe_write_to_disk(credentials_file_loc, json.dumps(credentials_json))


def ensure_aws_cloud_creds(config_dir, profile, cspr_override):
    token_info = get_aws_auth_credentials(config_dir, profile)

    try:
        token_file_loc = os.environ["OBP_AWS_WEB_IDENTITY_TOKEN_FILE"]

        # AWS_CONFIG_FILE is a well known aws cli environment variable
        config_file_loc = os.environ["AWS_CONFIG_FILE"]
    except KeyError:
        # This is most likely an old workstation when these params weren't set. Do nothing.
        # Alternatively, user might have deliberately unset it to use their own auth.
        return

    aws_config = configparser.ConfigParser()
    aws_config.read(config_file_loc)

    aws_config["profile task"] = {
        "role_arn": token_info["role_arn"],
        "web_identity_token_file": token_file_loc,
    }

    if token_info.get("cspr_role_arn") or cspr_override:
        # If CSPR role is present, then we need to use the task role (in the task profile)
        # to assume the CSPR role.
        aws_config["profile outerbounds"] = {
            "role_arn": cspr_override or token_info["cspr_role_arn"],
            "source_profile": "task",
        }
    else:
        # If no CSPR role is present, just use the task profile as the outerbounds profile.
        aws_config["profile outerbounds"] = aws_config["profile task"]

    aws_config_string = StringIO()
    aws_config.write(aws_config_string)

    safe_write_to_disk(token_file_loc, token_info["token"])
    safe_write_to_disk(config_file_loc, aws_config_string.getvalue())


def get_aws_auth_credentials(config_dir, profile):  # pragma: no cover
    token = metaflowconfig.get_metaflow_token_from_config(config_dir, profile)
    auth_server_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_AUTH_SERVER"
    )

    response = requests.get(
        "{}/generate/aws".format(auth_server_url), headers={"x-api-key": token}
    )
    response.raise_for_status()

    return response.json()


def get_gcp_auth_credentials(config_dir, profile):
    token = metaflowconfig.get_metaflow_token_from_config(config_dir, profile)
    auth_server_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_AUTH_SERVER"
    )

    response = requests.get(
        "{}/generate/gcp".format(auth_server_url), headers={"x-api-key": token}
    )
    response.raise_for_status()

    return response.json()


cli.add_command(perimeter, name="perimeter")
