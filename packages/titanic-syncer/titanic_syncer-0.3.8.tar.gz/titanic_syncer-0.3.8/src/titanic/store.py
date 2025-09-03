import os
import shutil
from rich.console import Console
from rich.progress import Progress
from .utils import hash_file, load_ignore_patterns, should_ignore, symlink


def fast_copy(src, dst):
    """Optimized file copy with larger buffer size."""
    with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
        # Use larger buffer (4MB) for better performance with large files
        shutil.copyfileobj(fsrc, fdst, length=4*1024*1024)
    # Copy metadata
    shutil.copystat(src, dst)


def batch_copy_files(file_operations):
    """Batch copy multiple files using system commands for better performance."""
    import subprocess
    import tempfile
    
    if not file_operations:
        return
        
    # For large batches, use system cp which is often faster
    if len(file_operations) > 1000:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sh') as script:
            script.write('#!/bin/bash\n')
            for src, dst in file_operations:
                # Escape paths for shell safety
                src_escaped = src.replace("'", "'\\''")
                dst_escaped = dst.replace("'", "'\\''")
                script.write(f"cp -p '{src_escaped}' '{dst_escaped}'\n")
            script_path = script.name
        
        try:
            subprocess.run(['bash', script_path], check=True, capture_output=True)
        finally:
            os.unlink(script_path)
    else:
        # For smaller batches, use our fast_copy
        for src, dst in file_operations:
            fast_copy(src, dst)


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
    # Get total count first for progress bar
    db_cursor.execute('SELECT COUNT(*) FROM files WHERE project_id = ?', (project_id,))
    total_files = db_cursor.fetchone()[0]

    # Use streaming query instead of fetchall()
    db_cursor.execute('SELECT * FROM files WHERE project_id = ?', (project_id,))

    os.makedirs(output_dir, exist_ok=True)

    console = Console(force_terminal=True)

    # Pre-collect all directories that need to be created
    all_dirs = set()
    temp_cursor = db_cursor.connection.cursor()
    temp_cursor.execute('SELECT path FROM files WHERE project_id = ?', (project_id,))
    for row in temp_cursor:
        dest_path = os.path.join(output_dir, row[0])
        all_dirs.add(os.path.dirname(dest_path))

    # Batch create all directories
    for dir_path in all_dirs:
        os.makedirs(dir_path, exist_ok=True)

    # Pre-process symlink decisions if using "ask" mode
    symlink_decisions = {}
    if symlink_handling == "ask":
        temp_cursor.execute('SELECT path, hash FROM files WHERE project_id = ?', (project_id,))
        for path, file_hash in temp_cursor:
            source_path = os.path.join(store_dir, file_hash[:3], file_hash)
            if os.path.islink(source_path):
                current_target = os.readlink(source_path)
                dest_path = os.path.join(output_dir, path)
                link_target = input(f"{dest_path} is a symlink. Please enter the target path to link to [current: {current_target}]: ") or current_target
                symlink_decisions[path] = link_target

    with Progress(console=console) as progress:
        task = progress.add_task("[green]Recreating project from store...", total=total_files)

        processed = 0
        copy_batch = []
        batch_size = 1000  # Larger batch size
        progress_update_size = 500  # Update progress less frequently

        # Process files in streaming fashion
        while True:
            file_info = db_cursor.fetchone()
            if file_info is None:
                break

            dest_path = os.path.join(output_dir, file_info[1])
            source_path = os.path.join(store_dir, file_info[2][:3], file_info[2])

            if os.path.islink(source_path):
                # Process any pending copies before handling symlink
                if copy_batch:
                    batch_copy_files(copy_batch)
                    copy_batch = []
                
                current_target = os.readlink(source_path)
                if symlink_handling == "ignore":
                    pass  # Skip file
                elif symlink_handling == "leave":
                    symlink(current_target, dest_path, overwrite=True)
                elif symlink_handling == "modify":
                    symlink(current_target.replace(original_path, replacement_path), dest_path, overwrite=True)
                elif symlink_handling == "ask":
                    symlink(symlink_decisions[file_info[1]], dest_path, overwrite=True)
            else:
                # Add to batch for processing
                copy_batch.append((source_path, dest_path))
                
                # Process batch when it reaches batch_size
                if len(copy_batch) >= batch_size:
                    batch_copy_files(copy_batch)
                    copy_batch = []

            processed += 1

            # Less frequent progress updates for better performance
            if processed % progress_update_size == 0:
                progress.update(task, advance=progress_update_size, refresh=True)

        # Process any remaining files in batch
        if copy_batch:
            batch_copy_files(copy_batch)

        # Update any remaining progress
        remaining = processed % progress_update_size
        if remaining > 0:
            progress.update(task, advance=remaining, refresh=True)


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
