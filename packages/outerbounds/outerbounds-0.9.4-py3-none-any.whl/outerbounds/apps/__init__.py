from outerbounds._vendor import click
import os

OUTERBOUNDS_APP_CLI_AVAILABLE = True
os.environ["APPS_CLI_LOADING_IN_OUTERBOUNDS"] = "true"
try:
    from metaflow.ob_internal import app_core  # type: ignore
except ImportError:
    OUTERBOUNDS_APP_CLI_AVAILABLE = False
except Exception as e:
    if not getattr(e, "_OB_CONFIG_EXCEPTION", None):
        raise e
    OUTERBOUNDS_APP_CLI_AVAILABLE = False


if not OUTERBOUNDS_APP_CLI_AVAILABLE:

    @click.group()
    def _cli():
        pass

    @_cli.group(help="Dummy Group to append to CLI for Safety")
    def app():
        pass

    @app.command(help="Dummy Command to append to CLI for Safety")
    def cannot_deploy():
        raise Exception("Outerbounds App CLI not available")

    app_cli_group = app  # type: ignore
else:
    app_cli_group = app_core.app_cli.app  # type: ignore
