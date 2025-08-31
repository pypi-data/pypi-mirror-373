from pathlib import Path
import duckdb
import git
import csv
import json
import pytest

from git_logger.git_history import GitLogger, Callback
from git_logger.utils import get_hash, parse_csv, parse_schema

@pytest.fixture
def git_repo(tmpdir):
    repo = git.Repo.init(tmpdir)
    yield repo

def test_git_logger_json(tmpdir, git_repo):
    # Create a JSON file and commit it twice
    json_file = (tmpdir / "data.json")
    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 40}]
    with open(json_file, "w") as f:
        json.dump(data, f)

    git_repo.git.checkout('-b', 'main')  # Create and checkout the 'main' branch
    git_repo.index.add([json_file])
    git_repo.index.commit("First commit")

    with open(json_file, "w") as f:
        data.append({"name": "Charlie", "age": 50})
        json.dump(data, f)

    git_repo.index.add([json_file])
    git_repo.index.commit("Second commit")

    # Test the GitLogger with the JSON file
    db_name = str(tmpdir / "test.db")
    table_name = "my_table"
    filepath = json_file
    repo_path = str(tmpdir)
    data_type = "json"

    logger = GitLogger(db_name, table_name, filepath, repo_path, data_type)
    logger.log_git_history()

    # Check that the data was inserted correctly
    with duckdb.connect(db_name) as con:
        result = con.sql(f"SELECT * FROM {table_name}").fetchall()
        assert len(result) == 5
        assert set(row[2] for row in result) == {"Alice", "Bob", "Charlie"}

    # Add a third commit and test the commits_to_skip functionality
    with open(json_file, "w") as f:
        data.append({"name": "David", "age": 60})
        json.dump(data, f)

    git_repo.index.add([json_file])
    git_repo.index.commit("Third commit")

    logger = GitLogger(db_name, table_name, filepath, repo_path, data_type)
    logger.log_git_history()

    with duckdb.connect(db_name) as con:
        result = con.sql(f"SELECT * FROM {table_name}").fetchall()
        assert len(result) == 9
        assert set(row[2] for row in result) == {"Alice", "Bob", "Charlie", "David"} 
        assert len(set(row[1] for row in result)) == 3

def test_git_logger_csv(tmpdir, git_repo):
    # Create a CSV file and commit it twice
    csv_file = (tmpdir / "data.csv")
    data = [["name", "age"], ["Alice", "30"], ["Bob", "40"]]
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    git_repo.git.checkout('-b', 'main')  # Create and checkout the 'main' branch
    git_repo.index.add([csv_file])
    git_repo.index.commit("First commit")

    data.append(["Charlie", "50"])
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    git_repo.index.add([csv_file])
    git_repo.index.commit("Second commit")

    # Test the GitLogger with the CSV file
    db_name = str(tmpdir / "test.db")
    table_name = "my_table"
    filepath = csv_file
    repo_path = str(tmpdir)
    data_type = "csv"

    logger = GitLogger(db_name, table_name, filepath, repo_path, data_type)
    logger.log_git_history()

    # Check that the data was inserted correctly
    with duckdb.connect(db_name) as con:
        result = con.sql(f"SELECT * FROM {table_name}").fetchall()
        assert len(result) == 5
        assert set(row[2] for row in result) == {"Alice", "Bob", "Charlie"}


class LineCounterCallback(Callback):
    def __init__(self): self.line_counts = []

    def format_data(self, git_logger):
        self.line_counts.append(len(git_logger.data))

def test_git_logger_callback(tmpdir, git_repo):
    # Create a JSON file and commit it twice
    json_file = (tmpdir / "data.json")
    data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 40}]
    with open(json_file, "w") as f:
        json.dump(data, f)

    git_repo.git.checkout('-b', 'main')  # Create and checkout the 'main' branch
    git_repo.index.add([json_file])
    git_repo.index.commit("First commit")

    with open(json_file, "w") as f:
        data.append({"name": "Charlie", "age": 50})
        json.dump(data, f)

    git_repo.index.add([json_file])
    git_repo.index.commit("Second commit")

    # Test the GitLogger with the JSON file and a callback
    db_name = str(tmpdir / "test.db")
    table_name = "my_table"
    filepath = json_file
    repo_path = str(tmpdir)
    data_type = "json"

    line_counter_callback = LineCounterCallback()
    logger = GitLogger(db_name, table_name, filepath, repo_path, data_type, cbs=[line_counter_callback])
    logger.log_git_history()

    # Check that the callback was executed correctly
    assert len(line_counter_callback.line_counts) == 2
    assert line_counter_callback.line_counts[0] == 2
    assert line_counter_callback.line_counts[1] == 3

def test_git_logger_csv_columns(tmpdir, git_repo):
    # Create a CSV file and commit it twice
    csv_file = (tmpdir / "data.csv")
    data = [["First Name", "Age"], ["Alice", "30"], ["Bob", "40"]]
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    git_repo.git.checkout('-b', 'main')  # Create and checkout the 'main' branch
    git_repo.index.add([csv_file])
    git_repo.index.commit("First commit")

    data.append(["Charlie", "50"])
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(data)

    git_repo.index.add([csv_file])
    git_repo.index.commit("Second commit")

    # Test the GitLogger with the CSV file
    db_name = str(tmpdir / "test.db")
    table_name = "my_table"
    filepath = csv_file
    repo_path = str(tmpdir)
    data_type = "csv"

    logger = GitLogger(db_name, table_name, filepath, repo_path, data_type)
    logger.log_git_history()

    # Check that the data was inserted correctly
    with duckdb.connect(db_name) as con:
        result = con.sql(f"SELECT * FROM {table_name}").fetchall()
        assert len(result) == 5
        assert set(row[2] for row in result) == {"Alice", "Bob", "Charlie"}

        # Check that the column names were parsed correctly
        assert set(col[1] for col in con.execute(f"PRAGMA table_info({table_name})").fetchall()) == {"t", "h", "First_Name", "Age"}