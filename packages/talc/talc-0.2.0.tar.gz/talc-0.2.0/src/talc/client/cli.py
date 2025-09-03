import asyncio
import datetime
import json
import os
from pathlib import Path
from typing import Any

import click
from pydantic import BaseModel
import yaml

from talc.client.api import (
    get_extraction_job,
    get_extraction_job_output,
    make_api_request,
    start_extraction_job,
    upload_execution_plan,
)
from talc.client.files import upload_file
from talc.client.shared import GetExtractionJobResult
from talc.client.vscode import get_vscode_settings_path

AUTH_TOKEN = os.getenv("TALC_AUTH")
SERVICE_ENDPOINT = os.getenv("TALC_ENDPOINT")


def _check_env():
    if not AUTH_TOKEN:
        raise click.ClickException(
            "TALC_AUTH environment variable is not set; set it to your Talc API token."
        )
    if not SERVICE_ENDPOINT:
        raise click.ClickException(
            "TALC_ENDPOINT environment variable is not set; set it to your Talc service endpoint."
        )


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--scenario",
    help="Scenario configuration file",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "--data", help="Data file (CSV)", required=True, type=click.Path(exists=True)
)
@click.option(
    "--no-wait",
    is_flag=True,
    help="Do not wait for the job to complete; just start it and exit, printing the job ID to STDOUT.",
)
def extract(scenario: str, data: str, no_wait: bool = False):
    """
    Start an extraction job using the specified scenario and data file.

    The scenario file should be a YAML file that defines the extraction configuration. Example:

    \b
        data_config:
          aggregation_columns:
            - subject_id
          ignored_columns:
            - filename
        attributes:
          blood_clot:
            labels:
              has_blood_clot: |
                The patient has any history of PE or **lower-body** DVT
              ambiguous: |
                The patient may have a PE or **lower-body** DVT, but there is not enough information to be sure
              otherwise: |
                (otherwise)
            rules:
              - Do not infer DVT location or extent beyond what is directly indicated by the text.
              - Do not use medical judgement to infer diagnosis of PE or DVT. Only use diagnoses directly indicated by the text.
          t1d:
            labels:
              has_t1d: |
                The patient has a Type 1 diabetes diagnosis
              ambiguous: |
                The patient may have had a Type 1 diabetes diagnosis, but there is not enough information to be sure (for example: the patient has a history of diabetes, but it is not specified whether it is Type 1 or Type 2)
              otherwise: |
                (otherwise)
            rules:
              - Do not use medical judgement to infer a diabetes diagnosis. Only use diagnoses directly indicated by the text.
    """

    _check_env()

    async def main():
        with open(scenario, "r") as f:
            scenario_config = yaml.safe_load(f)

        data_file_id = await upload_file(Path(data))

        start_job_response = await start_extraction_job(
            scenario=scenario_config,
            data_file_id=data_file_id,
        )

        job_id = start_job_response.job_id

        if no_wait:
            click.echo(f"{job_id}", err=False)
            return

        click.echo(f"Started extraction job with ID: {job_id}", err=True)

        while True:
            await asyncio.sleep(5)  # Poll every 5 seconds

            status = await get_extraction_job(job_id)

            _print_job_status(status)

            if status.status in {"completed", "failed", "abandoned"}:
                return

    asyncio.run(main())


@cli.command()
@click.argument("job_id", required=True)
@click.option(
    "--no-wait",
    is_flag=True,
    help="Do not wait for the job to complete; just print the status and exit.",
)
def status(job_id: str, no_wait: bool):
    """
    Fetch the status of a extraction job by its ID, and optionally wait for it to complete.
    """

    _check_env()

    async def main():
        while True:
            if not no_wait:
                click.echo(
                    f"Polling every 5 seconds for job {job_id} status...", err=True
                )

            status = await get_extraction_job(job_id)

            _print_job_status(status)

            if no_wait or status.status in {"completed", "failed", "abandoned"}:
                return

            await asyncio.sleep(5)

    asyncio.run(main())


def _print_job_status(status: GetExtractionJobResult):
    heartbeat_seconds_ago = (
        datetime.datetime.now() - status.last_heartbeat_timestamp
    ).total_seconds()

    click.echo(
        f"Job {status.job_id} status: {status.status}, last heartbeat: {status.last_heartbeat_timestamp} ({heartbeat_seconds_ago:.0f} seconds ago)",
        err=True,
    )

    match status.status:
        case "completed":
            click.echo("Job completed successfully.", err=True)
            click.echo(
                f"To fetch the output, run `talc output {status.job_id}`.", err=True
            )
            return
        case "failed":
            click.echo("Job failed.", err=True)
            if status.failure_reason:
                click.echo(f"Failure reason: {status.failure_reason}", err=True)
            return
        case "abandoned":
            click.echo(
                "Job was abandoned; this is likely due to a server restart.",
                err=True,
            )
            return
        case "running":
            pass


@cli.command()
@click.argument("job_id", required=True)
@click.option(
    "--format",
    default="json",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    help="Output format for the results (default: json)",
)
def output(job_id: str, format: str = "json"):
    """
    Fetch the results of a completed extraction job by its ID.

    The results will be printed to STDOUT.
    """

    _check_env()

    async def main():
        await get_extraction_job_output(job_id, format=format)  # type: ignore

    asyncio.run(main())


@cli.command(hidden=True)
@click.option(
    "--file",
    help="Path to the file to upload",
    required=True,
    type=click.Path(exists=True),
)
def upload(file: str):
    _check_env()
    uploaded_file_id = asyncio.run(upload_file(Path(file)))
    click.echo(f"File uploaded with ID: {uploaded_file_id}")


@cli.command()
def schema():
    """
    Fetch the JSON schema for the scenario configuration file and print it to STDOUT.
    """

    _check_env()

    async def main():
        response = await make_api_request(
            response_model=dict[str, Any],
            path="/metadata",
        )
        jsonschema = response["scenario_file_jsonschema"]
        click.echo(json.dumps(jsonschema, indent=2))

    asyncio.run(main())


@cli.command()
def vscode():
    """
    Update VSCode settings to use Talc config's format; this is experimental and **will modify** your user VSCode settings file.
    """

    _check_env()

    async def main():
        response = await make_api_request(
            response_model=dict[str, Any],
            path="/metadata",
        )
        jsonschema = response["scenario_file_jsonschema"]

        talc_dir = Path.home() / ".talc"
        talc_dir.mkdir(exist_ok=True)
        schema_path = talc_dir / "scenario.jsonschema"

        with open(schema_path, "w") as f:
            json.dump(jsonschema, f, indent=2)

        vscode_settings_path = get_vscode_settings_path()
        if not vscode_settings_path:
            click.echo(
                f"I'm not sure where VSCode settings live on this platform. Add a `yaml.schemas` entry to your VSCode settings manually:\n\n"
                f"  {{\n"
                f'      "yaml.schemas": {{"{schema_path.resolve()}": "*.talc.yaml"}}\n'
                f"  }}\n\n"
            )
            return

        with open(vscode_settings_path, "r") as f:
            vscode_settings = json.load(f)

        if "yaml.schemas" not in vscode_settings:
            vscode_settings["yaml.schemas"] = {}

        # if there's already an entry for *.talc.yaml, remove it
        for key in list(vscode_settings["yaml.schemas"].keys()):
            if vscode_settings["yaml.schemas"][key] == "*.talc.yaml":
                del vscode_settings["yaml.schemas"][key]

        vscode_settings["yaml.schemas"][str(schema_path.resolve())] = "*.talc.yaml"

        with open(vscode_settings_path, "w") as f:
            json.dump(vscode_settings, f, indent=2)

        click.echo(
            f"\nUpdated VSCode settings at {vscode_settings_path} to use Talc config schema at {schema_path.resolve()}\n\n"
            f"Make sure that the 'YAML Language Support by Red Hat' extension is installed.\n"
        )

    asyncio.run(main())


@cli.command()
@click.option(
    "--file",
    help="Path to the TypeScript file containing the execution plan",
    required=True,
    type=click.Path(exists=True),
)
def upload_plan(file: str):
    """
    Upload a TypeScript file containing an execution plan to the Talc server.
    """

    _check_env()

    async def main():
        with open(file, "r") as f:
            ts_code = f.read()

        response = await upload_execution_plan(ts_code)
        click.echo(f"Execution plan uploaded with ID: {response.plan_id}")

    asyncio.run(main())


@cli.command()
@click.option(
    "--plan-file",
    help="Path to the TypeScript file containing the execution plan",
    required=True,
    type=click.Path(exists=True),
)
@click.option(
    "--data", help="Data file (CSV)", required=True, type=click.Path(exists=True)
)
@click.option(
    "--no-wait",
    is_flag=True,
    help="Do not wait for the plan to complete; just start it and exit, printing the plan ID to STDOUT.",
)
@click.option(
    "--id-column",
    help="Column name containing the patient ID in the data file",
    required=True,
)
@click.option(
    "--note-column",
    help="Column name containing the free-text note in the data file",
    required=True,
)
@click.option(
    "--note-id-column",
    help="Column name containing the note ID in the data file",
    required=False,
    default=None,
)
def run_plan(
    plan_file: str,
    data: str,
    id_column: str,
    note_column: str,
    note_id_column: str | None = None,
    no_wait: bool = False,
):

    _check_env()

    async def main():
        with open(plan_file, "r") as f:
            ts_code = f.read()

        response = await upload_execution_plan(ts_code)

        plan_id = response.plan_id

        click.echo(f"Execution plan uploaded with ID: {plan_id}", err=True)

        data_file_id = await upload_file(Path(data))

        class PlanExecutionConfig(BaseModel):
            data_config: dict[str, Any]
            attributes: dict[str, Any]
            plan_execution_config: dict[str, Any]

        start_job_response = await start_extraction_job(
            scenario=PlanExecutionConfig(
                data_config={
                    "aggregation_columns": [id_column],
                    "ignored_columns": ["filename"],
                    "note_column": note_column,
                    "note_id_column": note_id_column,
                },
                attributes={},
                plan_execution_config={
                    "execution_plan_id": plan_id,
                },
            ),
            data_file_id=data_file_id,
        )

        job_id = start_job_response.job_id

        click.echo(f"Extraction job started with ID: {job_id}")

        if no_wait:
            click.echo(f"{job_id}", err=False)
            return

        click.echo(f"Waiting for job {job_id} to complete...", err=True)

        while True:
            await asyncio.sleep(5)
            status = await get_extraction_job(job_id)
            _print_job_status(status)
            if status.status in {"completed", "failed", "abandoned"}:
                return
            click.echo(f"Job {job_id} is still running...", err=True)

    asyncio.run(main())


if __name__ == "__main__":
    cli()
