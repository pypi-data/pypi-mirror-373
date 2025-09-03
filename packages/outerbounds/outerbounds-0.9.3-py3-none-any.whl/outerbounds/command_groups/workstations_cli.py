from outerbounds._vendor import click
from outerbounds._vendor import yaml
import requests
import base64
import datetime
import hashlib
import json
import os
from os import path
from pathlib import Path
from ..utils import kubeconfig, metaflowconfig, ssh_utils
from ..utils.kubectl_utils import exec_in_pod, cp_to_pod
from requests.exceptions import HTTPError
import platform
import subprocess
from subprocess import CalledProcessError
from ..utils.schema import (
    OuterboundsCommandResponse,
    CommandStatus,
    OuterboundsCommandStatus,
)
from tempfile import NamedTemporaryFile
from .perimeters_cli import (
    get_perimeters_from_api_or_fail_command,
    confirm_user_has_access_to_perimeter_or_fail,
)
import sys

KUBECTL_INSTALL_MITIGATION = "Please install kubectl manually from https://kubernetes.io/docs/tasks/tools/#kubectl"


@click.group()
def cli(**kwargs):
    pass


@cli.command(help="Generate a token to use your cloud workstation", hidden=True)
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
    default="",
    help="The named metaflow profile in which your workstation exists",
)
def generate_workstation_token(config_dir=None, profile=None):
    try:
        metaflow_token = metaflowconfig.get_metaflow_token_from_config(
            config_dir, profile
        )
        auth_url = metaflowconfig.get_sanitized_url_from_config(
            config_dir, profile, "OBP_AUTH_SERVER"
        )
        k8s_response = requests.get(
            f"{auth_url}/generate/k8s", headers={"x-api-key": metaflow_token}
        )
        try:
            k8s_response.raise_for_status()
            k8s_response_json = k8s_response.json()
            token = k8s_response_json["token"]
            token_data = base64.b64decode(token.split(".")[1] + "==")
            exec_creds = {
                "kind": "ExecCredential",
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "spec": {},
                "status": {
                    "token": token,
                    "expirationTimestamp": datetime.datetime.fromtimestamp(
                        json.loads(token_data)["exp"], datetime.timezone.utc
                    ).isoformat(),
                },
            }
            click.echo(json.dumps(exec_creds))
        except HTTPError:
            click.secho("Failed to generate workstation token.", fg="red")
            click.secho("Error: {}".format(json.dumps(k8s_response.json(), indent=4)))
    except Exception as e:
        click.secho("Failed to generate workstation token.", fg="red")
        click.secho("Error: {}".format(str(e)))


@cli.command(help="Configure a cloud workstation", hidden=True)
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
    "-b",
    "--binary",
    default="outerbounds",
    help="Path to the location of your outerbounds binary",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def configure_cloud_workstation(config_dir=None, profile=None, binary=None, output=""):
    configure_response = OuterboundsCommandResponse()
    kubeconfig_configure_step = CommandStatus(
        "ConfigureKubeConfig", OuterboundsCommandStatus.OK, "Kubeconfig is configured"
    )
    try:
        metaflow_token = metaflowconfig.get_metaflow_token_from_config(
            config_dir, profile
        )
        auth_url = metaflowconfig.get_sanitized_url_from_config(
            config_dir, profile, "OBP_AUTH_SERVER"
        )
        k8s_response = requests.get(
            f"{auth_url}/generate/k8s", headers={"x-api-key": metaflow_token}
        )

        try:
            k8s_response.raise_for_status()
            k8s_response_json = k8s_response.json()
            token_data = base64.b64decode(
                k8s_response_json["token"].split(".")[1] + "=="
            )
            ws_namespace = "ws-{}".format(
                hashlib.md5(
                    bytes(json.loads(token_data)["username"], "utf-8")
                ).hexdigest()
            )

            kubeconfig.set_context(
                "outerbounds-workstations",
                "outerbounds-cluster",
                ws_namespace,
                "obp-user",
            )
            kubeconfig.set_cluster(
                "outerbounds-cluster", k8s_response_json["endpoint"], True
            )
            kubeconfig.add_user_with_exec_credential(
                "obp-user", binary, config_dir, profile
            )
            if output == "json":
                configure_response.add_step(kubeconfig_configure_step)
                click.echo(json.dumps(configure_response.as_dict(), indent=4))
        except HTTPError:
            click.secho("Failed to configure cloud workstation", fg="red", err=True)
            click.secho(
                "Error: {}".format(json.dumps(k8s_response.json(), indent=4)), err=True
            )
            if output == "json":
                kubeconfig_configure_step.update(
                    OuterboundsCommandStatus.FAIL,
                    json.dumps(k8s_response.json(), indent=4),
                    "",
                )
                configure_response.add_step(kubeconfig_configure_step)
                click.echo(json.dumps(configure_response.as_dict(), indent=4))
        except kubeconfig.KubeconfigError as ke:
            click.secho("Failed to configure cloud workstation", fg="red", err=True)
            click.secho("Error: {}".format(str(ke)), err=True)
            if output == "json":
                kubeconfig_configure_step.update(
                    OuterboundsCommandStatus.FAIL, str(ke), ""
                )
                configure_response.add_step(kubeconfig_configure_step)
                click.echo(json.dumps(configure_response.as_dict(), indent=4))
    except Exception as e:
        click.secho("Failed to configure cloud workstation", fg="red", err=True)
        click.secho("Error: {}".format(str(e)), err=True)
        if output == "json":
            kubeconfig_configure_step.update(OuterboundsCommandStatus.FAIL, str(e), "")
            configure_response.add_step(kubeconfig_configure_step)
            click.echo(json.dumps(configure_response.as_dict(), indent=4))


@cli.command(help="List all existing workstations", hidden=True)
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
    default="json",
    help="Show output in the specified format.",
    type=click.Choice(["json"]),
)
def list_workstations(config_dir=None, profile=None, output="json"):
    list_response = OuterboundsCommandResponse()
    list_step = CommandStatus(
        "listWorkstations",
        OuterboundsCommandStatus.OK,
        "Workstation list successfully fetched!",
    )
    list_response.add_or_update_data("workstations", [])

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
        list_response.add_or_update_data(
            "workstations", workstations_response.json()["workstations"]
        )
        if output == "json":
            click.echo(json.dumps(list_response.as_dict(), indent=4))
    except Exception as e:
        list_step.update(
            OuterboundsCommandStatus.FAIL, "Failed to list workstations", ""
        )
        list_response.add_step(list_step)
        if output == "json":
            list_response.add_or_update_data("error", str(e))
            click.echo(json.dumps(list_response.as_dict(), indent=4))
        else:
            click.secho("Failed to list workstations", fg="red", err=True)
            click.secho("Error: {}".format(str(e)), fg="red", err=True)


@cli.command(help="Hibernate workstation", hidden=True)
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
    default="",
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "-w",
    "--workstation",
    default=os.environ.get("METAFLOW_PROFILE", ""),
    help="The ID of the workstation to hibernate",
)
def hibernate_workstation(config_dir=None, profile=None, workstation=None):
    if workstation is None or workstation == "":
        click.secho("Please specify a workstation ID", fg="red")
        return
    try:
        if not profile:
            profile = metaflowconfig.get_metaflow_profile()
        metaflow_token = metaflowconfig.get_metaflow_token_from_config(
            config_dir, profile
        )
        api_url = metaflowconfig.get_sanitized_url_from_config(
            config_dir, profile, "OBP_API_SERVER"
        )
        hibernate_response = requests.put(
            f"{api_url}/v1/workstations/hibernate/{workstation}",
            headers={"x-api-key": metaflow_token},
        )
        try:
            hibernate_response.raise_for_status()
            response_json = hibernate_response.json()
            if len(response_json) > 0:
                click.echo(json.dumps(response_json, indent=4))
            else:
                click.secho("Success", fg="green", bold=True)
        except HTTPError:
            click.secho("Failed to hibernate workstation", fg="red")
            click.secho(
                "Error: {}".format(json.dumps(hibernate_response.json(), indent=4))
            )
    except Exception as e:
        click.secho("Failed to hibernate workstation", fg="red")
        click.secho("Error: {}".format(str(e)), fg="red")


@cli.command(help="Restart workstation to the int", hidden=True)
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
    "-w",
    "--workstation",
    default="",
    help="The ID of the workstation to restart",
)
def restart_workstation(config_dir=None, profile=None, workstation=None):
    if workstation is None or workstation == "":
        click.secho("Please specify a workstation ID", fg="red")
        return
    try:
        metaflow_token = metaflowconfig.get_metaflow_token_from_config(
            config_dir, profile
        )
        api_url = metaflowconfig.get_sanitized_url_from_config(
            config_dir, profile, "OBP_API_SERVER"
        )
        restart_response = requests.put(
            f"{api_url}/v1/workstations/restart/{workstation}",
            headers={"x-api-key": metaflow_token},
        )
        try:
            restart_response.raise_for_status()
            response_json = restart_response.json()
            if len(response_json) > 0:
                click.echo(json.dumps(response_json, indent=4))
            else:
                click.secho("Success", fg="green", bold=True)
        except HTTPError:
            click.secho("Failed to restart workstation", fg="red")
            click.secho(
                "Error: {}".format(json.dumps(restart_response.json(), indent=4))
            )
    except Exception as e:
        click.secho("Failed to restart workstation", fg="red")
        click.secho("Error: {}".format(str(e)), fg="red")


@cli.command(help="Install dependencies needed by workstations", hidden=True)
@click.option(
    "-d",
    "--install-dir",
    default=path.expanduser("~/.metaflowconfig/bin"),
    help="Path to Metaflow configuration directory",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def install_workstation_dependencies(install_dir=None, output=""):
    install_response = OuterboundsCommandResponse()
    install_response.add_or_update_metadata("RELOAD_REQUIRED", False)
    kubectl_install_step = CommandStatus(
        "kubectl", OuterboundsCommandStatus.OK, "kubectl is installed."
    )

    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    # Check if kubectl exists
    try:
        # Check if kubectl can be executed from the command line
        subprocess.run(["kubectl", "--help"], capture_output=True, check=True)
        click.echo("kubectl already installed", err=True)
        click.secho("Success", fg="green", bold=True, err=True)
        if output == "json":
            install_response.add_step(kubectl_install_step)
            click.echo(json.dumps(install_response.as_dict(), indent=4))
        return
    except FileNotFoundError:
        pass

    plt = platform.system()
    arch_info = platform.machine()

    kubectl_url = ""
    if plt == "Darwin":
        if arch_info == "arm64":
            kubectl_url = f"https://dl.k8s.io/release/v1.27.3/bin/darwin/arm64/kubectl"
        elif arch_info == "x86_64":
            kubectl_url = f"https://dl.k8s.io/release/v1.27.3/bin/darwin/amd64/kubectl"
    elif plt == "Linux":
        if arch_info == "x86_64":
            kubectl_url = f"https://dl.k8s.io/release/v1.27.3/bin/linux/amd64/kubectl"
        elif arch_info == "aarch64":
            kubectl_url = f"https://dl.k8s.io/release/v1.27.3/bin/linux/arm64/kubectl"
    elif plt == "Windows":
        kubectl_url = "https://dl.k8s.io/release/v1.27.4/bin/windows/amd64/kubectl.exe"

    if kubectl_url == "":
        message = f"No kubectl install URL available for platform: {plt}/{arch_info}"
        click.secho(f"{message}. {KUBECTL_INSTALL_MITIGATION}", fg="red", err=True)
        if output == "json":
            kubectl_install_step.update(
                OuterboundsCommandStatus.FAIL, message, KUBECTL_INSTALL_MITIGATION
            )
            install_response.add_step(kubectl_install_step)
            click.echo(json.dumps(install_response.as_dict(), indent=4))
        return

    # Download kubectl
    try:
        click.echo(f"Downloading kubectl from {kubectl_url}", err=True)
        kubectl_response = requests.get(kubectl_url)
        kubectl_response.raise_for_status()

        with NamedTemporaryFile(dir=install_dir, delete=False) as f:
            f.write(kubectl_response.content)
            temp_file_name = f.name

        rename_path = (
            f"{install_dir}/kubectl.exe"
            if plt == "Windows"
            else f"{install_dir}/kubectl"
        )

        if os.path.exists(rename_path):
            os.remove(rename_path)
        os.rename(temp_file_name, rename_path)
        os.chmod(rename_path, 0o755)

        # check if install_dir is already in PATH
        if install_dir not in os.environ["PATH"]:
            add_to_path(install_dir, plt)
            install_response.add_or_update_metadata("RELOAD_REQUIRED", True)
        else:
            click.echo(f"{install_dir} is already in PATH", err=True)

        click.secho("Success", fg="green", bold=True, err=True)
        if output == "json":
            install_response.add_step(kubectl_install_step)
            click.echo(json.dumps(install_response.as_dict(), indent=4))
        return
    except Exception as e:
        reason = "Failed to install kubectl"
        click.secho(f"Error: {str(e)}", err=True)
        click.secho(f"{reason}. {KUBECTL_INSTALL_MITIGATION}", fg="red", err=True)
        if output == "json":
            kubectl_install_step.update(
                OuterboundsCommandStatus.FAIL, reason, KUBECTL_INSTALL_MITIGATION
            )
            install_response.add_step(kubectl_install_step)
            click.echo(json.dumps(install_response.as_dict(), indent=4))
        return


def add_to_path(program_path, platform):
    """Takes in a path to a program and adds it to the system path"""
    if platform == "Windows":  # Windows systems
        # This is mostly copy-paste from
        # https://stackoverflow.com/questions/63782773/how-to-modify-windows-10-path-variable-directly-from-a-python-script
        import winreg  # Allows access to the windows registry
        import ctypes  # Allows interface with low-level C API's

        program_path = to_windows_path(program_path)
        with winreg.ConnectRegistry(
            None, winreg.HKEY_CURRENT_USER
        ) as root:  # Get the current user registry
            with winreg.OpenKey(
                root, "Environment", 0, winreg.KEY_ALL_ACCESS
            ) as key:  # Go to the environment key
                try:
                    existing_path_value = winreg.QueryValueEx(key, "PATH")[
                        0
                    ]  # Grab the current path value
                    if program_path in existing_path_value:
                        return
                    new_path_value = (
                        existing_path_value + ";" + program_path
                    )  # Takes the current path value and appends the new program path
                except WindowsError:
                    new_path_value = program_path
                winreg.SetValueEx(
                    key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path_value
                )  # Updated the path with the updated path
            # Tell other processes to update their environment
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.c_long()
            SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
            SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                "Environment",
                SMTO_ABORTIFHUNG,
                5000,
                ctypes.byref(result),
            )
    else:  # If system is *nix
        path_to_rc_file = f"{os.getenv('HOME')}/.bashrc"
        if platform == "Darwin":  # If system is MacOS
            path_to_rc_file = f"{os.getenv('HOME')}/.zshrc"

        with open(path_to_rc_file, "a+") as f:  # Open bashrc file
            if program_path not in f.read():
                f.write("\n# Added by Outerbounds\n")
                f.write(f"export PATH=$PATH:{program_path}")


def to_windows_path(path):
    return os.path.normpath(path).replace(os.sep, "\\")


@cli.command(help="Show relevant links for a deployment & perimeter", hidden=True)
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
    default="",
    help="The named metaflow profile in which your workstation exists",
)
@click.option(
    "--perimeter-id",
    default="",
    help="The id of the perimeter to use",
)
@click.option(
    "-o",
    "--output",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
def show_relevant_links(config_dir=None, profile=None, perimeter_id="", output=""):
    show_links_response = OuterboundsCommandResponse()
    show_links_step = CommandStatus(
        "showRelevantLinks",
        OuterboundsCommandStatus.OK,
        "Relevant links successfully fetched!",
    )
    show_links_response.add_or_update_data("links", [])
    links = []
    try:
        if not perimeter_id:
            metaflow_config = metaflowconfig.init_config(config_dir, profile)
        else:
            perimeters_dict = get_perimeters_from_api_or_fail_command(
                config_dir, profile, output, show_links_response, show_links_step
            )
            confirm_user_has_access_to_perimeter_or_fail(
                perimeter_id,
                perimeters_dict,
                output,
                show_links_response,
                show_links_step,
            )

            metaflow_config = metaflowconfig.init_config_from_url(
                config_dir, profile, perimeters_dict[perimeter_id]["remote_config_url"]
            )

        links.append(
            {
                "id": "metaflow-ui-url",
                "url": metaflow_config["METAFLOW_UI_URL"],
                "label": "Metaflow UI URL",
            }
        )
        show_links_response.add_or_update_data("links", links)
        if output == "json":
            click.echo(json.dumps(show_links_response.as_dict(), indent=4))
    except Exception as e:
        show_links_step.update(
            OuterboundsCommandStatus.FAIL, "Failed to show relevant links", ""
        )
        show_links_response.add_step(show_links_step)
        if output == "json":
            show_links_response.add_or_update_data("error", str(e))
            click.echo(json.dumps(show_links_response.as_dict(), indent=4))
        else:
            click.secho("Failed to show relevant links", fg="red", err=True)
            click.secho("Error: {}".format(str(e)), fg="red", err=True)


WORKSTATION_CONNECT_MODE = "workstation-connect"
WORKSTATION_INIT_MODE = "workstation-init"


@cli.command(help="Prepare a workstation for SSH access", hidden=True)
@click.option(
    "--workstation-id",
    default="",
    help="The name of the workstation on the Outerbounds UI",
)
@click.option(
    "--setup-context",
    "-c",
    default="local",
    help="The context to use for the setup command",
    type=click.Choice(["local", "remote"]),
)
@click.option(
    "--output",
    "-o",
    default="",
    help="Show output in the specified format.",
    type=click.Choice(["json", ""]),
)
@click.option(
    "--mode",
    default="workstation-connect",
    help="The mode in which the command is being run.",
    type=click.Choice([WORKSTATION_CONNECT_MODE, WORKSTATION_INIT_MODE]),
)
def prepare_for_ssh_access(
    workstation_id="", setup_context="", output="", mode=WORKSTATION_CONNECT_MODE
):
    """
    Finds the pod whose WORKSTATION_NAME env var matches `workstation_name`
    and opens an interactive bash shell in its "workstation" container.
    """

    # Workstation Init is only supported on remote workstation.
    if mode == WORKSTATION_INIT_MODE and setup_context == "local":
        raise Exception("workstation-init mode is not supported for local setup")

    response = {
        "status": "OK",
        "message": "SSH access prepared successfully",
    }
    try:
        if setup_context == "local":
            prepare_for_ssh_access_local(workstation_id)
        elif setup_context == "remote":
            prepare_for_ssh_access_remote(mode)
    except Exception as e:
        response["message"] = str(e)
        response["status"] = "FAIL"

    if output == "json":
        click.echo(json.dumps(response, indent=4))
    else:
        colors = {"OK": "green", "FAIL": "red"}
        message = {"OK": "", "FAIL": f'\nError: {response["message"]}'}

        click.secho(
            f"SSH access setup status: {response['status']}. {message[response['status']]}",
            fg=colors[response["status"]],
        )


def get_workstation_namespace(workstation_id: str) -> str:
    profile = ""
    config_dir = os.getenv("METAFLOW_HOME", os.path.expanduser("~/.metaflowconfig"))
    metaflow_token = metaflowconfig.get_metaflow_token_from_config(config_dir, profile)
    api_url = metaflowconfig.get_sanitized_url_from_config(
        config_dir, profile, "OBP_API_SERVER"
    )
    workstations_response = requests.get(
        f"{api_url}/v1/workstations", headers={"x-api-key": metaflow_token}
    )
    workstations_response.raise_for_status()

    for workstation in workstations_response.json()["workstations"]:
        if workstation["instance_id"] == workstation_id:
            return workstation["kubernetes_metadata"]["workstation_pod_namespace"]

    raise Exception(f"Workstation {workstation_id} not found")


def prepare_for_ssh_access_local(workstation_id):
    """
    SSH connection requires both local instance and workstation pod to do some work.
    This function takes care of the local instance. It does the following:

    1. Creates a new ssh key pair, or re-uses an existing one.
    2. Copies the public key of the key pair to the workstation.
    3. Executes the `outerbounds prepare-ws-for-ssh-access` command on the workstation. This command would setup the workstation for remote access.
    4. Ensures that the SSH config is setup with the right parameters.
    """
    pod_name = f"{workstation_id}-0"
    ws_namespace = get_workstation_namespace(workstation_id)

    private_key_path, public_key_path = ssh_utils.create_ssh_key_pair()

    # Create the .ssh directory if it doesn't exist
    result, stdout, stderr = exec_in_pod(
        pod_name,
        ws_namespace,
        "mkdir -p /home/ob-workspace/.ssh",
    )
    if result != 0:
        raise Exception(f"Failed to create .ssh directory: {stderr}")

    # Copy the public key to the workstation
    result, stdout, stderr = cp_to_pod(
        pod_name,
        ws_namespace,
        public_key_path,
        f"/home/ob-workspace/.ssh/{ssh_utils.EXPECTED_PUBLIC_KEY_NAME}",
    )
    if result != 0:
        raise Exception(f"Failed to copy public key to workstation: {stderr}")

    # 4. Exec into the pod
    result, stdout, stderr = exec_in_pod(
        pod_name,
        ws_namespace,
        "outerbounds prepare-for-ssh-access -c remote",
    )
    if result != 0:
        raise Exception(f"Failed to exec into workstation: {stderr}")

    # 5. Add the entry to the ssh config file
    ok, msg = ssh_utils.add_entry_to_ssh_config(
        workstation_id, ws_namespace, private_key_path
    )
    if not ok:
        raise Exception(f"Failed to add entry to ssh config: {msg}")


def prepare_for_ssh_access_remote(mode: str):
    """
    SSH connection requires both local instance and workstation pod to do some work.
    This function takes care of the remote instance.

    For now, it assumes:

    1. The image of the workstation already has openssh-server, netcat installed.
    """

    if "WORKSTATION_ID" not in os.environ:
        raise Exception("This can only be run from a workstation!")

    ok, message = ssh_utils.best_effort_install_remote_deps()
    if not ok:
        raise Exception(f"Failed to install deps in remote instance: {message}")

    ok, msg = ssh_utils.configure_ssh_server()
    if not ok:
        raise Exception(f"Failed to configure ssh server: {msg}")

    # SSH keys can only be guaranteed to be present when a connection is initiated.
    if mode == WORKSTATION_CONNECT_MODE:
        ok, msg = ssh_utils.ensure_public_key_registered_in_ssh_agent()
        if not ok:
            raise Exception(
                f"Failed to ensure public key registered in ssh agent: {msg}"
            )

    ssh_utils.add_env_loader_to_bashrc()
