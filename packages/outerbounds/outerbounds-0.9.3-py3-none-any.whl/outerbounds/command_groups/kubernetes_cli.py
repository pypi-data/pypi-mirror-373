import json
import base64
import boto3
import requests
import os
import time
from datetime import datetime
from functools import partial

from os import path, environ
from sys import exit
from outerbounds._vendor import click

from ..utils import metaflowconfig


def _logger(
    body="", system_msg=False, head="", bad=False, timestamp=True, nl=True, color=None
):
    if timestamp:
        if timestamp is True:
            dt = datetime.now()
        else:
            dt = timestamp
        tstamp = dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        click.secho(tstamp + " ", fg=ColorTheme.TIMESTAMP, nl=False)
    if head:
        click.secho(head, fg=ColorTheme.INFO_COLOR, nl=False)
    click.secho(
        body,
        bold=system_msg,
        fg=ColorTheme.BAD_COLOR if bad else color if color is not None else None,
        nl=nl,
    )


class ColorTheme:
    TIMESTAMP = "magenta"
    LOADING_COLOR = "cyan"
    BAD_COLOR = "red"
    INFO_COLOR = "green"

    TL_HEADER_COLOR = "magenta"
    ROW_COLOR = "bright_white"

    INFO_KEY_COLOR = "green"
    INFO_VALUE_COLOR = "bright_white"


def print_table(data, headers):
    """Print data in a formatted table."""

    if not data:
        return

    # Calculate column widths
    col_widths = [len(h) for h in headers]

    # Calculate actual widths based on data
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print header
    header_row = " | ".join(
        [headers[i].ljust(col_widths[i]) for i in range(len(headers))]
    )
    click.secho("-" * len(header_row), fg=ColorTheme.TL_HEADER_COLOR)
    click.secho(header_row, fg=ColorTheme.TL_HEADER_COLOR, bold=True)
    click.secho("-" * len(header_row), fg=ColorTheme.TL_HEADER_COLOR)

    # Print data rows
    for row in data:
        formatted_row = " | ".join(
            [str(row[i]).ljust(col_widths[i]) for i in range(len(row))]
        )
        click.secho(formatted_row, fg=ColorTheme.ROW_COLOR, bold=True)
    click.secho("-" * len(header_row), fg=ColorTheme.TL_HEADER_COLOR)


def _get_kubernetes_client():
    """Get kubernetes client from metaflow configuration."""
    from metaflow.plugins.kubernetes.kubernetes_client import KubernetesClient

    return KubernetesClient()


def _get_current_user():
    """Get current user from environment or metaflow config."""
    # Try to get user from metaflow config first
    try:
        from metaflow.util import get_username

        user = get_username()
        if user:
            return user
    except:
        pass

    # Fallback to environment variables
    raise click.ClickException("Failed to get current user")


def _format_jobs_and_jobsets_table(
    jobs_with_outcomes, jobsets_with_outcomes, filter_unchanged=True
):
    """Format jobs and jobsets into a table for display."""
    headers = [
        "Type",
        "Name",
        "Namespace",
        "Status",
        "Outcome",
        "Created",
        "Flow",
        "Run ID",
        "User",
    ]
    table_data = []

    # Add jobs to table
    for job, outcome in jobs_with_outcomes:
        # Filter out unchanged resources if requested
        if filter_unchanged and outcome == "leave_unchanged":
            continue

        annotations = job.metadata.annotations or {}

        # Format creation timestamp
        created_time = "N/A"
        if job.metadata.creation_timestamp:
            created_time = job.metadata.creation_timestamp.strftime("%Y-%m-%d %H:%M:%S")

        table_data.append(
            [
                "Job",
                job.metadata.name,
                job.metadata.namespace,
                str(job.status.active or 0) + " active"
                if job.status.active
                else "inactive",
                outcome,
                created_time,
                annotations.get("metaflow/flow_name", "N/A"),
                annotations.get("metaflow/run_id", "N/A"),
                annotations.get("metaflow/user", "N/A"),
            ]
        )

    # Add jobsets to table
    for jobset, outcome in jobsets_with_outcomes:
        # Filter out unchanged resources if requested
        if filter_unchanged and outcome == "leave_unchanged":
            continue

        metadata = jobset.get("metadata", {})
        annotations = metadata.get("annotations", {})
        status = jobset.get("status", {})

        # Format creation timestamp
        created_time = "N/A"
        creation_timestamp = metadata.get("creationTimestamp")
        if creation_timestamp:
            try:
                from datetime import datetime

                # Parse ISO timestamp
                dt = datetime.fromisoformat(creation_timestamp.replace("Z", "+00:00"))
                created_time = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                created_time = (
                    creation_timestamp[:19]
                    if len(creation_timestamp) >= 19
                    else creation_timestamp
                )

        table_data.append(
            [
                "JobSet",
                metadata.get("name", "N/A"),
                metadata.get("namespace", "N/A"),
                "terminal" if status.get("terminalState") else "running",
                outcome,
                created_time,
                annotations.get("metaflow/flow_name", "N/A"),
                annotations.get("metaflow/run_id", "N/A"),
                annotations.get("metaflow/user", "N/A"),
            ]
        )

    return headers, table_data


@click.group()
def cli(**kwargs):
    pass


@click.group(help="Commands for interacting with Kubernetes.")
def kubernetes(**kwargs):
    pass


@kubernetes.command(help="Kill pods/jobs/jobsets for a specific flow.")
@click.option("--flow-name", required=True, help="Flow name to kill pods for")
@click.option("--run-id", help="Specific run ID to kill pods for")
@click.option("--my-runs", is_flag=True, help="Only kill runs by current user")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be killed without actually killing"
)
@click.option("--auto-approve", is_flag=True, help="Skip confirmation prompt")
@click.option(
    "--clear-everything",
    is_flag=True,
    help="Force delete ALL matching resources regardless of their status (including terminal/completed ones)",
)
def kill(flow_name, run_id, my_runs, dry_run, auto_approve, clear_everything):
    """Kill pods/jobs/jobsets for a specific flow."""
    import warnings
    from metaflow.ob_internal import PodKiller  # type: ignore

    warnings.filterwarnings("ignore")

    logger = partial(_logger, timestamp=True)

    # Get kubernetes client
    kubernetes_client = _get_kubernetes_client()

    # Determine user filter
    user = None
    if my_runs:
        user = _get_current_user()
        logger(f"🔍 Filtering for runs by user: {user}", color=ColorTheme.INFO_COLOR)

    pod_killer = PodKiller(
        kubernetes_client=kubernetes_client.get(),
        echo_func=lambda x: None,
        namespace=kubernetes_client._namespace,
    )

    # Find matching jobs and jobsets
    logger(
        f"🔍 Searching for jobs and jobsets matching flow: {flow_name}",
        color=ColorTheme.INFO_COLOR,
    )
    if run_id:
        logger(f"🔍 Filtering by run ID: {run_id}", color=ColorTheme.INFO_COLOR)

    try:
        (
            jobs_with_outcomes,
            jobsets_with_outcomes,
        ) = pod_killer.extract_matching_jobs_and_jobsets(
            flow_name=flow_name, run_id=run_id, user=user
        )
    except Exception as e:
        logger(f"Error finding matching resources: {e}", bad=True, system_msg=True)
        exit(1)

    # Check if anything was found
    total_resources_found = len(jobs_with_outcomes) + len(jobsets_with_outcomes)
    if total_resources_found == 0:
        logger("✅ No matching jobs or jobsets found.", color=ColorTheme.INFO_COLOR)
        return

    # Calculate resources that will be processed
    if clear_everything:
        # Process ALL resources regardless of status
        jobs_to_process = len(jobs_with_outcomes)
        jobsets_to_process = len(jobsets_with_outcomes)
        total_to_process = jobs_to_process + jobsets_to_process
        filter_table = False

        # Show warning for clear-everything mode
        logger(
            "⚠️  CLEAR EVERYTHING MODE: All matching resources will be force deleted regardless of status!",
            color=ColorTheme.BAD_COLOR,
            system_msg=True,
        )
    else:
        # Normal mode: only process resources not in terminal state
        jobs_to_process = len(
            [j for j, outcome in jobs_with_outcomes if outcome != "leave_unchanged"]
        )
        jobsets_to_process = len(
            [j for j, outcome in jobsets_with_outcomes if outcome != "leave_unchanged"]
        )
        total_to_process = jobs_to_process + jobsets_to_process
        filter_table = True

    # Display what will be affected
    headers, table_data = _format_jobs_and_jobsets_table(
        jobs_with_outcomes, jobsets_with_outcomes, filter_unchanged=filter_table
    )

    if total_to_process == 0:
        logger(
            "✅ All matching resources are already in terminal state. Nothing to do.",
            color=ColorTheme.INFO_COLOR,
        )
        return

    if dry_run:
        logger(
            "=== DRY RUN - The following resources would be affected ===",
            color=ColorTheme.INFO_COLOR,
            system_msg=True,
            timestamp=False,
        )
    else:
        logger(
            "=== The following resources will be killed/deleted ===",
            color=ColorTheme.BAD_COLOR,
            system_msg=True,
            timestamp=False,
        )

    print_table(table_data, headers)

    # Show summary
    logger(
        "📊 Summary:",
    )
    logger(
        f"  • Total resources found: {total_resources_found}",
    )
    logger(
        f"  • Jobs to process: {jobs_to_process}",
    )
    logger(
        f"  • JobSets to process: {jobsets_to_process}",
    )
    logger(
        f"  • Resources to process: {total_to_process}",
    )

    if clear_everything:
        logger(
            "  • Mode: CLEAR EVERYTHING (forcing deletion of ALL resources)",
            color=ColorTheme.BAD_COLOR,
        )
    else:
        # Show how many are being skipped in normal mode
        skipped_resources = total_resources_found - total_to_process
        if skipped_resources > 0:
            logger(
                f"  • Resources already in terminal state (skipped): {skipped_resources}",
                color=ColorTheme.INFO_COLOR,
            )

    if dry_run:
        logger(
            "🔍 Dry run completed. No resources were actually killed.",
            color=ColorTheme.INFO_COLOR,
            system_msg=True,
        )
        return

    # Confirm before proceeding (unless auto-approve is set)
    if not auto_approve:
        confirm = click.prompt(
            click.style(
                f"⚠️  Are you sure you want to kill/delete {total_to_process} resources?",
                fg=ColorTheme.BAD_COLOR,
                bold=True,
            ),
            default="no",
            type=click.Choice(["yes", "no"]),
        )
        if confirm == "no":
            logger("❌ Operation cancelled.", color=ColorTheme.BAD_COLOR)
            exit(1)

    # Execute the kills/deletions
    logger(
        f"🚀 Processing {total_to_process} resources...",
        color=ColorTheme.INFO_COLOR,
        system_msg=True,
    )

    try:
        progress_label = (
            f"⚰️ Coffin: Deleting jobs and jobsets matching flow: {flow_name}"
        )
        if clear_everything:
            progress_label = (
                f"🔥 CLEAR ALL: Force deleting ALL resources for flow: {flow_name}"
            )

        __progress_bar = click.progressbar(
            length=total_to_process,
            label=click.style(
                progress_label,
                fg=ColorTheme.BAD_COLOR if clear_everything else ColorTheme.INFO_COLOR,
                bold=True,
            ),
            fill_char=click.style(
                "█",
                fg=ColorTheme.BAD_COLOR if clear_everything else ColorTheme.INFO_COLOR,
                bold=True,
            ),
            empty_char=click.style(
                "░",
                fg=ColorTheme.BAD_COLOR if clear_everything else ColorTheme.INFO_COLOR,
                bold=True,
            ),
            item_show_func=lambda x: click.style(
                x,
                fg=ColorTheme.BAD_COLOR,
                bold=True,
            ),
        )

        pod_killer = PodKiller(
            kubernetes_client=kubernetes_client.get(),
            echo_func=lambda x: None,
            namespace=kubernetes_client._namespace,
            progress_bar=__progress_bar,
        )

        if clear_everything:
            # Force delete everything mode
            (
                results,
                jobs_processed,
                jobsets_processed,
            ) = pod_killer.process_matching_jobs_and_jobsets_force_all(
                flow_name=flow_name, run_id=run_id, user=user
            )
        else:
            # Normal mode
            (
                results,
                jobs_processed,
                jobsets_processed,
            ) = pod_killer.process_matching_jobs_and_jobsets(
                flow_name=flow_name, run_id=run_id, user=user
            )

        # Report results
        successful_operations = sum(1 for r in results if r is True)
        failed_operations = sum(1 for r in results if r is False)

        logger(
            "📊 Operation completed:",
        )
        logger(
            f"  • Jobs processed: {jobs_processed}",
        )
        logger(
            f"  • JobSets processed: {jobsets_processed}",
        )
        logger(
            f"  • Successful operations: {successful_operations}",
        )

        if failed_operations > 0:
            logger(
                f"  • Failed operations: {failed_operations}",
                color=ColorTheme.BAD_COLOR,
            )
            logger(
                "⚠️  Some operations failed. Check the logs above for details.",
                color=ColorTheme.BAD_COLOR,
                system_msg=True,
            )
        else:
            logger(
                "✅ All operations completed successfully!",
                color=ColorTheme.INFO_COLOR,
                system_msg=True,
            )

    except Exception as e:
        logger(f"Error during kill operation: {e}", bad=True, system_msg=True)
        raise e


cli.add_command(kubernetes, name="kubernetes")
