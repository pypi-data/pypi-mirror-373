import pytest
import subprocess
import sys
import os

CLI_PATH = os.path.join(os.path.dirname(__file__), '../akron/cli.py')
DB_URL = 'sqlite:///:memory:'

def run_cli(args):
    cmd = [sys.executable, CLI_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_create_table():
    result = run_cli(['create-table', 'users', '--db', DB_URL, '--schema', '{"id": "int", "name": "str"}'])
    assert 'Table users created.' in result.stdout

def test_seed_and_inspect():
    run_cli(['create-table', 'users', '--db', DB_URL, '--schema', '{"id": "int", "name": "str"}'])
    result = run_cli(['seed', 'users', '--db', DB_URL, '--data', '{"id": 1, "name": "Alice"}'])
    assert 'Seeded data into users.' in result.stdout
    result = run_cli(['inspect-schema', 'users', '--db', DB_URL])
    assert 'Alice' in result.stdout

def test_drop_table():
    run_cli(['create-table', 'users', '--db', DB_URL, '--schema', '{"id": "int", "name": "str"}'])
    result = run_cli(['drop-table', 'users', '--db', DB_URL])
    assert 'Table users dropped.' in result.stdout
