# git-logger

[![PyPI](https://img.shields.io/pypi/v/git-logger.svg)](https://pypi.org/project/git-logger/)
[![Tests](https://github.com/LVG77/git-logger/actions/workflows/test.yml/badge.svg)](https://github.com/LVG77/git-logger/actions/workflows/test.yml)
[![Changelog](https://img.shields.io/github/v/release/LVG77/git-logger?include_prereleases&label=changelog)](https://github.com/LVG77/git-logger/releases)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/LVG77/git-logger/blob/main/LICENSE)

Python package and CLI tool to log the historical versions of a file preserved in git repository to a DuckDB database.

The package is influenced and inspired heavily by Simon Willison's [git-history](https://github.com/simonw/git-history) package.

## Installation

Install this library using `pip`:
```bash
pip install git-logger
```
## Python API Usage

The `GitLogger` class provides a set of functions to log the history of a file in a Git repository to a DuckDB database.

Here's an example of how to use the `GitLogger` class:

```python
from git_logger.git_history import GitLogger

# Initialize the GitLogger
logger = GitLogger(
    db_name='my_database.db',
    table_name='my_table',
    filepath='path/to/your/file.txt',
    repo_path='path/to/your/git/repo',
    data_type='json'  # or 'csv'
)

# Log the git history to the DuckDB database
logger.log_git_history()
```

The `GitLogger` class takes the following parameters:

- `db_name`: The name of the DuckDB database file.
- `table_name`: The name of the table to store the git history.
- `filepath`: The path to the file in the Git repository.
- `repo_path`: The path to the Git repository (default is the current directory).
- `data_type`: The format of the file, either 'json' or 'csv' (default is 'json').

The `log_git_history()` method retrieves the git history of the specified file, parses the content of the file, and inserts the data into the DuckDB database. The method also creates the database and table if they don't already exist.

The `utils.py` file provides two helper functions:

- `parse_schema(d: dict)`: This function takes a dictionary of data and returns a dictionary of the inferred data types for each key.
- `parse_csv(data)`: This function takes a byte or string representation of CSV data and returns a list of lists.

The `get_hash(db_name: str, tbl_name: str)` function retrieves a list of unique commit hashes from the specified table in the DuckDB database.


### Format data callback

The `GitLogger` class in `git_logger/git_history.py` provides a way to add custom callbacks to format the data before it is inserted into the DuckDB database. The `callback` method in the `GitLogger` class allows you to register these callbacks.

Here's an example of how you can add a custom callback to format the data:

```python
class MyCallback(Callback):
    order = 0  # The order in which the callback is executed

    def format_data(self, data):
        # Customize the data format here
        data.data = [row for row in data.data if row['some_column'] > 0]

logger = GitLogger(
    db_name='my_database.db',
    table_name='my_table',
    filepath='path/to/your/file.txt',
    repo_path='path/to/your/git/repo',
    data_type='json',
    cbs=[MyCallback()]
)

logger.log_git_history()
```

In this example, we define a `MyCallback` class that inherits from the `Callback` class. The `order` attribute determines the order in which the callback is executed (lower values are executed first).

The `format_data` method is the callback that is executed when the `callback('format_data')` method is called in the `GitLogger` class. In this example, we filter the data to only include rows where the `some_column` value is greater than 0.

You can add multiple callbacks by passing a list of callback instances to the `cbs` parameter of the `GitLogger` constructor.


## CLI Usage

The `git-log` cli utility allows you to retrieve the git history of a specified file, parse its content, and insert the data into a DuckDB database from the command line.

Usage:
```
git-log [OPTIONS] FILE_PATH DB_NAME
```

You can run the `git-log` utility without installation using `uvx` tool from `uv` like so:

```bash
uvx --from git-logger git-log path/to/your/file.json file_history.db --table_name my_table
```

Arguments:
- `FILE_PATH`: The path to the file in the Git repository.
- `DB_NAME`: The name of the DuckDB database file.

Options:
- `--table_name TEXT`: The name of the table to store the data (default is "hist").
- `--repo_path TEXT`: The path to the Git repository (default is the current directory).
- `--flexible-schema`: Store JSON data as JSON column type instead of individual columns (default is False).
- `--version`: Show the version and exit.

Examples:
```
git-log path/to/your/file.json file_history.db --table_name my_table
```

This will retrieve the git history of the `file.json` file in the Git repository located at the current directory, parse the JSON content, and insert the data into the `my_table` table in the `file_history.db` DuckDB database.

```
git-log path/to/your/file.json file_history.db --table_name my_table --flexible-schema
```

This will use the flexible schema mode, storing JSON data with inconsistent structures as a single JSON column instead of creating individual columns. This is useful when your JSON file contains objects with varying keys across different git commits.

### Flexible Schema Mode

When working with JSON files that have inconsistent schemas across different git commits (e.g., some objects have different keys), you can use the `--flexible-schema` flag. This mode:

- Creates a simple table structure with only timestamp (`t`), hash (`h`), and JSON data (`data`) columns
- Stores the entire JSON array as a single JSON column in DuckDB
- Avoids binding errors when objects have different numbers of keys
- Allows you to query the JSON data using DuckDB's native JSON functions

This is particularly useful when your JSON file structure evolves over time in your git history.

## Development

To contribute to this library, first checkout the code. Then create a new virtual environment:
```bash
cd git-logger
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
pytest
```
