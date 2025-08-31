from __future__ import annotations

from contextlib import contextmanager
from enum import StrEnum
import json
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Final, Iterator, Annotated, TypedDict
import zipfile
import tempfile
import boto3
import typer

if TYPE_CHECKING:
    from mypy_boto3_lambda import LambdaClient


app = typer.Typer()


LAMBDA_FUNCTION_FILE: Final[str] = "lambda_function.py"
OUTPUT_ZIP_FILE: Final[str] = "deployment_package.zip"


class LambdaInfo(TypedDict):
    runtime: str
    architecture: str


def get_lambda_info(client: LambdaClient, name: str) -> LambdaInfo:
    response = client.get_function_configuration(FunctionName=name)
    match response:
        case {"Runtime": runtime, "Architectures": [architecture]}:
            return {"runtime": runtime, "architecture": architecture}
        case other:
            raise Exception(f"Unexpected response: {other}")


def upload_to_lambda(
    lambda_client: LambdaClient,
    function_name: str,
    zip_file_path: Path,
) -> str:
    """
    Uploads a .zip file to an AWS Lambda function using Boto3.
    """
    # Initialize Boto3 Lambda client
    lambda_client = boto3.client("lambda")

    with zip_file_path.open("rb") as f:
        # Update the function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=f.read(),
        )

    return response["FunctionArn"]


@contextmanager
def create_lambda_package(
    file_path: Path,
    platform: str,
    python_version: str,
) -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = Path(temp_dir)
        requirements = subprocess.run(
            [
                "uv",
                "export",
                "--script",
                str(file_path.absolute()),
                "--python",
                python_version,
            ],
            check=True,
            capture_output=True,
        ).stdout
        requirement_path = dir_path / "requirements.txt"
        requirement_path.write_bytes(requirements)
        dependency_path = dir_path / "dependencies"
        subprocess.run(
            [
                "uv",
                "pip",
                "install",
                "-r",
                str(requirement_path.absolute()),
                "--target",
                str(dependency_path.absolute()),
                "--python-platform",
                platform,
                "--python-version",
                python_version,
                "--link-mode",
                "copy",
                "--only-binary=:all:",
                "--upgrade",
            ],
            check=True,
        )

        requirement_path.unlink()

        path = Path(temp_dir)
        zip_path = path / OUTPUT_ZIP_FILE
        # --- Step 5: Create the final zip file ---
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add all contents of the temporary directory
            # Use rglob to find all files recursively
            for fp in dependency_path.rglob("*"):
                if fp.is_file():
                    # Get the relative path of the file to preserve the directory structure
                    relative_path = fp.relative_to(dependency_path)
                    zf.write(fp, relative_path)

            # Add the main Lambda function file
            zf.write(file_path, LAMBDA_FUNCTION_FILE)
        yield zip_path


class ArchitectureType(StrEnum):
    X86_64 = "x86_64"
    ARM64 = "arm64"


@app.command()
def query(name: str):
    typer.echo(json.dumps(get_lambda_info(boto3.client("lambda"), name)))


@app.command()
def build(
    file_path: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to the main Python file containing the Lambda function handler.",
        ),
    ],
    architecture: Annotated[
        ArchitectureType,
        typer.Option(help="The target architecture of the lambda."),
    ],
    output: Annotated[
        Path,
        typer.Option(
            ...,
            dir_okay=False,
            file_okay=True,
            writable=True,
            resolve_path=True,
            help="Path to the output .zip file.",
        ),
    ] = Path("deployment_package.zip"),
    python_version: Annotated[
        str,
        typer.Option(help="The Python version for the Lambda deployment package."),
    ] = "3.13",
):
    platform = (
        "x86_64-manylinux2014"
        if architecture == ArchitectureType.X86_64
        else "aarch64-manylinux2014"
    )
    with create_lambda_package(file_path, platform, python_version) as path:
        path.replace(output)


@app.command()
def deploy(
    function_name: str,
    file_path: Annotated[
        Path,
        typer.Argument(
            ...,
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
            help="Path to the main Python file containing the Lambda function handler.",
        ),
    ],
):
    lambda_client = boto3.client("lambda")
    info = get_lambda_info(lambda_client, function_name)
    platform = (
        "x86_64-manylinux2014"
        if info["architecture"] == ArchitectureType.X86_64
        else "aarch64-manylinux2014"
    )

    with create_lambda_package(
        file_path,
        platform,
        info["runtime"].removeprefix("python"),
    ) as zip_path:
        arn = upload_to_lambda(lambda_client, function_name, zip_path)
        typer.echo(f"Deployed to {arn}")
