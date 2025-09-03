#!/usr/bin/env python3
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -

import os
import click
    
from qalita.internal.utils import logger, get_version
from qalita.internal.config import Config


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(
    context_settings=dict(help_option_names=["-h", "--help"]),
    invoke_without_command=True,
)
@click.option(
    "--ui",
    is_flag=True,
    default=os.environ.get("QALITA_AGENT_UI", False),
    help="Open the local web UI dashboard",
)
@click.option(
    "--port",
    default=os.environ.get("QALITA_AGENT_UI_PORT", 7070),
    show_default=True,
    type=int,
    help="Port for the local web UI",
)
@click.option(
    "--host",
    default=os.environ.get("QALITA_AGENT_UI_HOST", "localhost"),
    show_default=True,
    help="Host interface to bind the local web UI",
)
@click.pass_context
def cli(ctx, ui=False, port=7070, host="localhost"):
    """
    ------------------ Qalita Platform Command Line Interface ------------------\n\r
    Hello and thanks for using Qalita Platform to monitor and ensure the quality of your data. \n\r
    ----------------------------------------------------------------------------\n\r
    Please, Help us improve our service by reporting any bug by filing a bug report, Thanks ! \n\r
    mail : contact@qalita.io \n\r
    ----------------------------------------------------------------------------"""
    if ui:
        try:
            from qalita.web.app import run_dashboard_ui
        except Exception as exc:
            logger.error(f"Unable to start web UI: {exc}")
        else:
            # Instantiate a Config to pass into the UI
            cfg = Config()
            cfg.load_source_config(verbose=False)
            run_dashboard_ui(cfg, host=host, port=port)
        raise SystemExit(0)
    # If invoked without a subcommand and without --ui, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        raise SystemExit(0)


@cli.command(context_settings=dict(help_option_names=["-h", "--help"]))
def version():
    """
    Display the version of the cli
    """
    print("--- QALITA CLI Version ---")
    print(f"Version : {get_version()}")


def add_commands_to_cli():
    from qalita.commands import agent, source, pack

    # Add pack command group to cli
    cli.add_command(pack.pack)
    cli.add_command(agent.agent)
    cli.add_command(source.source)


def main():
    add_commands_to_cli()
    cli()


if __name__ == "__main__":
    main()
