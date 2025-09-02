"""Command-line interface for the Redshift Utils MCP Server.

This module provides the main entry point for starting the server using Typer.
It handles parsing command-line arguments, setting corresponding environment
variables, performing a basic configuration pre-flight check, and running
the FastMCP server instance defined in `server.py`.
"""

import logging
import os
import sys
from typing import Optional, List, Dict

from typing_extensions import Annotated

import typer


from redshift_utils_mcp.server import mcp
from redshift_utils_mcp.utils.data_api import (
    DataApiConfigError,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    stream=sys.stderr,
)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


app: typer.Typer = typer.Typer(
    name="redshift-utils-mcp-server",
    help="Runs the Redshift Utils MCP Server using AWS Data API.",
    add_completion=False,
)


@app.command()
def main(
    cluster_id: Annotated[
        Optional[str],
        typer.Option(
            "--cluster-id",
            help="Redshift cluster identifier.",
            envvar="REDSHIFT_CLUSTER_ID",
        ),
    ] = None,
    database: Annotated[
        Optional[str],
        typer.Option(
            "--database", help="Redshift database name.", envvar="REDSHIFT_DATABASE"
        ),
    ] = None,
    secret_arn: Annotated[
        Optional[str],
        typer.Option(
            "--secret-arn",
            help="AWS Secrets Manager ARN for Redshift credentials.",
            envvar="REDSHIFT_SECRET_ARN",
        ),
    ] = None,
    region: Annotated[
        Optional[str],
        typer.Option(
            "--region",
            help="AWS region for Data API and Secrets Manager.",
            envvar=["AWS_REGION", "AWS_DEFAULT_REGION"],
        ),
    ] = None,
    aws_profile: Annotated[
        Optional[str],
        typer.Option(
            "--profile",
            help="AWS profile name to use.",
            envvar="AWS_PROFILE",
        ),
    ] = None,
):
    """Entry point for the Redshift Utils MCP Server.

    This function serves as the main command for the Typer CLI application.
    It orchestrates the configuration loading process and initiates the
    FastMCP server. Configuration values are sourced primarily from command-line
    options, falling back to environment variables if options are not provided.
    It performs a preliminary check for essential configuration variables
    before attempting to run the server.

    Args:
        cluster_id: Redshift cluster identifier. Reads from `--cluster-id` or `REDSHIFT_CLUSTER_ID`.
        database: Redshift database name. Reads from `--database` or `REDSHIFT_DATABASE`.
        secret_arn: AWS Secrets Manager ARN for Redshift credentials. Reads from `--secret-arn` or `REDSHIFT_SECRET_ARN`.
        region: AWS region for Data API and Secrets Manager. Reads from `--region` or `AWS_REGION`/`AWS_DEFAULT_REGION`.
        aws_profile: AWS profile name to use. Reads from `--profile` or `AWS_PROFILE`.
    """
    logger.info("Configuring Redshift Utils MCP Server...")

    final_config: Dict[str, Optional[str]] = {}

    if cluster_id:
        os.environ["REDSHIFT_CLUSTER_ID"] = cluster_id
        final_config["cluster_id"] = cluster_id
        logger.info(f"Using Cluster ID from argument: {cluster_id}")
    else:
        final_config["cluster_id"] = os.environ.get("REDSHIFT_CLUSTER_ID")

    if database:
        os.environ["REDSHIFT_DATABASE"] = database
        final_config["database"] = database
        logger.info(f"Using Database from argument: {database}")
    else:
        final_config["database"] = os.environ.get("REDSHIFT_DATABASE")

    if secret_arn:
        os.environ["REDSHIFT_SECRET_ARN"] = secret_arn
        final_config["secret_arn"] = secret_arn
        logger.info(f"Using Secret ARN from argument: {secret_arn}")
    else:
        final_config["secret_arn"] = os.environ.get("REDSHIFT_SECRET_ARN")

    if region:
        os.environ["AWS_REGION"] = region
        final_config["region"] = region
        logger.info(f"Using AWS Region from argument/env: {region}")
    else:

        final_config["region"] = os.environ.get("AWS_REGION") or os.environ.get(
            "AWS_DEFAULT_REGION"
        )

    if aws_profile:
        os.environ["AWS_PROFILE"] = aws_profile
        final_config["aws_profile"] = aws_profile
        logger.info(f"Using AWS Profile from argument/env: {aws_profile}")
    else:
        final_config["aws_profile"] = os.environ.get("AWS_PROFILE")

    missing_vars: List[str] = []
    if not final_config.get("cluster_id"):
        missing_vars.append("REDSHIFT_CLUSTER_ID or --cluster-id")
    if not final_config.get("database"):
        missing_vars.append("REDSHIFT_DATABASE or --database")
    if not final_config.get("secret_arn"):
        missing_vars.append("REDSHIFT_SECRET_ARN or --secret-arn")
    if not final_config.get("region"):
        missing_vars.append("AWS_REGION/AWS_DEFAULT_REGION or --region")

    if missing_vars:
        # Use typer for more elegant error output
        typer.echo(
            typer.style(
                "Error: Missing required configuration!", fg=typer.colors.RED, bold=True
            )
        )
        typer.echo(
            "\nPlease provide the following configuration items either via command-line arguments or environment variables:"
        )

        # Map description back to CLI option for clarity
        config_map = {
            "REDSHIFT_CLUSTER_ID": "--cluster-id",
            "REDSHIFT_DATABASE": "--database",
            "REDSHIFT_SECRET_ARN": "--secret-arn",
            "AWS_REGION/AWS_DEFAULT_REGION": "--region",
        }

        for var_desc in missing_vars:
            env_var_key = var_desc.split(" or ")[0]  # Get the ENV VAR part
            cli_opt = config_map.get(env_var_key)

            message = f"  - {typer.style(env_var_key, fg=typer.colors.YELLOW)} (Environment Variable)"
            if cli_opt:
                message += f" or {typer.style(cli_opt, fg=typer.colors.CYAN)} (Command-Line Argument)"
            typer.echo(message)

        typer.echo(
            f"\nFor example, set {typer.style('REDSHIFT_CLUSTER_ID', fg=typer.colors.YELLOW)} or use {typer.style('--cluster-id', fg=typer.colors.CYAN)}."
        )
        raise typer.Exit(code=1)

    logger.info("Configuration loaded. Starting MCP server...")

    try:

        mcp.run()
        logger.info("MCP server finished.")
    except DataApiConfigError as e:

        logger.error(f"Configuration Error during server startup: {e}")
        raise typer.Exit(code=1)
    except Exception as e:

        logger.error(
            f"An unexpected error occurred while running the MCP server: {e}",
            exc_info=True,
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
