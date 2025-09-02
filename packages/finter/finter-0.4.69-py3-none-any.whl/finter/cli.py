import os
import shutil

import click

from finter.framework_model.submission.config import get_model_info
from finter.framework_model.submission.helper_poetry import get_docker_file_content
from finter.framework_model.submission.helper_submission import submit_model
from finter.framework_model.validation import ValidationHelper


@click.group()
def finter():
    """Finter CLI - A tool for submitting models with specific configurations."""
    pass


@finter.command()
@click.option(
    "--universe",
    required=True,
    type=click.Choice(
        [
            "kr_stock",
            "us_etf",
            "us_stock",
            "us_future",
            "vn_stock",
            "id_stock",
            "id_bond",
            "id_fund",
            "btcusdt_spot_binance",
            "world",
        ],
        case_sensitive=False,
    ),
    help="The name of the universe (required).",
)
@click.option(
    "--gpu", required=False, is_flag=True, help="Whether to use GPU machine (optional)."
)
@click.option(
    "--image-tag",
    required=False,
    type=click.Choice(["2.1.0-gpu"], case_sensitive=False),
    help="Choose the SageMaker image tag (only applicable if GPU is true).",
)
@click.option(
    "--machine",
    required=False,
    type=click.Choice(["g4dn.4xlarge"], case_sensitive=False),
    help="Choose the machine type (only applicable if GPU is true).",
)
@click.option(
    "--poetry-path",
    required=False,
    type=str,
    help="Path to the directory containing the Poetry 'pyproject.toml' and 'poetry.lock' files to be copied to the current working directory (Optional). This option is not needed if these files already exist in the current workspace. If submitting for GPU tasks, specify only the additional packages required for the SageMaker image.",
)
@click.option(
    "--custom-docker-file",
    required=False,
    is_flag=True,
    help="Whether to use custom docker file (optional). If not provided, an appropriate Dockerfile will be generated.",
)
@click.option(
    "--start",
    required=False,
    type=int,
    help="Start date for submission in YYYYMMDD format (optional). If not provided, the system will automatically calculate the start date during submission.",
)
@click.option(
    "--ignore-local-validation",
    required=False,
    is_flag=True,
    help="Ignore local validation (optional).",
)
@click.option(
    "--benchmark",
    required=False,
    type=str,
    help="Specify a benchmark model to use (optional). Must be an identity_name or universe name.",
)
@click.option(
    "--staging",
    required=False,
    is_flag=True,
    help="Whether to use staging environment (optional).",
)
@click.option(
    "--legacy",
    required=False,
    is_flag=True,
    help="Use legacy submission mode without Docker (deprecated).",
)
def submit(
    universe,
    gpu,
    image_tag,
    machine,
    poetry_path,
    custom_docker_file,
    start,
    ignore_local_validation,
    benchmark,
    staging,
    legacy,
):
    current_dir = os.getcwd()
    click.echo(f"Current working directory: {current_dir}")

    model_alias = os.path.basename(current_dir)
    click.echo(f"Model alias: {model_alias}")

    model_files = [
        f for f in os.listdir(current_dir) if f in ["am.py", "pf.py", "ffd.py"]
    ]

    if len(model_files) != 1:
        click.echo(
            click.style(
                "Error: Exactly one model file (am.py, pf.py, ffd.py) must exist.",
                fg="red",
            ),
            err=True,
        )
        return

    model_file = model_files[0]

    model_type = {"am.py": "alpha", "pf.py": "portfolio", "ffd.py": "flexible_fund"}[
        model_file
    ]

    click.echo(f"Model type: {model_type}")

    poetry_file = os.path.join(current_dir, "pyproject.toml")
    poetry_lock_file = os.path.join(current_dir, "poetry.lock")

    if poetry_path:
        click.echo(f"Copying Poetry files from {poetry_path} to current directory...")
        poetry_source_file = os.path.join(poetry_path, "pyproject.toml")
        poetry_source_lock = os.path.join(poetry_path, "poetry.lock")

        if not os.path.exists(poetry_source_file) or not os.path.exists(
            poetry_source_lock
        ):
            click.echo(
                click.style(
                    f"Error: 'pyproject.toml' or 'poetry.lock' file not found in {poetry_path}",
                    fg="red",
                ),
                err=True,
            )
            return

        try:
            shutil.copy2(poetry_source_file, current_dir)
            shutil.copy2(poetry_source_lock, current_dir)
            click.echo("Poetry files copied successfully")
        except Exception as e:
            click.echo(
                click.style(f"Error copying Poetry files: {e}", fg="red"),
                err=True,
            )
            return
    elif not os.path.exists(poetry_file) and not os.path.exists(poetry_lock_file):
        home_dir = os.path.expanduser("~")
        home_poetry_file = os.path.join(home_dir, "pyproject.toml")
        home_poetry_lock_file = os.path.join(home_dir, "poetry.lock")

        if os.path.exists(home_poetry_file) and os.path.exists(home_poetry_lock_file):
            try:
                shutil.copy2(home_poetry_file, current_dir)
                shutil.copy2(home_poetry_lock_file, current_dir)
                click.echo("Poetry files copied from home directory successfully")
            except Exception as e:
                click.echo(
                    click.style(
                        f"Error copying Poetry files from home directory: {e}",
                        fg="red",
                    ),
                    err=True,
                )
                return

    if not os.path.exists(poetry_file) or not os.path.exists(poetry_lock_file):
        click.echo(
            click.style(
                "Error: 'pyproject.toml' or 'poetry.lock' file not found. Please ensure both exist in the current directory.",
                fg="red",
            ),
            err=True,
        )
        return

    venv_path = os.path.join(current_dir, ".venv")
    if os.path.exists(venv_path) and os.path.isdir(venv_path):
        click.echo(
            click.style(
                "Error: '.venv' directory exists in the submission directory. Virtual environment folders are not allowed for submission. Please either move your virtual environment to another location or delete it before submitting.",
                fg="red",
            ),
            err=True,
        )
        return

    if gpu:
        if not image_tag or not machine:
            click.echo(
                click.style(
                    "Error: Both image_tag and machine must be specified when GPU is true.",
                    fg="red",
                ),
                err=True,
            )
            return

        image = f"sagemaker-distribution:{image_tag}"
        docker_file_content = get_docker_file_content(gpu, image)
        click.echo(
            f"Submitting model: {model_alias}, using GPU with image: {image} and machine: {machine}."
        )
    else:
        if image_tag or machine:
            click.echo(
                "Warning: Image and machine options are ignored when GPU is not used."
            )
        docker_file_content = get_docker_file_content(gpu)
        click.echo(f"Submitting model: {model_alias}")

    docker_file = os.path.join(current_dir, "Dockerfile")

    if custom_docker_file:
        if not os.path.exists(docker_file):
            click.echo(
                click.style(
                    "Error: 'Dockerfile' file not found. Please ensure it exists in the current directory.",
                    fg="red",
                ),
                err=True,
            )
            return
    else:
        with open(docker_file, "w") as file:
            file.write(docker_file_content)

        click.echo(f"Dockerfile saved to {docker_file}")

    model_info = get_model_info(universe, model_type)

    model_info["gpu"] = gpu
    if start:
        model_info["start"] = start
    if benchmark:
        model_info["simulation_info"]["benchmark"] = benchmark

    try:
        if not ignore_local_validation:
            validator = ValidationHelper(
                model_path=current_dir, model_info=model_info, start_date=start
            )
            validator.validate()
        else:
            click.echo("Local validation skipped.")

        if legacy:
            click.echo(
                "Warning: Using legacy submission mode without Docker (deprecated)"
            )

        submit_result = submit_model(
            model_info=model_info,
            output_directory=current_dir,
            docker_submit=not legacy,
            staging=staging,
            model_nickname=model_alias,
        )

        click.echo(
            "Validation URL: "
            + click.style(submit_result.s3_url, fg="blue", underline=True)
        )
    except Exception as e:
        click.echo(
            click.style(f"Error submitting model: {e}", fg="red"),
            err=True,
        )
        return


@finter.command()
@click.option(
    "--path", type=str, required=False, help="Path in format 'folder/model_alias'"
)
def start(path):
    """Create a new model directory with template files.

    Usage:
        finter start --path folder/model_alias
        finter start  # Interactive mode
    """
    if not path:
        click.echo(
            "Interactive mode (alternatively, you can use: finter start --path folder/model_alias)"
        )
        click.echo("Example: models/my_alpha_model")
        click.echo("-" * 50)

        path = click.prompt("Enter path (e.g., 'models/my_alpha_model')", type=str)

    # Create the full path and get model alias
    full_path = os.path.normpath(os.path.join(os.getcwd(), path))

    # 폴더가 이미 존재하는 경우 경고 메시지 출력
    if os.path.exists(full_path):
        if os.listdir(full_path):
            click.echo(
                click.style(
                    f"Error: Directory '{full_path}' already exists.", fg="red"
                ),
                err=True,
            )
            click.echo("Please remove the directory manually and try again.")
            return

    try:
        # Create directories if they don't exist
        os.makedirs(full_path, exist_ok=True)

        # Create am.py with template content
        am_file = os.path.join(full_path, "am.py")
        with open(am_file, "w") as f:
            f.write('''from finter import BaseAlpha
from finter.data import ContentFactory
from finter.modeling.calendar import DateConverter


class Alpha(BaseAlpha):
    """
    Alpha model template function.

    Args:
        start (int): Start date in YYYYMMDD format
        end (int): End date in YYYYMMDD format

    Returns:
        pd.DataFrame: Predictions position dataframe
    """

    universe = "kr_stock"

    # Abstract method
    def get(self, start, end):
        lookback_days = 365
        pre_start = DateConverter.get_pre_start(start, lookback_days)

        cf = ContentFactory(self.universe, pre_start, end)
        price = cf.get_df("price_close")

        rank = price.rolling(21).mean().rank(pct=True, axis=1)

        selected = rank[rank > 0.8]

        position = selected.div(selected.sum(axis=1), axis=0) * 1e8
        position = position.shift()

        return position.loc[str(start) : str(end)]

    # Free method
    def run(self, start, end):
        return self.backtest(self.universe, start, end)


if __name__ == "__main__":
    alpha = Alpha()

    start, end = 20200101, 20240101
    results = alpha.run(start, end)
    results.nav.plot()

    # position = alpha.get(start, end)
''')

        click.echo(f"\nSuccessfully created model template at: {full_path}")
        click.echo("Created files:")
        click.echo(f"  - {am_file}")

    except Exception as e:
        click.echo(
            click.style(f"Error creating model template: {e}", fg="red"),
            err=True,
        )
        return


if __name__ == "__main__":
    finter()
