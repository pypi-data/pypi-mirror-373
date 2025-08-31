import csv
import duckdb


def parse_schema(d: dict):
    parsed_data = {}
    # fix column names
    d = {k.replace(' ','_'): v for k, v in d.items()}
    for key, value in d.items():
        try:
            _ = int(value)
            parsed_data[key] = 'int'
        except ValueError:
            try:
                _ = float(value)
                parsed_data[key] = 'float'
            except ValueError:
                parsed_data[key] = 'varchar'
    return parsed_data


def parse_csv(data):
    if isinstance(data, bytes): data = data.decode('utf-8')
    reader = csv.reader(data.splitlines())
    rows = []
    for row in reader:
        rows.append(row)
    return rows


def get_hash(db_name: str, tbl_name: str) -> list:
    with duckdb.connect(db_name) as con:
        hash_out = con.sql(f"select distinct h from {tbl_name}").fetchall()
        return [h[0] for h in hash_out]