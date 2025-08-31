from pathlib import Path
from operator import attrgetter
import json
import os
import tempfile
import csv
import git
import click
import duckdb

from git_logger.utils import get_hash, parse_csv, parse_schema

class Callback: order = 0

def run_cbs(cbs:list, method_nm:str, data):
    for cb in sorted(cbs, key=attrgetter('order')):
        method = getattr(cb, method_nm, None)
        if method is not None: method(data)


class GitLogger:
    def __init__(self, db_name:str, table_name:str, filepath:str, repo_path:str = ".",
                 data_type:str = "json", cbs:list = None, flexible_schema:bool = False):
        self.db_name = db_name
        self.table_name = table_name
        self.filepath = filepath
        self.repo_path = repo_path
        self.data_type = data_type
        self.flexible_schema = flexible_schema
        self.db_tbl_exist = self._db_and_table_exist()
        self.parse_func = json.loads if data_type == "json" else parse_csv
        self.con = None
        self.cbs = cbs or []

    def _get_file_stream(self, ref:str = "main", commits_to_skip=None, show_progress=True):
        relative_path = str(Path(self.filepath).relative_to(self.repo_path))
        repo = git.Repo(self.repo_path, odbt=git.GitDB)
        commits = reversed(list(repo.iter_commits(ref, paths=[relative_path])))
        progress_bar = None
        if commits_to_skip:
            # Filter down to just the ones we haven't seen
            new_commits = [commit for commit in commits if commit.hexsha not in commits_to_skip]
            commits = new_commits
        if show_progress:
            progress_bar = click.progressbar(commits, show_pos=True, show_percent=True)
        for commit in commits:
            if progress_bar:
                progress_bar.update(1)
            try:
                content = commit.tree[relative_path].data_stream.read()
                yield commit.committed_datetime, commit.hexsha, content
            except KeyError:
                # This commit doesn't have a copy of the requested file
                pass

    def _db_and_table_exist(self):
        "Check if the SQLite database and the table exists."
        if Path(self.db_name ).exists():
            with duckdb.connect(self.db_name) as con:
                con.execute(f"select exists(select * from information_schema.tables where table_name = '{self.table_name}')")
                return con.fetchone()[0]
        return False


    def insert_to_duckdb(self, data: list, timestamp: str, hash: str, con: duckdb.DuckDBPyConnection):
        """
        Save a list of list to a temporary file, load it into duckdb and then remove it.
        Accepts both lists of lists (which will be saved to a csv file) or list of dictionaries (which will be saved to a json file).
        """
        if self.data_type == "json":
            if self.flexible_schema:
                # Store the entire JSON data as a single JSON column
                json_data = json.dumps(data)
                con.execute(f"INSERT INTO {self.table_name} (t, h, data) VALUES (?, ?, ?)", 
                           [timestamp, hash, json_data])
            else:
                # Original logic for structured schema
                with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
                    json.dump(data, f)
                    fname = f.name

                con.sql(f"select '{timestamp}' stime, '{hash}' hash, * from read_json('{fname}')").insert_into(self.table_name)
                os.remove(fname)
        else:
            # CSV data handling (unchanged)
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
                writer = csv.writer(f)
                writer.writerows(data)
                fname = f.name

            con.sql(f"select '{timestamp}' stime, '{hash}' hash, * from read_csv_auto('{fname}')").insert_into(self.table_name)
            os.remove(fname)

    def log_git_history(self):
        commits_to_skip = None
        if self.db_tbl_exist: commits_to_skip = get_hash(db_name=self.db_name, tbl_name=self.table_name)
        git_data = self._get_file_stream(commits_to_skip=commits_to_skip)
        self.con = duckdb.connect(self.db_name)
        for i, git_version in enumerate(git_data):
            self.data = self.parse_func(git_version[2])
            self.callback('format_data')
            if i == 0:
                # import pdb; pdb.set_trace()
                if not self.db_tbl_exist:
                    if self.flexible_schema and self.data_type == "json":
                        # Create simple table with timestamp, hash, and JSON data column
                        self.con.sql(f"CREATE TABLE {self.table_name} (t timestamp, h varchar, data JSON)")
                    else:
                        # Original logic for structured schema
                        if self.data_type == "json":
                            db_schema = parse_schema(self.data[0])
                        else:
                            db_schema = parse_schema({k:v for k,v in zip(self.data[0], self.data[1])})
                        
                        self.con.sql(f"CREATE TABLE {self.table_name} ({'t timestamp, h varchar,'+','.join([f'{k} {v}' for k,v in db_schema.items()])})")
                
                # self.insert_to_duckdb(data=data, timestamp=git_version[0], hash=git_version[1], con=self.con)
            self.insert_to_duckdb(data=self.data, timestamp=git_version[0], hash=git_version[1], con=self.con)
        self.con.close()

    def callback(self, method_nm:str):
        run_cbs(cbs=self.cbs, method_nm=method_nm, data=self)
