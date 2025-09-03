import os
from outerbounds._vendor import click
import requests

import tarfile
import hashlib
import tempfile


@click.group()
def cli(**kwargs):
    pass


@click.group(help="Manage tutorials curated by Outerbounds.", hidden=True)
def tutorials(**kwargs):
    pass


@tutorials.command(help="Pull Outerbounds tutorials.")
@click.option(
    "--url",
    required=True,
    help="URL to pull the tutorials from.",
    type=str,
)
@click.option(
    "--destination-dir",
    help="Show output in the specified format.",
    type=str,
    required=True,
)
@click.option(
    "--force-overwrite",
    is_flag=True,
    help="Overwrite all existing files across all tutorials.",
    type=bool,
    required=False,
    default=False,
)
def pull(url="", destination_dir="", force_overwrite=False):
    try:
        secure_download_and_extract(
            url, destination_dir, force_overwrite=force_overwrite
        )
        click.secho("Tutorials pulled successfully.", fg="green", err=True)
    except Exception as e:
        print(e)
        click.secho(f"Failed to pull tutorials: {e}", fg="red", err=True)


def secure_download_and_extract(
    url, dest_dir, expected_hash=None, force_overwrite=False
):
    """
    Download a tar.gz file from a URL, verify its integrity, and extract its contents.

    :param url: URL of the tar.gz file to download
    :param dest_dir: Destination directory to extract the contents
    :param expected_hash: Expected SHA256 hash of the file (optional)
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = os.path.join(
            temp_dir, hashlib.md5(url.encode()).hexdigest() + ".tar.gz"
        )

        # Download the file
        try:
            response = requests.get(url, stream=True, verify=True)
            response.raise_for_status()

            with open(temp_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download file: {e}")

        if expected_hash:
            with open(temp_file, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            if file_hash != expected_hash:
                raise Exception("File integrity check failed")

        os.makedirs(dest_dir, exist_ok=True)

        try:
            with tarfile.open(temp_file, "r:gz") as tar:
                # Keep track of new journeys to extract.
                to_extract = []
                members = tar.getmembers()
                for member in members:
                    member_path = os.path.join(dest_dir, member.name)
                    # Check for any files trying to write outside the destination
                    if not os.path.abspath(member_path).startswith(
                        os.path.abspath(dest_dir)
                    ):
                        raise Exception("Attempted path traversal in tar file")
                    if not os.path.exists(member_path):
                        # The user might have modified the existing files, leave them untouched.
                        to_extract.append(member)

                if force_overwrite:
                    tar.extractall(path=dest_dir)
                else:
                    tar.extractall(path=dest_dir, members=to_extract)
        except tarfile.TarError as e:
            raise Exception(f"Failed to extract tar file: {e}")


cli.add_command(tutorials, name="tutorials")
