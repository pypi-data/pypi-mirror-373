from outerbounds._vendor import click
import json
import os
import requests
from os import path
from typing import Dict, Union
import sys

"""
key: perimeter specific URL to fetch the remote metaflow config from
value: the remote metaflow config
"""
CACHED_REMOTE_METAFLOW_CONFIG: Dict[str, Dict[str, str]] = {}


CURRENT_PERIMETER_KEY = "OB_CURRENT_PERIMETER"
CURRENT_PERIMETER_URL = "OB_CURRENT_PERIMETER_MF_CONFIG_URL"
CURRENT_PERIMETER_URL_LEGACY_KEY = (
    "OB_CURRENT_PERIMETER_URL"  # For backwards compatibility with workstations.
)


def init_config(config_dir, profile) -> Dict[str, str]:
    global CACHED_REMOTE_METAFLOW_CONFIG
    config = read_metaflow_config_from_filesystem(config_dir, profile)

    # Either user has an ob_config.json file with the perimeter URL
    # or the default config on the filesystem has the config URL in it.
    perimeter_specifc_url = get_perimeter_config_url_if_set_in_ob_config(
        config_dir, profile
    ) or config.get("OBP_METAFLOW_CONFIG_URL", "")

    if perimeter_specifc_url != "":
        if perimeter_specifc_url in CACHED_REMOTE_METAFLOW_CONFIG:
            return CACHED_REMOTE_METAFLOW_CONFIG[perimeter_specifc_url]

        remote_config = init_config_from_url(config_dir, profile, perimeter_specifc_url)
        remote_config["OBP_METAFLOW_CONFIG_URL"] = perimeter_specifc_url

        CACHED_REMOTE_METAFLOW_CONFIG[perimeter_specifc_url] = remote_config
        return remote_config

    return config


def init_config_from_url(config_dir, profile, url) -> Dict[str, str]:
    config = read_metaflow_config_from_filesystem(config_dir, profile)

    if config is None or "METAFLOW_SERVICE_AUTH_KEY" not in config:
        raise Exception("METAFLOW_SERVICE_AUTH_KEY not found in config file")

    config_response = requests.get(
        url,
        headers={"x-api-key": f'{config["METAFLOW_SERVICE_AUTH_KEY"]}'},
    )
    config_response.raise_for_status()
    remote_config = config_response.json()["config"]
    return remote_config


def read_metaflow_config_from_filesystem(config_dir, profile) -> Dict[str, str]:
    config_filename = f"config_{profile}.json" if profile else "config.json"

    path_to_config = os.path.join(config_dir, config_filename)

    if os.path.exists(path_to_config):
        with open(path_to_config, encoding="utf-8") as json_file:
            config = json.load(json_file)
    else:
        raise Exception("Unable to locate metaflow config at '%s')" % (path_to_config))
    return config


def get_metaflow_token_from_config(config_dir: str, profile: str) -> str:
    """
    Return the Metaflow service auth key from the config file.

    Args:
        config_dir (str): Path to the config directory
        profile (str): The named metaflow profile
    """
    config = init_config(config_dir, profile)
    if config is None or "METAFLOW_SERVICE_AUTH_KEY" not in config:
        raise Exception("METAFLOW_SERVICE_AUTH_KEY not found in config file")
    return config["METAFLOW_SERVICE_AUTH_KEY"]


def get_sanitized_url_from_config(config_dir: str, profile: str, key: str) -> str:
    """
    Given a key, return the value from the config file, with https:// prepended if not already present.

    Args:
        config_dir (str): Path to the config directory
        profile (str): The named metaflow profile
        key (str): The key to look up in the config file
    """
    config = init_config(config_dir, profile)
    if key not in config:
        raise Exception(f"Key {key} not found in config")
    url_in_config = config[key]
    if not url_in_config.startswith("https://"):
        url_in_config = f"https://{url_in_config}"

    url_in_config = url_in_config.rstrip("/")
    return url_in_config


def get_remote_metaflow_config_for_perimeter(
    origin_token: str, perimeter: str, api_server: str
):
    try:
        response = requests.get(
            f"{api_server}/v1/perimeters/{perimeter}/metaflowconfigs/default",
            headers={"x-api-key": origin_token},
        )
        response.raise_for_status()
        config = response.json()["config"]
        config["METAFLOW_SERVICE_AUTH_KEY"] = origin_token
        return config
    except Exception as e:
        click.secho(
            f"Failed to get metaflow config from {api_server}. Error: {str(e)}",
            fg="red",
        )
        sys.exit(1)


def get_ob_config_file_path(config_dir: str, profile: str) -> str:
    # If OBP_CONFIG_DIR is set, use that, otherwise use METAFLOW_HOME
    # If neither are set, use ~/.metaflowconfig
    obp_config_dir = path.expanduser(os.environ.get("OBP_CONFIG_DIR", config_dir))

    ob_config_filename = f"ob_config_{profile}.json" if profile else "ob_config.json"
    return os.path.expanduser(os.path.join(obp_config_dir, ob_config_filename))


def get_perimeter_config_url_if_set_in_ob_config(
    config_dir: str, profile: str
) -> Union[str, None]:
    file_path = get_ob_config_file_path(config_dir, profile)

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            ob_config = json.loads(f.read())

        if CURRENT_PERIMETER_URL in ob_config:
            return ob_config[CURRENT_PERIMETER_URL]
        elif CURRENT_PERIMETER_URL_LEGACY_KEY in ob_config:
            return ob_config[CURRENT_PERIMETER_URL_LEGACY_KEY]
        else:
            raise ValueError(
                "{} does not contain the key {}".format(
                    file_path, CURRENT_PERIMETER_KEY
                )
            )
    elif "OBP_CONFIG_DIR" in os.environ:
        raise FileNotFoundError(
            "Environment variable OBP_CONFIG_DIR is set to {} but this directory does not contain an ob_config.json file.".format(
                os.environ["OBP_CONFIG_DIR"]
            )
        )
    return None
