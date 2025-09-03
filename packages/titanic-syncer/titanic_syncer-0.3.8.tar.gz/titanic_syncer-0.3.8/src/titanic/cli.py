import os
import click
import sqlite3
from .store import add_to_store, list_projects, prune_store, recreate_from_store, remove_project
from .sync import sync_metadata_and_files
from importlib.metadata import version, PackageNotFoundError

HOME_PATH = os.path.expanduser("~")
DEFAULT_STORE_PATH = os.path.join(HOME_PATH, ".titanic_store")
DEFAULT_DB_PATH = os.path.join(HOME_PATH, ".titanic-metadata.db")


def get_version():
    try:
        return version("titanic-syncer")
    except PackageNotFoundError:
        try:
            with open("pyproject.toml") as f:
                for line in f:
                    if "version" in line:
                        return line.split("=")[1].strip().replace('"', '')
        except FileNotFoundError:
            pass
    return "unknown"


def init_database(db_path):
    if not os.path.exists(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            hash TEXT NOT NULL,
            mode INTEGER NOT NULL,
            project_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor


@click.group()
@click.option('--store-dir', type=click.Path(), default=DEFAULT_STORE_PATH, help="Path to the store directory (default: ~/.titanic_store).")
@click.option('--db-path', type=click.Path(), default=DEFAULT_DB_PATH, help="Path to the SQLite database file (default: ~/.titanic-metadata.db).")
@click.version_option(get_version())
@click.pass_context
def cli(ctx, store_dir, db_path):
    ctx.ensure_object(dict)
    ctx.obj['STORE_DIR'] = store_dir
    ctx.obj['DB_PATH'] = db_path
    conn, cursor = init_database(db_path)
    ctx.obj['DB_CURSOR'] = cursor
    ctx.obj['DB_CONN'] = conn


@cli.command()
@click.argument('app_dir', type=click.Path(exists=True))
@click.argument('project_id')
@click.option('--ignore-file', type=click.Path(exists=True), help="Path to a custom ignore file.")
@click.pass_context
def add(ctx, app_dir, project_id, ignore_file):
    store_dir = ctx.obj['STORE_DIR']
    db_cursor = ctx.obj['DB_CURSOR']
    db_conn = ctx.obj['DB_CONN']
    if add_to_store(db_cursor, app_dir, project_id, store_dir, ignore_file):
        db_conn.commit()
        click.echo(f"Added files from {app_dir} to titanic store.")


@cli.command()
@click.argument('project_id')
@click.argument('output_dir', type=click.Path(exists=False))
@click.option(
    "--symlink-handling",
    type=click.Choice(["ask", "leave", "modify", "ignore"], case_sensitive=False),
    default="ask",
    help="Specify how to handle symlinks: 'ask' (default), 'leave' (keep original), 'modify' (change path), or 'ignore' (don't copy)."
)
@click.option(
    "--original-path", type=click.Path(), default=None, help="Path to replace in symlink (required for 'modify' option)."
)
@click.option(
    "--replacement-path", type=click.Path(), default=None, help="Replacement path for symlink (required for 'modify' option)."
)
@click.pass_context
def recreate(ctx, project_id, output_dir, symlink_handling, original_path, replacement_path):
    store_dir = ctx.obj['STORE_DIR']
    db_cursor = ctx.obj['DB_CURSOR']

    if symlink_handling == "modify" and (original_path is None or replacement_path is None):
        raise click.UsageError("Both --original-path and --replacement-path must be provided for 'modify' option.")

    recreate_from_store(db_cursor, project_id, output_dir, store_dir, symlink_handling, original_path, replacement_path)
    click.echo(f"Recreated {project_id} in {output_dir}.")


@cli.command()
@click.argument('project_id')
@click.argument('output_dir')
@click.argument('remote_server')
@click.option(
    '--remote-metadata-path',
    type=click.Path(),
    default="~/.titanic-metadata.db",
    help="Path to the remote server's metadata file (default: ~/.titanic-metadata.db)."
)
@click.option(
    '--remote-store-dir',
    type=click.Path(),
    default="~/.titanic_store",
    help="Path to the remote server's store directory (default: ~/.titanic_store)."
)
@click.option(
    "--symlink-handling",
    type=click.Choice(["ask", "leave", "modify", "ignore"], case_sensitive=False),
    default="ask",
    help="Specify how to handle symlinks: 'ask' (default), 'leave' (keep original), 'modify' (change path), or 'ignore' (don't copy)."
)
@click.option(
    "--original-path", type=click.Path(), default=None, help="Path to replace in symlink (required for 'modify' option)."
)
@click.option(
    "--replacement-path", type=click.Path(), default=None, help="Replacement path for symlink (required for 'modify' option)."
)
@click.pass_context
def sync(ctx, project_id, output_dir, remote_server, remote_metadata_path, remote_store_dir, symlink_handling, original_path, replacement_path):
    store_dir = ctx.obj['STORE_DIR']
    db_cursor = ctx.obj['DB_CURSOR']
    db_conn = ctx.obj['DB_CONN']

    if symlink_handling == "modify" and (original_path is None or replacement_path is None):
        raise click.UsageError("Both --original-path and --replacement-path must be provided for 'modify' option.")

    if sync_metadata_and_files(db_cursor, remote_server, project_id, remote_metadata_path, store_dir, remote_store_dir):
        recreate_from_store(db_cursor, project_id, output_dir, store_dir, symlink_handling, original_path, replacement_path)
        db_conn.commit()
        click.echo(f"Synced and recreated {output_dir} from {remote_server}.")


@cli.command()
@click.pass_context
def list(ctx):
    db_cursor = ctx.obj['DB_CURSOR']
    projects = list_projects(db_cursor)
    for project in projects:
        click.echo(f"{project}")
    click.echo(f"Total projects: {len(projects)}")


@cli.command()
@click.argument('project_ids', nargs=-1)
@click.pass_context
def remove(ctx, project_ids):
    if not project_ids:
        click.echo("Please provide at least one project ID to remove.")
        return

    db_cursor = ctx.obj['DB_CURSOR']
    db_conn = ctx.obj['DB_CONN']

    for project_id in project_ids:
        remove_project(db_cursor, project_id)
        click.echo(f"Removed project {project_id}.")

    db_conn.commit()
    ctx.invoke(prune)


@cli.command()
@click.pass_context
def prune(ctx):
    store_dir = ctx.obj['STORE_DIR']
    db_cursor = ctx.obj['DB_CURSOR']
    deleted_size = prune_store(db_cursor, store_dir)
    click.echo(f"Pruned {deleted_size} bytes from the store.")


