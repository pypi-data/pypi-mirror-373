import os
import shutil
from rich.console import Console
from rich.progress import Progress
from .utils import hash_file, load_ignore_patterns, should_ignore, symlink


def add_to_store(db_cursor, app_dir, project_id, store_dir, ignore_file=None):
    db_cursor.execute('DELETE FROM files WHERE project_id = ?', (project_id,))

    os.makedirs(store_dir, exist_ok=True)

    if ignore_file is None:
        ignore_file = os.path.join(app_dir, '.titanic-ignore')

    ignore_patterns = load_ignore_patterns(ignore_file)

    all_files = []
    for root, _, files in os.walk(app_dir):
        for file in files:
            filepath = os.path.join(root, file)
            relative_path = os.path.relpath(filepath, app_dir)
            all_files.append((filepath, relative_path))

    console = Console(force_terminal=True)

    with Progress(console=console) as progress:
        task = progress.add_task("[green]Adding files to store...", total=len(all_files))

        for filepath, relative_path in all_files:
            if should_ignore(relative_path, ignore_patterns):
                progress.update(task, advance=1, refresh=True)
                continue

            file_hash = hash_file(filepath)
            file_mode = os.stat(filepath).st_mode
            prefix = file_hash[:3]
            store_path = os.path.join(store_dir, prefix, file_hash)

            db_cursor.execute('''
                INSERT INTO files (path, hash, mode, project_id)
                VALUES (?, ?, ?, ?)
            ''', (relative_path, file_hash, file_mode, project_id))

            if os.path.lexists(store_path):
                progress.update(task, advance=1, refresh=True)
                continue

            os.makedirs(os.path.dirname(store_path), exist_ok=True)
            shutil.copy2(filepath, store_path, follow_symlinks=False)

            progress.update(task, advance=1, refresh=True)

    return True


def recreate_from_store(db_cursor, project_id, output_dir, store_dir, symlink_handling, original_path, replacement_path):
    db_cursor.execute('SELECT * FROM files WHERE project_id = ?', (project_id,))
    files_to_process = db_cursor.fetchall()

    os.makedirs(output_dir, exist_ok=True)

    console = Console(force_terminal=True)

    with Progress(console=console) as progress:
        task = progress.add_task("[green]Recreating project from store...", total=len(files_to_process))

        for file_info in files_to_process:
            dest_path = os.path.join(output_dir, file_info[1])
            source_path = os.path.join(store_dir, file_info[2][:3], file_info[2])

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if os.path.islink(source_path):
                current_target = os.readlink(source_path)
                if symlink_handling == "ignore":
                    progress.update(task, advance=1, refresh=True)
                    continue
                elif symlink_handling == "leave":
                    symlink(current_target, dest_path, overwrite=True)
                elif symlink_handling == "modify":
                    symlink(current_target.replace(original_path, replacement_path), dest_path, overwrite=True)
                elif symlink_handling == "ask":
                    progress.stop()
                    link_target = input(f"{dest_path} is a symlink. Please enter the target path to link to [current: {current_target}]: ") or current_target
                    progress.start()
                    symlink(link_target, dest_path, overwrite=True)
            else:
                shutil.copy2(source_path, dest_path)

            progress.update(task, advance=1, refresh=True)


def list_projects(db_cursor):
    db_cursor.execute('SELECT DISTINCT project_id FROM files')
    return [row[0] for row in db_cursor.fetchall()]


def remove_project(db_cursor, project_id):
    db_cursor.execute('DELETE FROM files WHERE project_id = ?', (project_id,))


def prune_store(db_cursor, store_dir):
    db_cursor.execute('SELECT hash FROM files')
    hashes_in_db = [row[0] for row in db_cursor.fetchall()]

    deleted_size = 0

    console = Console(force_terminal=True)

    with Progress(console=console) as progress:
        task = progress.add_task("[red]Pruning store...", total=1)

        for root, _, files in os.walk(store_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if file not in hashes_in_db and os.path.exists(file_path):
                    deleted_size += os.path.getsize(file_path)
                    os.remove(file_path)

        progress.update(task, advance=1, refresh=True)

    return deleted_size
