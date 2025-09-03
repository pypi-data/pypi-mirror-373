import os
from outerbounds._vendor import yaml
from outerbounds._vendor.yaml.scanner import ScannerError
import subprocess
from os import path
import platform


class KubeconfigError(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self) -> str:
        return self.message


def get_kube_config_or_init_default(config_path: str = "") -> dict:
    """
    Get the Kubernetes configuration from the given path, or initialize
    a default configuration if the file does not exist.

    Args:
        config_path (str): Path to the Kubernetes configuration file.
    """
    # If no path provided, use the default path or read from $KUBECONFIG
    if config_path is None or config_path == "":
        config_path = os.path.expanduser(os.environ.get("KUBECONFIG", "~/.kube/config"))

    if path.isdir(config_path):
        raise KubeconfigError(f"Kubeconfig path {config_path} is a directory.")

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
        else:
            config_dir = os.path.dirname(config_path)

            config = {
                "apiVersion": "v1",
                "kind": "Config",
                "preferences": {},
                "clusters": [],
                "users": [],
                "contexts": [],
            }

            if not os.path.exists(config_dir):
                os.makedirs(config_dir)

            with open(config_path, "w") as f:
                yaml.safe_dump(config, f)
    except ScannerError:
        raise KubeconfigError(
            f"Kubeconfig file {config_path} is not a valid YAML file."
        )
    return config


def set_context(name: str, cluster: str, namespace: str, user: str) -> None:
    """
    Set a context in the Kubernetes configuration.

    If the context already exists, it will be updated with the provided
    details. If it does not exist, a new context will be added.

    Args:
        name (str): Name of the context.
        cluster (str): Name of the cluster for the context.
        namespace (str): Name of the namespace for the context.
        user (str): Name of the user for the context.
    """
    config_path = os.path.expanduser(os.environ.get("KUBECONFIG", "~/.kube/config"))
    config = get_kube_config_or_init_default(config_path)

    # Find if context already exists
    existing_context = next(
        (context for context in config["contexts"] if context["name"] == name), None
    )

    new_context = {
        "name": name,
        "context": {
            "cluster": cluster,
            "namespace": namespace,
            "user": user,
        },
    }

    # If context exists, update it. Otherwise, add as new context
    if existing_context:
        existing_context.update(new_context)
    else:
        config["contexts"].append(new_context)

    # Write the config back to the file
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)


def set_cluster(name: str, server: str, insecure_skip_tls_verify: bool) -> None:
    """
    Set a cluster in the Kubernetes configuration.

    If the cluster already exists, it will be updated with the provided
    details. If it does not exist, a new cluster will be added.

    Args:
        name (str): Name of the cluster.
        server (str): URL of the cluster.
        insecure_skip_tls_verify (bool): Whether to skip TLS verification.
    """
    config_path = os.path.expanduser(os.environ.get("KUBECONFIG", "~/.kube/config"))
    config = get_kube_config_or_init_default(config_path)

    # Find if cluster already exists
    existing_cluster = next(
        (cluster for cluster in config["clusters"] if cluster["name"] == name), None
    )

    new_cluster = {
        "name": name,
        "cluster": {
            "server": server,
            "insecure-skip-tls-verify": insecure_skip_tls_verify,
        },
    }

    # If cluster exists, update it. Otherwise, add as new cluster
    if existing_cluster:
        existing_cluster.update(new_cluster)
    else:
        config["clusters"].append(new_cluster)

    # Write the config back to the file
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)


def add_user_with_exec_credential(
    name: str, outerbounds_binary_path: str, config_dir: str, profile: str
) -> None:
    """
    Add a user with exec credentials to the Kubernetes configuration, based on user's metaflow profile, config and outerbounds binary path

    Args:
        name (str): Name of the user.
        outerbounds_binary_path (str): Command to execute to get credentials.
        config_dir (str): Arguments to pass to the command.
        profile (str): Environment variables to set when executing the command.
    """
    config_path = os.path.expanduser(os.environ.get("KUBECONFIG", "~/.kube/config"))
    config = get_kube_config_or_init_default(config_path)

    # Find if user already exists
    existing_user = next(
        (user for user in config["users"] if user["name"] == name), None
    )

    if platform.system() == "Windows":
        main_cmd = "py"
        cmd_args = [
            outerbounds_binary_path,
            "generate-workstation-token",
            "--config-dir",
            config_dir,
        ]
    else:
        main_cmd = outerbounds_binary_path
        cmd_args = ["generate-workstation-token", "--config-dir", config_dir]

    if profile != "":
        cmd_args.extend(["--profile", profile])
    new_user = {
        "name": name,
        "user": {
            "exec": {
                "apiVersion": "client.authentication.k8s.io/v1beta1",
                "command": main_cmd,
                "args": cmd_args,
                "env": None,
                "interactiveMode": "Never",
                "provideClusterInfo": False,
            }
        },
    }

    # If user exists, update it. Otherwise, add as new user
    if existing_user:
        existing_user.update(new_user)
    else:
        config["users"].append(new_user)

    # Write the config back to the file
    with open(config_path, "w") as f:
        yaml.safe_dump(config, f)


def validate_kubeconfig_fields_for_workstations(
    expected_server_url, expected_namespace, current_kubeconfig
) -> bool:
    """
    Validate that all kubeconfig fields are set correctly for workstations

    Args:
        expected_server_url (str): Expected server URL, this should correspond to the cluster referenced by the Metaflow config.
        expected_namespace (str): Expected namespace
        current_kubeconfig (dict): Current kubeconfig
    """

    obp_user_exists = False
    for user in current_kubeconfig["users"]:
        if user["name"] == "obp-user":
            ob_binary_loc = user["user"]["exec"]["command"]
            try:
                # Check outerbounds binary referenced by kubeconfig actually exists
                subprocess.run(
                    [ob_binary_loc, "--help"], capture_output=True, check=True
                )
            except:
                return False
            obp_user_exists = True
            break

    if not obp_user_exists:
        return False

    obp_cluster_exists = False
    for cluster in current_kubeconfig["clusters"]:
        if (
            cluster["name"] == "outerbounds-cluster"
            and cluster["cluster"]["server"] == expected_server_url
        ):
            obp_cluster_exists = True
            break

    if not obp_cluster_exists:
        return False

    context_exists = False
    for context in current_kubeconfig["contexts"]:
        if (
            context["name"] == "outerbounds-workstations"
            and context["context"]["cluster"] == "outerbounds-cluster"
            and context["context"]["user"] == "obp-user"
            and context["context"]["namespace"] == expected_namespace
        ):
            context_exists = True
            break

    return context_exists
