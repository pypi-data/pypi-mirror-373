import os
import shutil
import subprocess
from typing import Tuple
from pathlib import Path
import re

EXPECTED_PUBLIC_KEY_NAME = "ob_workstation_ed25519.pem.pub"
EXPECTED_PRIVATE_KEY_NAME = "ob_workstation_ed25519.pem"


def ensure_e25519_keypair_sshkeygen(
    directory,
    private_key_filename=EXPECTED_PRIVATE_KEY_NAME,
    public_key_filename=EXPECTED_PUBLIC_KEY_NAME,
    password=None,
):
    """
    Creates an Ed25519 key pair using ssh-keygen.
    """

    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    private_key_path = os.path.join(directory, private_key_filename)
    public_key_path = os.path.join(directory, public_key_filename)

    # No need to regenerate keys if they already exist.
    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        return private_key_path, public_key_path

    # Generate the Ed25519 key pair
    result = subprocess.run(
        ["ssh-keygen", "-t", "ed25519", "-f", private_key_path, "-N", ""],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise Exception(f"Failed to generate Ed25519 key pair: {result.stderr}")

    return private_key_path, public_key_path


def create_ssh_key_pair():
    location = os.environ.get("METAFLOW_HOME", os.path.expanduser("~/.metaflowconfig"))
    return ensure_e25519_keypair_sshkeygen(
        location, EXPECTED_PRIVATE_KEY_NAME, EXPECTED_PUBLIC_KEY_NAME
    )


def ensure_public_key_registered_in_ssh_agent():
    """
    This function ensures that the public key is registered in the ssh agent.
    This means making sure that the public key is added to the list of AuthorizedKeysFile entries in the ssh_config file.
    """
    WORKSPACE_DIR = "/home/ob-workspace/.ssh"
    AUTHORIZED_KEYS = f"{WORKSPACE_DIR}/authorized_keys"
    SOURCE_KEY = f"{WORKSPACE_DIR}/{EXPECTED_PUBLIC_KEY_NAME}"

    try:
        # Step 2: Handle authorized_keys file
        print("Setting up authorized_keys...")

        # Create .ssh directory if it doesn't exist
        Path(WORKSPACE_DIR).mkdir(parents=True, exist_ok=True, mode=0o700)

        # Check if authorized_keys exists, if not copy from ob-workstation-key
        if not os.path.exists(AUTHORIZED_KEYS):
            if os.path.exists(SOURCE_KEY):
                shutil.copy2(SOURCE_KEY, AUTHORIZED_KEYS)
                print(f"Copied {SOURCE_KEY} to {AUTHORIZED_KEYS}")
            else:
                return False, f"Source key file not found: {SOURCE_KEY}"

        # Set correct permissions for authorized_keys
        os.chmod(AUTHORIZED_KEYS, 0o600)
        return restart_ssh_service()
    except Exception as e:
        return False, f"Error during configuration: {str(e)}"


def restart_ssh_service():
    """
    This function restarts the ssh service.
    """
    print("Restarting SSH service...")

    # Try different service names and init systems
    restart_commands = [
        ["systemctl", "restart", "sshd"],
        ["systemctl", "restart", "ssh"],
        ["service", "sshd", "restart"],
        ["service", "ssh", "restart"],
    ]

    service_restarted = False
    for cmd in restart_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"SSH service restarted using: {' '.join(cmd)}")
            service_restarted = True
            break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue

    if not service_restarted:
        print("Warning: Could not restart SSH service automatically")
        print("Please restart manually with: sudo systemctl restart sshd")
        return False, f"SSH service could not be restarted automatically."

    return True, "SSH configuration completed successfully"


def configure_ssh_server() -> Tuple[bool, str]:
    """
    Configure SSH server to disable password authentication and set up authorized_keys.

    Returns:
        Tuple of (success: bool, message: str)
    """

    # Configuration paths
    SSHD_CONFIG = "/etc/ssh/sshd_config"
    SSHD_RUN_DIR = "/run/sshd"
    HOME_DIR = "/home/ob-workspace"

    try:
        # Step 1: Create and configure /run/sshd directory
        print("Setting up /run/sshd directory...")
        Path(SSHD_RUN_DIR).mkdir(parents=True, exist_ok=True, mode=0o755)
        os.chmod(SSHD_RUN_DIR, 0o755)
        print(f"Created {SSHD_RUN_DIR} with permissions 755")

        os.chmod(HOME_DIR, 0o755)

        # Step 3: Modify sshd_config
        print("Modifying SSH configuration...")

        # Check if we have permission to modify sshd_config
        if not os.access(SSHD_CONFIG, os.W_OK):
            return False, f"No write permission for {SSHD_CONFIG}. Run with sudo."

        # Create backup if requested
        backup_path = f"{SSHD_CONFIG}.backup"
        shutil.copy2(SSHD_CONFIG, backup_path)
        print(f"Backup created: {backup_path}")

        # Read current configuration
        with open(SSHD_CONFIG, "r") as f:
            lines = f.readlines()

        # Configuration settings to apply
        config_settings = {
            "PasswordAuthentication": "no",
            "ChallengeResponseAuthentication": "no",
            "PubkeyAuthentication": "yes",
            "AuthorizedKeysFile": "/home/ob-workspace/.ssh/authorized_keys .ssh/authorized_keys",
        }

        # Track which settings we've modified
        modified_settings = set()
        new_lines = []

        for line in lines:
            modified = False

            for setting, value in config_settings.items():
                # Check if this line contains the setting (commented or not)
                pattern = rf"^\s*#?\s*{setting}\s+"
                if re.match(pattern, line, re.IGNORECASE):
                    # Replace with our setting
                    new_lines.append(f"{setting} {value}\n")
                    modified_settings.add(setting)
                    modified = True
                    break

            if not modified:
                new_lines.append(line)

        # Add any settings that weren't found in the file
        for setting, value in config_settings.items():
            if setting not in modified_settings:
                new_lines.append(f"\n{setting} {value}\n")
                print(f"Added new setting: {setting} {value}")

        # Write the modified configuration
        with open(SSHD_CONFIG, "w") as f:
            f.writelines(new_lines)

        print("Configuration file updated successfully")

        # Step 4: Test configuration
        print("Testing SSH configuration...")
        result = subprocess.run(["sshd", "-t"], capture_output=True, text=True)

        if result.returncode != 0:
            return False, f"SSH configuration test failed: {result.stderr}"

        print("Configuration test passed")

        # Step 5: Restart SSH service if requested
        return restart_ssh_service()

    except Exception as e:
        return False, f"Error during configuration: {str(e)}"


def add_entry_to_ssh_config(
    workstation_id: str, namespace: str, private_key_path: str
) -> Tuple[bool, str]:
    """
    Adds an entry to the ssh config file if one doesn't already exist.

    Example Entry:
    Host ws-bae81a70-0
        ProxyCommand kubectl exec -i --context outerbounds-workstations ws-bae81a70-0 -n ws-69304f8188e31a0745bace40b9378c6b --container workstation -- nc localhost 22
        User root
        StrictHostKeyChecking no
        UserKnownHostsFile /dev/null
        IdentityFile ~/.ssh/id_ed25519
        ControlMaster auto
        ControlPath ~/.ssh/control-%h-%p-%r
        ControlPersist 10m
    """

    with open(os.path.expanduser("~/.ssh/config"), "r") as f:
        lines = f.readlines()

    for line in lines:
        if f"Host {workstation_id}-0" in line:
            return True, "Entry already exists"

    indent = " " * 2
    with open(os.path.expanduser("~/.ssh/config"), "a") as f:
        f.write("\n")
        f.write(f"Host {workstation_id}-0\n")
        f.write(
            f"{indent}ProxyCommand kubectl exec -i --context outerbounds-workstations {workstation_id}-0 -n {namespace} --container workstation -- nc localhost 22\n"
        )
        f.write(f"{indent}User root\n")
        f.write(f"{indent}StrictHostKeyChecking no\n")
        f.write(f"{indent}UserKnownHostsFile /dev/null\n")
        f.write(f"{indent}IdentityFile {private_key_path}\n")
        f.write(f"{indent}ControlMaster auto\n")
        f.write(f"{indent}ControlPath ~/.ssh/control-%h-%p-%r\n")
        f.write(f"{indent}ControlPersist 10m\n")

    return True, "Entry added to ssh config"


def add_env_loader_to_bashrc():
    """
    Adds the environment variable loader block to ~/.bashrc if not already present.
    Uses marker comments to identify the block.
    """

    # Define the block content with marker comments
    env_loader_block = """
# BEGIN WORKSTATION_ENV_LOADER
# Only proceed if WORKSTATION_ID is not already set
if [ -z "$WORKSTATION_ID" ]; then
    # Read environment variables from /proc/1/environ (init process)
    # This file contains null-separated env vars
    if [ -r /proc/1/environ ]; then
        while IFS= read -r -d '' var; do
            # Extract the variable name (everything before the first '=')
            var_name="${var%%=*}"

            # Check if the variable name contains any of our keywords
            if [[ "$var_name" == *"WORKSTATION"* ]] || \\
               [[ "$var_name" == *"METAFLOW"* ]] || \\
               [[ "$var_name" == *"AWS"* ]] || \\
               [[ "$var_name" == *"GCP"* ]] || \\
               [[ "$var_name" == *"CLOUDSDK"* ]] || \\
               [[ "$var_name" == *"OBP"* ]]; then
                # Export the variable to the current session
                export "$var"
            fi
        done < /proc/1/environ
    fi
fi
# END WORKSTATION_ENV_LOADER
"""

    # Get the path to ~/.bashrc
    bashrc_path = Path.home() / ".bashrc"

    # Create .bashrc if it doesn't exist
    if not bashrc_path.exists():
        bashrc_path.touch()
        print(f"Created {bashrc_path}")

    # Read the current content
    try:
        with open(bashrc_path, "r") as f:
            current_content = f.read()
    except Exception as e:
        print(f"Error reading {bashrc_path}: {e}")
        return False

    # Check if the marker is already present
    marker = "BEGIN WORKSTATION_ENV_LOADER"
    if marker in current_content:
        print(f"Environment loader block already present in {bashrc_path}")
        return True

    # Add the block to the end of the file
    try:
        with open(bashrc_path, "a") as f:
            # Add a newline before our block if file doesn't end with one
            if current_content and not current_content.endswith("\n"):
                f.write("\n")
            f.write(env_loader_block)
        print(f"Successfully added environment loader block to {bashrc_path}")
        return True
    except Exception as e:
        print(f"Error writing to {bashrc_path}: {e}")
        return False


def best_effort_install_remote_deps():
    """
    Best effort installation of openssh-server and netcat.

    Returns:
        tuple: (success: bool, message: str)
    """

    def run_command(cmd, check=False):
        """Helper to run shell commands"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def check_command_exists(cmd):
        """Check if a command exists in PATH"""
        return shutil.which(cmd) is not None

    def check_ssh_server():
        """Check if SSH server is installed"""
        # Check for sshd in common locations
        sshd_paths = ["/usr/sbin/sshd", "/sbin/sshd"]
        for path in sshd_paths:
            if os.path.exists(path):
                return True
        # Also check if sshd is in PATH
        return check_command_exists("sshd")

    def check_sudo_access():
        """Check if we have sudo access"""
        success, _, _ = run_command("sudo -n true 2>/dev/null")
        if success:
            return True
        # Try with -v flag (might prompt for password)
        success, _, _ = run_command("sudo -v 2>/dev/null")
        return success

    def detect_package_manager():
        """Detect which package manager is available"""
        package_managers = {
            "apt-get": {
                "update": "apt-get update",
                "install": "apt-get install -y",
                "ssh_package": "openssh-server",
                "nc_packages": ["netcat-openbsd", "netcat-traditional", "netcat"],
                "curl_package": "curl",
            },
            "apt": {
                "update": "apt update",
                "install": "apt install -y",
                "ssh_package": "openssh-server",
                "nc_packages": ["netcat-openbsd", "netcat-traditional", "netcat"],
                "curl_package": "curl",
            },
            "yum": {
                "update": "yum makecache",
                "install": "yum install -y",
                "ssh_package": "openssh-server",
                "nc_packages": ["nmap-ncat", "nc", "netcat"],
                "curl_package": "curl",
            },
            "dnf": {
                "update": "dnf makecache",
                "install": "dnf install -y",
                "ssh_package": "openssh-server",
                "nc_packages": ["nmap-ncat", "nc", "netcat"],
                "curl_package": "curl",
            },
            "zypper": {
                "update": "zypper refresh",
                "install": "zypper install -n",
                "ssh_package": "openssh",
                "nc_packages": ["netcat-openbsd", "gnu-netcat", "netcat"],
                "curl_package": "curl",
            },
            "pacman": {
                "update": "pacman -Sy",
                "install": "pacman -S --noconfirm",
                "ssh_package": "openssh",
                "nc_packages": ["gnu-netcat", "openbsd-netcat"],
                "curl_package": "curl",
            },
            "apk": {
                "update": "apk update",
                "install": "apk add --no-cache",
                "ssh_package": "openssh-server",
                "nc_packages": ["netcat-openbsd"],
                "curl_package": "curl",
            },
        }

        for pm, config in package_managers.items():
            if check_command_exists(pm):
                return pm, config
        return None, None

    def install_package(package, pm_config, use_sudo=True):
        """Try to install a package"""
        install_cmd = pm_config["install"]
        if use_sudo:
            cmd = f"sudo {install_cmd} {package}"
        else:
            cmd = f"{install_cmd} {package}"

        success, stdout, stderr = run_command(cmd)
        return success

    # Step 1: Check if both are already installed
    ssh_installed = check_ssh_server()
    nc_installed = (
        check_command_exists("nc")
        or check_command_exists("netcat")
        or check_command_exists("ncat")
    )
    curl_installed = check_command_exists("curl")

    if ssh_installed and nc_installed and curl_installed:
        return True, "openssh-server, netcat, and curl are already installed"

    # Prepare status messages
    status = []
    if ssh_installed:
        status.append("openssh-server is already installed")
    if nc_installed:
        status.append("netcat is already installed")
    if curl_installed:
        status.append("curl is already installed")

    # Step 2 & 3: Check sudo availability and access
    has_sudo = check_command_exists("sudo")
    has_sudo_access = has_sudo and check_sudo_access()

    # Step 4: Detect package manager
    pm_name, pm_config = detect_package_manager()

    if not pm_name:
        missing = []
        if not ssh_installed:
            missing.append("openssh-server")
        if not nc_installed:
            missing.append("netcat")
        return (
            False,
            f"No supported package manager found. Unable to install: {', '.join(missing)}",
        )

    # Step 5 & 6: Try to install missing packages
    use_sudo = has_sudo and has_sudo_access

    # Update package manager cache first
    update_cmd = pm_config["update"]
    if use_sudo:
        update_cmd = f"sudo {update_cmd}"

    update_success, _, _ = run_command(update_cmd)
    if not update_success:
        status.append(
            f"Warning: Failed to update package cache with '{pm_config['update']}'"
        )

    # Install SSH server if needed
    if not ssh_installed:
        ssh_package = pm_config["ssh_package"]
        if install_package(ssh_package, pm_config, use_sudo):
            status.append(f"Successfully installed {ssh_package}")
            ssh_installed = check_ssh_server()
        else:
            status.append(f"Failed to install {ssh_package}")

    # Install netcat if needed
    if not nc_installed:
        # Try different netcat package names
        nc_packages = pm_config["nc_packages"]
        nc_install_success = False

        for nc_package in nc_packages:
            if install_package(nc_package, pm_config, use_sudo):
                status.append(f"Successfully installed {nc_package}")
                nc_install_success = True
                break

        if not nc_install_success:
            status.append(f"Failed to install netcat (tried: {', '.join(nc_packages)})")

        nc_installed = (
            check_command_exists("nc")
            or check_command_exists("netcat")
            or check_command_exists("ncat")
        )

    # Install curl if needed
    if not curl_installed:
        curl_package = pm_config["curl_package"]
        if install_package(curl_package, pm_config, use_sudo):
            status.append(f"Successfully installed {curl_package}")
            curl_installed = check_command_exists("curl")
        else:
            status.append(f"Failed to install {curl_package}")

    # Step 7: Final check and return appropriate message
    ssh_final = check_ssh_server()
    nc_final = (
        check_command_exists("nc")
        or check_command_exists("netcat")
        or check_command_exists("ncat")
    )
    curl_final = check_command_exists("curl")

    if ssh_final and nc_final and curl_final:
        return True, "Successfully installed all required packages. " + " ".join(status)
    elif ssh_final or nc_final or curl_final:
        installed = []
        missing = []
        if ssh_final:
            installed.append("openssh-server")
        else:
            missing.append("openssh-server")
        if nc_final:
            installed.append("netcat")
        else:
            missing.append("netcat")

        msg = f"Partial success. Installed: {', '.join(installed)}. "
        msg += f"Failed to install: {', '.join(missing)}. "
        if not use_sudo and has_sudo:
            msg += "Try running with sudo privileges."
        return False, msg + " " + " ".join(status)
    else:
        msg = "Failed to install both openssh-server and netcat. "
        if not use_sudo and has_sudo:
            msg += "No sudo access available. Try running with sudo privileges. "
        elif not has_sudo:
            msg += "sudo is not installed. May need root access. "
        return False, msg + " ".join(status)
