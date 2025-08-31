from pathlib import Path
import click
from .git_history import GitLogger

@click.command()
@click.argument(
    "file_path",
    type=click.Path(exists=True)
)
@click.argument(
    "db_name",
    type=str
)
@click.option(
    "--table_name",
    type=str,
    default="hist",
    help="The name of the table to store the data",
)
@click.option(
    "--repo_path",
    type=click.Path(exists=True),
    default=".",
    help="The path to the Git repository",
)
@click.option(
    "--flexible-schema",
    is_flag=True,
    default=False,
    help="Store JSON data as JSON column type instead of individual columns",
)
@click.version_option()
def cli(file_path, db_name, table_name, repo_path, flexible_schema):
    """
    Retrieves the git history of the specified file, parses its content,
    and inserts the data into the DuckDB database.
    """
    file_path = Path(file_path)
    if file_path.suffix == ".json":
        data_type = "json"
    elif file_path.suffix == ".csv":
        data_type = "csv"
    else:
        raise click.ClickException(f"Unsupported file format: {file_path.suffix}. Please provide a JSON or CSV file.")

    logger = GitLogger(
        db_name=db_name,
        table_name=table_name,
        filepath=str(file_path),
        repo_path=repo_path,
        data_type=data_type,
        flexible_schema=flexible_schema,
    )
    logger.log_git_history()
    click.echo(f"Git history has been logged to {db_name}.{table_name}")