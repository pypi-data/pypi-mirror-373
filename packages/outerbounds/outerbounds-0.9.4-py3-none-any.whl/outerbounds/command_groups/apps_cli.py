import os
from os import path
from outerbounds._vendor import click
import requests
import time
import random
import shutil
import subprocess

from ..utils import metaflowconfig
from ..apps import app_cli_group as app

APP_READY_POLL_TIMEOUT_SECONDS = 300
# Even after our backend validates that the app routes are ready, it takes a few seconds for
# the app to be accessible via the browser. Till we hunt down this delay, add an extra buffer.
APP_READY_EXTRA_BUFFER_SECONDS = 30


@click.group()
def cli(**kwargs):
    pass


@app.command(help="Start an app using a port and a name")
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
    "--port",
    required=True,
    help="Port number where you want to start your app",
    type=int,
)
@click.option(
    "--name",
    required=True,
    help="Name of your app",
    type=str,
)
def start(config_dir=None, profile=None, port=-1, name=""):
    if len(name) == 0 or len(name) >= 20:
        click.secho(
            "App name should not be more than 20 characters long.",
            fg="red",
            err=True,
        )
        return
    elif not name.isalnum() or not name.islower():
        click.secho(
            "App name can only contain lowercase alphanumeric characters.",
            fg="red",
            err=True,
        )
        return

    if "WORKSTATION_ID" not in os.environ:
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )
        return

    workstation_id = os.environ["WORKSTATION_ID"]

    try:
        try:
            metaflow_token = metaflowconfig.get_metaflow_token_from_config(
                config_dir, profile
            )
            api_url = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

            workstations_response = requests.get(
                f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
            )
            workstations_response.raise_for_status()
        except:
            click.secho("Failed to list workstations!", fg="red", err=True)
            return

        workstations_json = workstations_response.json()["workstations"]
        for workstation in workstations_json:
            if workstation["instance_id"] == os.environ["WORKSTATION_ID"]:
                if "named_ports" in workstation["spec"]:
                    try:
                        ensure_app_start_request_is_valid(
                            workstation["spec"]["named_ports"], port, name
                        )
                    except ValueError as e:
                        click.secho(str(e), fg="red", err=True)
                        return

                    for named_port in workstation["spec"]["named_ports"]:
                        if int(named_port["port"]) == port:
                            if named_port["enabled"] and named_port["name"] == name:
                                click.secho(
                                    f"App {name} already running on port {port}!",
                                    fg="green",
                                    err=True,
                                )
                                click.secho(
                                    f"Browser URL: {api_url.replace('api', 'ui')}/apps/{workstation_id}/{name}/",
                                    fg="green",
                                    err=True,
                                )
                                click.secho(
                                    f"App URL: {api_url}/apps/{workstation_id}/{name}/",
                                    fg="green",
                                    err=True,
                                )
                                return
                            else:
                                try:
                                    response = requests.put(
                                        f"{api_url}/v1/workstations/update/{workstation_id}/namedports",
                                        headers={"x-api-key": metaflow_token},
                                        json={
                                            "port": port,
                                            "name": name,
                                            "enabled": True,
                                        },
                                    )

                                    response.raise_for_status()
                                    poll_success = wait_for_app_port_to_be_accessible(
                                        api_url,
                                        metaflow_token,
                                        workstation_id,
                                        name,
                                        APP_READY_POLL_TIMEOUT_SECONDS,
                                    )
                                    if poll_success:
                                        click.secho(
                                            f"App {name} started on port {port}!",
                                            fg="green",
                                            err=True,
                                        )
                                        click.secho(
                                            f"Browser URL: {api_url.replace('api', 'ui')}/apps/{os.environ['WORKSTATION_ID']}/{name}/",
                                            fg="green",
                                            err=True,
                                        )
                                        click.secho(
                                            f"App URL: {api_url}/apps/{os.environ['WORKSTATION_ID']}/{name}/",
                                            fg="green",
                                            err=True,
                                        )
                                    else:
                                        click.secho(
                                            f"The app could not be deployed in {APP_READY_POLL_TIMEOUT_SECONDS / 60} minutes. Please try again later.",
                                            fg="red",
                                            err=True,
                                        )
                                        return
                                except Exception:
                                    click.secho(
                                        f"Failed to start app {name} on port {port}!",
                                        fg="red",
                                        err=True,
                                    )
                                return
    except Exception as e:
        click.secho(f"Failed to start app {name} on port {port}!", fg="red", err=True)


@app.command(help="Stop an app using its port number")
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
    "--port",
    required=False,
    default=-1,
    help="Port number where you want to start your app.",
    type=int,
)
@click.option(
    "--name",
    required=False,
    help="Name of your app",
    default="",
    type=str,
)
def stop(config_dir=None, profile=None, port=-1, name=""):
    if port == -1 and not name:
        click.secho(
            "Please provide either a port number or a name to stop the app.",
            fg="red",
            err=True,
        )
        return
    elif port > 0 and name:
        click.secho(
            "Please provide either a port number or a name to stop the app, not both.",
            fg="red",
            err=True,
        )
        return

    if "WORKSTATION_ID" not in os.environ:
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )

        return

    try:
        try:
            metaflow_token = metaflowconfig.get_metaflow_token_from_config(
                config_dir, profile
            )
            api_url = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

            workstations_response = requests.get(
                f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
            )
            workstations_response.raise_for_status()
        except:
            click.secho("Failed to list workstations!", fg="red", err=True)
            return

        app_found = False
        workstations_json = workstations_response.json()["workstations"]
        for workstation in workstations_json:
            if workstation["instance_id"] == os.environ["WORKSTATION_ID"]:
                if "named_ports" in workstation["spec"]:
                    for named_port in workstation["spec"]["named_ports"]:
                        if (
                            int(named_port["port"]) == port
                            or named_port["name"] == name
                        ):
                            app_found = True
                            if named_port["enabled"]:
                                try:
                                    response = requests.put(
                                        f"{api_url}/v1/workstations/update/{os.environ['WORKSTATION_ID']}/namedports",
                                        headers={"x-api-key": metaflow_token},
                                        json={
                                            "port": named_port["port"],
                                            "name": named_port["name"],
                                            "enabled": False,
                                        },
                                    )
                                    response.raise_for_status()
                                    click.secho(
                                        f"App {named_port['name']} stopped on port {named_port['port']}!",
                                        fg="green",
                                        err=True,
                                    )
                                except Exception as e:
                                    click.secho(
                                        f"Failed to stop app {named_port['name']} on port {named_port['port']}!",
                                        fg="red",
                                        err=True,
                                    )
                                return

        if app_found:
            already_stopped_message = (
                f"No deployed app named {name} found."
                if name
                else f"There is no app deployed on port {port}"
            )
            click.secho(
                already_stopped_message,
                fg="green",
                err=True,
            )
            return

        err_message = (
            (f"Port {port} not found on workstation {os.environ['WORKSTATION_ID']}")
            if port != -1
            else f"App {name} not found on workstation {os.environ['WORKSTATION_ID']}"
        )

        click.secho(
            err_message,
            fg="red",
            err=True,
        )
    except Exception as e:
        click.secho(f"Failed to stop app on port {port}!", fg="red", err=True)


@app.command(help="Kill the process associated with an app.")
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
    "--name",
    required=False,
    help="Name of your app",
    default="",
    type=str,
)
def kill_process(config_dir=None, profile=None, port=-1, name=""):
    if port > 0 and name:
        click.secho(
            "Please provide either a port number or a name to stop the app, not both.",
            fg="red",
            err=True,
        )
        return

    if "WORKSTATION_ID" not in os.environ:
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )

        return

    supervisorctl_exists = shutil.which("supervisorctl")
    if not supervisorctl_exists:
        click.secho(
            "This workstation does not support automated app deployment and management. Pleasr reach out to outerbounds support!",
            fg="red",
            err=True,
        )
        return

    supervisorctl_command = ["supervisorctl", "stop", name]

    # This is somewhat ugly way of doing this, but there aren't any better ways.
    # Since we use supervisorctl to manage our apps, we have to rely on external calls to
    # kill the process.
    result = subprocess.run(supervisorctl_command, capture_output=True, text=True)
    if result.returncode == 0:
        # It gets uglier.
        # When the process is not running, which is likely due to a user error, the output looks like:
        # myapp: ERROR (not running)
        # but the return code is still 0.
        # If the stop is successful, the output looks like:
        # myapp: stopped

        if result.stdout.startswith(f"{name}: ERROR (not running)"):
            click.secho(
                f"Process {name} is not in a running state to kill!",
                fg="yellow",
                err=True,
            )
            return
        elif result.stdout.startswith(f"{name}: stopped"):
            click.secho(f"Process {name} killed successfully!", fg="green", err=True)
            return
        else:
            click.secho(f"Process {name} stopped!", fg="red", err=True)
            return
    elif result.returncode == 1:
        # One of the cases where this can happen is if the app name itself is wrong.
        # In this case, the output looks like:
        # 'mya111pp: ERROR (no such process)\n'
        if result.stdout.startswith(f"{name}: ERROR (no such process)"):
            click.secho(f"Process {name} does not exist!", fg="red", err=True)
            return
        else:
            click.secho(f"Failed to kill process {name}!", fg="red", err=True)
            return


@app.command(help="List all apps on the workstation")
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
def list_local(config_dir=None, profile=None):
    if "WORKSTATION_ID" not in os.environ:
        click.secho(
            "All outerbounds app commands can only be run from a workstation.",
            fg="red",
            err=True,
        )

        return

    try:
        try:
            metaflow_token = metaflowconfig.get_metaflow_token_from_config(
                config_dir, profile
            )
            api_url = metaflowconfig.get_sanitized_url_from_config(
                config_dir, profile, "OBP_API_SERVER"
            )

            workstations_response = requests.get(
                f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
            )
            workstations_response.raise_for_status()
        except:
            click.secho("Failed to list workstations!", fg="red", err=True)
            return

        workstations_json = workstations_response.json()["workstations"]
        for workstation in workstations_json:
            if workstation["instance_id"] == os.environ["WORKSTATION_ID"]:
                if "named_ports" in workstation["spec"]:
                    for named_port in workstation["spec"]["named_ports"]:
                        if named_port["enabled"]:
                            click.secho(
                                f"App Name: {named_port['name']}", fg="green", err=True
                            )
                            click.secho(
                                f"App Port on Workstation: {named_port['port']}",
                                fg="green",
                                err=True,
                            )
                            click.secho(f"App Status: Deployed", fg="green", err=True)
                            click.secho(
                                f"App URL: {api_url.replace('api', 'ui')}/apps/{os.environ['WORKSTATION_ID']}/{named_port['name']}/",
                                fg="green",
                                err=True,
                            )
                        else:
                            click.secho(
                                f"App Port on Workstation: {named_port['port']}",
                                fg="yellow",
                                err=True,
                            )
                            click.secho(
                                f"App Status: Not Deployed", fg="yellow", err=True
                            )

                        click.echo("\n", err=True)
    except Exception as e:
        click.secho(f"Failed to list apps!", fg="red", err=True)


def ensure_app_start_request_is_valid(existing_named_ports, port: int, name: str):
    existing_apps_by_port = {np["port"]: np for np in existing_named_ports}

    if port not in existing_apps_by_port:
        raise ValueError(f"Port {port} not found on workstation")

    for existing_named_port in existing_named_ports:
        if (
            name == existing_named_port["name"]
            and existing_named_port["port"] != port
            and existing_named_port["enabled"]
        ):
            raise ValueError(
                f"App with name '{name}' is already deployed on port {existing_named_port['port']}"
            )


def wait_for_app_port_to_be_accessible(
    api_url, metaflow_token, workstation_id, app_name, poll_timeout_seconds
) -> bool:
    num_retries_per_request = 3
    start_time = time.time()
    retry_delay = 1.0
    poll_interval = 10
    wait_message = f"App {app_name} is currently being deployed..."
    while time.time() - start_time < poll_timeout_seconds:
        for _ in range(num_retries_per_request):
            try:
                workstations_response = requests.get(
                    f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
                )
                workstations_response.raise_for_status()
                if is_app_ready(workstations_response.json(), workstation_id, app_name):
                    click.secho(
                        wait_message,
                        fg="yellow",
                        err=True,
                    )
                    time.sleep(APP_READY_EXTRA_BUFFER_SECONDS)
                    return True
                else:
                    click.secho(
                        wait_message,
                        fg="yellow",
                        err=True,
                    )
                    time.sleep(poll_interval)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
            ):
                time.sleep(retry_delay)
                retry_delay *= 2  # Double the delay for the next attempt
                retry_delay += random.uniform(0, 1)  # Add jitter
                retry_delay = min(retry_delay, 10)
    return False


def is_app_ready(response_json: dict, workstation_id: str, app_name: str) -> bool:
    """Checks if the app is ready in the given workstation's response."""
    workstations = response_json.get("workstations", [])
    for workstation in workstations:
        if workstation.get("instance_id") == workstation_id:
            hosted_apps = workstation.get("status", {}).get("hosted_apps", [])
            for hosted_app in hosted_apps:
                if hosted_app.get("name") == app_name:
                    return bool(hosted_app.get("ready"))
    return False


cli.add_command(app, name="app")
