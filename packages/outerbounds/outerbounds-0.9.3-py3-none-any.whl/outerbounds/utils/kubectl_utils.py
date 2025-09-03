import os
import subprocess
from typing import Tuple


def exec_in_pod(pod_name: str, namespace: str, command: str) -> Tuple[int, str, str]:
    """
    Executes a command using kubectl exec in the remote pod.
    """

    try:
        result = subprocess.run(
            [
                "kubectl",
                "--context",
                "outerbounds-workstations",
                "exec",
                "-i",
                pod_name,
                "-n",
                namespace,
                "-c",
                "workstation",
                "--",
                "sh",
                "-c",
                command,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, "", f"Error executing command: {e.stderr}"
    except Exception as e:
        return 1, "", f"Error executing command: {e}"


def cp_to_pod(
    pod_name: str, namespace: str, source_on_local: str, destination_on_pod: str
) -> Tuple[int, str, str]:
    """
    Copies a file to a pod using kubectl cp.
    """
    try:
        result = subprocess.run(
            [
                "kubectl",
                "--context",
                "outerbounds-workstations",
                "--container",
                "workstation",
                "cp",
                source_on_local,
                "-n",
                namespace,
                f"{pod_name}:{destination_on_pod}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, "", f"Error copying file: {e.stderr}"
    except Exception as e:
        return 1, "", f"Error copying file: {e}"
